#!/usr/bin/env node
/* Python CI-oriented self-heal entrypoint.
   This repo's automatic trigger follows .github/workflows/ci.yml, so repairs must
   be validated by scripts/healthcheck.mjs instead of pnpm workspace checks.
*/
import { execFileSync, spawnSync } from "node:child_process";

const run = (cmd, args) => {
  console.log(`\n$ ${[cmd, ...args].join(" ")}`);
  execFileSync(cmd, args, { stdio: "inherit" });
};

const changed = () => {
  const out = spawnSync(
    "git",
    ["status", "--porcelain", "--", ".", ":!selfheal-*.txt"],
    { encoding: "utf8" },
  );
  return (out.stdout || "").trim().length > 0;
};

const passHealth = () => {
  try {
    run("node", ["scripts/healthcheck.mjs"]);
    return true;
  } catch {
    return false;
  }
};

// Placeholder for future targeted Python repairs. For now, only report success
// when an earlier/manual repair changed files and the reproduced CI check passes.
if (changed() && passHealth()) {
  process.exit(0);
}

console.error("[self-heal] No automatic Python repair was produced.");
process.exit(1);
