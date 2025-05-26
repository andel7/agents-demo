#!/usr/bin/env python

# Copyright 2024 Amazon.com and its affiliates; all rights reserved.
# This file is AWS Content and may not be duplicated or distributed without permission

import streamlit as st
import sys
from pathlib import Path
import datetime
import traceback
import yaml
import uuid
from textwrap import dedent
import os
import json
import logging
import boto3
import time
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get current directory for YAML files
current_dir = os.path.dirname(os.path.abspath(__file__))
task_yaml_path = os.path.join(current_dir, "tasks.yaml")
agent_yaml_path = os.path.join(current_dir, "agents.yaml")

# AWS clients
@st.cache_resource
def get_aws_clients():
    """Initialize AWS clients with caching."""
    return {
        'bedrock_agent': boto3.client('bedrock-agent'),
        'bedrock_agent_runtime': boto3.client('bedrock-agent-runtime'),
        'iam': boto3.client('iam'),
        'sts': boto3.client('sts')
    }

# Get AWS account info
@st.cache_data
def get_aws_info():
    """Get AWS account information."""
    clients = get_aws_clients()
    account_id = clients['sts'].get_caller_identity()["Account"]
    region = boto3.Session().region_name
    return account_id, region

# Product catalog
PRODUCTS = {
    'hashicorp_vault': {
        'name': 'HashiCorp Vault',
        'description': 'Enterprise secrets management and encryption platform',
        'icon': '🔐'
    },
    'upwind_security': {
        'name': 'UpWind Security',
        'description': 'Cloud-native security platform for Kubernetes',
        'icon': '🛡️'
    },
    'portworx': {
        'name': 'Portworx by Pure',
        'description': 'Enterprise-grade storage platform for Kubernetes',
        'icon': '💾'
    },
    'prompt_security': {
        'name': 'Prompt.security',
        'description': 'AI security and compliance platform',
        'icon': '🤖'
    },
    'spectro_cloud': {
        'name': 'Spectro Cloud',
        'description': 'Kubernetes management platform',
        'icon': '☁️'
    },
    'other': {
        'name': 'Other TeraSky Solutions',
        'description': 'Custom enterprise solutions and consulting',
        'icon': '⚡'
    }
}

