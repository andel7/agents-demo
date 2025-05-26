import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path
import boto3
from typing import Dict, List, Optional
import logging
from utils.logger import setup_logger
from utils.config import load_config
from agents.supervisor import CampaignSupervisor

# Configure logging
logger = setup_logger()

# Initialize session state
if 'campaign_started' not in st.session_state:
    st.session_state.campaign_started = False
if 'agent_logs' not in st.session_state:
    st.session_state.agent_logs = {}
if 'campaign_results' not in st.session_state:
    st.session_state.campaign_results = None

# Load configuration
config = load_config()

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-runtime')

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

def initialize_supervisor(product_key: str) -> CampaignSupervisor:
    """Initialize the campaign supervisor with selected product."""
    return CampaignSupervisor(
        product_info=PRODUCTS[product_key],
        bedrock_client=bedrock_client,
        config=config
    )

def update_agent_logs(agent_name: str, message: str):
    """Update agent logs in session state."""
    if agent_name not in st.session_state.agent_logs:
        st.session_state.agent_logs[agent_name] = []
    st.session_state.agent_logs[agent_name].append({
        'timestamp': datetime.now().isoformat(),
        'message': message
    })

def display_agent_status(agent_name: str):
    """Display agent status and logs in the UI."""
    with st.expander(f"🤖 {agent_name.replace('_', ' ').title()}", expanded=True):
        if agent_name in st.session_state.agent_logs:
            for log in st.session_state.agent_logs[agent_name]:
                st.text(f"{log['timestamp']}: {log['message']}")

def main():
    st.set_page_config(
        page_title="TeraSky Marketing AI Demo",
        page_icon="🚀",
        layout="wide"
    )

    # Header
    st.title("🚀 TeraSky Marketing AI Demo")
    st.subheader("AWS Summit TLV 2025")
    
    # Product Selection
    st.header("Select a Product")
    selected_product = st.selectbox(
        "Choose a TeraSky product to generate a marketing campaign:",
        options=list(PRODUCTS.keys()),
        format_func=lambda x: PRODUCTS[x]['name']
    )
    
    if selected_product:
        st.info(PRODUCTS[selected_product]['description'])

    # Generate Campaign Button
    if st.button("🚀 Generate Marketing Campaign", disabled=st.session_state.campaign_started):
        st.session_state.campaign_started = True
        st.session_state.agent_logs = {}
        
        # Initialize supervisor
        supervisor = initialize_supervisor(selected_product)
        
        # Start campaign generation
        with st.spinner("Initializing marketing campaign generation..."):
            try:
                # Start the campaign generation process
                campaign_results = supervisor.generate_campaign()
                st.session_state.campaign_results = campaign_results
                
                # Display results
                st.success("🎉 Campaign Generation Complete!")
                display_campaign_results(campaign_results)
                
            except Exception as e:
                st.error(f"Error generating campaign: {str(e)}")
                logger.error(f"Campaign generation failed: {str(e)}")
                st.session_state.campaign_started = False

    # Display agent status and logs
    if st.session_state.campaign_started:
        st.header("Agent Status")
        cols = st.columns(3)
        
        agents = [
            "product_researcher",
            "audience_researcher",
            "campaign_strategist",
            "content_creator",
            "image_generator",
            "qa_validator"
        ]
        
        for i, agent in enumerate(agents):
            with cols[i % 3]:
                display_agent_status(agent)

def display_campaign_results(results: Dict):
    """Display the generated campaign results."""
    st.header("Campaign Results")
    
    # Campaign Strategy
    with st.expander("📊 Campaign Strategy", expanded=True):
        st.write(results.get('strategy', {}))
    
    # Target Audience
    with st.expander("👥 Target Audience", expanded=True):
        st.write(results.get('audience', {}))
    
    # Content
    with st.expander("✍️ Generated Content", expanded=True):
        st.write(results.get('content', {}))
    
    # Images
    with st.expander("🎨 Generated Images", expanded=True):
        for image in results.get('images', []):
            st.image(image['url'], caption=image['description'])
    
    # Export Options
    st.download_button(
        "📥 Export Campaign",
        data=json.dumps(results, indent=2),
        file_name=f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main() 