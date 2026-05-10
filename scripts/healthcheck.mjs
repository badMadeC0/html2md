#!/usr/bin/env node
/* Minimal, opinionated healthcheck for this Python project:
   - install Python test dependencies before running the same pytest suite as CI
   - optionally run root package scripts, without pnpm workspace flags
   - in real pnpm workspaces only, smoke build packages that declare build
*/
import { execFileSync, execSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const run = (cmd, opts = {}) => execSync(cmd, { stdio: "inherit", ...opts });
const runFile = (cmd, args, opts = {}) => execFileSync(cmd, args, { stdio: "inherit", ...opts });
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

const pyenvPythonCandidates = () => {
  const pyenvRoot = process.env.PYENV_ROOT ?? join(homedir(), ".pyenv");
  const versionsDir = join(pyenvRoot, "versions");
  if (!existsSync(versionsDir)) return [];

  return readdirSync(versionsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => ({
      command: join(versionsDir, entry.name, "bin", "python"),
      args: [],
    }))
    .filter((candidate) => existsSync(candidate.command));
};

const canUsePython = (candidate) => {
  execFileSync(
    candidate.command,
    [
      ...candidate.args,
      "-c",
      "import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)",
    ],
    { stdio: "ignore" },
  );
  execFileSync(candidate.command, [...candidate.args, "-m", "pip", "--version"], {
    stdio: "ignore",
  });
};

const resolvePython = () => {
  const candidates = [];
  if (process.env.PYTHON) candidates.push({ command: process.env.PYTHON, args: [] });
  candidates.push(
    ...pyenvPythonCandidates(),
    { command: "python3", args: [] },
    { command: "python", args: [] },
    { command: "py", args: ["-3"] },
  );

  for (const candidate of candidates) {
    try {
      canUsePython(candidate);
      return candidate;
    } catch {
      // Try the next interpreter. This avoids pyenv's bare `python` shim when
      // .python-version names a patch release that is not installed locally.
    }
  }

  throw new Error("No Python >=3.8 interpreter with pip found; set PYTHON to a usable interpreter.");
};

const runPython = (name, python, args) => {
  console.log(`\n==> ${name}`);
  runFile(python.command, [...python.args, ...args]);
};

const runPythonTests = () => {
  if (!existsSync("tests")) return;

  const python = resolvePython();

  // Match CI's Python setup before invoking pytest so clean self-heal runners
  // have pytest and the src-layout package installed.
  runPython("Python packaging tools", python, [
    "-m",
    "pip",
    "install",
    "--upgrade",
    "pip",
    "wheel",
    "setuptools",
  ]);
  runPython("Python test dependencies", python, ["-m", "pip", "install", "-e", ".", "pytest"]);
  runPython("Python tests", python, ["-m", "pytest", "-q"]);
};

try {
  // Run the repository's Python CI gate first; this repo is not a pnpm workspace.
  runPythonTests();

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
        try {
          const pkg = readJson(pkgPath);
          if (!pkg.scripts?.build) continue;
          run("pnpm run build", { cwd: dir });
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
