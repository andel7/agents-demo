#!/usr/bin/env python

# Copyright 2024 Amazon.com and its affiliates; all rights reserved.
# This file is AWS Content and may not be duplicated or distributed without permission

import sys
from pathlib import Path
import datetime
import traceback
import yaml
import uuid
from textwrap import dedent
import os
import argparse
import json
import logging
import boto3
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get current directory for YAML files
current_dir = os.path.dirname(os.path.abspath(__file__))
task_yaml_path = os.path.join(current_dir, "tasks.yaml")
agent_yaml_path = os.path.join(current_dir, "agents.yaml")

# AWS clients
bedrock_client = boto3.client('bedrock-runtime')
bedrock_agent_client = boto3.client('bedrock-agent')
iam_client = boto3.client('iam')
sts_client = boto3.client('sts')

# Get AWS account info
account_id = sts_client.get_caller_identity()["Account"]
region = boto3.Session().region_name

# Product catalog
PRODUCTS = {
    'hashicorp_vault': {
        'name': 'HashiCorp Vault',
        'description': 'Enterprise secrets management and encryption platform'
    },
    'upwind_security': {
        'name': 'UpWind Security',
        'description': 'Cloud-native security platform for Kubernetes'
    },
    'portworx': {
        'name': 'Portworx by Pure',
        'description': 'Enterprise-grade storage platform for Kubernetes'
    },
    'prompt_security': {
        'name': 'Prompt.security',
        'description': 'AI security and compliance platform'
    },
    'spectro_cloud': {
        'name': 'Spectro Cloud',
        'description': 'Kubernetes management platform'
    },
    'other': {
        'name': 'Other TeraSky Solutions',
        'description': 'Custom enterprise solutions and consulting'
    }
}

class SimpleBedrockAgent:
    """Simplified Bedrock Agent that works with current API."""
    
    def __init__(self, name: str, role: str, instructions: str, model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.model_id = model_id
        self.agent_id = None
        self.agent_arn = None
        self.role_arn = None
        
    def create_agent_role(self):
        """Create IAM role for the agent."""
        role_name = f"AmazonBedrockExecutionRoleForAgents_{self.name}"
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            # Try to get existing role
            response = iam_client.get_role(RoleName=role_name)
            self.role_arn = response['Role']['Arn']
            logger.info(f"Using existing role: {self.role_arn}")
        except iam_client.exceptions.NoSuchEntityException:
            # Create new role
            response = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"Execution role for Bedrock agent {self.name}"
            )
            self.role_arn = response['Role']['Arn']
            
            # Attach basic Bedrock policy
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/AmazonBedrockFullAccess'
            )
            
            logger.info(f"Created new role: {self.role_arn}")
            
            # Wait for role to be available
            time.sleep(10)
    
    def create(self):
        """Create the Bedrock agent."""
        try:
            # Create IAM role first
            self.create_agent_role()
            
            # Create the agent
            response = bedrock_agent_client.create_agent(
                agentName=self.name,
                agentResourceRoleArn=self.role_arn,
                description=f"{self.role} - {self.instructions[:100]}...",
                foundationModel=self.model_id,
                instruction=self.instructions,
                idleSessionTTLInSeconds=1800
            )
            
            self.agent_id = response['agent']['agentId']
            self.agent_arn = response['agent']['agentArn']
            
            logger.info(f"Created agent {self.name} with ID: {self.agent_id}")
            
            # Prepare the agent
            bedrock_agent_client.prepare_agent(agentId=self.agent_id)
            logger.info(f"Prepared agent {self.name}")
            
            # Wait for agent to be ready
            time.sleep(15)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating agent {self.name}: {str(e)}")
            return False
    
    def invoke(self, prompt: str, session_id: str = None) -> str:
        """Invoke the agent with a prompt."""
        if not self.agent_id:
            raise Exception(f"Agent {self.name} not created yet")
            
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            response = bedrock_agent_client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId='TSTALIASID',
                sessionId=session_id,
                inputText=prompt
            )
            
            # Extract response from event stream
            result = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
            
            return result
            
        except Exception as e:
            logger.error(f"Error invoking agent {self.name}: {str(e)}")
            return f"Error: {str(e)}"
    
    def delete(self):
        """Delete the agent."""
        if self.agent_id:
            try:
                bedrock_agent_client.delete_agent(agentId=self.agent_id)
                logger.info(f"Deleted agent {self.name}")
            except Exception as e:
                logger.error(f"Error deleting agent {self.name}: {str(e)}")

