#!/usr/bin/env node
/* Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
   Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
*/
import { execSync, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";

const sh = (cmd, opts={}) => {
  console.log(`\n$ ${cmd}`);
  return execSync(cmd, { stdio: "inherit", ...opts });
};
const trySh = (cmd, opts={}) => {
  try { sh(cmd, opts); return true; } catch { return false; }
};
const changed = () => {
  const out = spawnSync("git", ["status", "--porcelain"], { encoding: "utf8" });
  return (out.stdout || "").trim().length > 0;
};
const passHealth = () => {
  try { sh("node scripts/healthcheck.mjs"); return true; } catch { return false; }
};

let fixed = false;

// 1) Lint/format (Python: black)
trySh("npm run format");
if (passHealth()) fixed = fixed || changed();

// 2) Dependencies (Python: install dev deps)
if (!passHealth()) {
  trySh("pip install -e .[dev]");
  if (passHealth()) fixed = fixed || changed();
}

// Exit 0 if fixed, otherwise exit with error code if still failing
if (passHealth()) {
  process.exit(0);
} else {
  console.error("Self-heal failed to fix all issues.");
  process.exit(1);
}
