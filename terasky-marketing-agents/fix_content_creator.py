#!/usr/bin/env python3

import boto3
import json
import time
import argparse

def fix_content_creator_permissions(agent_name=None):
    """Fix IAM permissions specifically for the content_creator agent."""
    
    iam_client = boto3.client('iam')
    bedrock_client = boto3.client('bedrock-agent')
    
    # If specific agent name provided, use it; otherwise default to content_creator
    if agent_name:
        role_name = f'AmazonBedrockExecutionRoleForAgents_{agent_name}'
    else:
        role_name = 'AmazonBedrockExecutionRoleForAgents_content_creator'
    
    print(f"🔧 Fixing permissions for agent role: {role_name}")
    
    # Comprehensive Bedrock policy with all necessary permissions
    comprehensive_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:GetFoundationModel",
                    "bedrock:ListFoundationModels",
                    "bedrock:GetModelInvocationLoggingConfiguration",
                    "bedrock:GetUsageMetrics",
                    "bedrock:ApplyGuardrail",
                    "bedrock:GetGuardrail",
                    "bedrock:ListGuardrails"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock-agent:InvokeAgent",
                    "bedrock-agent:GetAgent",
                    "bedrock-agent:ListAgents",
                    "bedrock-agent:GetAgentAlias",
                    "bedrock-agent:ListAgentAliases"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:CreateLogDelivery",
                    "logs:DescribeResourcePolicies",
                    "logs:DescribeLogGroups"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:PassRole"
                ],
                "Resource": "arn:aws:iam::*:role/AmazonBedrockExecutionRoleForAgents_*"
            }
        ]
    }
    
    try:
        # Check if role exists
        try:
            iam_client.get_role(RoleName=role_name)
            print(f"✅ Found role: {role_name}")
        except iam_client.exceptions.NoSuchEntityException:
            print(f"❌ Role {role_name} not found!")
            return False
        
        # Remove any existing conflicting policies first
        try:
            existing_policies = iam_client.list_role_policies(RoleName=role_name)
            for policy_name in existing_policies['PolicyNames']:
                if 'BedrockAccess' in policy_name:
                    iam_client.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
                    print(f"🗑️  Removed old policy: {policy_name}")
        except Exception as e:
            print(f"⚠️  Warning cleaning old policies: {str(e)}")
        
        # Add the comprehensive inline policy
        policy_name = f"{role_name}_ComprehensiveBedrockAccess"
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(comprehensive_policy)
        )
        print(f"✅ Added comprehensive policy: {policy_name}")
        
        # Update the trust policy to ensure proper service access
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        iam_client.update_assume_role_policy(
            RoleName=role_name,
            PolicyDocument=json.dumps(trust_policy)
        )
        print(f"✅ Updated trust policy for {role_name}")
        
        print(f"\n⏰ Waiting 30 seconds for IAM propagation...")
        time.sleep(30)
        
        # Test the agent
        if agent_name:
            test_agent_name = agent_name
        else:
            test_agent_name = 'content_creator'
            
        print(f"\n🧪 Testing agent: {test_agent_name}")
        try:
            # Get agent ID
            agents_response = bedrock_client.list_agents()
            agent_id = None
            for agent in agents_response['agentSummaries']:
                if agent['agentName'] == test_agent_name:
                    agent_id = agent['agentId']
                    break
            
            if agent_id:
                # Test agent invocation
                bedrock_runtime = boto3.client('bedrock-agent-runtime')
                response = bedrock_runtime.invoke_agent(
                    agentId=agent_id,
                    agentAliasId='TSTALIASID',
                    sessionId='test-session',
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
                    print(f"✅ SUCCESS: Agent {test_agent_name} is working!")
                    print(f"Response: {result[:100]}...")
                    return True
                else:
                    print(f"❌ No response from agent {test_agent_name}")
                    return False
            else:
                print(f"❌ Could not find agent {test_agent_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing agent: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing permissions: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Fix Content Creator Agent Permissions")
    parser.add_argument("--agent_name", type=str, default=None,
                       help="Specific agent name to fix (default: content_creator)")
    args = parser.parse_args()
    
    print("🔧 CONTENT CREATOR PERMISSION FIX")
    print("=" * 50)
    
    success = fix_content_creator_permissions(args.agent_name)
    
    if success:
        print("\n🎉 Permission fix completed successfully!")
        print("The agent should now work properly.")
    else:
        print("\n❌ Permission fix failed!")
        print("You may need to manually check the IAM role in the AWS console.")

if __name__ == '__main__':
    main() 