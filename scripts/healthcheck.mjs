#!/usr/bin/env node
/* Repository healthcheck for self-heal automation.
   Mirrors the existing CI signal first (Python pytest), then runs any
   explicitly configured root/package Node checks without assuming a pnpm
   workspace or using workspace-only pnpm flags.
*/
import { execSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const run = (cmd, opts = {}) => execSync(cmd, { stdio: "inherit", ...opts });

const readPackage = (pkgPath) => {
  try {
    return JSON.parse(readFileSync(pkgPath, "utf8"));
  } catch {
    return null;
  }
};

const rootPackage = readPackage("package.json") ?? {};
const hasRootScript = (name) => !!rootPackage.scripts?.[name];
const hasPackageScript = (dir, name) => {
  const pkg = readPackage(join(dir, "package.json"));
  return !!pkg?.scripts?.[name];
};
const python = process.env.PYTHON ?? (process.platform === "win32" ? "python" : "python3");
const pythonEnv = {
  ...process.env,
  LANG: "C",
  LANGUAGE: "C",
  LC_ALL: "C",
  LC_MESSAGES: "C",
};

const tryRun = (name, cmd, opts = {}) => {
  if (!cmd) return;
  console.log(`\n==> ${name}`);
  try {
    run(cmd, opts);
  } catch {
    process.exitCode = 1;
  }
};

// Match the repository's existing CI workflow.
tryRun("Python tests", existsSync("tests") ? `${python} -m pytest -q` : null, { env: pythonEnv });

// Root-level JavaScript checks, if this repository later opts into them.
tryRun("Typecheck", hasRootScript("typecheck") ? "pnpm run typecheck" : null);
tryRun("Lint", hasRootScript("lint") ? "pnpm run lint" : null);
tryRun("Unit tests", hasRootScript("test") ? "pnpm run test" : null);
tryRun("Build", hasRootScript("build") ? "pnpm run build" : null);

// Workspace smoke builds are only meaningful in an actual pnpm workspace.
if (existsSync("pnpm-workspace.yaml")) {
  for (const base of ["apps", "packages"]) {
    if (!existsSync(base)) continue;
    for (const name of readdirSync(base)) {
      const dir = join(base, name);
      if (!statSync(dir).isDirectory() || !hasPackageScript(dir, "build")) continue;
      tryRun(`Build ${dir}`, "pnpm run -s build", { cwd: dir });
    }
  }
}

process.exit(process.exitCode ?? 0);
