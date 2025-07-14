import { StackContext, Api } from "sst/constructs";

export function API({ stack }: StackContext) {
  const api = new Api(stack, "api", {
    defaults: {
      function: {
        runtime: "python3.9",
        timeout: "30 seconds",
        environment: {
          PYTHONPATH: "/var/task",
          API_KEY: process.env.API_KEY || "dev-api-key",
          CORS_ORIGINS: process.env.CORS_ORIGINS || "http://localhost:3000",
          LOG_LEVEL: process.env.LOG_LEVEL || "INFO",
          ENVIRONMENT: stack.stage,
          AWS_REGION: stack.region,
        },
      },
    },
    cors: {
      allowCredentials: false,
      allowHeaders: ["Content-Type", "Authorization", "X-Api-Key"],
      allowMethods: ["GET", "POST", "OPTIONS"],
      allowOrigins: stack.stage === "prod" 
        ? ["https://heidimcp.uk"] 
        : ["http://localhost:3000", "https://heidimcp.uk"],
    },
    routes: {
      "POST /process": "backend/lambda/process.handler",
      "GET /health": "backend/lambda/health.handler",
    },
  });

  stack.addOutputs({
    ApiEndpoint: api.url,
    Stage: stack.stage,
    Region: stack.region,
  });

  return api;
}