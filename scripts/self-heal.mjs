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

// Only attempt repairs if healthcheck fails
if (!passHealth()) {
  // 1) Lint/format (Python specific: black)
  trySh("python -m black .");
  if (changed() && passHealth()) {
    fixed = true;
  }

  // 2) Update test snapshots or similar test generation (if any Python script handles it)
  // For this repo, tests just use standard asserts. We can skip a dedicated snapshot updater
  // or implement one if the repo gets python-snapshottest.

  // 3) Lockfile/Dependency repair (Python specific: pip requirements)
  if (!fixed && !passHealth()) {
    // If there are pip lockfiles or similar, we might refresh them.
    // In this repo, tests are run with plain pip installs or `pip install -e .`
    trySh("pip install -e .");
    if (changed() && passHealth()) fixed = true;
  }

  // 5) Known generators (icons/docs), if present
  if (!fixed && !passHealth()) {
    if (existsSync("scripts/update-icon-docs.mjs")) {
      trySh("node scripts/update-icon-docs.mjs");
    }
    if (existsSync("scripts/verify-static.mjs")) {
      trySh("node scripts/verify-static.mjs");
    }
    if (changed() && passHealth()) fixed = true;
  }
}

if (fixed) {
  console.log("Self-heal successful and produced a diff.");
  process.exit(0);
} else {
  console.log("Self-heal failed or no changes were needed.");
  process.exit(1);
}