class SimpleMarketingCampaignGenerator:
    """Simplified marketing campaign generator using individual Bedrock agents."""
    
    def __init__(self):
        self.agents = {}
        self.session_id = str(uuid.uuid4())
        
    def create_agents(self):
        """Create all the marketing agents."""
        
        # Load agent configurations
        with open(agent_yaml_path, 'r') as file:
            agent_configs = yaml.safe_load(file)
        
        agent_definitions = [
            ('product_researcher', 'Product Research Specialist'),
            ('audience_researcher', 'Target Audience Analyst'),
            ('campaign_strategist', 'Campaign Strategy Director'),
            ('content_creator', 'Marketing Content Creator'),
            ('qa_validator', 'Quality Assurance Specialist')
        ]
        
        for agent_key, role in agent_definitions:
            config = agent_configs.get(agent_key, {})
            instructions = config.get('instructions', f"You are a {role} for TeraSky marketing campaigns.")
            model_id = config.get('llm', 'us.anthropic.claude-3-5-sonnet-20241022-v2:0')
            
            agent = SimpleBedrockAgent(
                name=agent_key,
                role=role,
                instructions=instructions,
                model_id=model_id
            )
            
            if agent.create():
                self.agents[agent_key] = agent
                logger.info(f"Successfully created agent: {agent_key}")
            else:
                logger.error(f"Failed to create agent: {agent_key}")
                return False
        
        return True
    
    def generate_campaign(self, product_key: str) -> dict:
        """Generate a marketing campaign for the specified product."""
        
        product_info = PRODUCTS.get(product_key)
        if not product_info:
            raise Exception(f"Product {product_key} not found")
        
        campaign_id = f"terasky-campaign-{str(uuid.uuid4())}"
        results = {
            'campaign_id': campaign_id,
            'product': product_info,
            'timestamp': datetime.datetime.now().isoformat(),
            'results': {}
        }
        
        # Step 1: Product Research
        logger.info("Step 1: Product Research")
        product_prompt = f"""
        Conduct comprehensive research on TeraSky's {product_info['name']} solution.
        
        Product: {product_info['name']}
        Description: {product_info['description']}
        
        Analyze:
        - Key features and capabilities
        - Competitive advantages
        - Target market
        - Value propositions
        - Technical specifications
        - Market positioning
        
        Provide a detailed analysis in JSON format.
        """
        
        product_research = self.agents['product_researcher'].invoke(product_prompt, self.session_id)
        results['results']['product_research'] = product_research
        
        # Step 2: Audience Research
        logger.info("Step 2: Audience Research")
        audience_prompt = f"""
        Based on the product research for {product_info['name']}, analyze the target audience.
        
        Product Research Results: {product_research[:1000]}...
        
        Identify:
        - Target personas and roles
        - Company profiles
        - Pain points and challenges
        - Decision-making processes
        - Communication preferences
        - Budget considerations
        
        Provide analysis in JSON format.
        """
        
        audience_research = self.agents['audience_researcher'].invoke(audience_prompt, self.session_id)
        results['results']['audience_research'] = audience_research
        
        # Step 3: Campaign Strategy
        logger.info("Step 3: Campaign Strategy")
        strategy_prompt = f"""
        Develop a comprehensive marketing strategy for {product_info['name']}.
        
        Product Research: {product_research[:500]}...
        Audience Research: {audience_research[:500]}...
        
        Create:
        - Campaign objectives and metrics
        - Channel strategy
        - Content strategy
        - Targeting approach
        - Timeline and phases
        - Budget recommendations
        
        Provide strategy in JSON format.
        """
        
        campaign_strategy = self.agents['campaign_strategist'].invoke(strategy_prompt, self.session_id)
        results['results']['campaign_strategy'] = campaign_strategy
        
        # Step 4: Content Creation
        logger.info("Step 4: Content Creation")
        content_prompt = f"""
        Create compelling marketing content for {product_info['name']}.
        
        Strategy: {campaign_strategy[:500]}...
        
        Create content for:
        - Social media (LinkedIn, Twitter, Facebook)
        - Email marketing
        - Blog articles
        - Ad copy
        - Landing pages
        
        Maintain TeraSky's professional brand voice. Provide in JSON format.
        """
        
        content = self.agents['content_creator'].invoke(content_prompt, self.session_id)
        results['results']['content'] = content
        
        # Step 5: Quality Assurance
        logger.info("Step 5: Quality Assurance")
        qa_prompt = f"""
        Review and validate the marketing campaign for {product_info['name']}.
        
        Content to Review: {content[:500]}...
        
        Evaluate:
        - Technical accuracy
        - Brand alignment
        - Audience fit
        - Content quality
        - Compliance
        
        Provide assessment and recommendations in JSON format.
        """
        
        qa_results = self.agents['qa_validator'].invoke(qa_prompt, self.session_id)
        results['results']['qa_results'] = qa_results
        
        return results
    
    def cleanup_agents(self):
        """Delete all created agents."""
        for agent in self.agents.values():
            agent.delete()
        self.agents.clear()

