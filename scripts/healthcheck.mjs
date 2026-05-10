#!/usr/bin/env node
/* Minimal, opinionated healthcheck for a pnpm project:
   - root: typecheck? test? lint? build?
   - package directories: smoke build where available
*/
import { execSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const run = (cmd) => execSync(cmd, { stdio: "inherit" });
const readPackage = (dir = ".") => {
  try {
    return JSON.parse(readFileSync(join(dir, "package.json"), "utf8"));
  } catch {
    return null;
  }
};
const rootPackage = readPackage();
const hasRootScript = (name) => Boolean(rootPackage?.scripts?.[name]);
const hasPackageScript = (dir, name) => Boolean(readPackage(dir)?.scripts?.[name]);

const tryRun = (name, cmd) => {
  if (!cmd) return;
  console.log(`\n==> ${name}`);
  run(cmd);
};

try {
  // Root-level checks (best-effort if scripts exist)
  tryRun("Typecheck", hasRootScript("typecheck") ? "pnpm run typecheck" : null);
  tryRun("Lint", hasRootScript("lint") ? "pnpm run lint" : null);
  tryRun("Unit tests", hasRootScript("test") ? "pnpm run test -- --run" : null);

  // Package smoke builds (apps/* and packages/* if build exists)
  const roots = ["apps", "packages"];
  for (const base of roots) {
    if (!existsSync(base)) continue;
    for (const name of readdirSync(base)) {
      const dir = join(base, name);
      if (!statSync(dir).isDirectory()) continue;
      if (!hasPackageScript(dir, "build")) continue;
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
