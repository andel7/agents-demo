#!/usr/bin/env python3

import boto3
import yaml
import json
import time

def fix_all_agent_models():
    """Fix all agent model IDs to use the correct format for this region."""
    
    print("🔧 FIXING ALL AGENT MODEL CONFIGURATIONS")
    print("=" * 55)
    
    # Read current agents.yaml
    try:
        with open('agents.yaml', 'r') as file:
            agents_config = yaml.safe_load(file)
        print("✅ Loaded agents.yaml configuration")
    except Exception as e:
        print(f"❌ Error loading agents.yaml: {str(e)}")
        return False
    
    # Model mapping: incorrect -> correct
    model_fixes = {
        'us.anthropic.claude-3-5-sonnet-20241022-v2:0': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
        'us.anthropic.claude-3-haiku-20240307-v1:0': 'anthropic.claude-3-5-sonnet-20241022-v2:0',  # Switch to working model
        'us.anthropic.claude-3-5-sonnet-20240620-v1:0': 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    }
    
    print("\n📋 Current agent model configurations:")
    changes_made = False
    
    for agent_name, agent_config in agents_config.items():
        if isinstance(agent_config, dict) and 'llm' in agent_config:
            current_model = agent_config['llm']
            print(f"  {agent_name}: {current_model}")
            
            if current_model in model_fixes:
                new_model = model_fixes[current_model]
                agent_config['llm'] = new_model
                print(f"    ➜ Fixed to: {new_model}")
                changes_made = True
            elif current_model.startswith('us.anthropic'):
                # Fix any other us.anthropic models
                new_model = current_model.replace('us.anthropic', 'anthropic')
                agent_config['llm'] = new_model
                print(f"    ➜ Fixed to: {new_model}")
                changes_made = True
    
    if not changes_made:
        print("✅ No model fixes needed in agents.yaml")
    else:
        # Backup and save
        try:
            with open('agents.yaml.backup', 'w') as file:
                yaml.dump(agents_config, file, default_flow_style=False)
            print("✅ Created backup: agents.yaml.backup")
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {str(e)}")
        
        try:
            with open('agents.yaml', 'w') as file:
                yaml.dump(agents_config, file, default_flow_style=False)
            print("✅ Updated agents.yaml with correct model IDs")
        except Exception as e:
            print(f"❌ Error updating agents.yaml: {str(e)}")
            return False
    
    # Now update all agents in AWS
    print("\n🔧 Updating agents in AWS...")
    
    try:
        bedrock_client = boto3.client('bedrock-agent')
        
        # Get all agents
        agents_response = bedrock_client.list_agents()
        terasky_agents = []
        
        for agent in agents_response['agentSummaries']:
            if agent['agentName'] in ['product_researcher', 'audience_researcher', 
                                     'campaign_strategist', 'content_creator', 'qa_validator']:
                terasky_agents.append(agent)
        
        print(f"✅ Found {len(terasky_agents)} TeraSky agents to update")
        
        success_count = 0
        
        for agent_summary in terasky_agents:
            agent_name = agent_summary['agentName']
            agent_id = agent_summary['agentId']
            
            print(f"\n🔄 Updating {agent_name} (ID: {agent_id})")
            
            try:
                # Get current agent details
                agent_details = bedrock_client.get_agent(agentId=agent_id)
                agent_info = agent_details['agent']
                
                # Get the correct model for this agent
                agent_config = agents_config.get(agent_name, {})
                new_model = agent_config.get('llm', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
                
                print(f"  Current model: {agent_info.get('foundationModel', 'N/A')}")
                print(f"  New model: {new_model}")
                
                # Update the agent with correct parameters
                update_response = bedrock_client.update_agent(
                    agentId=agent_id,
                    agentName=agent_info['agentName'],
                    description=agent_info.get('description', ''),
                    instruction=agent_info['instruction'],
                    foundationModel=new_model,
                    agentResourceRoleArn=agent_info['agentResourceRoleArn'],  # This was missing!
                    idleSessionTTLInSeconds=agent_info.get('idleSessionTTLInSeconds', 1800)
                )
                
                print(f"  ✅ Updated {agent_name} in AWS")
                
                # Prepare the agent
                bedrock_client.prepare_agent(agentId=agent_id)
                print(f"  ✅ Prepared {agent_name}")
                
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ Error updating {agent_name}: {str(e)}")
        
        if success_count > 0:
            print(f"\n⏰ Waiting 45 seconds for all agent updates to propagate...")
            time.sleep(45)
            
            # Test all updated agents
            print("\n🧪 Testing updated agents...")
            return test_all_agents()
        else:
            print("\n❌ No agents were successfully updated")
            return False
            
    except Exception as e:
        print(f"❌ Error updating agents in AWS: {str(e)}")
        return False

def test_all_agents():
    """Test all TeraSky agents to verify they're working."""
    
    bedrock_client = boto3.client('bedrock-agent')
    bedrock_runtime = boto3.client('bedrock-agent-runtime')
    
    try:
        agents_response = bedrock_client.list_agents()
        terasky_agents = []
        
        for agent in agents_response['agentSummaries']:
            if agent['agentName'] in ['product_researcher', 'audience_researcher', 
                                     'campaign_strategist', 'content_creator', 'qa_validator']:
                terasky_agents.append(agent)
        
        success_count = 0
        
        for agent_summary in terasky_agents:
            agent_name = agent_summary['agentName']
            agent_id = agent_summary['agentId']
            
            print(f"Testing {agent_name} (ID: {agent_id})")
            
            try:
                response = bedrock_runtime.invoke_agent(
                    agentId=agent_id,
                    agentAliasId='TSTALIASID',
                    sessionId=f'test-{agent_name}',
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
                    print(f"  ✅ SUCCESS: {result[:100]}...")
                    success_count += 1
                else:
                    print(f"  ❌ No response")
                    
            except Exception as e:
                print(f"  ❌ ERROR: {str(e)}")
        
        print(f"\n📊 Results: {success_count}/{len(terasky_agents)} agents working")
        return success_count == len(terasky_agents)
        
    except Exception as e:
        print(f"❌ Error testing agents: {str(e)}")
        return False

def main():
    print("🚀 COMPREHENSIVE AGENT MODEL FIX")
    print("This will fix all agent model IDs and update them in AWS Bedrock")
    print("to use the correct models available in your region.\n")
    
    success = fix_all_agent_models()
    
    if success:
        print("\n🎉 ALL AGENT MODELS FIXED SUCCESSFULLY!")
        print("✅ Updated agents.yaml with correct model IDs")
        print("✅ Updated all agents in AWS Bedrock")
        print("✅ Verified all agents are working")
        print("\n🚀 You can now generate complete marketing campaigns!")
        print("   Try: python3 setup_and_run.py")
    else:
        print("\n❌ AGENT MODEL FIX FAILED!")
        print("Some agents may still have issues.")
        print("Check the error messages above for details.")

if __name__ == '__main__':
    main() 