class StreamlitBedrockAgent:
    """Streamlit-optimized Bedrock Agent wrapper."""
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.clients = get_aws_clients()
        
    def invoke(self, prompt: str, session_id: str = None) -> str:
        """Invoke the agent with a prompt."""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            with st.spinner(f"🤖 {self.agent_name} is thinking..."):
                response = self.clients['bedrock_agent_runtime'].invoke_agent(
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
            logger.error(f"Error invoking agent {self.agent_name}: {str(e)}")
            return f"Error: {str(e)}"

class StreamlitMarketingCampaignGenerator:
    """Streamlit marketing campaign generator using real Bedrock agents."""
    
    def __init__(self):
        self.agents = {}
        self.session_id = str(uuid.uuid4())
        self.clients = get_aws_clients()
        
    def discover_agents(self) -> bool:
        """Discover existing TeraSky marketing agents."""
        try:
            response = self.clients['bedrock_agent'].list_agents()
            agents = response.get('agentSummaries', [])
            
            # Find TeraSky marketing agents
            agent_names = ['product_researcher', 'audience_researcher', 'campaign_strategist', 'content_creator', 'qa_validator']
            
            for agent in agents:
                agent_name = agent['agentName']
                if agent_name in agent_names and agent['agentStatus'] in ['PREPARED', 'CREATED']:
                    self.agents[agent_name] = StreamlitBedrockAgent(
                        agent_id=agent['agentId'],
                        agent_name=agent_name
                    )
            
            return len(self.agents) > 0
            
        except Exception as e:
            st.error(f"Error discovering agents: {str(e)}")
            return False
    
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
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Product Research
        if 'product_researcher' in self.agents:
            status_text.text("🔍 Step 1/5: Conducting Product Research...")
            progress_bar.progress(0.2)
            
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
        if 'audience_researcher' in self.agents:
            status_text.text("👥 Step 2/5: Analyzing Target Audience...")
            progress_bar.progress(0.4)
            
            audience_prompt = f"""
            Based on the product research for {product_info['name']}, analyze the target audience.
            
            Product Research Results: {results['results'].get('product_research', '')[:1000]}...
            
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
        if 'campaign_strategist' in self.agents:
            status_text.text("📋 Step 3/5: Developing Campaign Strategy...")
            progress_bar.progress(0.6)
            
            strategy_prompt = f"""
            Develop a comprehensive marketing strategy for {product_info['name']}.
            
            Product Research: {results['results'].get('product_research', '')[:500]}...
            Audience Research: {results['results'].get('audience_research', '')[:500]}...
            
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
        if 'content_creator' in self.agents:
            status_text.text("✍️ Step 4/5: Creating Marketing Content...")
            progress_bar.progress(0.8)
            
            content_prompt = f"""
            Create compelling marketing content for {product_info['name']}.
            
            Strategy: {results['results'].get('campaign_strategy', '')[:500]}...
            
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
        if 'qa_validator' in self.agents:
            status_text.text("✅ Step 5/5: Quality Assurance Review...")
            progress_bar.progress(1.0)
            
            qa_prompt = f"""
            Review and validate the marketing campaign for {product_info['name']}.
            
            Content to Review: {results['results'].get('content', '')[:500]}...
            
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
        
        status_text.text("🎉 Campaign generation completed!")
        return results

def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="TeraSky Marketing Campaign Generator",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 TeraSky Marketing Campaign Generator</h1>
        <p>Powered by Amazon Bedrock Agents</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # AWS Info
        account_id, region = get_aws_info()
        st.info(f"**AWS Region:** {region}\n\n**Account ID:** {account_id}")
        
        # Product selection
        st.subheader("📦 Select Product")
        product_key = st.selectbox(
            "Choose a TeraSky product:",
            options=list(PRODUCTS.keys()),
            format_func=lambda x: f"{PRODUCTS[x]['icon']} {PRODUCTS[x]['name']}"
        )
        
        # Agent discovery
        st.subheader("🤖 Bedrock Agents")
        if st.button("🔍 Discover Agents", type="primary"):
            with st.spinner("Discovering Bedrock agents..."):
                campaign_generator = StreamlitMarketingCampaignGenerator()
                if campaign_generator.discover_agents():
                    st.session_state['agents'] = campaign_generator.agents
                    st.session_state['campaign_generator'] = campaign_generator
                    st.success(f"Found {len(campaign_generator.agents)} agents!")
                else:
                    st.error("No TeraSky marketing agents found. Please create them first.")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"{PRODUCTS[product_key]['icon']} {PRODUCTS[product_key]['name']}")
        st.write(PRODUCTS[product_key]['description'])
        
        # Show discovered agents
        if 'agents' in st.session_state:
            st.subheader("🤖 Available Agents")
            for agent_name, agent in st.session_state['agents'].items():
                st.markdown(f"""
                <div class="agent-card">
                    <strong>{agent_name.replace('_', ' ').title()}</strong><br>
                    <small>Agent ID: {agent.agent_id}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Generate campaign button
        if st.button("🚀 Generate Marketing Campaign", type="primary", disabled='agents' not in st.session_state):
            if 'campaign_generator' in st.session_state:
                try:
                    start_time = time.time()
                    
                    # Generate campaign
                    results = st.session_state['campaign_generator'].generate_campaign(product_key)
                    
                    # Store results
                    st.session_state['campaign_results'] = results
                    
                    duration = time.time() - start_time
                    st.success(f"✅ Campaign generated successfully in {duration:.1f} seconds!")
                    
                except Exception as e:
                    st.error(f"Error generating campaign: {str(e)}")
                    st.exception(e)
    
    with col2:
        st.subheader("📊 Campaign Status")
        if 'campaign_results' in st.session_state:
            results = st.session_state['campaign_results']
            st.json({
                'Campaign ID': results['campaign_id'],
                'Product': results['product']['name'],
                'Generated': results['timestamp'],
                'Steps Completed': len(results['results'])
            })
    
    # Display results
    if 'campaign_results' in st.session_state:
        st.header("📋 Campaign Results")
        results = st.session_state['campaign_results']
        
        tabs = st.tabs(["📊 Overview", "🔍 Product Research", "👥 Audience Analysis", "📋 Strategy", "✍️ Content", "✅ QA Review"])
        
        with tabs[0]:
            st.subheader("Campaign Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Campaign ID", results['campaign_id'][-8:])
            with col2:
                st.metric("Product", results['product']['name'])
            with col3:
                st.metric("Steps Completed", len(results['results']))
        
        with tabs[1]:
            if 'product_research' in results['results']:
                st.subheader("🔍 Product Research")
                st.text_area("Research Results", results['results']['product_research'], height=400)
        
        with tabs[2]:
            if 'audience_research' in results['results']:
                st.subheader("👥 Audience Analysis")
                st.text_area("Audience Analysis", results['results']['audience_research'], height=400)
        
        with tabs[3]:
            if 'campaign_strategy' in results['results']:
                st.subheader("📋 Campaign Strategy")
                st.text_area("Strategy Details", results['results']['campaign_strategy'], height=400)
        
        with tabs[4]:
            if 'content' in results['results']:
                st.subheader("✍️ Marketing Content")
                st.text_area("Content", results['results']['content'], height=400)
        
        with tabs[5]:
            if 'qa_results' in results['results']:
                st.subheader("✅ Quality Assurance")
                st.text_area("QA Review", results['results']['qa_results'], height=400)

if __name__ == "__main__":
    main() 