import { StackContext, Api, Function } from "sst/constructs";
import { Certificate } from "aws-cdk-lib/aws-certificatemanager";
import { MethodLoggingLevel } from "aws-cdk-lib/aws-apigateway";

export function API({ stack }: StackContext) {
  const api = new Api(stack, "api", {
    defaults: {
      function: {
        runtime: "python3.10",
        timeout: "30 seconds",
        memorySize: "512 MB",
        environment: {
          PYTHONPATH: "/var/task:/opt/python",
          API_KEY: process.env.API_KEY || "dev-api-key-change-in-production",
          CORS_ORIGINS: process.env.CORS_ORIGINS || "http://localhost:3000,https://noteparser.uk,https://www.noteparser.uk",
          LOG_LEVEL: process.env.LOG_LEVEL || "INFO",
          ENVIRONMENT: stack.stage,
          DATA_PATH: "/var/task/mcp_server/data/",
          CONDITIONS_FILE: "conditions.json",
          GUIDELINES_FILE: "guidelines.json",
        },
        // Copy MCP server files and data to Lambda
        copyFiles: [
          {
            from: "../backend/mcp_server",
            to: "mcp_server"
          }
        ],
      },
    },
    // Custom domain disabled - using Cloudflare DNS, will point to API Gateway URL directly
    // customDomain: stack.stage === "prod" ? "api.noteparser.uk" : undefined,
    cdk: {
      restApi: {
        deployOptions: {
          loggingLevel: MethodLoggingLevel.INFO,
          dataTraceEnabled: true,
          metricsEnabled: true,
        },
      },
    },
    cors: {
      allowCredentials: false,
      allowHeaders: ["Content-Type", "Authorization", "x-api-key"],
      allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
      allowOrigins: ["*"],
    },
    routes: {
      // Main application routes
      "POST /process": "../backend/lambda/process.handler",
      "GET /health": "../backend/lambda/health.handler",
      "GET /auth": "../backend/lambda/auth.handler",
      "POST /auth": "../backend/lambda/auth.handler",
      
      // API versioned routes
      "POST /api/process": "../backend/lambda/process.handler",
      "GET /api/health": "../backend/lambda/health.handler",
      "GET /api/auth": "../backend/lambda/auth.handler",
      "POST /api/auth": "../backend/lambda/auth.handler",
      
      // CORS support
      "OPTIONS /{proxy+}": "../backend/lambda/cors.handler",
      
      // Fallback router (handles any unmatched routes)
      "$default": "../backend/lambda/main.handler",
    },
  });

  stack.addOutputs({
    ApiEndpoint: api.url,
    Stage: stack.stage,
    Region: stack.region,
    Environment: stack.stage,
    ApiId: api.id,
  });

  return api;
}