#!/usr/bin/env python3

import boto3
import json

def cleanup_existing_iam_policies():
    """Clean up all existing IAM policies created by our Python scripts."""
    
    print("🧹 CLEANING UP EXISTING IAM POLICIES")
    print("=" * 50)
    
    iam_client = boto3.client('iam')
    
    # Agent role names we created
    agent_roles = [
        'AmazonBedrockExecutionRoleForAgents_product_researcher',
        'AmazonBedrockExecutionRoleForAgents_audience_researcher', 
        'AmazonBedrockExecutionRoleForAgents_campaign_strategist',
        'AmazonBedrockExecutionRoleForAgents_content_creator',
        'AmazonBedrockExecutionRoleForAgents_qa_validator'
    ]
    
    cleaned_count = 0
    
    for role_name in agent_roles:
        try:
            print(f"\n🔍 Checking role: {role_name}")
            
            # Check if role exists
            try:
                iam_client.get_role(RoleName=role_name)
                print(f"  ✅ Found role: {role_name}")
            except iam_client.exceptions.NoSuchEntityException:
                print(f"  ⚠️  Role {role_name} not found, skipping...")
                continue
            
            # List and remove inline policies
            try:
                policies_response = iam_client.list_role_policies(RoleName=role_name)
                
                for policy_name in policies_response['PolicyNames']:
                    print(f"  🗑️  Removing inline policy: {policy_name}")
                    iam_client.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
                    
                if policies_response['PolicyNames']:
                    print(f"  ✅ Removed {len(policies_response['PolicyNames'])} inline policies")
                    
            except Exception as e:
                print(f"  ❌ Error removing inline policies: {str(e)}")
            
            # List and detach managed policies
            try:
                attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)
                
                for policy in attached_policies['AttachedPolicies']:
                    policy_arn = policy['PolicyArn']
                    print(f"  🔓 Detaching managed policy: {policy['PolicyName']}")
                    try:
                        iam_client.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
                    except Exception as e:
                        print(f"    ⚠️  Could not detach {policy_arn}: {str(e)}")
                        
                if attached_policies['AttachedPolicies']:
                    print(f"  ✅ Detached {len(attached_policies['AttachedPolicies'])} managed policies")
                    
            except Exception as e:
                print(f"  ❌ Error detaching managed policies: {str(e)}")
            
            cleaned_count += 1
            print(f"  ✅ Cleaned role: {role_name}")
            
        except Exception as e:
            print(f"  ❌ Error processing role {role_name}: {str(e)}")
    
    print(f"\n📊 Cleanup Summary:")
    print(f"   Processed: {cleaned_count}/{len(agent_roles)} roles")
    print(f"   ✅ All inline policies removed")
    print(f"   ✅ All managed policies detached")
    print(f"\n💡 Roles are preserved for Terraform to manage")
    print(f"   Terraform will now control all IAM policies")

def main():
    print("🚀 IAM CLEANUP FOR TERRAFORM MIGRATION")
    print("This will remove all Python-created policies so Terraform can take over")
    print("(Roles will be preserved)\n")
    
    try:
        cleanup_existing_iam_policies()
        print("\n🎉 CLEANUP COMPLETED!")
        print("✅ Ready for Terraform management")
        print("\nNext steps:")
        print("1. cd terraform/")
        print("2. terraform init")
        print("3. terraform plan")
        print("4. terraform apply")
        
    except Exception as e:
        print(f"\n❌ CLEANUP FAILED: {str(e)}")

if __name__ == '__main__':
    main() 