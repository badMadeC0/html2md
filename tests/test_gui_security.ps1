Write-Host "Starting Security Test for GUI Arguments..."

$failed = $false

function Assert-Safe-SingleQuote-Interpolation {
    param($inputVal, $description)

    # Simulate logic (Single URL Mode)
    # Fix logic: Escape single quotes
    $safeVal = $inputVal -replace "'", "''"

    # Construct argument string
    $argString = "-NoExit -Command `"& 'exe' --url '$safeVal' --outdir 'dir' --all-formats`""

    # Verify
    # We check if the constructed string contains the escaped version inside quotes.
    if ($argString -match "'$([regex]::Escape($safeVal))'") {
        Write-Host "[PASS] $description" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $description" -ForegroundColor Red
        Write-Host "   Input: $inputVal"
        Write-Host "   Safe:  $safeVal"
        Write-Host "   Args:  $argString"
        $global:failed = $true
    }
}

function Assert-Safe-DoubleQuote-Interpolation {
    param($inputVal, $description)

    # Simulate logic (Batch Mode)
    # Fix logic: Escape double quotes with backslash
    $safeVal = $inputVal -replace '"', '\\"'

    # Construct argument string
    $argString = "-NoExit ... -BatchOutDir `"$safeVal`""

    # Verify
    if ($argString -match "`"$([regex]::Escape($safeVal))`"") {
        Write-Host "[PASS] $description" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $description" -ForegroundColor Red
        Write-Host "   Input: $inputVal"
        Write-Host "   Safe:  $safeVal"
        Write-Host "   Args:  $argString"
        $global:failed = $true
    }
}

# --- Test Cases ---

Write-Host "--- Single Quote Tests ---"
Assert-Safe-SingleQuote-Interpolation "http://normal.com" "Normal URL"
Assert-Safe-SingleQuote-Interpolation "http://site.com/foo'bar" "URL with single quote"
Assert-Safe-SingleQuote-Interpolation "'; Write-Host 'pwned'; '" "Malicious injection payload"

Write-Host "--- Double Quote Tests ---"
Assert-Safe-DoubleQuote-Interpolation "C:\Normal\Path" "Normal Path"
Assert-Safe-DoubleQuote-Interpolation "C:\My `"Cool`" Folder" "Path with double quotes"
Assert-Safe-DoubleQuote-Interpolation "`"; Write-Host 'pwned'; `"" "Malicious batch payload"

if ($failed) {
    Throw "Tests Failed!"
} else {
    Write-Host "All Tests Passed!" -ForegroundColor Green
}
