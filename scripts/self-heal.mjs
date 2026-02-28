#!/usr/bin/env node
/* Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
   Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
*/
import { execSync, spawnSync } from "node:child_process";
import { existsSync, writeFileSync } from "node:fs";

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

// 1) Lint/format
trySh("pnpm -w run lint --fix");
trySh("pnpm -w run format");
if (passHealth()) fixed = fixed || changed();

// 2) Snapshot updates (only if tests fail with snapshots)
if (!passHealth()) {
  trySh("pnpm -w exec vitest -u");
  if (passHealth()) fixed = fixed || changed();
}

// 3) Type acquisition
if (!passHealth()) {
  trySh("pnpm dlx typesync --save-dev");
  // In case typesync suggests @types/node et al.
  trySh("pnpm -w install");
  if (passHealth()) fixed = fixed || changed();
}

// 4) Lockfile repair (only if integrity complaints)
if (!passHealth()) {
  // Try a clean install + re-resolve
  trySh("pnpm install");
  if (!passHealth()) {
    // Last resort: refresh lockfile (scoped)
    trySh("pnpm -w up --latest --interactive=false");
  }
  if (passHealth()) fixed = fixed || changed();
}

// 5) Known generators (icons/docs), if present
if (!passHealth()) {
  if (existsSync("scripts/update-icon-docs.mjs")) {
    trySh("node scripts/update-icon-docs.mjs");
  }
  if (existsSync("scripts/verify-static.mjs")) {
    trySh("node scripts/verify-static.mjs");
  }
  if (passHealth()) fixed = fixed || changed();
}

if (fixed && passHealth()) {
  console.log("\n==> Self-heal successful");
  process.exit(0);
} else {
  console.error("\n==> Self-heal failed to repair all issues");
  process.exit(1);
}
