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
    },
  });

  stack.addOutputs({
    SiteUrl: site.url,
  });

  return site;
}