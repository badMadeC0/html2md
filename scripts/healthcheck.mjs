#!/usr/bin/env node
/* Healthcheck aligned with .github/workflows/ci.yml:
   - install the Python package in editable mode
   - install pytest
   - run the same pytest suite used by CI
*/
import { execFileSync, spawnSync } from "node:child_process";

const pythonCandidates = [
  process.env.PYTHON,
  process.platform === "win32" ? "python" : "python3",
  "python",
].filter(Boolean);

const python = pythonCandidates.find((candidate, index, candidates) => {
  if (candidates.indexOf(candidate) !== index) return false;
  const result = spawnSync(candidate, ["--version"], { stdio: "pipe" });
  return result.status === 0;
});

if (!python) {
  console.error("[healthcheck] Could not find a usable Python interpreter.");
  process.exit(1);
}

const runCheck = (name, args) => {
  console.log(`\n==> ${name}`);
  try {
    execFileSync(python, args, { stdio: "inherit" });
  } catch {
    process.exitCode = 1;
  }
};

runCheck("Upgrade Python packaging tools", [
  "-m",
  "pip",
  "install",
  "--upgrade",
  "pip",
  "wheel",
  "setuptools",
]);
runCheck("Install package", ["-m", "pip", "install", "-e", "."]);
runCheck("Install pytest", ["-m", "pip", "install", "pytest"]);
runCheck("Python test suite", ["-m", "pytest", "-q"]);

process.exit(process.exitCode ?? 0);
