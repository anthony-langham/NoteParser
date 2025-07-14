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
    app.stack(API).stack(Web);
  },
} satisfies SSTConfig;