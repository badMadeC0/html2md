## 2024-03-10 - Uninitialized variable leading to command execution errors
**Vulnerability:** In `gui-url-convert.ps1`, the PowerShell `$bat` variable was used in an executed `cmd.exe` command line string (`$psi.Arguments = "/c ""$bat" ..."`) but `$bat` was never initialized.
**Learning:** Shell-wrapping with uninitialized variables can result in unexpected and potentially dangerous command interpretation (though here it likely resulted in command failure). PowerShell's default behavior allows referencing undefined variables.
**Prevention:** Strictly run PowerShell with strict mode (`Set-StrictMode`) or thoroughly verify variable definitions via linters before using them in execution contexts.

## 2024-03-10 - Pre-emptive SSRF Protection in URL parsing tools
**Vulnerability:** The CLI `process_url` accepted URLs pointing to localhost and internal loopbacks.
**Learning:** CLI tools handling user URLs are often deployed in server environments where internal network access via SSRF is a critical risk. Validating scheme (`http/https`) alone is not sufficient; checking the resolved IP address using `socket` and `ipaddress` against private IP ranges provides stronger defense.
**Prevention:** Always implement IP-level restrictions alongside scheme and input validation when performing automated outbound requests.
