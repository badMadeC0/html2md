# Sentinel Security Journal

## Security Regression Prevention

### [HIGH] Guard PowerShell GUI URL scheme validation against loop-variable regressions
**File:** `gui-url-convert.ps1`
**Issue:** URL validation in `gui-url-convert.ps1` depends on casting the current `foreach ($u in $urlList)` iterator value with `[System.Uri]$u`. Accidentally casting a different variable, such as `$url`, would validate stale or uninitialized data instead of the current URL.
**Action:** Added regression coverage in `test_ps_url_validation.py` to verify the loop continues to cast the iterator variable directly and to reject vulnerable `[System.Uri]$url` patterns.
**Impact:** A regression to a stale or uninitialized variable could allow a maliciously crafted URL (e.g., without an `http` or `https` scheme) to bypass validation and reach later processing unexpectedly.
**Prevention:** Keep the URL-validation loop tied to its iterator variable and rely on the static regression test to catch future mismatches.
