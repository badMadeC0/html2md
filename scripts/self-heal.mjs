#!/usr/bin/env node
/*
 * Targeted, ordered repairs for this Python repository.
 * Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
 */
import { execSync, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";

const sh = (cmd, opts = {}) => {
  console.log(`\n$ ${cmd}`);
  return execSync(cmd, { stdio: "inherit", ...opts });
};

const trySh = (cmd, opts = {}) => {
  try {
    sh(cmd, opts);
    return true;
  } catch {
    return false;
  }
};

const getStatus = () => spawnSync("git", ["status", "--porcelain"], { encoding: "utf8" }).stdout || "";
const initialStatus = getStatus();
const changed = () => getStatus() !== initialStatus;

const passHealth = () => {
  try {
    sh("node scripts/healthcheck.mjs");
    return true;
  } catch {
    return false;
  }
};

let fixed = false;

// 1) If optional Python formatters are available, let them normalize the tree.
for (const cmd of ["python -m ruff check --fix .", "python -m ruff format .", "python -m black ."]) {
  trySh(cmd);
  if (passHealth()) fixed = fixed || changed();
}

// 2) Known generators, if present.
for (const script of ["scripts/update-icon-docs.mjs", "scripts/verify-static.mjs"]) {
  if (!passHealth() && existsSync(script)) {
    trySh(`node ${script}`);
    if (passHealth()) fixed = fixed || changed();
  }
}

if (fixed) {
  console.log("Self-heal successful and produced a diff.");
  process.exit(0);
}

console.log("Self-heal failed or no changes were needed.");
process.exit(1);
