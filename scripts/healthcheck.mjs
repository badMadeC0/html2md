/* Repository healthcheck aligned with the actual Python CI.
   This repository is not a pnpm workspace, so keep these checks on
   Python commands instead of workspace-only pnpm invocations.
   - install the package in editable mode
   - run the pytest suite
*/
import { execSync } from "node:child_process";
import { existsSync } from "node:fs";

const run = (cmd) => execSync(cmd, { stdio: "inherit" });

const tryExec = (cmd) => {
  try {
    execSync(cmd, { stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
};

const getPythonCommand = () => {
  const candidates = [
    'python -c "import sys; print(sys.version)"',
    'py -3 -c "import sys; print(sys.version)"',
    'py -c "import sys; print(sys.version)"',
  ];

  for (const probe of candidates) {
    if (tryExec(probe)) {
      return probe.slice(0, probe.indexOf(" -c "));
    }
  }

  throw new Error("No supported Python interpreter was found in PATH.");
};

const tryRun = (name, cmd) => {
  console.log(`\n==> ${name}`);
  run(cmd);
};

try {
  if (!existsSync("pyproject.toml")) {
    throw new Error("pyproject.toml was not found at the repository root.");
  }

  const python = getPythonCommand();

  tryRun("Install package", `${python} -m pip install -e .`);
  tryRun("Unit tests", `${python} -m pytest -q`);

  process.exit(0);
} catch (e) {
  console.error(e);
  process.exit(1);
}