#!/bin/bash
# AWS Bedrock Setup Script
# Copyright 2025-2030 all rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com

echo "================================================================"
echo "AWS BEDROCK COMPREHENSIVE EXAMPLES - SETUP SCRIPT"
echo "Copyright 2025-2030 all rights reserved"
echo "Ashutosh Sinha, Email: ajsinha@gmail.com"
echo "================================================================"

# Step 1: Check Python version
echo ""
echo "[Step 1/5] Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION found"
else
    echo "✗ Python 3 not found. Please install Python 3.7 or later."
    exit 1
fi

# Step 2: Install dependencies
echo ""
echo "[Step 2/5] Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Step 3: Check AWS CLI
echo ""
echo "[Step 3/5] Checking AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    echo "✓ $AWS_VERSION found"
else
    echo "⚠ AWS CLI not found. Install from: https://aws.amazon.com/cli/"
    echo "  Or run: pip3 install awscli"
fi

# Step 4: Check AWS credentials
echo ""
echo "[Step 4/5] Checking AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✓ AWS credentials configured"
    aws sts get-caller-identity --query '[Account,UserId,Arn]' --output text
else
    echo "⚠ AWS credentials not configured"
    echo "  Run: aws configure"
    echo "  You'll need:"
    echo "    - AWS Access Key ID"
    echo "    - AWS Secret Access Key"
    echo "    - Default region (e.g., us-east-1)"
fi

# Step 5: Instructions
echo ""
echo "[Step 5/5] Setup complete! Next steps:"
echo ""
echo "================================================================"
echo "IMPORTANT: Enable Model Access in AWS Console"
echo "================================================================"
echo "1. Go to: https://console.aws.amazon.com/bedrock/"
echo "2. Click 'Model access' in left sidebar"
echo "3. Click 'Manage model access'"
echo "4. Select these models:"
echo "   ✓ Meta Llama 3 8B Instruct (Required)"
echo "   ✓ Meta Llama 3 70B Instruct"
echo "   ✓ Claude 3 Haiku"
echo "   ✓ Claude 3 Sonnet"
echo "   ✓ Amazon Titan Express"
echo "   ✓ Any other models you want to use"
echo "5. Click 'Request model access'"
echo "6. Wait for approval (usually instant)"
echo ""
echo "================================================================"
echo "Run Examples"
echo "================================================================"
echo ""
echo "Quick Test (recommended first):"
echo "  python3 quick_start.py"
echo ""
echo "Basic Examples (13+ models):"
echo "  python3 aws_bedrock_comprehensive_examples.py"
echo ""
echo "Advanced Features:"
echo "  python3 aws_bedrock_advanced_examples.py"
echo ""
echo "Real-World Use Cases:"
echo "  python3 real_world_use_cases.py"
echo ""
echo "================================================================"
echo "Documentation"
echo "================================================================"
echo "Read full documentation:"
echo "  cat README.md"
echo ""
echo "Project summary:"
echo "  cat PROJECT_SUMMARY.md"
echo ""
echo "================================================================"
echo "Copyright 2025-2030 all rights reserved"
echo "Ashutosh Sinha, Email: ajsinha@gmail.com"
echo "================================================================"
