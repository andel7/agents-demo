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
import streamlit as st
import json
import time
from typing import Dict, List, Optional
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

class BedrockAgentMarketingCampaign:
    def __init__(self, recreate_agents: bool = True):
        self.recreate_agents = recreate_agents
        self.agents = {}
        self.supervisor = None
        self.setup_agents()

    def setup_agents(self):
        """Setup Bedrock Agents for marketing campaign generation."""
        try:
            # Set force recreate based on parameter
            Agent.set_force_recreate_default(self.recreate_agents)
            
            # Clean up existing agents if recreating
            if self.recreate_agents:
                logger.info("Cleaning up existing agents...")
                Agent.delete_by_name("marketing_supervisor", verbose=True)
                Agent.delete_by_name("product_researcher", verbose=True)
                Agent.delete_by_name("audience_researcher", verbose=True)
                Agent.delete_by_name("campaign_strategist", verbose=True)
                Agent.delete_by_name("content_creator", verbose=True)
                Agent.delete_by_name("qa_validator", verbose=True)

            # Load agent configurations
            with open(agent_yaml_path, 'r') as file:
                agent_yaml_content = yaml.safe_load(file)

            # Define tools for agents (if needed)
            # For now, we'll use basic agents without external tools
            # You can add Lambda functions for web search, data storage, etc.
            
            # Create individual agents
            logger.info("Creating individual agents...")
            self.agents['product_researcher'] = Agent('product_researcher', agent_yaml_content)
            self.agents['audience_researcher'] = Agent('audience_researcher', agent_yaml_content)
            self.agents['campaign_strategist'] = Agent('campaign_strategist', agent_yaml_content)
            self.agents['content_creator'] = Agent('content_creator', agent_yaml_content)
            self.agents['qa_validator'] = Agent('qa_validator', agent_yaml_content)

            # Create supervisor agent
            logger.info("Creating supervisor agent...")
            self.supervisor = SupervisorAgent(
                "marketing_supervisor", 
                agent_yaml_content,
                [
                    self.agents['product_researcher'],
                    self.agents['audience_researcher'], 
                    self.agents['campaign_strategist'],
                    self.agents['content_creator'],
                    self.agents['qa_validator']
                ], 
                verbose=False
            )
            
            logger.info("All agents created successfully!")
            
        except Exception as e:
            logger.error(f"Error setting up agents: {str(e)}")
            raise

    def generate_campaign(self, product_key: str, enable_trace: bool = True, trace_level: str = "core") -> Dict:
        """Generate marketing campaign using Bedrock Agents."""
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
            logger.info("Starting campaign generation...")
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
                'timestamp': datetime.datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating campaign: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }

    def cleanup_agents(self):
        """Clean up all created agents."""
        try:
            logger.info("Cleaning up agents...")
            Agent.delete_by_name("marketing_supervisor", verbose=True)
            Agent.delete_by_name("product_researcher", verbose=True)
            Agent.delete_by_name("audience_researcher", verbose=True)
            Agent.delete_by_name("campaign_strategist", verbose=True)
            Agent.delete_by_name("content_creator", verbose=True)
            Agent.delete_by_name("qa_validator", verbose=True)
            logger.info("Agent cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

def main():
    st.set_page_config(
        page_title="TeraSky Marketing AI Demo - Bedrock Agents",
        page_icon="🚀",
        layout="wide"
    )

    # Header
    st.title("🚀 TeraSky Marketing AI Demo")
    st.subheader("AWS Summit TLV 2025 - Powered by Amazon Bedrock Agents")
    
    # Initialize session state
    if 'campaign_system' not in st.session_state:
        st.session_state.campaign_system = None
    if 'campaign_started' not in st.session_state:
        st.session_state.campaign_started = False
    if 'campaign_results' not in st.session_state:
        st.session_state.campaign_results = None

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        recreate_agents = st.checkbox(
            "Recreate Agents", 
            value=True, 
            help="Whether to recreate Bedrock Agents (slower but ensures latest configuration)"
        )
        
        enable_trace = st.checkbox(
            "Enable Tracing", 
            value=True, 
            help="Enable detailed tracing for debugging"
        )
        
        trace_level = st.selectbox(
            "Trace Level",
            options=["core", "outline", "all"],
            index=0,
            help="Level of detail in tracing"
        )

        if st.button("🧹 Cleanup Agents"):
            if st.session_state.campaign_system:
                st.session_state.campaign_system.cleanup_agents()
                st.session_state.campaign_system = None
            st.success("Agents cleaned up!")

    # Product Selection
    st.header("Select a Product")
    selected_product = st.selectbox(
        "Choose a TeraSky product to generate a marketing campaign:",
        options=list(PRODUCTS.keys()),
        format_func=lambda x: PRODUCTS[x]['name']
    )
    
    if selected_product:
        st.info(f"**{PRODUCTS[selected_product]['name']}**: {PRODUCTS[selected_product]['description']}")

    # Initialize campaign system if needed
    if st.session_state.campaign_system is None and not st.session_state.campaign_started:
        if st.button("🔧 Initialize Bedrock Agents"):
            with st.spinner("Initializing Bedrock Agents... This may take a few minutes."):
                try:
                    st.session_state.campaign_system = BedrockAgentMarketingCampaign(recreate_agents=recreate_agents)
                    st.success("✅ Bedrock Agents initialized successfully!")
                    st.info("You can now generate marketing campaigns. The agents are visible in your AWS Bedrock console.")
                except Exception as e:
                    st.error(f"❌ Failed to initialize agents: {str(e)}")
                    st.session_state.campaign_system = None

    # Generate Campaign Button
    if st.session_state.campaign_system and not st.session_state.campaign_started:
        if st.button("🚀 Generate Marketing Campaign", type="primary"):
            st.session_state.campaign_started = True
            
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("🤖 Starting Bedrock Agent collaboration...")
                progress_bar.progress(10)
                
                # Generate campaign using Bedrock Agents
                result = st.session_state.campaign_system.generate_campaign(
                    selected_product, 
                    enable_trace=enable_trace,
                    trace_level=trace_level
                )
                
                progress_bar.progress(100)
                
                if result['success']:
                    status_text.text("🎉 Campaign generation completed!")
                    st.session_state.campaign_results = result
                    
                    # Display results
                    st.success(f"✅ Marketing campaign generated successfully in {result['duration']:.1f} seconds!")
                    
                    # Show campaign details
                    with st.expander("📊 Campaign Details", expanded=True):
                        st.json({
                            'campaign_id': result['campaign_id'],
                            'product': result['product'],
                            'duration': f"{result['duration']:.1f} seconds",
                            'timestamp': result['timestamp']
                        })
                    
                    # Show agent results
                    with st.expander("🤖 Agent Collaboration Results", expanded=True):
                        st.text(result['result'])
                        
                else:
                    st.error(f"❌ Campaign generation failed: {result['error']}")
                    
            except Exception as e:
                st.error(f"❌ Error during campaign generation: {str(e)}")
                st.session_state.campaign_started = False
            
            finally:
                st.session_state.campaign_started = False

    # Display previous results if available
    if st.session_state.campaign_results and not st.session_state.campaign_started:
        st.header("📋 Previous Campaign Results")
        
        result = st.session_state.campaign_results
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Campaign ID", result['campaign_id'])
            st.metric("Duration", f"{result['duration']:.1f}s")
        with col2:
            st.metric("Product", result['product']['name'])
            st.metric("Status", "✅ Success" if result['success'] else "❌ Failed")
        
        # Show full results
        with st.expander("📄 Full Campaign Results"):
            st.text(result['result'])

if __name__ == '__main__':
    main() 