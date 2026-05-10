#!/usr/bin/env node
/* Repository healthcheck aligned with the existing Python CI workflow. */
import { execSync } from "node:child_process";

const checks = [
  ["Python tests", "python -m pytest -q"],
];

let failed = false;

for (const [name, cmd] of checks) {
  console.log(`\n==> ${name}`);
  try {
    execSync(cmd, { stdio: "inherit" });
  } catch {
    failed = true;
  }
}

process.exit(failed ? 1 : 0);
