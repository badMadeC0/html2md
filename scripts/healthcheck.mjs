#!/usr/bin/env node
/* Healthcheck aligned with .github/workflows/ci.yml:
   - create an isolated Python virtual environment
   - install the Python package in editable mode
   - install pytest
   - run the same pytest suite used by CI
*/
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const MIN_PYTHON_VERSION = [3, 8];

const pythonCandidates = [
  process.env.PYTHON,
  process.platform === "win32" ? "python" : "python3",
  "python",
].filter(Boolean);

const isSupportedPython = (candidate) => {
  const result = spawnSync(
    candidate,
    [
      "-c",
      `import sys; sys.exit(0 if sys.version_info >= ` +
        `(${MIN_PYTHON_VERSION[0]}, ${MIN_PYTHON_VERSION[1]}) else 1)`,
    ],
    { stdio: "pipe" },
  );
  return result.status === 0;
};

const hasVenvModule = (candidate) => {
  const result = spawnSync(candidate, ["-m", "venv", "--help"], { stdio: "pipe" });
  return result.status === 0;
};
const python = pythonCandidates.find((candidate, index, candidates) => {
  if (candidates.indexOf(candidate) !== index) return false;
  const result = spawnSync(candidate, ["-c", "import sys; print(sys.version_info >= (3, 8))"], { stdio: "pipe" });
  return result.status === 0 && result.stdout?.toString().trim() === "True";
});

if (!python) {
  console.error(
    `[healthcheck] Could not find a Python ${MIN_PYTHON_VERSION.join(".")}+ interpreter with the venv module.`,
  );
  process.exit(1);
}

const venvDir = mkdtempSync(join(tmpdir(), "html2md-healthcheck-"));
const venvPython = join(
  venvDir,
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
);

const runCommand = (command, args) => {
  execFileSync(command, args, { stdio: "inherit" });
};

const runCheck = (name, command, args) => {
  console.log(`\n==> ${name}`);
  try {
    runCommand(command, args);
  } catch (error) {
    const status =
      typeof error.status === "number" ? ` (exit ${error.status})` : "";
    console.error(`[healthcheck] ${name} failed${status}: ${error.message}`);
    process.exitCode = 1;
  }
};

try {
  runCheck("Create isolated Python virtual environment", python, ["-m", "venv", venvDir]);
  runCheck("Upgrade Python packaging tools", venvPython, [
    "-m",
    "pip",
    "install",
    "--upgrade",
    "pip",
    "wheel",
    "setuptools",
  ]);
  runCheck("Install package", venvPython, ["-m", "pip", "install", "-e", "."]);
  runCheck("Install pytest", venvPython, ["-m", "pip", "install", "pytest"]);
  runCheck("Python test suite", venvPython, ["-m", "pytest", "-q"]);
} finally {
  rmSync(venvDir, { force: true, recursive: true });
}

process.exit(process.exitCode ?? 0);
