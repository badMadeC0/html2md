#!/usr/bin/env node
/*
 * Launch the sensitive-file protection hook without relying on pyenv's
 * repository-local `python` shim. Unix-like systems normally provide `python3`,
 * while Windows commonly provides the `py -3` launcher. A bare `python` is kept
 * as a final fallback for environments that only expose that command.
 */

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const hookScript = path.join(__dirname, "protect_sensitive_files.py");
const stdin = fs.readFileSync(0);

const candidates = [
  { command: "python3", args: [hookScript] },
  { command: "py", args: ["-3", hookScript] },
  { command: "python", args: [hookScript] },
];

for (const candidate of candidates) {
  const result = spawnSync(candidate.command, candidate.args, {
    input: stdin,
    stdio: ["pipe", "inherit", "inherit"],
  });

  if (result.error && result.error.code === "ENOENT") {
    continue;
  }

  if (result.error) {
    console.error(
      `protect-sensitive-files: failed to launch ${candidate.command}: ${result.error.message}`,
    );
    continue;
  }

  if (result.signal) {
    console.error(
      `protect-sensitive-files: ${candidate.command} terminated by signal ${result.signal}`,
    );
    process.exit(1);
  }

  const status = result.status === null ? 1 : result.status;
  if (status === 0 || status === 2) {
    process.exit(status);
  }

  console.error(
    `protect-sensitive-files: ${candidate.command} exited with status ${status}; trying next Python launcher`,
  );
}

console.error(
  "protect-sensitive-files: no working Python 3 launcher found (tried python3, py -3, python)",
);
process.exit(2);
