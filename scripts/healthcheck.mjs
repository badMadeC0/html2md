#!/usr/bin/env node
/* Repository healthcheck for the Python CI surface.
   Mirrors .github/workflows/ci.yml by running the pytest suite after the
   workflow has installed the package and test dependencies.
*/
import { spawnSync } from "node:child_process";

const candidates = process.env.PYTHON
  ? [[process.env.PYTHON, []]]
  : [
      ["python", []],
      ["python3", []],
      ["py", ["-3"]],
    ];

console.log("\n==> Python tests");

const testEnv = process.platform === "win32"
  ? process.env
  : { ...process.env, LC_ALL: "C", LANG: "C" };

let lastResult;
for (const [command, prefixArgs] of candidates) {
  console.log(`$ ${[command, ...prefixArgs, "-m", "pytest", "-q"].join(" ")}`);
  const result = spawnSync(command, [...prefixArgs, "-m", "pytest", "-q"], {
    stdio: "inherit",
    env: testEnv,
  });
  lastResult = result;

  if (result.error?.code === "ENOENT" || result.status === 127) {
    continue;
  }

  process.exit(result.status ?? 1);
}

if (lastResult?.error && lastResult.error.code !== "ENOENT") {
  console.error(lastResult.error);
}
process.exit(lastResult?.status ?? 1);
