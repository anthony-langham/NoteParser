# SST Deployment Guide & Troubleshooting

## Overview

This guide covers common issues and solutions when deploying SST applications, particularly when using CloudFront with custom domains and external DNS providers like Cloudflare.

## Table of Contents

1. [CloudFront Function Conflicts](#cloudfront-function-conflicts)
2. [Custom Domains with External DNS](#custom-domains-with-external-dns)
3. [CloudFront Distribution Aliases](#cloudfront-distribution-aliases)
4. [Resource Cleanup Best Practices](#resource-cleanup-best-practices)
5. [Stack Deployment Order](#stack-deployment-order)
6. [Environment Variable Management](#environment-variable-management)
7. [Common Error Messages](#common-error-messages)

## CloudFront Function Conflicts

### Problem
```
Resource handler returned message: "Invalid request provided: AWS::CloudFront::Function: (Service: CloudFront, Status Code: 409, Request ID: xxx) One or more of the CNAMEs you provided are already associated with a different resource."
```

### Root Cause
- CloudFront functions are global resources with auto-generated names based on stack and construct names
- Previous deployments may leave orphaned functions that conflict with new deployments
- Function names follow pattern: `{region}{stage}{app}{stack}{construct}CloudFrontFunction{hash}`

### Solution

1. **Identify conflicting functions:**
```bash
aws cloudfront list-functions --query 'FunctionList.Items[?contains(Name, `your-app-name`)].{Name:Name,Stage:FunctionMetadata.Stage}' --output table
```

2. **Check which distributions use the functions:**
```bash
aws cloudfront get-distribution --id DISTRIBUTION_ID --query 'Distribution.DistributionConfig.DefaultCacheBehavior.FunctionAssociations'
```

3. **Remove function associations from distributions:**
```bash
# Get current config
aws cloudfront get-distribution-config --id DISTRIBUTION_ID > current-config.json

# Update config to remove function associations
jq '.DistributionConfig.DefaultCacheBehavior.FunctionAssociations = {"Quantity": 0, "Items": []}' current-config.json > updated-config.json

# Apply update
ETAG=$(jq -r '.ETag' current-config.json)
aws cloudfront update-distribution --id DISTRIBUTION_ID --distribution-config file://updated-config.json --if-match "$ETAG"
```

4. **Delete orphaned functions:**
```bash
# Get function ETag
ETAG=$(aws cloudfront describe-function --name FUNCTION_NAME --stage DEVELOPMENT --query 'ETag' --output text)

# Delete function
aws cloudfront delete-function --name FUNCTION_NAME --if-match "$ETAG"
```

### Prevention
- Use unique construct names in SST configurations
- Clean up resources when removing stacks: `npx sst remove --stage STAGE`
- Consider using different app names for different environments

## Custom Domains with External DNS

### Problem
```
Error: It seems you are configuring custom domains for you URL. And SST is not able to find the hosted zone "example.com" in your AWS Route 53 account.
```

### Root Cause
SST's `customDomain` configuration expects Route 53 hosted zones, but many projects use external DNS providers like Cloudflare.

### Solution: Use CDK Property Overrides

Instead of SST's `customDomain`, use CDK property overrides:

```typescript
// ❌ Don't use this with external DNS
const site = new StaticSite(stack, "frontend", {
  customDomain: {
    domainName: "example.com"
  }
});

// ✅ Use CDK overrides instead
const site = new StaticSite(stack, "frontend", {
  // ... other config
});

// Configure custom domains via CDK overrides
if (stack.stage === "prod" && site.cdk?.distribution) {
  const cfnDistribution = site.cdk.distribution.node.defaultChild as any;
  cfnDistribution.addPropertyOverride("DistributionConfig.Aliases", [
    "example.com",
    "www.example.com"
  ]);
  cfnDistribution.addPropertyOverride("DistributionConfig.ViewerCertificate", {
    AcmCertificateArn: "arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT_ID",
    SslSupportMethod: "sni-only",
    MinimumProtocolVersion: "TLSv1.2_2021"
  });
}
```

### SSL Certificate Requirements
- Certificate must be in `us-east-1` region for CloudFront
- Certificate must include all domain aliases
- Verify certificate is issued before deployment

### DNS Configuration (Cloudflare)
After successful deployment:
1. Get CloudFront distribution domain from outputs
2. Create CNAME records in Cloudflare:
   - `example.com` → `d1234567890abc.cloudfront.net`
   - `www.example.com` → `d1234567890abc.cloudfront.net`

## CloudFront Distribution Aliases

### Problem
```
One or more of the CNAMEs you provided are already associated with a different resource.
```

### Root Cause
Domain aliases can only be associated with one CloudFront distribution at a time.

### Solution

1. **Find which distribution has the aliases:**
```bash
aws cloudfront list-distributions --query 'DistributionList.Items[?Aliases.Quantity > `0`].{Id:Id,Aliases:Aliases.Items,Comment:Comment}' --output table
```

2. **Remove aliases from existing distribution:**
```bash
# Get current config
aws cloudfront get-distribution-config --id OLD_DISTRIBUTION_ID > old-config.json

# Remove aliases
jq '.DistributionConfig.Aliases = {"Quantity": 0, "Items": []}' old-config.json > updated-old-config.json

# Apply update
ETAG=$(jq -r '.ETag' old-config.json)
aws cloudfront update-distribution --id OLD_DISTRIBUTION_ID --distribution-config file://updated-old-config.json --if-match "$ETAG"
```

3. **Wait for distribution to update** (status: "Deployed")
4. **Deploy new stack with custom domains**

## Resource Cleanup Best Practices

### Before Deployment
1. **Check existing resources:**
```bash
# CloudFront distributions
aws cloudfront list-distributions --query 'DistributionList.Items[?contains(Comment, `your-app`)].{Id:Id,Status:Status,Comment:Comment}'

# CloudFront functions
aws cloudfront list-functions --query 'FunctionList.Items[?contains(Name, `your-app`)].{Name:Name,Stage:FunctionMetadata.Stage}'

# Origin Access Identities
aws cloudfront list-cloud-front-origin-access-identities --query 'CloudFrontOriginAccessIdentityList.Items[?contains(Comment, `your-app`)].{Id:Id,Comment:Comment}'
```

2. **Clean up orphaned resources** before deploying

### After Failed Deployments
1. **Remove failed stacks:**
```bash
npx sst remove --stage STAGE STACK_NAME
```

2. **Manual cleanup if needed** (use commands above)

### Stack Removal
```bash
# Remove specific stack
npx sst remove --stage prod Web

# Remove all stacks
npx sst remove --stage prod
```

## Stack Deployment Order

### Dependencies
- API stack should deploy before Web stack if Web depends on API outputs
- Deploy dependencies first, then dependent stacks

### Deployment Commands
```bash
# Deploy specific stack
npx sst deploy --stage prod API
npx sst deploy --stage prod Web

# Deploy all stacks
npx sst deploy --stage prod

# Check deployment status
aws cloudformation describe-stacks --stack-name prod-your-app-Web --query 'Stacks[0].StackStatus'
```

## Environment Variable Management

### SST Environment Variables
```typescript
const site = new StaticSite(stack, "frontend", {
  environment: {
    VITE_API_URL: api.url,
    VITE_API_KEY: process.env.API_KEY || "default",
    VITE_ENVIRONMENT: stack.stage,
  }
});
```

### Local Environment Files
- Create `.env` files for each component
- Never commit `.env` files to version control
- Use `.env.example` templates

### Infrastructure Environment
```bash
# infrastructure/.env
API_KEY=your-secure-api-key
AWS_REGION=eu-west-2
```

## Common Error Messages

### "Stack does not exist"
**Cause:** Stack was removed or never created
**Solution:** Deploy the stack fresh: `npx sst deploy --stage STAGE STACK_NAME`

### "Stack is in ROLLBACK_IN_PROGRESS"
**Cause:** Previous deployment failed and is rolling back
**Solution:** Wait for rollback to complete, then remove and redeploy

### "Command timed out"
**Cause:** CloudFront distributions take 10-15 minutes to deploy
**Solution:** Wait longer or check CloudFormation console for progress

### "Invalid If-Match version"
**Cause:** ETag mismatch when updating CloudFront resources
**Solution:** Get fresh ETag and retry

### "Resource creation cancelled"
**Cause:** One resource failed, causing dependent resources to cancel
**Solution:** Check failed resource, fix issue, redeploy

## Best Practices

1. **Use consistent naming patterns** for stacks and constructs
2. **Clean up resources** between major changes
3. **Test deployments** in dev environment first
4. **Monitor CloudFormation events** during deployment
5. **Keep SSL certificates** in us-east-1 for CloudFront
6. **Use CDK overrides** for complex configurations
7. **Version your infrastructure** changes
8. **Document custom domain setup** for team members

## Debugging Commands

```bash
# Check SST version
npx sst version

# List current stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# Check stack events
aws cloudformation describe-stack-events --stack-name STACK_NAME --query 'StackEvents[0:10]'

# Get stack outputs
aws cloudformation describe-stacks --stack-name STACK_NAME --query 'Stacks[0].Outputs'

# Check CloudFront distribution status
aws cloudfront get-distribution --id DISTRIBUTION_ID --query 'Distribution.Status'
```

## Resources

- [SST Documentation](https://docs.sst.dev/)
- [AWS CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [AWS CLI CloudFront Commands](https://docs.aws.amazon.com/cli/latest/reference/cloudfront/)
- [Cloudflare DNS Documentation](https://developers.cloudflare.com/dns/)