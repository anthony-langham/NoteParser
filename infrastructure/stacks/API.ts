import { StackContext, Api, Function } from "sst/constructs";
import { Certificate } from "aws-cdk-lib/aws-certificatemanager";

export function API({ stack }: StackContext) {
  // Create a Lambda layer for Python dependencies
  const pythonDependencyLayer = new Function(stack, "python-deps", {
    handler: "backend/lambda/health.handler",
    runtime: "python3.9",
    layers: [
      "arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p39-requests:2"
    ]
  });

  const api = new Api(stack, "api", {
    defaults: {
      function: {
        runtime: "python3.9",
        timeout: "30 seconds",
        memorySize: "512 MB",
        environment: {
          PYTHONPATH: "/var/task:/opt/python",
          API_KEY: process.env.API_KEY || "dev-api-key-change-in-production",
          CORS_ORIGINS: process.env.CORS_ORIGINS || "http://localhost:3000,https://heidimcp.uk",
          LOG_LEVEL: process.env.LOG_LEVEL || "INFO",
          ENVIRONMENT: stack.stage,
          DATA_PATH: "/opt/data/",
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
    // Custom domain configuration for production
    customDomain: stack.stage === "prod" ? "api.heidimcp.uk" : undefined,
    cors: {
      allowCredentials: false,
      allowHeaders: ["Content-Type", "Authorization", "X-Api-Key", "x-api-key"],
      allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
      allowOrigins: stack.stage === "prod" 
        ? ["https://heidimcp.uk", "https://www.heidimcp.uk"] 
        : ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173", "https://heidimcp.uk"],
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