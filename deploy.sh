#!/bin/bash

# Heidi Deployment Script
# This script handles the full deployment process for the Heidi Clinical Decision Support system

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
STAGE="prod"
SKIP_BUILD=false
STACK=""

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --stage) STAGE="$2"; shift ;;
        --skip-build) SKIP_BUILD=true ;;
        --stack) STACK="$2"; shift ;;
        -h|--help) 
            echo "Usage: ./deploy.sh [options]"
            echo "Options:"
            echo "  --stage <stage>     Deploy to specific stage (default: prod)"
            echo "  --skip-build        Skip frontend build step (SST will build it anyway)"
            echo "  --stack <stack>     Deploy specific stack (API or Web)"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo -e "${GREEN}🚀 Starting Heidi deployment to stage: ${STAGE}${NC}"

# Check if we're in the project root
if [ ! -f "CLAUDE.md" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Use correct Node version
if command -v nvm &> /dev/null; then
    echo -e "${YELLOW}📦 Setting Node version...${NC}"
    nvm use
fi

# Optional: Build frontend manually (SST will do this automatically)
if [ "$SKIP_BUILD" = false ]; then
    echo -e "${YELLOW}🔨 Pre-building frontend (optional - SST will also build)...${NC}"
    cd frontend
    npm install
    npm run build
    cd ..
    echo -e "${GREEN}✅ Frontend build complete${NC}"
else
    echo -e "${YELLOW}⏭️  Skipping manual frontend build (SST will build during deployment)${NC}"
fi

# Install infrastructure dependencies
echo -e "${YELLOW}📦 Installing infrastructure dependencies...${NC}"
cd infrastructure
npm install

# Deploy to AWS (from infrastructure directory as SST expects)
echo -e "${YELLOW}☁️  Deploying to AWS (stage: ${STAGE})...${NC}"
echo -e "${YELLOW}   Note: SST will automatically build the frontend from ../frontend${NC}"

if [ -n "$STACK" ]; then
    echo -e "${YELLOW}   Deploying specific stack: ${STACK}${NC}"
    npx sst deploy --stage "$STAGE" "$STACK"
else
    echo -e "${YELLOW}   Deploying all stacks (API and Web)...${NC}"
    npx sst deploy --stage "$STAGE"
fi

# Return to project root
cd ..

# Get deployment outputs
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${YELLOW}📊 Stack outputs:${NC}"
aws cloudformation describe-stacks --stack-name "${STAGE}-heidi-Web" --query 'Stacks[0].Outputs' --output table 2>/dev/null || true

# Show the deployed URLs
echo -e "${GREEN}🌐 Deployed URLs:${NC}"
if [ "$STAGE" = "prod" ]; then
    echo -e "   Frontend: ${GREEN}https://noteparser.uk${NC}"
    echo -e "   API: Based on API Gateway configuration"
    
    # Get the CloudFront distribution ID for cache invalidation tip
    DISTRIBUTION_ID=$(aws cloudformation describe-stacks --stack-name "${STAGE}-heidi-Web" --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' --output text 2>/dev/null || echo "")
    if [ -n "$DISTRIBUTION_ID" ]; then
        echo -e "${YELLOW}💡 Tip: To force immediate cache refresh, run:${NC}"
        echo -e "   aws cloudfront create-invalidation --distribution-id ${DISTRIBUTION_ID} --paths '/*'"
    fi
else
    FRONTEND_URL=$(aws cloudformation describe-stacks --stack-name "${STAGE}-heidi-Web" --query 'Stacks[0].Outputs[?OutputKey==`SiteUrl`].OutputValue' --output text 2>/dev/null || echo "Check AWS Console")
    API_URL=$(aws cloudformation describe-stacks --stack-name "${STAGE}-heidi-API" --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' --output text 2>/dev/null || echo "Check AWS Console")
    echo -e "   Frontend: ${GREEN}${FRONTEND_URL}${NC}"
    echo -e "   API: ${GREEN}${API_URL}${NC}"
fi

echo -e "${GREEN}🎉 Deployment successful!${NC}"

# Reminder about CloudFront
echo -e "${YELLOW}⏳ Note: CloudFront distribution may take 10-20 minutes to fully propagate changes${NC}"
echo -e "${YELLOW}   The site will be available immediately, but global edge locations take time to update${NC}"