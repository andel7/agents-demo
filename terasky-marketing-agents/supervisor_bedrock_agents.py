#!/usr/bin/env python3
"""
TeraSky Marketing Campaign Generator using Bedrock Supervisor Agent
This implementation uses the Marketing Supervisor agent to orchestrate the entire workflow.
"""

import os
import sys
import yaml
import json
import uuid
import time
import datetime
import logging
import argparse
from typing import Dict, List, Optional
from textwrap import dedent

# Add the parent directory to the path to import from src
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.utils.bedrock_agent import Agent, SupervisorAgent, Task

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File paths
task_yaml_path = os.path.join(current_dir, "tasks.yaml")
agent_yaml_path = os.path.join(current_dir, "agents.yaml")

# Product definitions
PRODUCTS = {
    'cloud_migration': {
        'name': 'TeraSky Cloud Migration Services',
        'description': 'Comprehensive cloud migration and modernization services for enterprise applications, including assessment, planning, execution, and optimization across AWS, Azure, and Google Cloud platforms.'
    },
    'data_analytics': {
        'name': 'TeraSky Advanced Data Analytics Platform',
        'description': 'End-to-end data analytics and business intelligence solutions leveraging cloud-native technologies, machine learning, and real-time processing capabilities.'
    },
    'cybersecurity': {
        'name': 'TeraSky Cybersecurity Solutions',
        'description': 'Enterprise-grade cybersecurity services including threat detection, incident response, compliance management, and security architecture design.'
    },
    'devops': {
        'name': 'TeraSky DevOps Transformation',
        'description': 'Complete DevOps transformation services including CI/CD pipeline implementation, infrastructure as code, containerization, and automation.'
    },
    'ai_ml': {
        'name': 'TeraSky AI/ML Solutions',
        'description': 'Artificial intelligence and machine learning solutions for business automation, predictive analytics, and intelligent decision-making systems.'
    }
}

