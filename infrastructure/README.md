# Heidi Infrastructure - SST Deployment

This directory contains the AWS infrastructure configuration using SST (Serverless Stack).

## Prerequisites

- Node.js 18+ (use `nvm use` in project root)
- AWS CLI configured with appropriate credentials
- SST CLI installed (`npm install -g sst`)

## Quick Start

### 1. Install Dependencies

```bash
cd infrastructure
npm install
```

### 2. Deploy to Production

```bash
# From infrastructure directory
npx sst deploy --stage prod

# Or use the deployment script from project root
./deploy.sh
```

### 3. Check Deployment Status

```bash
# View stack outputs
npx sst console --stage prod

# Check CloudFormation stacks
aws cloudformation describe-stacks --stack-name prod-heidi-Web --query 'Stacks[0].Outputs'
```

## Stack Architecture

- **API Stack**: Lambda functions, API Gateway, and backend configuration
- **Web Stack**: CloudFront distribution, S3 bucket for frontend static files

## Deployment Process

1. **Frontend Build**: The deployment automatically builds the frontend from `../frontend`
2. **Backend Package**: Python dependencies are bundled with Lambda functions
3. **CloudFront Update**: Distribution is updated with new static assets

## Common Commands

### Deploy Specific Stack

```bash
# Deploy only API
npx sst deploy --stage prod API

# Deploy only Web (frontend)
npx sst deploy --stage prod Web
```

### Remove Infrastructure

```bash
# Remove development environment
npx sst remove --stage dev

# Remove production (be careful!)
npx sst remove --stage prod
```

### View Logs

```bash
# Tail Lambda function logs
npx sst console --stage prod
```

### Local Development

```bash
# Start local development (not recommended for this project)
npx sst dev --stage dev
```

## Environment Variables

The infrastructure uses environment variables from:
- Backend: `../backend/.env`
- Frontend: `../frontend/.env`

These are automatically loaded during deployment.

## Troubleshooting

### CloudFront Takes Long to Deploy
CloudFront distributions can take 10-20 minutes to fully deploy. Check AWS Console for progress.

### Stack Update Failed
If deployment fails:
1. Check CloudFormation console for detailed error
2. Fix the issue
3. Re-run deployment command

### Custom Domain Issues
See `../docs/SST_Deployment_Guide.md` for detailed custom domain configuration.

## Cost Considerations

- Lambda: Pay per request (very low for this use case)
- CloudFront: Pay per request and data transfer
- S3: Minimal storage costs for static files
- Estimated monthly cost: $5-15 for moderate usage

## Security

- API Gateway uses API key authentication
- CloudFront uses Origin Access Identity for S3
- Lambda functions have minimal IAM permissions
- All traffic is HTTPS encrypted

## Deployment Checklist

Before deploying to production:
- [ ] Frontend builds successfully (`cd ../frontend && npm run build`)
- [ ] Backend tests pass (`cd ../backend && python -m pytest`)
- [ ] Environment variables are set correctly
- [ ] Current git branch is clean and up to date