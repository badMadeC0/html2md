#!/usr/bin/env node
/* Minimal, opinionated healthcheck for this Python project:
   - install Python test dependencies before running the same pytest suite as CI
   - optionally run root package scripts, without pnpm workspace flags
   - in real pnpm workspaces only, smoke build packages that declare build
*/
import { execFileSync, execSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const run = (cmd, opts = {}) => execSync(cmd, { stdio: "inherit", ...opts });
const runFile = (cmd, args, opts = {}) =>
  execFileSync(cmd, args, { stdio: "inherit", ...opts });
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

const pyenvVersionCandidates = () => {
  try {
    const output = execFileSync("pyenv", ["versions", "--bare"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    });
    const versions = output
      .split("\n")
      .map((version) => version.trim())
      .filter(Boolean);
    if (!versions.length) return [];

    const pinned = existsSync(".python-version")
      ? readFileSync(".python-version", "utf8").trim()
      : null;
    const pinnedSeries = pinned?.split(".").slice(0, 2).join(".");
    const sorted = pinnedSeries
      ? [
          ...versions.filter((version) => version.startsWith(`${pinnedSeries}.`)),
          ...versions.filter((version) => !version.startsWith(`${pinnedSeries}.`)),
        ]
      : versions;

    return sorted.map((version) => ({
      command: "pyenv",
      args: ["exec", "python"],
      env: { ...process.env, PYENV_VERSION: version },
    }));
  } catch {
    return [];
  }
};

const pythonCandidates = () => {
  const candidates = [];
  if (process.env.PYTHON) {
    candidates.push({ command: process.env.PYTHON, args: [], env: process.env });
  }
  candidates.push(
    { command: "python3", args: [], env: process.env },
    ...pyenvVersionCandidates(),
    { command: "python", args: [], env: process.env },
    { command: "py", args: ["-3"], env: process.env },
  );
  return candidates;
};

const isSupportedPython = ({ command, args, env }) => {
  const check =
    "import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)";
  try {
    execFileSync(command, [...args, "-c", check], { env, stdio: "ignore" });
    execFileSync(command, [...args, "-m", "pip", "--version"], {
      env,
      stdio: "ignore",
    });
    return true;
  } catch {
    return false;
  }
};

const resolvePython = () => {
  const seen = new Set();
  for (const candidate of pythonCandidates()) {
    const key = [candidate.env?.PYENV_VERSION, candidate.command, ...candidate.args].join(
      " ",
    );
    if (seen.has(key)) continue;
    seen.add(key);
    if (isSupportedPython(candidate)) return candidate;
  }

  throw new Error(
    "No supported Python interpreter found. Install Python >=3.8 or set PYTHON " +
      "to a working interpreter before running the healthcheck.",
  );
};

const tryRunPython = (name, python, args) => {
  console.log(`\n==> ${name}`);
  runFile(python.command, [...python.args, ...args], { env: python.env });
};

const runPythonTests = () => {
  if (!existsSync("tests")) return;

  const python = resolvePython();

  // Match CI's Python setup before invoking pytest so clean self-heal runners
  // have pytest and the src-layout package installed. Resolve an available
  // interpreter first instead of relying on pyenv's bare `python` shim matching
  // the exact version pinned in .python-version.
  tryRunPython("Python test dependencies", python, [
    "-m",
    "pip",
    "install",
    "-e",
    ".",
    "pytest",
  ]);
  tryRunPython("Python tests", python, ["-m", "pytest", "-q"]);
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