class SupervisorMarketingCampaignGenerator:
    """Marketing campaign generator using Bedrock Supervisor Agent."""
    
    def __init__(self, recreate_agents: bool = False):
        self.supervisor = None
        self.individual_agents = {}
        self.recreate_agents = recreate_agents
        self.session_id = str(uuid.uuid4())
        
        # Set force recreate flag
        Agent.default_force_recreate = recreate_agents
        
    def create_agents(self):
        """Create all agents including the supervisor."""
        try:
            # Load agent configurations
            with open(agent_yaml_path, 'r') as file:
                agent_yaml_content = yaml.safe_load(file)
            
            # Create individual agents first
            logger.info("Creating individual agents...")
            
            agent_definitions = [
                'product_researcher',
                'audience_researcher', 
                'campaign_strategist',
                'content_creator',
                'qa_validator'
            ]
            
            for agent_name in agent_definitions:
                logger.info(f"Creating agent: {agent_name}")
                agent = Agent(agent_name, agent_yaml_content, verbose=False)
                self.individual_agents[agent_name] = agent
                logger.info(f"Successfully created agent: {agent_name}")
            
            # Create supervisor agent
            logger.info("Creating Marketing Supervisor agent...")
            self.supervisor = SupervisorAgent(
                "marketing_supervisor", 
                agent_yaml_content,
                [
                    self.individual_agents['product_researcher'],
                    self.individual_agents['audience_researcher'], 
                    self.individual_agents['campaign_strategist'],
                    self.individual_agents['content_creator'],
                    self.individual_agents['qa_validator']
                ], 
                verbose=True
            )
            
            logger.info("All agents created successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error creating agents: {str(e)}")
            return False
    
    def generate_campaign(self, product_key: str, enable_trace: bool = True, trace_level: str = "core") -> Dict:
        """Generate marketing campaign using the supervisor agent."""
        try:
            if not self.supervisor:
                raise Exception("Supervisor agent not initialized")

            product_info = PRODUCTS.get(product_key)
            if not product_info:
                raise Exception(f"Product {product_key} not found")

            # Prepare inputs for tasks
            inputs = {
                'product_name': product_info['name'],
                'product_description': product_info['description'],
                'product_key': product_key
            }

            # Load task configurations
            with open(task_yaml_path, 'r') as file:
                task_yaml_content = yaml.safe_load(file)

            # Create tasks
            logger.info("Creating tasks...")
            product_research_task = Task('product_research_task', task_yaml_content, inputs)
            audience_research_task = Task('audience_research_task', task_yaml_content, inputs)
            campaign_strategy_task = Task('campaign_strategy_task', task_yaml_content, inputs)
            content_creation_task = Task('content_creation_task', task_yaml_content, inputs)
            quality_assurance_task = Task('quality_assurance_task', task_yaml_content, inputs)
            final_campaign_report_task = Task('final_campaign_report_task', task_yaml_content, inputs)

            # Execute campaign generation
            logger.info("Starting campaign generation with Marketing Supervisor...")
            time_before_call = datetime.datetime.now()
            
            campaign_id = f"terasky-campaign-{str(uuid.uuid4())}"
            
            result = self.supervisor.invoke_with_tasks(
                [
                    product_research_task,
                    audience_research_task, 
                    campaign_strategy_task,
                    content_creation_task,
                    quality_assurance_task,
                    final_campaign_report_task
                ],
                additional_instructions=dedent(f"""
                    You are the Marketing Campaign Supervisor for TeraSky, orchestrating a comprehensive 
                    marketing campaign for {product_info['name']}.
                    
                    Campaign ID: {campaign_id}
                    
                    As the supervisor, coordinate your team of specialists:
                    - Product Researcher: For deep product analysis and competitive positioning
                    - Audience Researcher: For target audience identification and persona development
                    - Campaign Strategist: For comprehensive marketing strategy development
                    - Content Creator: For compelling multi-channel content creation
                    - QA Validator: For quality assurance and brand alignment
                    
                    Ensure each specialist provides detailed, actionable insights that build upon 
                    previous work. Maintain TeraSky's professional and technical brand voice throughout.
                    
                    Focus on creating a campaign that:
                    1. Clearly articulates the product's unique value proposition
                    2. Targets the right enterprise decision-makers
                    3. Uses appropriate channels and messaging
                    4. Drives measurable business results
                    5. Maintains the highest quality standards
                """),
                processing_type="sequential",
                enable_trace=enable_trace,
                trace_level=trace_level,
                verbose=True
            )

            duration = datetime.datetime.now() - time_before_call
            logger.info(f"Campaign generation completed in {duration.total_seconds():,.1f} seconds")
            
            return {
                'success': True,
                'campaign_id': campaign_id,
                'product': product_info,
                'result': result,
                'duration': duration.total_seconds(),
                'timestamp': datetime.datetime.now().isoformat(),
                'supervisor_used': True,
                'agents_involved': list(self.individual_agents.keys()) + ['marketing_supervisor']
            }
            
        except Exception as e:
            logger.error(f"Error generating campaign: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }
    
    def cleanup_agents(self):
        """Delete all created agents."""
        try:
            # Delete supervisor first
            if self.supervisor:
                logger.info("Deleting supervisor agent...")
                # The supervisor deletion is handled by the SupervisorAgent class
                
            # Delete individual agents
            for agent_name, agent in self.individual_agents.items():
                logger.info(f"Deleting agent: {agent_name}")
                agent.delete()
                
            self.individual_agents.clear()
            self.supervisor = None
            logger.info("All agents deleted successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

def main(args):
    """Main function to run the supervisor-based marketing campaign generation."""
    
    # Handle cleanup
    if args.clean_up == "true":
        logger.info("Cleaning up agents...")
        
        # Delete agents by name
        agent_names = ['product_researcher', 'audience_researcher', 'campaign_strategist', 
                      'content_creator', 'qa_validator', 'marketing_supervisor']
        
        for agent_name in agent_names:
            try:
                Agent.delete_by_name(agent_name, verbose=True)
                logger.info(f"Deleted agent: {agent_name}")
            except Exception as e:
                logger.warning(f"Could not delete agent {agent_name}: {str(e)}")
        
        logger.info("Cleanup completed")
        return

    # Get product information
    product_info = PRODUCTS.get(args.product_key)
    if not product_info:
        logger.error(f"Product {args.product_key} not found. Available products: {list(PRODUCTS.keys())}")
        return

    logger.info(f"Generating marketing campaign for: {product_info['name']}")
    logger.info(f"Using Marketing Supervisor agent for orchestration")

    try:
        # Create campaign generator
        campaign_generator = SupervisorMarketingCampaignGenerator(
            recreate_agents=(args.recreate_agents == "true")
        )
        
        # Create agents
        logger.info("Creating Bedrock Agents...")
        if not campaign_generator.create_agents():
            logger.error("Failed to create agents")
            return
        
        # Generate campaign
        logger.info("Generating marketing campaign...")
        result = campaign_generator.generate_campaign(
            product_key=args.product_key,
            enable_trace=(args.enable_trace == "true"),
            trace_level=args.trace_level
        )
        
        if result['success']:
            logger.info("Campaign generation completed successfully!")
            
            # Save results
            output_file = f"campaign_result_{result['campaign_id']}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.info(f"Results saved to: {output_file}")
            
            # Print summary
            print("\n" + "="*80)
            print("MARKETING CAMPAIGN GENERATION SUMMARY")
            print("="*80)
            print(f"Campaign ID: {result['campaign_id']}")
            print(f"Product: {result['product']['name']}")
            print(f"Duration: {result['duration']:.1f} seconds")
            print(f"Supervisor Used: {result['supervisor_used']}")
            print(f"Agents Involved: {', '.join(result['agents_involved'])}")
            print(f"Timestamp: {result['timestamp']}")
            print("="*80)
            
        else:
            logger.error(f"Campaign generation failed: {result.get('error', 'Unknown error')}")
        
        # Cleanup if requested
        if args.clean_up_after == "true":
            logger.info("Cleaning up agents after generation...")
            campaign_generator.cleanup_agents()
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TeraSky Marketing Campaign Generator with Supervisor Agent")
    parser.add_argument("--product_key", type=str, default="cloud_migration",
                       choices=list(PRODUCTS.keys()),
                       help="Product key for campaign generation")
    parser.add_argument("--recreate_agents", type=str, default="false", 
                       choices=["true", "false"],
                       help="Whether to recreate agents")
    parser.add_argument("--clean_up", type=str, default="false",
                       choices=["true", "false"], 
                       help="Clean up agents and exit")
    parser.add_argument("--clean_up_after", type=str, default="false",
                       choices=["true", "false"],
                       help="Clean up agents after generation")
    parser.add_argument("--enable_trace", type=str, default="true",
                       choices=["true", "false"],
                       help="Enable tracing")
    parser.add_argument("--trace_level", type=str, default="core",
                       choices=["core", "full"],
                       help="Trace level")
    
    args = parser.parse_args()
    main(args) 