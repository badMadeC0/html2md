#!/usr/bin/env node
/* Minimal, opinionated healthcheck for a pnpm monorepo:
   - root: typecheck? test? lint? build?
   - workspaces: smoke build where available
*/
import { execSync } from "node:child_process";
import { existsSync } from "node:fs";
import { readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const rootPackage = JSON.parse(readFileSync("./package.json", "utf-8"));
const run = (cmd) => execSync(cmd, { stdio: "inherit" });
const hasScript = (name) => name in (rootPackage.scripts ?? {});

const tryRun = (name, cmd) => {
  if (!cmd) return;
  console.log(`\n==> ${name}`);
  run(cmd);
};

try {
  // Root-level checks (best-effort if scripts exist)
  tryRun("Typecheck", hasScript("typecheck") ? "pnpm -w run typecheck" : null);
  tryRun("Lint", hasScript("lint") ? "pnpm -w run lint" : null);
  tryRun("Unit tests", hasScript("test") ? "pnpm -w run test -- --run" : null);

  // Workspace smoke builds (apps/* and packages/* if build exists)
  const roots = ["apps", "packages"];
  for (const base of roots) {
    if (!existsSync(base)) continue;
    for (const name of readdirSync(base)) {
      const dir = join(base, name);
      if (!statSync(dir).isDirectory()) continue;
      const pkgJsonPath = join(dir, 'package.json');
      if (existsSync(pkgJsonPath)) {
        const pkg = JSON.parse(readFileSync(pkgJsonPath, 'utf-8'));
        if (pkg.scripts?.build) {
          try {
            execSync("pnpm run -s build", { cwd: dir, stdio: "inherit" });
          } catch (e) {
            console.error(`[healthcheck] build failed in ${dir}`);
            process.exitCode = 1;
          }
        }
      }
    }
  }
  process.exit(process.exitCode ?? 0);
} catch (e) {
  console.error(e);
  process.exit(1);
}
