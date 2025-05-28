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

# Initialize session state for agent activity tracking
if 'agent_activity_log' not in st.session_state:
    st.session_state['agent_activity_log'] = []
if 'current_session_id' not in st.session_state:
    st.session_state['current_session_id'] = str(uuid.uuid4())
if 'agent_invocation_count' not in st.session_state:
    st.session_state['agent_invocation_count'] = 0

# AWS clients
def get_aws_clients():
    """Initialize AWS clients with caching."""
    return {
        'bedrock_agent': boto3.client('bedrock-agent'),
        'bedrock_agent_runtime': boto3.client('bedrock-agent-runtime'),
        'iam': boto3.client('iam'),
        'sts': boto3.client('sts')
    }

# Get AWS account info
def get_aws_info():
    """Get AWS account information."""
    clients = get_aws_clients()
    account_id = clients['sts'].get_caller_identity()["Account"]
    region = boto3.Session().region_name
    return account_id, region

def log_agent_activity(agent_name: str, agent_id: str, action: str, details: dict = None):
    """Log agent activity for visitor visibility."""
    activity_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'agent_name': agent_name,
        'agent_id': agent_id,
        'action': action,
        'session_id': st.session_state['current_session_id'],
        'details': details or {}
    }
    st.session_state['agent_activity_log'].append(activity_entry)
    st.session_state['agent_invocation_count'] += 1

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
    """Streamlit-optimized Bedrock Agent wrapper with enhanced visibility."""
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.clients = get_aws_clients()
        
    def invoke(self, prompt: str, session_id: str = None) -> dict:
        """Invoke the agent with a prompt and return detailed response."""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Log invocation start
        log_agent_activity(
            self.agent_name, 
            self.agent_id, 
            "INVOCATION_START",
            {
                'prompt_length': len(prompt),
                'session_id': session_id
            }
        )
        
        try:
            # Create a status container for real-time updates
            status_container = st.container()
            with status_container:
                st.info(f"🤖 **{self.agent_name.replace('_', ' ').title()}** (ID: `{self.agent_id}`) is processing your request...")
                
                # Show the actual API call being made
                with st.expander("📡 Real-time Agent API Call", expanded=True):
                    st.code(f"""
# LIVE BEDROCK AGENT INVOCATION
Agent ID: {self.agent_id}
Agent Alias: TSTALIASID
Session ID: {session_id}
Timestamp: {datetime.datetime.now().isoformat()}
                    """, language="yaml")
            
            start_time = time.time()
            
            # Make the actual Bedrock agent call
            response = self.clients['bedrock_agent_runtime'].invoke_agent(
                agentId=self.agent_id,
                agentAliasId='TSTALIASID',
                sessionId=session_id,
                inputText=prompt
            )
            
            # Extract response from event stream
            result = ""
            event_count = 0
            
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
                        event_count += 1
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Update status with success
            status_container.empty()
            with status_container:
                st.success(f"✅ **{self.agent_name.replace('_', ' ').title()}** completed successfully!")
                
                with st.expander("📊 Agent Response Details", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Response Time", f"{duration:.2f}s")
                    with col2:
                        st.metric("Events Processed", event_count)
                    with col3:
                        st.metric("Response Length", len(result))
            
            # Log successful completion
            log_agent_activity(
                self.agent_name, 
                self.agent_id, 
                "INVOCATION_SUCCESS",
                {
                    'duration_seconds': duration,
                    'response_length': len(result),
                    'events_processed': event_count
                }
            )
            
            return {
                'content': result,
                'metadata': {
                    'agent_id': self.agent_id,
                    'agent_name': self.agent_name,
                    'session_id': session_id,
                    'duration': duration,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'events_processed': event_count
                }
            }
                
        except Exception as e:
            # Log error
            log_agent_activity(
                self.agent_name, 
                self.agent_id, 
                "INVOCATION_ERROR",
                {
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )
            
            logger.error(f"Error invoking agent {self.agent_name}: {str(e)}")
            return {
                'content': f"Error: {str(e)}",
                'metadata': {
                    'agent_id': self.agent_id,
                    'agent_name': self.agent_name,
                    'session_id': session_id,
                    'error': str(e),
                    'timestamp': datetime.datetime.now().isoformat()
                }
            }

class StreamlitMarketingCampaignGenerator:
    """Streamlit marketing campaign generator using real Bedrock agents with enhanced visibility."""
    
    def __init__(self):
        self.agents = {}
        self.session_id = st.session_state['current_session_id']
        self.clients = get_aws_clients()
        
    def discover_agents(self) -> bool:
        """Discover existing TeraSky marketing agents."""
        try:
            # Create a real-time discovery status
            discovery_container = st.container()
            with discovery_container:
                st.info("🔍 Discovering TeraSky Bedrock Agents...")
                
                with st.expander("📡 Live Agent Discovery API Call", expanded=True):
                    st.code(f"""
# LIVE BEDROCK AGENT DISCOVERY
API Endpoint: bedrock-agent.list_agents()
Timestamp: {datetime.datetime.now().isoformat()}
Session: {self.session_id}
                    """, language="yaml")
            
            response = self.clients['bedrock_agent'].list_agents()
            agents = response.get('agentSummaries', [])
            
            # Find TeraSky marketing agents
            agent_names = ['product_researcher', 'audience_researcher', 'campaign_strategist', 'content_creator', 'qa_validator']
            discovered_agents = []
            
            for agent in agents:
                agent_name = agent['agentName']
                if agent_name in agent_names and agent['agentStatus'] in ['PREPARED', 'CREATED']:
                    self.agents[agent_name] = StreamlitBedrockAgent(
                        agent_id=agent['agentId'],
                        agent_name=agent_name
                    )
                    discovered_agents.append({
                        'name': agent_name,
                        'id': agent['agentId'],
                        'status': agent['agentStatus']
                    })
            
            # Update discovery status
            discovery_container.empty()
            with discovery_container:
                if len(self.agents) > 0:
                    st.success(f"✅ Discovered {len(self.agents)} TeraSky Bedrock Agents!")
                    
                    with st.expander("🤖 Discovered Agent Details", expanded=True):
                        for agent_info in discovered_agents:
                            st.write(f"**{agent_info['name'].replace('_', ' ').title()}**")
                            st.write(f"- Agent ID: `{agent_info['id']}`")
                            st.write(f"- Status: `{agent_info['status']}`")
                            st.write("---")
                else:
                    st.warning("No TeraSky marketing agents found in PREPARED or CREATED status.")
            
            # Log discovery activity
            log_agent_activity(
                "SYSTEM",
                "DISCOVERY",
                "AGENT_DISCOVERY",
                {
                    'total_agents_found': len(agents),
                    'terasky_agents_found': len(self.agents),
                    'discovered_agents': discovered_agents
                }
            )
            
            return len(self.agents) > 0
            
        except Exception as e:
            st.error(f"Error discovering agents: {str(e)}")
            log_agent_activity("SYSTEM", "DISCOVERY", "DISCOVERY_ERROR", {'error': str(e)})
            return False
    
    def generate_campaign(self, product_key: str) -> dict:
        """Generate a marketing campaign for the specified product with full agent visibility."""
        
        product_info = PRODUCTS.get(product_key)
        if not product_info:
            raise Exception(f"Product {product_key} not found")
        
        campaign_id = f"terasky-campaign-{str(uuid.uuid4())}"
        results = {
            'campaign_id': campaign_id,
            'product': product_info,
            'timestamp': datetime.datetime.now().isoformat(),
            'session_id': self.session_id,
            'results': {},
            'agent_metadata': {}
        }
        
        # Create campaign tracking section
        st.subheader("🚀 Live Campaign Generation")
        campaign_container = st.container()
        
        with campaign_container:
            st.info(f"**Campaign Session**: `{self.session_id}`")
            st.info(f"**Campaign ID**: `{campaign_id}`")
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Real-time agent workflow display
            workflow_container = st.container()
            
        # Step 1: Product Research
        if 'product_researcher' in self.agents:
            with workflow_container:
                st.markdown("### 🔍 Step 1/5: Product Research Agent")
                
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
            
            agent_response = self.agents['product_researcher'].invoke(product_prompt, self.session_id)
            results['results']['product_research'] = agent_response['content']
            results['agent_metadata']['product_researcher'] = agent_response['metadata']
        
        # Step 2: Audience Research
        if 'audience_researcher' in self.agents:
            with workflow_container:
                st.markdown("### 👥 Step 2/5: Audience Research Agent")
                
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
            
            agent_response = self.agents['audience_researcher'].invoke(audience_prompt, self.session_id)
            results['results']['audience_research'] = agent_response['content']
            results['agent_metadata']['audience_researcher'] = agent_response['metadata']
        
        # Step 3: Campaign Strategy
        if 'campaign_strategist' in self.agents:
            with workflow_container:
                st.markdown("### 📋 Step 3/5: Campaign Strategist Agent")
                
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
            
            agent_response = self.agents['campaign_strategist'].invoke(strategy_prompt, self.session_id)
            results['results']['campaign_strategy'] = agent_response['content']
            results['agent_metadata']['campaign_strategist'] = agent_response['metadata']
        
        # Step 4: Content Creation
        if 'content_creator' in self.agents:
            with workflow_container:
                st.markdown("### ✍️ Step 4/5: Content Creator Agent")
                
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
            
            agent_response = self.agents['content_creator'].invoke(content_prompt, self.session_id)
            results['results']['content'] = agent_response['content']
            results['agent_metadata']['content_creator'] = agent_response['metadata']
        
        # Step 5: Quality Assurance
        if 'qa_validator' in self.agents:
            with workflow_container:
                st.markdown("### ✅ Step 5/5: QA Validator Agent")
                
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
            
            agent_response = self.agents['qa_validator'].invoke(qa_prompt, self.session_id)
            results['results']['qa_results'] = agent_response['content']
            results['agent_metadata']['qa_validator'] = agent_response['metadata']
        
        status_text.text("🎉 Campaign generation completed!")
        
        # Log campaign completion
        log_agent_activity(
            "SYSTEM",
            "CAMPAIGN",
            "CAMPAIGN_COMPLETED",
            {
                'campaign_id': campaign_id,
                'agents_used': len(results['agent_metadata']),
                'total_duration': sum(meta.get('duration', 0) for meta in results['agent_metadata'].values())
            }
        )
        
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
    .activity-log {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.25rem 0;
        font-family: monospace;
        font-size: 0.8rem;
    }
    .agent-invocation {
        background: #e7f3ff;
        border-left: 4px solid #0066cc;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    .agent-success {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    .agent-error {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white;">🚀 TeraSky Marketing Campaign Generator</h1>
        <p style="color: white;">Powered by Amazon Bedrock Agents</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # AWS Info
        account_id, region = get_aws_info()
        st.info(f"**AWS Region:** {region}\n\n**Account ID:** {account_id}")
        
        # Session Info
        st.subheader("🔄 Current Session")
        st.info(f"**Session ID:** `{st.session_state['current_session_id'][:8]}...`")
        st.metric("Agent Invocations", st.session_state['agent_invocation_count'])
        
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
        
        # Agent Activity Dashboard
        st.subheader("📊 Live Agent Activity")
        if st.session_state['agent_activity_log']:
            # Show recent activity (last 5 entries)
            recent_activities = st.session_state['agent_activity_log'][-5:]
            
            for activity in reversed(recent_activities):  # Show most recent first
                timestamp = datetime.datetime.fromisoformat(activity['timestamp']).strftime("%H:%M:%S")
                
                if activity['action'] == 'INVOCATION_START':
                    st.markdown(f"""
                    <div class="agent-invocation">
                        <strong>{timestamp}</strong><br>
                        🚀 {activity['agent_name'].replace('_', ' ').title()}<br>
                        <small>Started processing...</small>
                    </div>
                    """, unsafe_allow_html=True)
                elif activity['action'] == 'INVOCATION_SUCCESS':
                    duration = activity['details'].get('duration_seconds', 0)
                    st.markdown(f"""
                    <div class="agent-success">
                        <strong>{timestamp}</strong><br>
                        ✅ {activity['agent_name'].replace('_', ' ').title()}<br>
                        <small>Completed in {duration:.1f}s</small>
                    </div>
                    """, unsafe_allow_html=True)
                elif activity['action'] == 'INVOCATION_ERROR':
                    st.markdown(f"""
                    <div class="agent-error">
                        <strong>{timestamp}</strong><br>
                        ❌ {activity['agent_name'].replace('_', ' ').title()}<br>
                        <small>Error occurred</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            if st.button("🗑️ Clear Activity Log", type="secondary"):
                st.session_state['agent_activity_log'] = []
                st.session_state['agent_invocation_count'] = 0
                st.rerun()
        else:
            st.info("No agent activity yet. Start generating a campaign!")
        
        # New session button
        if st.button("🔄 New Session", type="secondary"):
            st.session_state['current_session_id'] = str(uuid.uuid4())
            st.session_state['agent_activity_log'] = []
            st.session_state['agent_invocation_count'] = 0
            st.rerun()
    
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
            
            # Campaign overview metrics
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("Agents Used", len(results.get('agent_metadata', {})))
            with col2_2:
                total_duration = sum(meta.get('duration', 0) for meta in results.get('agent_metadata', {}).values())
                st.metric("Total Time", f"{total_duration:.1f}s")
            
            # Campaign details
            st.json({
                'Campaign ID': results['campaign_id'],
                'Product': results['product']['name'],
                'Session ID': results.get('session_id', 'N/A'),
                'Generated': results['timestamp'],
                'Steps Completed': len(results['results'])
            })
            
            # Agent execution summary
            if 'agent_metadata' in results:
                st.subheader("🤖 Agent Execution Details")
                for agent_name, metadata in results['agent_metadata'].items():
                    with st.expander(f"📋 {agent_name.replace('_', ' ').title()}", expanded=False):
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Duration", f"{metadata.get('duration', 0):.2f}s")
                        with col_b:
                            st.metric("Events", metadata.get('events_processed', 0))
                        with col_c:
                            st.metric("Response Size", metadata.get('response_length', 0))
                        
                        st.code(f"Agent ID: {metadata.get('agent_id', 'N/A')}", language="text")
                        st.code(f"Timestamp: {metadata.get('timestamp', 'N/A')}", language="text")
    
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