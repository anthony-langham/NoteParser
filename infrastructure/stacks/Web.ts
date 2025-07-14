import { StackContext, StaticSite, use } from "sst/constructs";
import { API } from "./API";

export function Web({ stack }: StackContext) {
  const api = use(API);

  const site = new StaticSite(stack, "web", {
    path: "frontend",
    buildCommand: "npm run build",
    buildOutput: "dist",
    environment: {
      VITE_API_URL: api.url,
      VITE_API_KEY: process.env.API_KEY || "dev-api-key",
      VITE_APP_NAME: "Heidi Clinical Decision Support",
      VITE_APP_VERSION: "1.0.0",
      VITE_ENVIRONMENT: stack.stage,
    },
    // Custom domain configuration for production
    customDomain: stack.stage === "prod" ? {
      domainName: "heidimcp.uk",
      hostedZone: "heidimcp.uk",
    } : undefined,
  });

  stack.addOutputs({
    SiteUrl: site.url,
    CustomDomain: stack.stage === "prod" ? "https://heidimcp.uk" : undefined,
  });

  return site;
}