import { StackContext, StaticSite, use } from "sst/constructs";
import { ViewerProtocolPolicy, PriceClass } from "aws-cdk-lib/aws-cloudfront";
import { Certificate } from "aws-cdk-lib/aws-certificatemanager";
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
      VITE_APP_NAME: "Heidi Clinical Decision Support",
      VITE_APP_VERSION: "1.0.0",
      VITE_ENVIRONMENT: stack.stage,
    },
    // CloudFront distribution configuration
    cdk: {
      distribution: {
        defaultBehavior: {
          compress: true,
          viewerProtocolPolicy: ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          cachePolicy: {
            cachePolicyId: "4135ea2d-6df8-44a3-9df3-4b5a84be39ad", // CachingDisabled for API calls
          },
        },
        comment: `Heidi Clinical Decision Support - ${stack.stage}`,
        priceClass: PriceClass.PRICE_CLASS_100, // Use only North America and Europe
      },
    },
    // Custom domain configuration for production
    // Note: Using Cloudflare for DNS, SSL cert must be in us-east-1 for CloudFront
    // Infrastructure in eu-west-2 (London), but CloudFront is global
    // Custom domain configuration for production - CloudFront certificate is validated
    customDomain: stack.stage === "prod" ? "heidimcp.uk" : undefined,
  });

  stack.addOutputs({
    SiteUrl: site.url,
    CloudFrontDistribution: site.cdk?.distribution?.distributionDomainName,
    CustomDomain: stack.stage === "prod" ? "https://heidimcp.uk" : undefined,
  });

  return site;
}