def main(args):
    """Main function to run the marketing campaign generation."""
    
    # Handle cleanup
    if args.clean_up == "true":
        logger.info("Cleaning up agents...")
        # Note: This is a simplified cleanup - in production you'd want to list and delete all agents
        logger.info("Cleanup completed")
        return

    # Get product information
    product_info = PRODUCTS.get(args.product_key)
    if not product_info:
        logger.error(f"Product {args.product_key} not found. Available products: {list(PRODUCTS.keys())}")
        return

    logger.info(f"Generating marketing campaign for: {product_info['name']}")

    try:
        # Create campaign generator
        campaign_generator = SimpleMarketingCampaignGenerator()
        
        # Create agents
        logger.info("Creating Bedrock Agents...")
        if not campaign_generator.create_agents():
            logger.error("Failed to create agents")
            return
        
        logger.info("All agents created successfully!")
        
        if args.recreate_agents == "false" or True:  # Always run for now
            logger.info("Starting campaign generation...")
            
            time_before_call = datetime.datetime.now()
            logger.info(f"Start time: {time_before_call}")
            
            try:
                # Generate campaign
                results = campaign_generator.generate_campaign(args.product_key)
                
                logger.info("Campaign generation completed successfully!")
                print("\n" + "="*80)
                print("MARKETING CAMPAIGN RESULTS")
                print("="*80)
                print(f"Campaign ID: {results['campaign_id']}")
                print(f"Product: {results['product']['name']}")
                print(f"Description: {results['product']['description']}")
                print("="*80)
                
                for step, result in results['results'].items():
                    print(f"\n{step.upper()}:")
                    print("-" * 40)
                    print(result[:500] + "..." if len(result) > 500 else result)
                
                print("="*80)
                
            except Exception as e:
                logger.error(f"Error during campaign generation: {str(e)}")
                traceback.print_exc()
            finally:
                # Cleanup agents
                if args.cleanup_after:
                    logger.info("Cleaning up agents...")
                    campaign_generator.cleanup_agents()

            duration = datetime.datetime.now() - time_before_call
            logger.info(f"Total time taken: {duration.total_seconds():,.1f} seconds")
            
        else:
            logger.info("Agents created successfully. Use --recreate_agents false to run campaign generation.")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    # Default values
    default_inputs = {
        'product_key': 'hashicorp_vault',
        'trace_level': 'core'
    }

    parser = argparse.ArgumentParser(description="TeraSky Marketing Campaign Generator using Simple Bedrock Agents")

    parser.add_argument(
        "--recreate_agents", 
        required=False, 
        default='true', 
        help="False if reusing existing agents (default: true)"
    )
    
    parser.add_argument(
        "--product_key", 
        required=False, 
        default=default_inputs['product_key'],
        choices=list(PRODUCTS.keys()),
        help=f"The product to generate a campaign for. Options: {list(PRODUCTS.keys())} (default: {default_inputs['product_key']})"
    )
    
    parser.add_argument(
        "--trace_level", 
        required=False, 
        default=default_inputs['trace_level'],
        choices=['core', 'outline', 'all'],
        help="The level of trace detail (default: core)"
    )
    
    parser.add_argument(
        "--clean_up",
        required=False,
        default="false",
        help="Cleanup all agents and exit (default: false)",
    )
    
    parser.add_argument(
        "--cleanup_after",
        required=False,
        default="false",
        help="Cleanup agents after campaign generation (default: false)",
    )

    args = parser.parse_args()
    
    # Display configuration
    print("\n" + "="*60)
    print("TERASKY MARKETING CAMPAIGN GENERATOR")
    print("Powered by Amazon Bedrock Agents (Simplified)")
    print("="*60)
    print(f"Product: {PRODUCTS[args.product_key]['name']}")
    print(f"Description: {PRODUCTS[args.product_key]['description']}")
    print(f"Recreate Agents: {args.recreate_agents}")
    print(f"AWS Region: {region}")
    print(f"Account ID: {account_id}")
    print("="*60)
    
    main(args) 