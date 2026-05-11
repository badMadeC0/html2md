#!/usr/bin/env node
/* Repository healthcheck used by the self-heal workflow.
   Run checks only when this repository is configured for them; do not assume
   a pnpm workspace or a TypeScript project exists.
*/
import { execSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";

const run = (cmd) => execSync(cmd, { stdio: "inherit" });
const readPackageJson = () => {
  if (!existsSync("package.json")) return {};
  const contents = readFileSync("package.json", "utf8").trim();
  if (!contents) return {};
  try {
    return JSON.parse(contents);
  } catch (error) {
    console.warn(`Ignoring unreadable package.json: ${error.message}`);
    return {};
  }
};
const packageJson = readPackageJson();
const scripts = packageJson.scripts && typeof packageJson.scripts === "object" ? packageJson.scripts : {};
const hasScript = (name) => typeof scripts[name] === "string";
const hasTypeScriptConfig = () => existsSync("tsconfig.json") || existsSync("jsconfig.json");

const tryRun = (name, cmd) => {
  if (!cmd) return;
  console.log(`\n==> ${name}`);
  run(cmd);
};

try {
  // JavaScript checks are opt-in and run at the package root. This repository
  // is not a pnpm workspace, so avoid workspace-only flags such as `-w`.
  tryRun("Typecheck", hasScript("typecheck") && hasTypeScriptConfig() ? "pnpm run typecheck" : null);
  tryRun("Lint", hasScript("lint") ? "pnpm run lint" : null);
  tryRun("Unit tests", hasScript("test") ? "pnpm run test" : null);
  tryRun("Build", hasScript("build") ? "pnpm run build" : null);

  // Native Python project checks. Invoke pytest through the configured Python
  // interpreter and mirror the quiet pytest invocation used by CI.
  tryRun("Python tests", existsSync("pyproject.toml") && existsSync("tests") ? "python -m pytest -q" : null);

  process.exit(0);
} catch (e) {
  console.error(e);
  process.exit(1);
}
