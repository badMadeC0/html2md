#!/usr/bin/env node
/* Minimal, opinionated healthcheck for a pnpm project:
   - root: typecheck? test? lint?
   - workspaces: smoke build where available
*/
import { execSync } from "node:child_process";
import { existsSync, readdirSync, statSync, readFileSync } from "node:fs";
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
  // Root-level checks (best-effort if scripts exist)
  if (hasScript("typecheck")) tryRun("Typecheck", "pnpm run typecheck");
  if (hasScript("lint")) tryRun("Lint", "pnpm run lint");
  if (hasScript("test")) tryRun("Unit tests", "pnpm run test");

  // Workspace smoke builds (apps/* and packages/* if build exists)
  const roots = ["apps", "packages"];
  for (const base of roots) {
    if (!existsSync(base)) continue;
    for (const name of readdirSync(base)) {
      const dir = join(base, name);
      if (!statSync(dir).isDirectory()) continue;
      try {
        // Only try build if package.json exists in subdir
        if (existsSync(join(dir, "package.json"))) {
             execSync("pnpm run -s build", { cwd: dir, stdio: "inherit" });
        }
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
