#!/usr/bin/env node
/* Minimal, opinionated healthcheck for this Python project:
   - install Python test dependencies before running the same pytest suite as CI
   - optionally run root package scripts, without pnpm workspace flags
   - in real pnpm workspaces only, smoke build packages that declare build
*/
import { execFileSync, execSync, spawnSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const run = (cmd, opts = {}) => execSync(cmd, { stdio: "inherit", ...opts });
const runFile = (file, args, opts = {}) =>
  execFileSync(file, args, { stdio: "inherit", ...opts });
const readJson = (path) => JSON.parse(readFileSync(path, "utf8"));
const rootPkgPath = join(process.cwd(), "package.json");
const rootPkg = existsSync(rootPkgPath) ? readJson(rootPkgPath) : {};
const hasScript = (name) => !!rootPkg.scripts?.[name];
const hasPnpmWorkspace = existsSync("pnpm-workspace.yaml");
const requestedPython = existsSync(".python-version")
  ? readFileSync(".python-version", "utf8").trim()
  : null;
const minPython = [3, 8];
const versionProbe =
  "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')";

const tryRun = (name, cmd) => {
  if (!cmd) return;
  console.log(`\n==> ${name}`);
  run(cmd);
};

const parseVersion = (version) => version.trim().split(".").map(Number);
const compareVersions = (left, right) => {
  const leftParts = parseVersion(left);
  const rightParts = parseVersion(right);
  for (let i = 0; i < Math.max(leftParts.length, rightParts.length); i += 1) {
    const diff = (leftParts[i] ?? 0) - (rightParts[i] ?? 0);
    if (diff !== 0) return diff;
  }
  return 0;
};
const sameMajorMinor = (left, right) => {
  if (!left || !right) return false;
  const [leftMajor, leftMinor] = parseVersion(left);
  const [rightMajor, rightMinor] = parseVersion(right);
  return leftMajor === rightMajor && leftMinor === rightMinor;
};
const isSupportedPython = (version) => {
  const [major = 0, minor = 0] = parseVersion(version);
  return major > minPython[0] || (major === minPython[0] && minor >= minPython[1]);
};

const probePython = ({ file, args = [], env = process.env, label = file }) => {
  const result = spawnSync(file, [...args, "-c", versionProbe], {
    encoding: "utf8",
    env,
  });
  if (result.status !== 0) return null;

  const version = result.stdout.trim();
  if (!isSupportedPython(version)) return null;

  const pip = spawnSync(file, [...args, "-m", "pip", "--version"], {
    encoding: "utf8",
    env,
  });
  if (pip.status !== 0) return null;

  return { file, args, env, label, version };
};

const pyenvPythonCandidates = () => {
  const result = spawnSync("pyenv", ["versions", "--bare", "--skip-aliases"], {
    encoding: "utf8",
  });
  if (result.status !== 0) return [];

  return result.stdout
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .sort((left, right) => {
      const leftMatches = sameMajorMinor(left, requestedPython);
      const rightMatches = sameMajorMinor(right, requestedPython);
      if (leftMatches !== rightMatches) return leftMatches ? -1 : 1;
      return compareVersions(right, left);
    })
    .map((version) => ({
      file: "python",
      env: { ...process.env, PYENV_VERSION: version },
      label: `pyenv ${version}`,
    }));
};

const findPython = () => {
  const candidates = [
    ...(process.env.PYTHON ? [{ file: process.env.PYTHON, label: "$PYTHON" }] : []),
    { file: "python" },
    { file: "python3" },
    ...pyenvPythonCandidates(),
  ];

  if (process.platform === "win32") {
    candidates.push({ file: "py", args: ["-3"] });
  }

  for (const candidate of candidates) {
    const python = probePython(candidate);
    if (python) return python;
  }

  throw new Error(
    `Unable to find a working Python >=${minPython.join(".")} interpreter. ` +
      "Install Python or set PYTHON to an interpreter path before running healthcheck.",
  );
};

const runPython = (name, python, args) => {
  console.log(`\n==> ${name} (${python.label}, Python ${python.version})`);
  runFile(python.file, [...python.args, ...args], { env: python.env });
};

const runPythonTests = () => {
  if (!existsSync("tests")) return;

  const python = findPython();

  // Match CI's Python setup before invoking pytest so clean self-heal runners
  // have pytest and the src-layout package installed.
  runPython("Python test dependencies", python, [
    "-m",
    "pip",
    "install",
    "-e",
    ".",
    "pytest",
  ]);
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
