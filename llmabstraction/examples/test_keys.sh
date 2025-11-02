#!/bin/bash

# API Key Test Script
# Tests if your API keys are properly configured for each provider

echo "================================"
echo "AI API Provider Key Test Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test Anthropic
echo -n "Testing Anthropic API Key... "
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}NOT SET${NC}"
    echo "  Set with: export ANTHROPIC_API_KEY='your-key'"
else
    echo -e "${GREEN}SET${NC}"
    echo "  Key: ${ANTHROPIC_API_KEY:0:10}...${ANTHROPIC_API_KEY: -4}"
fi
echo ""

# Test OpenAI
echo -n "Testing OpenAI API Key... "
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}NOT SET${NC}"
    echo "  Set with: export OPENAI_API_KEY='your-key'"
else
    echo -e "${GREEN}SET${NC}"
    echo "  Key: ${OPENAI_API_KEY:0:10}...${OPENAI_API_KEY: -4}"
fi
echo ""

# Test Together AI
echo -n "Testing Together AI API Key... "
if [ -z "$TOGETHER_API_KEY" ]; then
    echo -e "${RED}NOT SET${NC}"
    echo "  Set with: export TOGETHER_API_KEY='your-key'"
else
    echo -e "${GREEN}SET${NC}"
    echo "  Key: ${TOGETHER_API_KEY:0:10}...${TOGETHER_API_KEY: -4}"
fi
echo ""

# Test AWS Credentials
echo -n "Testing AWS Credentials... "
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo -e "${RED}NOT SET${NC}"
    echo "  Set with: aws configure"
    echo "  Or: export AWS_ACCESS_KEY_ID='your-key'"
    echo "      export AWS_SECRET_ACCESS_KEY='your-secret'"
else
    echo -e "${GREEN}SET${NC}"
    echo "  Access Key: ${AWS_ACCESS_KEY_ID:0:10}..."
    echo "  Region: ${AWS_REGION:-not set (using default)}"
fi
echo ""

# Test Google Cloud
echo -n "Testing Google Cloud Credentials... "
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ] && [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo -e "${RED}NOT SET${NC}"
    echo "  Authenticate with: gcloud auth application-default login"
    echo "  Set project: export GOOGLE_CLOUD_PROJECT='your-project-id'"
else
    echo -e "${GREEN}SET${NC}"
    if [ ! -z "$GOOGLE_CLOUD_PROJECT" ]; then
        echo "  Project: $GOOGLE_CLOUD_PROJECT"
    fi
    if [ ! -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        echo "  Credentials file: $GOOGLE_APPLICATION_CREDENTIALS"
    fi
fi
echo ""

# Summary
echo "================================"
echo "Summary"
echo "================================"
echo ""
echo "Run the example scripts:"
echo "  python anthropic_example.py    # If Anthropic key is set"
echo "  python openai_example.py       # If OpenAI key is set"
echo "  python together_example.py     # If Together key is set"
echo "  python bedrock_example.py      # If AWS credentials are set"
echo "  python vertex_ai_example.py    # If GCP credentials are set"
echo ""
echo "Get API keys:"
echo "  Anthropic:   https://console.anthropic.com"
echo "  OpenAI:      https://platform.openai.com/api-keys"
echo "  Together AI: https://api.together.xyz/settings/api-keys"
echo ""
