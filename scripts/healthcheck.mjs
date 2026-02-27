#!/usr/bin/env node
/* Minimal, opinionated healthcheck for a pnpm monorepo (adapted for Python):
   - root: typecheck? test? lint? build?
*/
import { execSync } from "node:child_process";
import { existsSync } from "node:fs";

const run = (cmd) => execSync(cmd, { stdio: "inherit" });
const hasScript = (name) => {
  try {
    const out = execSync("npm run", { stdio: "pipe" }).toString();
    return out.includes(name);
  } catch { return false; }
};

const tryRun = (name, cmd) => {
  if (!cmd) return;
  console.log(`\n==> ${name}`);
  run(cmd);
};

try {
  // Root-level checks (best-effort if scripts exist)
  tryRun("Lint", hasScript("lint") ? "npm run lint" : null);
  tryRun("Unit tests", hasScript("test") ? "npm run test" : null);

  process.exit(process.exitCode ?? 0);
} catch (e) {
  console.error(e);
  process.exit(1);
}
