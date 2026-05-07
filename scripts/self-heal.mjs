#!/usr/bin/env node
/* Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
   Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
*/
import { execSync, spawnSync } from "node:child_process";

const sh = (cmd, opts={}) => {
  console.log(`\n$ ${cmd}`);
  return execSync(cmd, { stdio: "inherit", ...opts });
};
const trySh = (cmd, opts={}) => {
  try { sh(cmd, opts); return true; } catch { return false; }
};
const workflowArtifactPaths = new Set([
  "selfheal-pre.txt",
  "selfheal-repair.txt",
  "selfheal-post.txt",
]);

const statusPath = (line) => line.slice(3).replace(/^\"|\"$/g, "");
const isWorkflowArtifact = (line) => {
  const path = statusPath(line);
  if (path.includes(" -> ")) {
    return path.split(" -> ").every((part) => workflowArtifactPaths.has(part));
  }

  return workflowArtifactPaths.has(path);
};
const changed = () => {
  const out = spawnSync("git", ["status", "--porcelain"], { encoding: "utf8" });
  return (out.stdout || "")
    .split("\n")
    .filter(Boolean)
    .some((line) => !isWorkflowArtifact(line));
};
let lastHealth = null;
const passHealth = () => {
  if (lastHealth !== null) return lastHealth;
  try { sh("node scripts/healthcheck.mjs"); lastHealth = true; return true; } catch { lastHealth = false; return false; }
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
