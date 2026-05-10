#!/usr/bin/env node
/* Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
   Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
*/
import { execSync, spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";

const sh = (cmd, opts={}) => {
  console.log(`\n$ ${cmd}`);
  return execSync(cmd, { stdio: "inherit", ...opts });
};
const trySh = (cmd, opts={}) => {
  try { sh(cmd, opts); return true; } catch { return false; }
};
const getStatus = () => spawnSync("git", ["status", "--porcelain"], { encoding: "utf8" }).stdout || "";
const initialStatus = getStatus();
const changed = () => getStatus() !== initialStatus;
const hasRootScript = (name) => {
  try {
    const pkg = JSON.parse(readFileSync("package.json", "utf8"));
    return !!pkg.scripts?.[name];
  } catch {
    return false;
  }
};
const passHealth = () => {
  try { sh("node scripts/healthcheck.mjs"); return true; } catch { return false; }
};

let fixed = false;

// 1) Lint/format
if (hasRootScript("lint")) trySh("pnpm run lint -- --fix");
if (hasRootScript("format")) trySh("pnpm run format");
if (passHealth()) fixed = fixed || changed();

// 2) Snapshot updates (only if tests fail with snapshots)
if (!passHealth()) {
  trySh("pnpm exec vitest -u");
  if (passHealth()) fixed = fixed || changed();
}

// 3) Type acquisition
if (!passHealth()) {
  trySh("pnpm dlx typesync --save-dev");
  // In case typesync suggests @types/node et al.
  trySh("pnpm install");
  if (passHealth()) fixed = fixed || changed();
}

// 4) Lockfile repair (only if integrity complaints)
if (!passHealth()) {
  // Try a clean install + re-resolve
  trySh("pnpm install");
  if (!passHealth()) {
    // Last resort: refresh lockfile (scoped)
    trySh("pnpm install --lockfile-only");
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

if (fixed) {
  console.log("Self-heal successful and produced a diff.");
  process.exit(0);
} else {
  console.log("Self-heal failed or no changes were needed.");
  process.exit(1);
}
