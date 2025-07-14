# SST with Cloudflare DNS (No Route 53) - Complete Guide

This document details how to configure AWS SST (Serverless Stack) with custom domains using Cloudflare DNS management while avoiding Route 53 entirely.

## Problem Overview

**The Core Issue**: SST's `customDomain` configuration assumes Route 53 hosted zone management. When you specify a custom domain, SST automatically tries to:
1. Find a hosted zone in Route 53 for your domain
2. Create DNS records for domain validation
3. Manage SSL certificate validation through Route 53

**Our Requirement**: Use Cloudflare for all DNS management while still having custom domains work with CloudFront and API Gateway.

## Error Messages You'll Encounter

### 1. Route 53 Hosted Zone Error
```
Error: It seems you are configuring custom domains for you URL. And SST is not able to find the hosted zone "yourdomain.com" in your AWS Route 53 account. Please double check and make sure the zone exists, or pass in a different zone.
```

### 2. SSL Certificate Validation Errors
```
Invalid request provided: The specified SSL certificate doesn't exist, isn't in us-east-1 region, isn't valid, or doesn't include a valid certificate chain.
```

### 3. TypeScript/CDK Version Conflicts
```
Type 'import(".../aws-cdk-lib/aws-certificatemanager/lib/certificate").ICertificate' is not assignable to type 'import(".../sst/node_modules/aws-cdk-lib/aws-certificatemanager/lib/certificate").ICertificate'
```

## Solution Architecture

### Step 1: SSL Certificate Setup
**CRITICAL**: SSL certificates for CloudFront MUST be in `us-east-1` region, regardless of where your main infrastructure is deployed.

```bash
# Create/validate SSL certificate in us-east-1 for CloudFront
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names "*.yourdomain.com" \
  --validation-method DNS \
  --region us-east-1

# List certificates to get ARN
aws acm list-certificates --region us-east-1 --query 'CertificateSummaryList[*].[DomainName,CertificateArn,Status]' --output table
```

**Important**: You'll need to manually add the DNS validation records to Cloudflare when the certificate is requested.

### Step 2: Infrastructure Configuration

#### Web Stack (CloudFront) - DO NOT Use customDomain

**File: `infrastructure/stacks/Web.ts`**

```typescript
import { StackContext, StaticSite, use } from "sst/constructs";
import { ViewerProtocolPolicy, PriceClass } from "aws-cdk-lib/aws-cloudfront";
import { API } from "./API";

export function Web({ stack }: StackContext) {
  const api = use(API);

  const site = new StaticSite(stack, "web", {
    path: "../frontend",
    buildCommand: "npm run build",
    buildOutput: "dist",
    environment: {
      VITE_API_URL: api.url,
      VITE_API_KEY: process.env.API_KEY || "dev-api-key",
      // ... other env vars
    },
    // CloudFront distribution configuration - NO customDomain here
    cdk: {
      distribution: {
        defaultBehavior: {
          compress: true,
          viewerProtocolPolicy: ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          cachePolicy: {
            cachePolicyId: "4135ea2d-6df8-44a3-9df3-4b5a84be39ad", // CachingDisabled
          },
        },
        comment: `Your App - ${stack.stage}`,
        priceClass: PriceClass.PRICE_CLASS_100,
      },
    },
    // DO NOT use customDomain - this triggers Route 53 requirement
  });

  // Configure custom domains using CDK override (bypasses SST's Route 53 requirement)
  if (stack.stage === "prod" && site.cdk?.distribution) {
    const cfnDistribution = site.cdk.distribution.node.defaultChild as any;
    cfnDistribution.addPropertyOverride("DistributionConfig.Aliases", [
      "yourdomain.com",
      "www.yourdomain.com"
    ]);
    cfnDistribution.addPropertyOverride("DistributionConfig.ViewerCertificate", {
      AcmCertificateArn: "arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT-ID",
      SslSupportMethod: "sni-only",
      MinimumProtocolVersion: "TLSv1.2_2021"
    });
  }

  stack.addOutputs({
    SiteUrl: site.url,
    CloudFrontDistribution: site.cdk?.distribution?.distributionDomainName,
    CustomDomain: stack.stage === "prod" ? "https://yourdomain.com" : undefined,
  });

  return site;
}
```

#### API Stack (API Gateway) - Disable Custom Domain

**File: `infrastructure/stacks/API.ts`**

