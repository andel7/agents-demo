#!/usr/bin/env python3
"""
TeraSky Marketing Campaign Generator - Streamlit App with Supervisor Agent
This Streamlit application uses the Marketing Supervisor agent to orchestrate campaign generation.
"""

import os
import sys
import yaml
import json
import uuid
import time
import datetime
import logging
import streamlit as st
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
        'description': 'Comprehensive cloud migration and modernization services for enterprise applications, including assessment, planning, execution, and optimization across AWS, Azure, and Google Cloud platforms.',
        'icon': '☁️'
    },
    'data_analytics': {
        'name': 'TeraSky Advanced Data Analytics Platform',
        'description': 'End-to-end data analytics and business intelligence solutions leveraging cloud-native technologies, machine learning, and real-time processing capabilities.',
        'icon': '📊'
    },
    'cybersecurity': {
        'name': 'TeraSky Cybersecurity Solutions',
        'description': 'Enterprise-grade cybersecurity services including threat detection, incident response, compliance management, and security architecture design.',
        'icon': '🔒'
    },
    'devops': {
        'name': 'TeraSky DevOps Transformation',
        'description': 'Complete DevOps transformation services including CI/CD pipeline implementation, infrastructure as code, containerization, and automation.',
        'icon': '⚙️'
    },
    'ai_ml': {
        'name': 'TeraSky AI/ML Solutions',
        'description': 'Artificial intelligence and machine learning solutions for business automation, predictive analytics, and intelligent decision-making systems.',
        'icon': '🤖'
    }
}

class StreamlitSupervisorCampaignGenerator:
    """Streamlit-integrated supervisor campaign generator."""
    
    def __init__(self):
        self.supervisor = None
        self.individual_agents = {}
        self.session_id = str(uuid.uuid4())
        
        # Initialize session state
        if 'agents_created' not in st.session_state:
            st.session_state.agents_created = False
        if 'supervisor_generator' not in st.session_state:
            st.session_state.supervisor_generator = None
    
    def create_agents(self, progress_callback=None):
        """Create all agents including the supervisor."""
        try:
            if progress_callback:
                progress_callback("Loading agent configurations...", 10)
            
            # Load agent configurations
            with open(agent_yaml_path, 'r') as file:
                agent_yaml_content = yaml.safe_load(file)
            
            if progress_callback:
                progress_callback("Creating individual agents...", 20)
            
            # Create individual agents first
            agent_definitions = [
                'product_researcher',
                'audience_researcher', 
                'campaign_strategist',
                'content_creator',
                'qa_validator'
            ]
            
            for i, agent_name in enumerate(agent_definitions):
                if progress_callback:
                    progress = 20 + (i * 12)  # 20-80% for individual agents
                    progress_callback(f"Creating {agent_name}...", progress)
                
                agent = Agent(agent_name, agent_yaml_content, verbose=False)
                self.individual_agents[agent_name] = agent
                logger.info(f"Successfully created agent: {agent_name}")
            
            if progress_callback:
                progress_callback("Creating Marketing Supervisor...", 85)
            
            # Create supervisor agent
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
                verbose=False
            )
            
            if progress_callback:
                progress_callback("All agents created successfully!", 100)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating agents: {str(e)}")
            if progress_callback:
                progress_callback(f"Error: {str(e)}", 0)
            return False
    
    def generate_campaign(self, product_key: str, progress_callback=None) -> Dict:
        """Generate marketing campaign using the supervisor agent."""
        try:
            if not self.supervisor:
                raise Exception("Supervisor agent not initialized")

            product_info = PRODUCTS.get(product_key)
            if not product_info:
                raise Exception(f"Product {product_key} not found")

            if progress_callback:
                progress_callback("Preparing campaign inputs...", 5)

            # Prepare inputs for tasks
            inputs = {
                'product_name': product_info['name'],
                'product_description': product_info['description'],
                'product_key': product_key
            }

            # Load task configurations
            with open(task_yaml_path, 'r') as file:
                task_yaml_content = yaml.safe_load(file)

            if progress_callback:
                progress_callback("Creating task definitions...", 10)

            # Create tasks
            product_research_task = Task('product_research_task', task_yaml_content, inputs)
            audience_research_task = Task('audience_research_task', task_yaml_content, inputs)
            campaign_strategy_task = Task('campaign_strategy_task', task_yaml_content, inputs)
            content_creation_task = Task('content_creation_task', task_yaml_content, inputs)
            quality_assurance_task = Task('quality_assurance_task', task_yaml_content, inputs)
            final_campaign_report_task = Task('final_campaign_report_task', task_yaml_content, inputs)

            if progress_callback:
                progress_callback("Starting Marketing Supervisor orchestration...", 15)

            # Execute campaign generation
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
                enable_trace=True,
                trace_level="core",
                verbose=True
            )

            duration = datetime.datetime.now() - time_before_call
            
            if progress_callback:
                progress_callback("Campaign generation completed!", 100)
            
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
            if progress_callback:
                progress_callback(f"Error: {str(e)}", 0)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }

