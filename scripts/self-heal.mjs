#!/usr/bin/env node
/* Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
   Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
*/
import { execFileSync, execSync, spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const trustedHealthcheck = join(dirname(fileURLToPath(import.meta.url)), "healthcheck.mjs");

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
let lastHealth = null;
const passHealth = () => {
  if (lastHealth !== null) return lastHealth;
  try {
    console.log(`\n$ node ${trustedHealthcheck}`);
    execFileSync(process.execPath, [trustedHealthcheck], { stdio: "inherit" });
    lastHealth = true;
    return true;
  } catch { lastHealth = false; return false; }
};
const clearHealthCache = () => { lastHealth = null; };

let fixed = false;

// 1) Lint/format using black
trySh("python -m black src tests");
clearHealthCache();
if (passHealth()) fixed = fixed || changed();

if (fixed) {
  process.exit(0);
} else {
  process.exit(1);
}
