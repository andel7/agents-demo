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

# Add the parent directory to the path to import bedrock_agent utilities
sys.path.append(str(Path(__file__).parent.parent))
from src.utils.bedrock_agent import Agent, SupervisorAgent, Task, region, account_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get current directory for YAML files
current_dir = os.path.dirname(os.path.abspath(__file__))
task_yaml_path = os.path.join(current_dir, "tasks.yaml")
agent_yaml_path = os.path.join(current_dir, "agents.yaml")

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

def main(args):
    """Main function to run the marketing campaign generation."""
    
    # Handle cleanup
    if args.clean_up == "true":
        logger.info("Cleaning up all agents...")
        Agent.delete_by_name("marketing_supervisor", verbose=True)
        Agent.delete_by_name("product_researcher", verbose=True)
        Agent.delete_by_name("audience_researcher", verbose=True)
        Agent.delete_by_name("campaign_strategist", verbose=True)
        Agent.delete_by_name("content_creator", verbose=True)
        Agent.delete_by_name("qa_validator", verbose=True)
        logger.info("Cleanup completed")
        return

    # Set force recreate based on parameter
    if args.recreate_agents == "false":
        Agent.set_force_recreate_default(False)
    else:
        Agent.set_force_recreate_default(True)
        # Clean up existing agents if recreating
        logger.info("Cleaning up existing agents for recreation...")
        Agent.delete_by_name("marketing_supervisor", verbose=True)
        Agent.delete_by_name("product_researcher", verbose=True)
        Agent.delete_by_name("audience_researcher", verbose=True)
        Agent.delete_by_name("campaign_strategist", verbose=True)
        Agent.delete_by_name("content_creator", verbose=True)
        Agent.delete_by_name("qa_validator", verbose=True)

    # Get product information
    product_info = PRODUCTS.get(args.product_key)
    if not product_info:
        logger.error(f"Product {args.product_key} not found. Available products: {list(PRODUCTS.keys())}")
        return

    logger.info(f"Generating marketing campaign for: {product_info['name']}")

    # Prepare inputs for tasks
    inputs = {
        'product_name': product_info['name'],
        'product_description': product_info['description'],
        'product_key': args.product_key
    }

    # Load configurations
    with open(task_yaml_path, 'r') as file:
        task_yaml_content = yaml.safe_load(file)

    with open(agent_yaml_path, 'r') as file:
        agent_yaml_content = yaml.safe_load(file)

    try:
        # Create tasks
        logger.info("Creating tasks...")
        product_research_task = Task('product_research_task', task_yaml_content, inputs)
        audience_research_task = Task('audience_research_task', task_yaml_content, inputs)
        campaign_strategy_task = Task('campaign_strategy_task', task_yaml_content, inputs)
        content_creation_task = Task('content_creation_task', task_yaml_content, inputs)
        quality_assurance_task = Task('quality_assurance_task', task_yaml_content, inputs)
        final_campaign_report_task = Task('final_campaign_report_task', task_yaml_content, inputs)

        # Create individual agents
        logger.info("Creating individual agents...")
        product_researcher = Agent('product_researcher', agent_yaml_content)
        audience_researcher = Agent('audience_researcher', agent_yaml_content)
        campaign_strategist = Agent('campaign_strategist', agent_yaml_content)
        content_creator = Agent('content_creator', agent_yaml_content)
        qa_validator = Agent('qa_validator', agent_yaml_content)

        # Create supervisor agent
        logger.info("Creating supervisor agent...")
        marketing_supervisor = SupervisorAgent(
            "marketing_supervisor", 
            agent_yaml_content,
            [
                product_researcher,
                audience_researcher, 
                campaign_strategist,
                content_creator,
                qa_validator
            ], 
            verbose=False
        )

        if args.recreate_agents == "false":
            logger.info("Starting campaign generation with Bedrock Agents...")

            time_before_call = datetime.datetime.now()
            logger.info(f"Start time: {time_before_call}")
            
            try:
                campaign_id = f"terasky-campaign-{str(uuid.uuid4())}"
                logger.info(f"Campaign ID: {campaign_id}")
                
                result = marketing_supervisor.invoke_with_tasks(
                    [
                        product_research_task,
                        audience_research_task, 
                        campaign_strategy_task,
                        content_creation_task,
                        quality_assurance_task,
                        final_campaign_report_task
                    ],
                    additional_instructions=dedent(f"""
                        You are generating a comprehensive marketing campaign for TeraSky's {product_info['name']} solution.
                        
                        Campaign ID: {campaign_id}
                        
                        Focus on:
                        1. Understanding the product's unique value proposition
                        2. Identifying the right target audience and personas
                        3. Developing a multi-channel marketing strategy
                        4. Creating compelling content across all channels
                        5. Ensuring quality and brand consistency
                        
                        Maintain TeraSky's professional and technical brand voice throughout.
                        Ensure all content is accurate, engaging, and drives business results.
                        
                        This campaign will be used for the AWS Summit TLV 2025 demonstration.
                    """),
                    processing_type="sequential",
                    enable_trace=True,
                    trace_level=args.trace_level,
                    verbose=True
                )
                
                logger.info("Campaign generation completed successfully!")
                print("\n" + "="*80)
                print("MARKETING CAMPAIGN RESULTS")
                print("="*80)
                print(f"Campaign ID: {campaign_id}")
                print(f"Product: {product_info['name']}")
                print(f"Description: {product_info['description']}")
                print("="*80)
                print(result)
                print("="*80)
                
            except Exception as e:
                logger.error(f"Error during campaign generation: {str(e)}")
                traceback.print_exc()

            duration = datetime.datetime.now() - time_before_call
            logger.info(f"Total time taken: {duration.total_seconds():,.1f} seconds")
            
        else:
            logger.info("Agents recreated successfully. Use --recreate_agents false to run campaign generation.")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    # Default values
    default_inputs = {
        'product_key': 'hashicorp_vault',
        'trace_level': 'core'
    }

    parser = argparse.ArgumentParser(description="TeraSky Marketing Campaign Generator using Amazon Bedrock Agents")

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

    args = parser.parse_args()
    
    # Display configuration
    print("\n" + "="*60)
    print("TERASKY MARKETING CAMPAIGN GENERATOR")
    print("Powered by Amazon Bedrock Agents")
    print("="*60)
    print(f"Product: {PRODUCTS[args.product_key]['name']}")
    print(f"Description: {PRODUCTS[args.product_key]['description']}")
    print(f"Recreate Agents: {args.recreate_agents}")
    print(f"Trace Level: {args.trace_level}")
    print(f"AWS Region: {region}")
    print(f"Account ID: {account_id}")
    print("="*60)
    
    main(args) 