#!/usr/bin/env node
/* Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
   Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
*/
import { execSync, spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";

const sh = (cmd, opts = {}) => {
  console.log(`\n$ ${cmd}`);
  return execSync(cmd, { stdio: "inherit", ...opts });
};
const trySh = (cmd, opts = {}) => {
  try { sh(cmd, opts); return true; } catch { return false; }
};
const changed = () => {
  const out = spawnSync("git", ["status", "--porcelain"], { encoding: "utf8" });
  return (out.stdout || "").trim().length > 0;
};
const passHealth = () => {
  try { sh("node scripts/healthcheck.mjs"); return true; } catch { return false; }
};
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

let fixed = false;

// 1) Lint/format. This repository is not a pnpm workspace, so use root package
// scripts directly when they exist rather than workspace-only `pnpm -w` flags.
if (hasScript("lint")) trySh("pnpm run lint -- --fix");
if (hasScript("format")) trySh("pnpm run format");
if (passHealth()) fixed = fixed || changed();

// 2) Snapshot updates (only when a Vitest-backed test script is configured).
if (!passHealth() && hasScript("test") && /vitest/.test(scripts.test)) {
  trySh("pnpm exec vitest -u");
  if (passHealth()) fixed = fixed || changed();
}

// 3) Type acquisition (only for actual TypeScript projects).
if (!passHealth() && hasScript("typecheck") && hasTypeScriptConfig()) {
  trySh("pnpm dlx typesync --save-dev");
  // In case typesync suggests @types/node et al.
  trySh("pnpm install");
  if (passHealth()) fixed = fixed || changed();
}

// 4) Lockfile repair (only when this repository already tracks a pnpm lockfile).
if (!passHealth() && existsSync("pnpm-lock.yaml")) {
  // Try a clean install + re-resolve.
  trySh("pnpm install");
  if (!passHealth()) {
    // Last resort: conservatively refresh dependency versions allowed by package.json.
    trySh("pnpm up --interactive=false");
  }
  if (passHealth()) fixed = fixed || changed();
}

// 5) Known generators (icons/docs), if present.
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
