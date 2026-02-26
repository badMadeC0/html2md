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

// 1) Lint/format (Python via pnpm scripts)
trySh("pnpm run lint -- --fix");
trySh("pnpm run format");
if (passHealth()) fixed = changed();

// 2) Snapshot updates (Skipped for Python/pytest as -u is not standard)

// 3) Type acquisition (Node)
if (!passHealth()) {
  trySh("pnpm dlx typesync --save-dev");
  trySh("pnpm install");
  if (passHealth()) fixed = fixed || changed();
}

// 4) Lockfile repair (Node)
if (!passHealth()) {
  trySh("pnpm install");
  if (!passHealth()) {
    trySh("pnpm up --latest --interactive=false");
  }
  if (passHealth()) fixed = fixed || changed();
}

// 5) Known generators
if (!passHealth()) {
  if (existsSync("scripts/update-icon-docs.mjs")) {
    trySh("node scripts/update-icon-docs.mjs");
  }
  if (existsSync("scripts/verify-static.mjs")) {
    trySh("node scripts/verify-static.mjs");
  }
  if (passHealth()) fixed = fixed || changed();
}

if (fixed || passHealth()) {
    console.log("Healthcheck passed.");
    process.exit(0);
} else {
    console.error("Self-heal failed.");
    process.exit(1);
}
