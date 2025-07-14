import { StackContext, Api } from "sst/constructs";

export function API({ stack }: StackContext) {
  const api = new Api(stack, "api", {
    defaults: {
      function: {
        runtime: "python3.9",
        environment: {
          PYTHONPATH: "/var/task",
        },
      },
    },
    routes: {
      "POST /process": "backend/lambda/process.handler",
      "GET /health": "backend/lambda/health.handler",
    },
  });

  stack.addOutputs({
    ApiEndpoint: api.url,
  });

  return api;
}