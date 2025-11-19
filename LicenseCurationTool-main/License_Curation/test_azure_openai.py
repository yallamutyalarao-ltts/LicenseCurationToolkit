#!/usr/bin/env python3
"""
Test Azure OpenAI Configuration

This script tests your Azure OpenAI configuration to ensure it's set up correctly
before running the full AI analysis scripts.

Usage:
    export AZURE_OPENAI_API_KEY="your-key"
    export AZURE_OPENAI_ENDPOINT="your-endpoint"
    export AZURE_OPENAI_MODEL="your-deployment-name"  # Optional
    python test_azure_openai.py
"""

import os
import sys
from openai import AzureOpenAI

def test_azure_openai():
    """Test Azure OpenAI configuration"""

    print("=" * 80)
    print("AZURE OPENAI CONFIGURATION TEST")
    print("=" * 80)
    print()

    # Check environment variables
    api_key = os.environ.get('AZURE_OPENAI_API_KEY')
    endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT', 'https://ltts-cariad-ddd-mvp-ai-foundry.cognitiveservices.azure.com')
    model_deployment = os.environ.get('AZURE_OPENAI_MODEL', 'gpt-4.1-mini')
    api_version = '2025-01-01-preview'

    print("📋 Configuration:")
    print(f"  API Key: {'✓ Set' if api_key else '✗ Missing'}")
    print(f"  Endpoint: {endpoint}")
    print(f"  Model Deployment: {model_deployment}")
    print(f"  API Version: {api_version}")
    print()

    if not api_key:
        print("❌ ERROR: AZURE_OPENAI_API_KEY environment variable not set!")
        print()
        print("Please set it:")
        print("  export AZURE_OPENAI_API_KEY='your-key-here'")
        print()
        return False

    # Test connection
    print("🔌 Testing Azure OpenAI connection...")
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )

        print("  ✓ Client initialized successfully")
        print()

        # Test simple completion
        print("🤖 Testing model deployment with simple prompt...")
        response = client.chat.completions.create(
            model=model_deployment,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, ORT!' in 3 words or less."}
            ],
            temperature=0.3,
            max_tokens=50
        )

        result = response.choices[0].message.content
        print(f"  ✓ Model responded: {result}")
        print()

        print("=" * 80)
        print("✅ SUCCESS! Azure OpenAI is configured correctly.")
        print("=" * 80)
        print()
        print("Your configuration is ready for:")
        print("  • ort_curation_script_html.py")
        print("  • ai_multilayer_resolution.py")
        print("  • enhanced_ai_curation.py")
        print("  • ai_missing_licenses_analyzer.py")
        print()
        return True

    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        print()

        error_str = str(e).lower()

        if 'deploymentnotfound' in error_str or '404' in error_str:
            print("💡 ISSUE: Deployment not found")
            print()
            print("The deployment name doesn't match what's in your Azure Portal.")
            print()
            print("To fix this:")
            print("1. Go to https://portal.azure.com")
            print("2. Navigate to your Azure OpenAI resource")
            print("3. Click 'Model deployments' in the sidebar")
            print("4. Copy the exact deployment name (NOT the model name)")
            print("5. Set it as an environment variable:")
            print(f"   export AZURE_OPENAI_MODEL='your-actual-deployment-name'")
            print()
            print(f"Currently trying to use: {model_deployment}")
            print()

        elif 'authentication' in error_str or 'unauthorized' in error_str or '401' in error_str:
            print("💡 ISSUE: Authentication failed")
            print()
            print("Your API key may be incorrect or expired.")
            print()
            print("To fix this:")
            print("1. Go to https://portal.azure.com")
            print("2. Navigate to your Azure OpenAI resource")
            print("3. Click 'Keys and Endpoint' in the sidebar")
            print("4. Copy KEY 1 or KEY 2")
            print("5. Set it as an environment variable:")
            print("   export AZURE_OPENAI_API_KEY='your-api-key'")
            print()

        elif 'endpoint' in error_str or 'host' in error_str:
            print("💡 ISSUE: Endpoint URL incorrect")
            print()
            print("Your endpoint URL may be incorrect.")
            print()
            print("To fix this:")
            print("1. Go to https://portal.azure.com")
            print("2. Navigate to your Azure OpenAI resource")
            print("3. Click 'Keys and Endpoint' in the sidebar")
            print("4. Copy the Endpoint URL")
            print("5. Set it as an environment variable:")
            print("   export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'")
            print()
            print(f"Currently using: {endpoint}")
            print()

        else:
            print("💡 TROUBLESHOOTING:")
            print()
            print("Check:")
            print("  1. API key is valid and not expired")
            print("  2. Endpoint URL is correct")
            print("  3. Deployment name matches what's in Azure Portal")
            print("  4. Your Azure OpenAI resource has sufficient quota")
            print()

        print("See AZURE_OPENAI_SETUP.md for detailed setup instructions.")
        print()
        return False

if __name__ == '__main__':
    success = test_azure_openai()
    sys.exit(0 if success else 1)
