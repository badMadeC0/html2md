# tests/test_ps_sanitization.ps1

# This script verifies the sanitization logic to be used in gui-url-convert.ps1
# to prevent command injection.

$global:testFailed = $false

function Verify-Sanitization {
    param(
        [string]$InputString,
        [string]$Expected,
        [string]$Context
    )

    $sanitized = $InputString

    if ($Context -eq "SingleQuoteContext") {
        # Logic for embedding inside '...' in a -Command string
        # Replace ' with ''
        $sanitized = $sanitized -replace "'", "''"
    }
    elseif ($Context -eq "DoubleQuoteContext") {
        # Logic for embedding inside "..." in a -File argument
        # We escape " with `" (backtick-quote) so it passes through to the script argument
        $sanitized = $sanitized -replace '"', '`"'
    }

    if ($sanitized -eq $Expected) {
        Write-Host "[PASS] [$Context] Input: '$InputString' -> Output: '$sanitized'" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] [$Context] Input: '$InputString'" -ForegroundColor Red
        Write-Host "       Expected: '$Expected'" -ForegroundColor Yellow
        Write-Host "       Actual:   '$sanitized'" -ForegroundColor Yellow
        $global:testFailed = $true
    }
}

Write-Host "--- Starting Sanitization Tests ---"

# 1. Test Single-Quote Context (Critical for Command Injection)
# Code to be fixed: $psi.Arguments = "... --url '$url' ..."
# Injection: $url = "'; calc; '"
# Fix: Escape ' as ''

Verify-Sanitization "http://example.com" "http://example.com" "SingleQuoteContext"
Verify-Sanitization "http://example.com'; calc; '" "http://example.com''; calc; ''" "SingleQuoteContext"
Verify-Sanitization "'test'" "''test''" "SingleQuoteContext"
Verify-Sanitization "O'Reilly" "O''Reilly" "SingleQuoteContext"

# 2. Test Double-Quote Context (Argument Injection/Parsing)
# Code to be fixed: $psi.Arguments = "... -BatchOutDir \"$outdir\""
# Injection: $outdir = 'foo" -BatchFile "malicious'
# Fix: Escape " as `"

Verify-Sanitization "C:\Normal\Path" "C:\Normal\Path" "DoubleQuoteContext"
Verify-Sanitization 'C:\Path "With" Quotes' 'C:\Path `"With`" Quotes' "DoubleQuoteContext"
Verify-Sanitization '"injection"' '`"injection`"' "DoubleQuoteContext"

if (-not $global:testFailed) {
    Write-Host "--- All Tests Passed ---" -ForegroundColor Green
    [Environment]::Exit(0)
} else {
    Write-Host "--- Some Tests Failed ---" -ForegroundColor Red
    [Environment]::Exit(1)
}
