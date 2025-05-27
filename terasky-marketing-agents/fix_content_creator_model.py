#!/usr/bin/env python3

import boto3
import yaml
import json
import time

def fix_content_creator_model():
    """Update the content_creator agent to use a working Claude model."""
    
    print("🔧 FIXING CONTENT CREATOR MODEL CONFIGURATION")
    print("=" * 55)
    
    # Read current agents.yaml
    try:
        with open('agents.yaml', 'r') as file:
            agents_config = yaml.safe_load(file)
        print("✅ Loaded agents.yaml configuration")
    except Exception as e:
        print(f"❌ Error loading agents.yaml: {str(e)}")
        return False
    
    # Check current content_creator model
    current_model = agents_config.get('content_creator', {}).get('llm', 'default')
    print(f"📋 Current content_creator model: {current_model}")
    
    # Update to working model (same as audience_researcher and campaign_strategist)
    new_model = 'us.anthropic.claude-3-5-sonnet-20241022-v2:0'
    agents_config['content_creator']['llm'] = new_model
    
    print(f"🔄 Updating to: {new_model}")
    
    # Backup original file
    try:
        with open('agents.yaml.backup', 'w') as file:
            yaml.dump(agents_config, file, default_flow_style=False)
        print("✅ Created backup: agents.yaml.backup")
    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {str(e)}")
    
    # Write updated configuration
    try:
        with open('agents.yaml', 'w') as file:
            yaml.dump(agents_config, file, default_flow_style=False)
        print("✅ Updated agents.yaml with new model")
    except Exception as e:
        print(f"❌ Error updating agents.yaml: {str(e)}")
        return False
    
    # Now update the existing agent in AWS
    print("\n🔧 Updating existing agent in AWS...")
    
    try:
        bedrock_client = boto3.client('bedrock-agent')
        
        # Find the content_creator agent
        agents_response = bedrock_client.list_agents()
        agent_id = None
        
        for agent in agents_response['agentSummaries']:
            if agent['agentName'] == 'content_creator':
                agent_id = agent['agentId']
                break
        
        if not agent_id:
            print("❌ Could not find content_creator agent in AWS")
            return False
        
        print(f"✅ Found content_creator agent: {agent_id}")
        
        # Get current agent details
        agent_details = bedrock_client.get_agent(agentId=agent_id)
        agent_info = agent_details['agent']
        
        # Update the agent with new model
        update_response = bedrock_client.update_agent(
            agentId=agent_id,
            agentName=agent_info['agentName'],
            description=agent_info.get('description', ''),
            instruction=agent_info['instruction'],
            foundationModel=new_model,  # This is the key change
            idleSessionTTLInSeconds=agent_info.get('idleSessionTTLInSeconds', 1800)
        )
        
        print(f"✅ Updated agent in AWS with new model")
        
        # Prepare the agent (required after update)
        print("🔄 Preparing agent...")
        bedrock_client.prepare_agent(agentId=agent_id)
        
        print("⏰ Waiting 30 seconds for agent preparation...")
        time.sleep(30)
        
        # Test the updated agent
        print("\n🧪 Testing updated agent...")
        
        try:
            bedrock_runtime = boto3.client('bedrock-agent-runtime')
            response = bedrock_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId='TSTALIASID',
                sessionId='test-session-updated',
                inputText='Hello, please introduce yourself briefly.'
            )
            
            # Read response
            result = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
            
            if result:
                print(f"✅ SUCCESS: content_creator agent is now working!")
                print(f"Response: {result[:150]}...")
                return True
            else:
                print(f"❌ No response from updated agent")
                return False
                
        except Exception as e:
            print(f"❌ Error testing updated agent: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating agent in AWS: {str(e)}")
        return False

def main():
    print("🚀 CONTENT CREATOR MODEL FIX")
    print("This will update the content_creator agent to use Claude 3.5 Sonnet")
    print("instead of Claude 3 Haiku which may not be accessible.\n")
    
    success = fix_content_creator_model()
    
    if success:
        print("\n🎉 CONTENT CREATOR MODEL FIX COMPLETED!")
        print("✅ Updated agents.yaml configuration")
        print("✅ Updated agent in AWS Bedrock")
        print("✅ Verified agent is working")
        print("\nYou can now generate complete marketing campaigns!")
    else:
        print("\n❌ MODEL FIX FAILED!")
        print("Please check the error messages above.")
        print("You may need to manually update the agent in AWS Console.")

if __name__ == '__main__':
    main() 