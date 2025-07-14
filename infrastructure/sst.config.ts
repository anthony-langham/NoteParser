import { SSTConfig } from "sst";
import { API } from "./stacks/API";
import { Web } from "./stacks/Web";

export default {
  config(_input) {
    return {
      name: "heidi",
      region: "us-east-1",
    };
  },
  stacks(app) {
    // Set default removal policy based on stage
    app.setDefaultRemovalPolicy(
      app.stage === "prod" ? "retain" : "destroy"
    );

    // Configure function defaults
    app.setDefaultFunctionProps({
      runtime: "python3.9",
      architecture: "arm_64", // Use ARM for better cost efficiency
      timeout: "30 seconds",
      memorySize: "256 MB",
    });

    // Deploy stacks
    app.stack(API).stack(Web);
  },
} satisfies SSTConfig;