#!/usr/bin/env python

import subprocess
import sys
import boto3
import time

def check_agents_exist():
    """Check if TeraSky marketing agents already exist."""
    try:
        bedrock_agent_client = boto3.client('bedrock-agent')
        response = bedrock_agent_client.list_agents()
        agents = response.get('agentSummaries', [])
        
        agent_names = ['product_researcher', 'audience_researcher', 'campaign_strategist', 'content_creator', 'qa_validator']
        existing_agents = [agent['agentName'] for agent in agents if agent['agentName'] in agent_names]
        
        return len(existing_agents), existing_agents
        
    except Exception as e:
        print(f"Error checking agents: {str(e)}")
        return 0, []

def create_agents():
    """Create the Bedrock agents."""
    print("🤖 Creating Bedrock agents...")
    try:
        result = subprocess.run([
            sys.executable, 'simple_bedrock_agents.py', 
            '--product_key', 'hashicorp_vault',
            '--recreate_agents', 'true',
            '--cleanup_after', 'false'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Agents created successfully!")
            return True
        else:
            print(f"❌ Error creating agents: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running agent creation: {str(e)}")
        return False

def fix_permissions():
    """Fix agent permissions."""
    print("🔧 Fixing agent permissions...")
    try:
        result = subprocess.run([sys.executable, 'fix_agent_permissions.py'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Permissions updated!")
            print("⏰ Waiting 30 seconds for IAM propagation...")
            time.sleep(30)
            return True
        else:
            print(f"❌ Error fixing permissions: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running permission fix: {str(e)}")
        return False

def launch_streamlit():
    """Launch the Streamlit app."""
    print("🚀 Launching Streamlit app...")
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'streamlit_bedrock_agents.py'])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped.")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {str(e)}")

def main():
    """Main setup and run function."""
    print("="*60)
    print("🚀 TERASKY MARKETING CAMPAIGN GENERATOR SETUP")
    print("="*60)
    
    # Check if agents exist
    agent_count, existing_agents = check_agents_exist()
    
    if agent_count == 5:
        print(f"✅ Found all 5 agents: {existing_agents}")
        print("🔧 Updating permissions just in case...")
        fix_permissions()
    elif agent_count > 0:
        print(f"⚠️  Found {agent_count} agents: {existing_agents}")
        print("🤖 Creating missing agents...")
        if create_agents():
            fix_permissions()
        else:
            print("❌ Failed to create agents. Exiting.")
            return
    else:
        print("🤖 No agents found. Creating all agents...")
        if create_agents():
            fix_permissions()
        else:
            print("❌ Failed to create agents. Exiting.")
            return
    
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE! LAUNCHING STREAMLIT APP...")
    print("="*60)
    print("📝 Instructions:")
    print("1. Click 'Discover Agents' in the sidebar")
    print("2. Select a product")
    print("3. Click 'Generate Marketing Campaign'")
    print("4. Watch real Bedrock agents collaborate!")
    print("="*60)
    
    # Launch Streamlit
    launch_streamlit()

if __name__ == '__main__':
    main() 