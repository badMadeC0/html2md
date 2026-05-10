#!/usr/bin/env node
/* Minimal healthcheck for this Python repository:
   - mirrors CI by running the pytest suite
*/
import { execSync } from "node:child_process";

const run = (cmd) => execSync(cmd, {
  stdio: "inherit",
  env: {
    ...process.env,
    LC_ALL: "C",
    PYTHONCOERCECLOCALE: process.env.PYTHONCOERCECLOCALE || "0",
  },
});

try {
  console.log("\n==> Unit tests");
  run("pytest -q");
} catch (e) {
  console.error(e);
  process.exit(1);
}
