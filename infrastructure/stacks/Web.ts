import { StackContext, StaticSite, use } from "sst/constructs";
import { ViewerProtocolPolicy, PriceClass } from "aws-cdk-lib/aws-cloudfront";
import { API } from "./API";

export function Web({ stack }: StackContext) {
  const api = use(API);

  const site = new StaticSite(stack, "frontend", {
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
    // CloudFront distribution configuration with custom domains via CDK overrides
    cdk: {
      distribution: {
        defaultBehavior: {
          compress: true,
          viewerProtocolPolicy: ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          cachePolicy: {
            cachePolicyId: "4135ea2d-6df8-44a3-9df3-4b5a84be39ad", // CachingDisabled for API calls
          },
        },
        comment: `Heidi Clinical Decision Support - ${stack.stage} - v2`,
        priceClass: PriceClass.PRICE_CLASS_100, // Use only North America and Europe
      },
    },
  });

  // Configure custom domains for production using CDK override (bypasses SST's Route 53 requirement)
  if (stack.stage === "prod" && site.cdk?.distribution) {
    const cfnDistribution = site.cdk.distribution.node.defaultChild as any;
    cfnDistribution.addPropertyOverride("DistributionConfig.Aliases", [
      "heidimcp.uk",
      "www.heidimcp.uk"
    ]);
    cfnDistribution.addPropertyOverride("DistributionConfig.ViewerCertificate", {
      AcmCertificateArn: "arn:aws:acm:us-east-1:146409062658:certificate/fdc74de3-d68d-422f-9f07-74527254e98d",
      SslSupportMethod: "sni-only",
      MinimumProtocolVersion: "TLSv1.2_2021"
    });
  }

  stack.addOutputs({
    SiteUrl: site.url,
    CloudFrontDistribution: site.cdk?.distribution?.distributionDomainName,
    CustomDomain: stack.stage === "prod" ? "https://heidimcp.uk" : undefined,
  });

  return site;
}