def display_campaign_results(result: Dict):
    """Display campaign results in a structured format."""
    if not result.get('success', False):
        st.error(f"Campaign generation failed: {result.get('error', 'Unknown error')}")
        return
    
    # Campaign Summary
    st.success("🎉 Campaign Generated Successfully!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Campaign ID", result['campaign_id'][-8:])
    with col2:
        st.metric("Duration", f"{result['duration']:.1f}s")
    with col3:
        st.metric("Agents Used", len(result['agents_involved']))
    
    # Product Information
    st.subheader("📋 Product Information")
    product = result['product']
    st.write(f"**{product['name']}**")
    st.write(product['description'])
    
    # Campaign Results
    st.subheader("📊 Campaign Results")
    
    # Display the main result
    if isinstance(result['result'], str):
        st.text_area("Campaign Output", result['result'], height=400)
    elif isinstance(result['result'], dict):
        st.json(result['result'])
    else:
        st.write(result['result'])
    
    # Agent Information
    st.subheader("🤖 Agents Involved")
    st.write("**Supervisor Agent:** Marketing Supervisor")
    st.write("**Collaborator Agents:**")
    for agent in result['agents_involved'][:-1]:  # Exclude supervisor from list
        st.write(f"- {agent.replace('_', ' ').title()}")
    
    # Download Results
    st.subheader("💾 Download Results")
    result_json = json.dumps(result, indent=2, default=str)
    st.download_button(
        label="Download Campaign Results (JSON)",
        data=result_json,
        file_name=f"campaign_{result['campaign_id']}.json",
        mime="application/json"
    )

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="TeraSky Marketing Campaign Generator",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🚀 TeraSky Marketing Campaign Generator")
    st.subheader("Powered by AWS Bedrock Supervisor Agents")
    
    # Sidebar
    st.sidebar.title("🎯 Campaign Configuration")
    
    # Product Selection
    st.sidebar.subheader("Select Product")
    product_options = {key: f"{value['icon']} {value['name']}" for key, value in PRODUCTS.items()}
    selected_product = st.sidebar.selectbox(
        "Choose a TeraSky product:",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x]
    )
    
    # Display selected product info
    if selected_product:
        product_info = PRODUCTS[selected_product]
        st.sidebar.write("**Description:**")
        st.sidebar.write(product_info['description'][:200] + "...")
    
    # Agent Management
    st.sidebar.subheader("🤖 Agent Management")
    
    # Initialize generator if not exists
    if st.session_state.supervisor_generator is None:
        st.session_state.supervisor_generator = StreamlitSupervisorCampaignGenerator()
    
    # Create Agents Button
    if not st.session_state.agents_created:
        if st.sidebar.button("🔧 Create Bedrock Agents", type="primary"):
            with st.spinner("Creating Bedrock Agents..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(message, progress):
                    status_text.text(message)
                    progress_bar.progress(progress)
                
                success = st.session_state.supervisor_generator.create_agents(progress_callback)
                
                if success:
                    st.session_state.agents_created = True
                    st.success("✅ All agents created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to create agents")
    else:
        st.sidebar.success("✅ Agents Ready")
        
        # Generate Campaign Button
        if st.sidebar.button("🎯 Generate Campaign", type="primary"):
            if selected_product:
                # Main content area for campaign generation
                st.header(f"Generating Campaign for {PRODUCTS[selected_product]['name']}")
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(message, progress):
                    status_text.text(message)
                    progress_bar.progress(progress)
                
                # Generate campaign
                with st.spinner("Marketing Supervisor orchestrating campaign generation..."):
                    result = st.session_state.supervisor_generator.generate_campaign(
                        selected_product, 
                        progress_callback
                    )
                
                # Display results
                display_campaign_results(result)
                
                # Store result in session state
                st.session_state.last_result = result
            else:
                st.error("Please select a product first")
    
    # Main content area
    if not st.session_state.agents_created:
        st.info("👈 Please create the Bedrock Agents first using the sidebar")
        
        # Show agent architecture
        st.subheader("🏗️ Agent Architecture")
        st.write("""
        This application uses a **Supervisor Agent** architecture with the following components:
        
        **Marketing Supervisor Agent** (Orchestrator)
        - Coordinates the entire campaign generation workflow
        - Manages task distribution and execution
        - Ensures quality and consistency across all outputs
        
        **Specialist Agents** (Collaborators)
        - **Product Researcher**: Deep product analysis and competitive positioning
        - **Audience Researcher**: Target audience identification and persona development  
        - **Campaign Strategist**: Comprehensive marketing strategy development
        - **Content Creator**: Multi-channel content creation
        - **QA Validator**: Quality assurance and brand alignment
        """)
        
        # Show product options
        st.subheader("📦 Available Products")
        cols = st.columns(len(PRODUCTS))
        for i, (key, product) in enumerate(PRODUCTS.items()):
            with cols[i]:
                st.write(f"**{product['icon']} {product['name']}**")
                st.write(product['description'][:100] + "...")
    
    else:
        if 'last_result' not in st.session_state:
            st.info("👈 Select a product and click 'Generate Campaign' to start")
            
            # Show supervisor benefits
            st.subheader("🎯 Supervisor Agent Benefits")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("""
                **True Agent Collaboration**
                - Real AWS Bedrock Agents (not simulations)
                - Visible in AWS Console
                - Enterprise-grade orchestration
                - Scalable architecture
                """)
            
            with col2:
                st.write("""
                **Quality Assurance**
                - Coordinated workflow execution
                - Consistent brand voice
                - Quality validation at each step
                - Professional output standards
                """)
        else:
            # Show last result
            st.subheader("📊 Last Generated Campaign")
            display_campaign_results(st.session_state.last_result)

if __name__ == "__main__":
    main() 