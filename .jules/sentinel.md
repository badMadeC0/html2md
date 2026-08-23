## 2024-05-18 - CLI Subprocess Injection Risk
**Vulnerability:** Smoke test uses `shell=True` with `subprocess.run` to execute command. Although current inputs are static, this is a dangerous pattern that can lead to command injection if test parameters change or if the pattern is copied to production code.
**Learning:** Python PR rules explicitly forbid `subprocess` calls with `shell=True` and unsanitized user input. Tests should be held to the same standard to prevent bad copy-pasting.
**Prevention:** Avoid `shell=True` when running commands via `subprocess`, even in tests.
