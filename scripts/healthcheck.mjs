#!/usr/bin/env node
/* Minimal healthcheck aligned with this Python package CI.
   Runs the root test script when present, otherwise falls back to pytest.
*/
import { execSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const run = (cmd) => execSync(cmd, { stdio: "inherit" });
const hasScript = (name) => {
  try {
    const pkg = JSON.parse(readFileSync("package.json", "utf8"));
    return !!pkg.scripts?.[name];
  } catch { return false; }
};

const tryRun = (name, cmd) => {
  if (!cmd) return;
  console.log(`\n==> ${name}`);
  run(cmd);
};

try {
  // Match the repository CI by validating the Python test suite, not Vitest.
  tryRun("Python tests", hasScript("test") ? "pnpm run test" : "pytest -q");

  // Optional workspace smoke builds (apps/* and packages/* if build exists)
  const roots = ["apps", "packages"];
  for (const base of roots) {
    if (!existsSync(base)) continue;
    for (const name of readdirSync(base)) {
      const dir = join(base, name);
      if (!statSync(dir).isDirectory()) continue;
      try {
        execSync("pnpm run -s build", { cwd: dir, stdio: "inherit" });
      } catch (e) {
        console.error(`[healthcheck] build failed in ${dir}`);
        process.exitCode = 1;
      }
    }
  }
  process.exit(process.exitCode ?? 0);
} catch (e) {
  console.error(e);
  process.exit(1);
}
