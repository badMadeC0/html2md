# Sentinel Security Journal

## Security Vulnerability Fixes

### [HIGH] Uninitialized variable bypasses security check in PowerShell GUI
**File:** `gui-url-convert.ps1`
**Issue:** `[System.Uri]$url` was used inside a `foreach ($u in $urlList)` loop, causing the URL validation to always act on the uninitialized `$url` variable (or a previously set variable outside the loop context) rather than the current `$u` string.
**Fix:** Updated the cast to correctly use the iterator variable: `[System.Uri]$u`.
**Impact:** A maliciously crafted URL (e.g., without `http` schema) could bypass validation if `$url` was uninitialized (evaluating to `$null` or empty string in some contexts, or carrying over from a previous operation). This led to missing scheme checking and could result in arbitrary input passing the validation block.
**Prevention:** Ensured loop iterators match the referenced variable. Added `test_ps_url_validation.py` static analysis test to prevent regressions.
