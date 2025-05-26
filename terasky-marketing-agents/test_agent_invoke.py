#!/usr/bin/env python

import boto3
import json
import uuid

def test_agent_invoke():
    """Test invoking a Bedrock agent."""
    
    # Initialize clients
    bedrock_agent_client = boto3.client('bedrock-agent')
    bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')
    
    try:
        # List agents
        response = bedrock_agent_client.list_agents()
        agents = response.get('agentSummaries', [])
        
        if not agents:
            print("No agents found")
            return
            
        # Use the first agent
        agent = agents[0]
        agent_id = agent['agentId']
        agent_name = agent['agentName']
        
        print(f"Testing agent: {agent_name} (ID: {agent_id})")
        
        # Test invoke
        session_id = str(uuid.uuid4())
        test_prompt = "Hello, please introduce yourself and your role."
        
        print(f"Sending prompt: {test_prompt}")
        
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
        
        print(f"Agent response: {result}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_agent_invoke() 