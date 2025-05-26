#!/usr/bin/env python

import boto3
import json

def fix_agent_permissions():
    """Fix IAM permissions for existing Bedrock agent roles."""
    
    iam_client = boto3.client('iam')
    
    # List of agent role names
    agent_roles = [
        'AmazonBedrockExecutionRoleForAgents_product_researcher',
        'AmazonBedrockExecutionRoleForAgents_audience_researcher', 
        'AmazonBedrockExecutionRoleForAgents_campaign_strategist',
        'AmazonBedrockExecutionRoleForAgents_content_creator',
        'AmazonBedrockExecutionRoleForAgents_qa_validator'
    ]
    
    # Enhanced inline policy for Bedrock access
    enhanced_policy = {
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
                    "bedrock:GetUsageMetrics"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }
    
    # Additional managed policies to attach
    additional_policies = [
        'arn:aws:iam::aws:policy/service-role/AmazonBedrockExecutionRoleForAgents'
    ]
    
    for role_name in agent_roles:
        try:
            print(f"Updating permissions for role: {role_name}")
            
            # Check if role exists
            try:
                iam_client.get_role(RoleName=role_name)
            except iam_client.exceptions.NoSuchEntityException:
                print(f"  ⚠️  Role {role_name} not found, skipping...")
                continue
            
            # Add/update inline policy
            try:
                iam_client.put_role_policy(
                    RoleName=role_name,
                    PolicyName=f"{role_name}_EnhancedBedrockAccess",
                    PolicyDocument=json.dumps(enhanced_policy)
                )
                print(f"  ✅ Updated inline policy for {role_name}")
            except Exception as e:
                print(f"  ❌ Error updating inline policy: {str(e)}")
            
            # Attach additional managed policies
            for policy_arn in additional_policies:
                try:
                    iam_client.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy_arn
                    )
                    print(f"  ✅ Attached policy {policy_arn}")
                except Exception as e:
                    if "already attached" in str(e).lower():
                        print(f"  ℹ️  Policy {policy_arn} already attached")
                    else:
                        print(f"  ❌ Error attaching policy {policy_arn}: {str(e)}")
            
        except Exception as e:
            print(f"  ❌ Error processing role {role_name}: {str(e)}")
    
    print("\n🔄 Permission updates completed!")
    print("⏰ Wait 2-3 minutes for IAM changes to propagate, then test again.")

if __name__ == '__main__':
    fix_agent_permissions() 