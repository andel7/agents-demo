#!/usr/bin/env python

import boto3
import json

def list_bedrock_agents():
    """List all Bedrock agents in the current region."""
    
    bedrock_agent_client = boto3.client('bedrock-agent')
    
    try:
        response = bedrock_agent_client.list_agents()
        agents = response.get('agentSummaries', [])
        
        print(f"Found {len(agents)} Bedrock agents:")
        print("="*60)
        
        for agent in agents:
            print(f"Name: {agent['agentName']}")
            print(f"ID: {agent['agentId']}")
            print(f"Status: {agent['agentStatus']}")
            print(f"Description: {agent.get('description', 'N/A')}")
            print(f"Updated: {agent['updatedAt']}")
            print("-" * 40)
            
        return agents
        
    except Exception as e:
        print(f"Error listing agents: {str(e)}")
        return []

def get_agent_details(agent_id):
    """Get detailed information about a specific agent."""
    
    bedrock_agent_client = boto3.client('bedrock-agent')
    
    try:
        response = bedrock_agent_client.get_agent(agentId=agent_id)
        agent = response['agent']
        
        print(f"Agent Details for {agent['agentName']}:")
        print("="*50)
        print(f"ID: {agent['agentId']}")
        print(f"ARN: {agent['agentArn']}")
        print(f"Status: {agent['agentStatus']}")
        print(f"Foundation Model: {agent['foundationModel']}")
        print(f"Role ARN: {agent['agentResourceRoleArn']}")
        print(f"Instructions: {agent['instruction'][:200]}...")
        print("="*50)
        
    except Exception as e:
        print(f"Error getting agent details: {str(e)}")

if __name__ == '__main__':
    print("Testing Bedrock Agents...")
    
    # List all agents
    agents = list_bedrock_agents()
    
    # Get details for TeraSky marketing agents
    terasky_agents = [agent for agent in agents if any(name in agent['agentName'] for name in ['product_researcher', 'audience_researcher', 'campaign_strategist', 'content_creator', 'qa_validator'])]
    
    if terasky_agents:
        print(f"\nFound {len(terasky_agents)} TeraSky marketing agents:")
        for agent in terasky_agents:
            get_agent_details(agent['agentId'])
    else:
        print("\nNo TeraSky marketing agents found. Run simple_bedrock_agents.py first.") 