```typescript
import { StackContext, Api } from "sst/constructs";

export function API({ stack }: StackContext) {
  const api = new Api(stack, "api", {
    defaults: {
      function: {
        runtime: "python3.10", // or nodejs18.x
        timeout: "30 seconds",
        memorySize: "512 MB",
        environment: {
          // ... your env vars
        },
      },
    },
    // DO NOT use customDomain - this also triggers Route 53 requirement
    // customDomain: stack.stage === "prod" ? "api.yourdomain.com" : undefined,
    cors: {
      allowCredentials: false,
      allowHeaders: ["Content-Type", "Authorization", "X-Api-Key"],
      allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
      allowOrigins: stack.stage === "prod" 
        ? ["https://yourdomain.com", "https://www.yourdomain.com"] 
        : ["http://localhost:3000", "http://localhost:5173"],
    },
    routes: {
      "POST /process": "../backend/lambda/process.handler",
      "GET /health": "../backend/lambda/health.handler",
      // ... your routes
    },
  });

  stack.addOutputs({
    ApiEndpoint: api.url,
    // ... other outputs
  });

  return api;
}
```

### Step 3: DNS Configuration in Cloudflare

After successful deployment, configure these DNS records in Cloudflare:

#### Frontend (CloudFront)
```
Type: CNAME
Name: yourdomain.com (or @)
Target: d1234567890123.cloudfront.net (from deployment output)
Proxy: 🟠 ON (orange cloud) - Optional, can be proxied
TTL: Auto
```

```
Type: CNAME  
Name: www.yourdomain.com
Target: d1234567890123.cloudfront.net
Proxy: 🟠 ON (orange cloud) - Optional, can be proxied
TTL: Auto
```

#### API (API Gateway)
```
Type: CNAME
Name: api.yourdomain.com  
Target: abcd1234.execute-api.region.amazonaws.com
Proxy: ⚫ OFF (gray cloud) - IMPORTANT: Must be DNS-only
TTL: Auto
```

**Critical**: API Gateway DNS records must NOT be proxied (gray cloud) to avoid SSL and CORS conflicts.

### Step 4: Deployment Commands

```bash
# Use correct Node version
nvm use

# Deploy infrastructure
npx sst deploy --stage prod

# Remove if needed
npx sst remove --stage prod
```

## Common Issues and Solutions

### Issue 1: Certificate ARN Not Found
**Problem**: Wrong certificate ARN or certificate in wrong region.

**Solution**: 
```bash
# List certificates in us-east-1 (required for CloudFront)
aws acm list-certificates --region us-east-1
```
Use the exact ARN from this command.

### Issue 2: Docker Issues (Python Lambdas)
**Problem**: `Cannot connect to the Docker daemon`

**Solution**:
```bash
# Install Docker Desktop
brew install --cask docker-desktop

# Start Docker Desktop (can be done via GUI or)
open -a Docker

# Verify Docker is running
docker info
```

### Issue 3: CORS Duplicate Headers
**Problem**: `Duplicated values are not allowed in allow-headers`

**Solution**: Remove duplicate headers from CORS config:
```typescript
allowHeaders: ["Content-Type", "Authorization", "X-Api-Key"], // No duplicates
```

### Issue 4: Python Runtime Compatibility
**Problem**: MCP libraries require Python 3.10+, but Lambda defaults to 3.9

**Solution**: Update runtime in all function configs:
```typescript
defaults: {
  function: {
    runtime: "python3.10", // Updated from python3.9
  },
},
```

### Issue 5: TypeScript CDK Version Conflicts
**Problem**: Mixing direct CDK imports with SST's bundled CDK

**Solution**: Use property overrides instead of direct CDK constructs:
```typescript
// DON'T do this:
import { Certificate } from "aws-cdk-lib/aws-certificatemanager";

// DO this instead:
cfnDistribution.addPropertyOverride("DistributionConfig.ViewerCertificate", {
  AcmCertificateArn: "arn:aws:acm:...",
  SslSupportMethod: "sni-only",
  MinimumProtocolVersion: "TLSv1.2_2021"
});
```

## Testing and Verification

### 1. Test CloudFront Distribution
```bash
# Test direct CloudFront URL first
curl -I https://d1234567890123.cloudfront.net

# Then test custom domain
curl -I https://yourdomain.com
```

### 2. Test API Gateway
```bash
# Test direct API Gateway URL
curl https://abcd1234.execute-api.region.amazonaws.com/health

# Test custom domain (if configured)
curl https://api.yourdomain.com/health
```

### 3. Verify SSL Certificate
```bash
# Check certificate details
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com < /dev/null | openssl x509 -noout -text
```

## Key Principles

1. **Never use SST's `customDomain`** - it always requires Route 53
2. **Use CDK property overrides** to configure custom domains
3. **SSL certificates must be in us-east-1** for CloudFront
4. **API Gateway DNS records must not be proxied** in Cloudflare
5. **Test direct AWS URLs first** before configuring custom domains
6. **Use specific certificate ARNs** from `aws acm list-certificates`

## File Structure Reference

```
infrastructure/
├── sst.config.ts
└── stacks/
    ├── API.ts          # No customDomain, use property overrides
    └── Web.ts          # CDK overrides for CloudFront domains
```

This approach gives you full custom domain functionality while keeping all DNS management in Cloudflare and avoiding Route 53 entirely.