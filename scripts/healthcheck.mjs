#!/usr/bin/env node
/* Repository healthcheck for the self-heal workflow.
   This repository's required CI is Python/pytest, with optional root package
   scripts for local convenience. Avoid pnpm workspace-only flags because this
   repo is not a pnpm workspace.
*/
import { execSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";

const run = (cmd) => execSync(cmd, { stdio: "inherit" });

const packageJson = existsSync("package.json")
  ? JSON.parse(readFileSync("package.json", "utf8"))
  : { scripts: {} };

const hasScript = (name) => Boolean(packageJson.scripts?.[name]);
const hasLocalBin = (name) => existsSync(`node_modules/.bin/${name}`);

const tryRun = (name, cmd) => {
  if (!cmd) return;
  console.log(`\n==> ${name}`);
  run(cmd);
};

try {
  // Optional JavaScript checks only run when the matching local tool exists.
  tryRun("Typecheck", hasScript("typecheck") && hasLocalBin("tsc") ? "pnpm run typecheck" : null);
  tryRun("Lint", hasScript("lint") && hasLocalBin("eslint") ? "pnpm run lint" : null);

  // Required repository tests: keep this aligned with .github/workflows/ci.yml.
  tryRun("Unit tests", hasScript("test") ? "pnpm run test" : "python -m pytest -q");

  // Workspace smoke builds are only valid in actual pnpm workspaces.
  if (existsSync("pnpm-workspace.yaml")) {
    tryRun("Workspace builds", "pnpm -r --if-present run build");
  }

  process.exit(0);
} catch (e) {
  console.error(e);
  process.exit(1);
}
