## 2026-03-11 - [CRITICAL] Uninitialized Command Execution Variable
**Vulnerability:** The `$bat` variable in `gui-url-convert.ps1` used for executing command strings was not properly initialized before being passed into `ProcessStartInfo.Arguments`, leaving it empty.
**Learning:** This exposes a command-line injection and arbitrary execution risk since `cmd.exe /c "" ""` does unexpected things depending on arguments that follow, such as executing things that come from `--url "$url"`.
**Prevention:** Always verify that shell script commands and arguments variables are initialized properly before constructing the final execution command, and use safer parameter-passing like `-File` instead of `-Command` when feasible.
