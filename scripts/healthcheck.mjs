#!/usr/bin/env node
/* Minimal, opinionated healthcheck for a pnpm project:
   - root: typecheck? test? lint?
   - workspaces: smoke build where available
*/
import { execSync } from "node:child_process";
import { existsSync, readdirSync, statSync, readFileSync } from "node:fs";
import { join } from "node:path";

const run = (cmd) => execSync(cmd, { stdio: "inherit" });

const hasScript = (name) => !!pkg.scripts?.[name];

const tryRun = (name, cmd) => {
  if (!cmd) return;
  console.log(`\n==> ${name}`);
  run(cmd);
};

try {
  // Delegate to the Python healthcheck which matches this project's structure.
  const commands = [
    "python scripts/healthcheck.py",
    "python3 scripts/healthcheck.py",
  ];

  let succeeded = false;

  for (const cmd of commands) {
    try {
      console.log(`\n==> Running project healthcheck via: ${cmd}`);
      run(cmd);
      succeeded = true;
      break;
    } catch (e) {
      // Try the next interpreter; remember that a failure occurred.
      console.error(`[healthcheck] Failed with "${cmd}": ${e.message || e}`);
      process.exitCode = 1;
    }
  }

  if (!succeeded) {
    console.error("[healthcheck] Unable to run Python healthcheck.");
    process.exit(process.exitCode ?? 1);
  } else {
    process.exit(process.exitCode ?? 0);
  }
} catch (e) {
  console.error(e);
  process.exit(1);
}
