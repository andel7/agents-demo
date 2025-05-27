#!/usr/bin/env python3

import boto3
import json

def check_available_models():
    """Check what Bedrock models are available and their access status."""
    
    bedrock_client = boto3.client('bedrock')
    
    print("🔍 CHECKING AVAILABLE BEDROCK MODELS")
    print("=" * 60)
    
    try:
        response = bedrock_client.list_foundation_models()
        
        # Models used by agents
        agent_models = [
            'us.anthropic.claude-3-5-sonnet-20241022-v2:0',  # Most agents
            'us.anthropic.claude-3-haiku-20240307-v1:0',     # content_creator
            'us.anthropic.claude-3-5-sonnet-20240620-v1:0'   # qa_validator
        ]
        
        print(f"Found {len(response['modelSummaries'])} total models\n")
        
        # Check Claude models specifically
        claude_models = [model for model in response['modelSummaries'] 
                        if 'claude' in model['modelId'].lower()]
        
        print(f"🤖 CLAUDE MODELS AVAILABLE ({len(claude_models)}):")
        print("-" * 40)
        
        available_agent_models = []
        
        for model in sorted(claude_models, key=lambda x: x['modelId']):
            model_id = model['modelId']
            status = "✅ AVAILABLE"
            
            if model_id in agent_models:
                status += " (USED BY AGENTS)"
                available_agent_models.append(model_id)
            
            print(f"{status}")
            print(f"  Model ID: {model_id}")
            print(f"  Name: {model.get('modelName', 'N/A')}")
            print(f"  Provider: {model.get('providerName', 'N/A')}")
            print()
        
        print("🎯 AGENT MODEL STATUS:")
        print("-" * 30)
        
        for agent_model in agent_models:
            if agent_model in available_agent_models:
                print(f"✅ {agent_model}")
                
                # Identify which agent uses this model
                if agent_model == 'us.anthropic.claude-3-haiku-20240307-v1:0':
                    print("   Used by: content_creator")
                elif agent_model == 'us.anthropic.claude-3-5-sonnet-20240620-v1:0':
                    print("   Used by: qa_validator")
                elif agent_model == 'us.anthropic.claude-3-5-sonnet-20241022-v2:0':
                    print("   Used by: audience_researcher, campaign_strategist")
                else:
                    print("   Used by: product_researcher (default)")
            else:
                print(f"❌ {agent_model}")
                if agent_model == 'us.anthropic.claude-3-haiku-20240307-v1:0':
                    print("   ⚠️  PROBLEM: content_creator agent can't access this model!")
                    print("   💡 SOLUTION: Update content_creator to use available model")
        
        # Test model access
        print("\n🧪 TESTING MODEL ACCESS:")
        print("-" * 25)
        
        bedrock_runtime = boto3.client('bedrock-runtime')
        
        for model_id in available_agent_models:
            try:
                response = bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "Hello"}]
                    }),
                    contentType='application/json'
                )
                print(f"✅ {model_id} - Access OK")
            except Exception as e:
                print(f"❌ {model_id} - Access DENIED: {str(e)}")
                if 'us.anthropic.claude-3-haiku-20240307-v1:0' in model_id:
                    print("   🚨 This is why content_creator is failing!")
        
    except Exception as e:
        print(f"❌ Error checking models: {str(e)}")

def suggest_fix():
    """Suggest how to fix the content_creator model issue."""
    
    print("\n💡 SUGGESTED FIX:")
    print("=" * 20)
    print("1. Update content_creator agent to use a working Claude model")
    print("2. Run: python3 fix_content_creator_model.py")
    print("3. This will change content_creator to use Claude 3.5 Sonnet")
    print("4. Test again with: python3 test_current_agents.py")

if __name__ == '__main__':
    check_available_models()
    suggest_fix() 