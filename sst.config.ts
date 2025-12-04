/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "sandbox-incode-risk-model",
      removal: input?.stage === "production" ? "retain" : "remove",
      protect: ["production"].includes(input?.stage),
      home: "aws",
      providers: {
        aws: {
          profile: "asu-frog-sandbox",
          region: "us-west-2",
        },
      },
    };
  },
  async run() {
    const catBoostFn = new sst.aws.Function(
      "sandbox-iden-catboost-risk-model",
      {
        handler: "risk_model/handler.handler",
        runtime: "python3.11",
        memory: "1024 MB",
        timeout: "10 seconds",
        python: {
          container: true,
        },
        architecture: "x86_64",
        environment: {
          DEFAULT_THRESHOLD: "0.75",
        },
        url: true,
      }
    );

    return {
      catBoostFnUrl: catBoostFn.url,
    };
  },
});
