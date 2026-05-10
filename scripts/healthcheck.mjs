#!/usr/bin/env node
/* Reproduce this repository's Python CI locally:
   - install package/test dependencies the same way .github/workflows/ci.yml does
   - run pytest -q so self-heal gates PR creation on the same check that failed
*/
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";

const run = (cmd, args) => {
  console.log(`\n$ ${[cmd, ...args].join(" ")}`);
  execFileSync(cmd, args, { stdio: "inherit" });
};

const python = process.platform === "win32" ? "python" : "python3";

if (!existsSync("pyproject.toml")) {
  console.error("[healthcheck] pyproject.toml not found; cannot reproduce Python CI");
  process.exit(1);
}

try {
  run(python, ["-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"]);
  run(python, ["-m", "pip", "install", "-e", "."]);
  run(python, ["-m", "pip", "install", "pytest"]);
  run(python, ["-m", "pytest", "-q"]);
} catch (error) {
  process.exit(error.status ?? 1);
}
