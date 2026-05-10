#!/usr/bin/env node
/* Minimal, opinionated healthcheck for this Python project:
   - run the same pytest suite as CI when tests are present
   - optionally run root package scripts, without pnpm workspace flags
   - in real pnpm workspaces only, smoke build packages that declare build
*/
import { execSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const run = (cmd, opts = {}) => execSync(cmd, { stdio: "inherit", ...opts });
const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));
const rootPkgPath = join(process.cwd(), "package.json");
const rootPkg = existsSync(rootPkgPath) ? readJson(rootPkgPath) : {};
const hasScript = (name) => !!rootPkg.scripts?.[name];
const hasPnpmWorkspace = existsSync("pnpm-workspace.yaml");

const tryRun = (name, cmd) => {
  if (!cmd) return;
  console.log(`\n==> ${name}`);
  run(cmd);
};

try {
  // Match the repository's Python CI gate first; this repo is not a pnpm workspace.
  tryRun("Python tests", existsSync("tests") ? "python -m pytest -q" : null);

  // Optional root-level package checks. Use plain pnpm commands, never `pnpm -w`,
  // because this repository has no pnpm-workspace.yaml.
  tryRun("Typecheck", hasScript("typecheck") ? "pnpm run typecheck" : null);
  tryRun("Lint", hasScript("lint") ? "pnpm run lint" : null);
  tryRun("Unit tests", hasScript("test") ? "pnpm run test" : null);
  tryRun("Build", hasScript("build") ? "pnpm run build" : null);

  // Workspace smoke builds only apply to actual pnpm workspaces.
  if (hasPnpmWorkspace) {
    const roots = ["apps", "packages"];
    for (const base of roots) {
      if (!existsSync(base)) continue;
      for (const name of readdirSync(base)) {
        const dir = join(base, name);
        const pkgPath = join(dir, "package.json");
        if (!statSync(dir).isDirectory() || !existsSync(pkgPath)) continue;
        const pkg = readJson(pkgPath);
        if (!pkg.scripts?.build) continue;
        try {
          execSync("pnpm run --if-present build", { cwd: dir, stdio: "inherit" });
        } catch (e) {
          console.error(`[healthcheck] build failed in ${dir}`);
          process.exitCode = 1;
        }
      }
    }
  }

  process.exit(process.exitCode ?? 0);
} catch (e) {
  console.error(e);
  process.exit(1);
}
