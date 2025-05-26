#!/usr/bin/env python

import boto3
import json
import uuid

def test_current_agents():
    """Test the currently created TeraSky marketing agents."""
    
    # Initialize clients
    bedrock_agent_client = boto3.client('bedrock-agent')
    bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')
    
    try:
        # List agents
        response = bedrock_agent_client.list_agents()
        agents = response.get('agentSummaries', [])
        
        print(f"Found {len(agents)} Bedrock agents:")
        print("="*60)
        
        terasky_agents = []
        for agent in agents:
            print(f"Name: {agent['agentName']}")
            print(f"ID: {agent['agentId']}")
            print(f"Status: {agent['agentStatus']}")
            print(f"Description: {agent.get('description', 'N/A')}")
            print(f"Updated: {agent['updatedAt']}")
            print("-" * 40)
            
            # Check if it's a TeraSky marketing agent
            if any(keyword in agent['agentName'] for keyword in ['product_researcher', 'audience_researcher', 'campaign_strategist', 'content_creator', 'qa_validator']):
                terasky_agents.append(agent)
        
        if not terasky_agents:
            print("No TeraSky marketing agents found.")
            return
            
        print(f"\nTesting {len(terasky_agents)} TeraSky marketing agents:")
        print("="*60)
        
        # Test each agent
        for agent in terasky_agents:
            agent_id = agent['agentId']
            agent_name = agent['agentName']
            
            print(f"\nTesting {agent_name} (ID: {agent_id})")
            
            # Simple test prompt
            session_id = str(uuid.uuid4())
            test_prompt = f"Hello, please briefly introduce yourself as a {agent_name} for TeraSky."
            
            try:
                response = bedrock_agent_runtime_client.invoke_agent(
                    agentId=agent_id,
                    agentAliasId='TSTALIASID',
                    sessionId=session_id,
                    inputText=test_prompt
                )
                
                # Extract response
                result = ""
                for event in response['completion']:
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'bytes' in chunk:
                            result += chunk['bytes'].decode('utf-8')
                
                print(f"✅ SUCCESS: {result[:200]}...")
                
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_current_agents() 