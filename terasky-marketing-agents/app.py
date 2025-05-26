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

# Debug: Print configuration
print("DEBUG: Loaded configuration:")
print(f"  AWS region: {config.get('aws', {}).get('region', 'not found')}")
print(f"  Model ID: {config.get('bedrock', {}).get('model_id', 'not found')}")
print(f"  Full config: {config}")

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name=config.get('aws', {}).get('region', 'us-east-2'))

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
        
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Start campaign generation
        try:
            # Step 1: Product Research
            status_text.text("🔍 Researching product information...")
            progress_bar.progress(20)
            
            product_research = supervisor.agents['product_researcher'].research(PRODUCTS[selected_product])
            if isinstance(product_research, dict) and product_research.get('error', False):
                error_msg = product_research.get('message', 'Unknown error')
                st.error(f"Product research failed: {error_msg}")
                # Show the raw response if available for debugging
                if 'raw_response' in product_research:
                    with st.expander("Debug: Raw Response"):
                        st.text(product_research['raw_response'])
                raise Exception(f"Product research failed: {error_msg}")
            st.success("✅ Product research completed")
            
            # Step 2: Audience Research  
            status_text.text("👥 Analyzing target audience...")
            progress_bar.progress(40)
            
            audience_research = supervisor.agents['audience_researcher'].research(product_research)
            if isinstance(audience_research, dict) and audience_research.get('error', False):
                error_msg = audience_research.get('message', 'Unknown error')
                st.error(f"Audience research failed: {error_msg}")
                if 'raw_response' in audience_research:
                    with st.expander("Debug: Raw Response"):
                        st.text(audience_research['raw_response'])
                raise Exception(f"Audience research failed: {error_msg}")
            st.success("✅ Audience analysis completed")
            
            # Step 3: Campaign Strategy
            status_text.text("📊 Developing campaign strategy...")
            progress_bar.progress(60)
            
            strategy = supervisor.agents['campaign_strategist'].develop_strategy(product_research, audience_research)
            if isinstance(strategy, dict) and strategy.get('error', False):
                error_msg = strategy.get('message', 'Unknown error')
                st.error(f"Strategy development failed: {error_msg}")
                if 'raw_response' in strategy:
                    with st.expander("Debug: Raw Response"):
                        st.text(strategy['raw_response'])
                raise Exception(f"Strategy development failed: {error_msg}")
            st.success("✅ Campaign strategy developed")
            
            # Step 4: Content Creation
            status_text.text("✍️ Creating marketing content...")
            progress_bar.progress(80)
            
            content = supervisor.agents['content_creator'].create_content(product_research, audience_research, strategy)
            if isinstance(content, dict) and content.get('error', False):
                error_msg = content.get('message', 'Unknown error')
                st.error(f"Content creation failed: {error_msg}")
                if 'raw_response' in content:
                    with st.expander("Debug: Raw Response"):
                        st.text(content['raw_response'])
                raise Exception(f"Content creation failed: {error_msg}")
            st.success("✅ Marketing content created")
            
            # Step 5: Generate limited images (only 2 types)
            status_text.text("🎨 Generating marketing visuals...")
            progress_bar.progress(90)
            
            # Generate only social media and blog images
            limited_images = _generate_limited_images(supervisor, product_research, content)
            
            progress_bar.progress(100)
            status_text.text("🎉 Campaign generation completed!")
            
            # Compile results
            campaign_results = {
                'product': PRODUCTS[selected_product],
                'strategy': strategy,
                'audience': audience_research,
                'content': content,
                'images': limited_images
            }
            
            st.session_state.campaign_results = campaign_results
            st.session_state.campaign_started = False
            
            # Display results
            st.success("🎉 Campaign Generation Complete!")
            display_campaign_results(campaign_results)
            
        except Exception as e:
            st.error(f"Error generating campaign: {str(e)}")
            logger.error(f"Campaign generation failed: {str(e)}")
            st.session_state.campaign_started = False
            progress_bar.empty()
            status_text.empty()

def _generate_limited_images(supervisor, product_research, content):
    """Generate only 2 types of images to reduce complexity."""
    try:
        # Handle case where product_research might be an error or invalid format
        product_name = "TeraSky product"
        if isinstance(product_research, dict) and not product_research.get('error', False):
            product_name = product_research.get('name', 'TeraSky product')
        
        # Create simplified image prompts
        simple_prompts = {
            "social_media": {
                "prompt": f"Professional marketing image for {product_name}, modern tech style, blue and orange colors",
                "description": "Social media marketing image"
            },
            "blog": {
                "prompt": f"Technical illustration for {product_name}, clean professional design, technology theme",
                "description": "Blog header image"
            }
        }
        
        generated_images = []
        for image_type, details in simple_prompts.items():
            try:
                image_data = supervisor.agents['image_generator']._generate_image(
                    details['prompt'], 
                    "1024x1024"
                )
                generated_images.append({
                    'type': image_type,
                    'description': details['description'],
                    'image_data': image_data
                })
            except Exception as e:
                st.warning(f"Could not generate {image_type} image: {str(e)}")
        
        return generated_images
        
    except Exception as e:
        st.warning(f"Image generation failed: {str(e)}")
        return []

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
        images = results.get('images', [])
        if images:
            for image in images:
                st.subheader(f"{image['type'].replace('_', ' ').title()}")
                st.text(image['description'])
                if image.get('image_data'):
                    try:
                        # Decode base64 image and display
                        import base64
                        from io import BytesIO
                        image_bytes = base64.b64decode(image['image_data'])
                        st.image(image_bytes, caption=image['description'], width=400)
                    except Exception as e:
                        st.error(f"Could not display image: {str(e)}")
                else:
                    st.info("No image data available")
        else:
            st.info("No images were generated")
    
    # Export Options
    st.download_button(
        "📥 Export Campaign",
        data=json.dumps(results, indent=2),
        file_name=f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main() 