#!/usr/bin/env python3

import boto3
import json

def check_inference_profiles():
    """Check available inference profiles for Bedrock models."""
    
    bedrock_client = boto3.client('bedrock')
    
    print("🔍 CHECKING AVAILABLE INFERENCE PROFILES")
    print("=" * 60)
    
    try:
        # List inference profiles
        profiles_response = bedrock_client.list_inference_profiles()
        
        print(f"Found {len(profiles_response['inferenceProfileSummaries'])} inference profiles\n")
        
        claude_profiles = []
        
        for profile in profiles_response['inferenceProfileSummaries']:
            profile_id = profile['inferenceProfileId']
            
            if 'claude' in profile_id.lower():
                claude_profiles.append(profile)
                print(f"✅ {profile_id}")
                print(f"   Status: {profile.get('status', 'N/A')}")
                print(f"   Type: {profile.get('type', 'N/A')}")
                if 'models' in profile:
                    for model in profile['models']:
                        print(f"   Model: {model.get('modelId', 'N/A')}")
                print()
        
        if not claude_profiles:
            print("❌ No Claude inference profiles found!")
            print("💡 Checking foundation models directly...")
            
            models_response = bedrock_client.list_foundation_models()
            claude_models = [model for model in models_response['modelSummaries'] 
                           if 'claude' in model['modelId'].lower() and model.get('inferenceTypesSupported', []) == ['ON_DEMAND']]
            
            if claude_models:
                print(f"\n🤖 AVAILABLE CLAUDE MODELS (ON_DEMAND):")
                for model in claude_models[:5]:  # Show first 5
                    print(f"✅ {model['modelId']}")
                
                # Suggest using the first available model
                suggested_model = claude_models[0]['modelId']
                print(f"\n💡 SUGGESTED MODEL TO USE: {suggested_model}")
                return suggested_model
        else:
            # Return the first working Claude profile
            suggested_profile = claude_profiles[0]['inferenceProfileId']
            print(f"💡 SUGGESTED INFERENCE PROFILE: {suggested_profile}")
            return suggested_profile
            
    except Exception as e:
        print(f"❌ Error checking inference profiles: {str(e)}")
        
        # Fallback to basic model check
        try:
            models_response = bedrock_client.list_foundation_models()
            claude_models = [model for model in models_response['modelSummaries'] 
                           if 'claude' in model['modelId'].lower()]
            
            if claude_models:
                # Try to find a basic Claude 3 model that works
                basic_models = [m for m in claude_models if 'claude-3-haiku' in m['modelId'] or 'claude-3-sonnet' in m['modelId']]
                if basic_models:
                    suggested_model = basic_models[0]['modelId']
                    print(f"💡 FALLBACK MODEL: {suggested_model}")
                    return suggested_model
                    
        except Exception as e2:
            print(f"❌ Fallback check failed: {str(e2)}")
    
    return None

if __name__ == '__main__':
    suggested = check_inference_profiles()
    if suggested:
        print(f"\n🔧 Next step: Update agents to use: {suggested}")
    else:
        print("\n❌ No working Claude models found!") 