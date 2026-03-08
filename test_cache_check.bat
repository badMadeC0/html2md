@echo off
setlocal enabledelayedexpansion

set "CACHE_DIR=C:\Users\runneradmin\Downloads\html2md-cache\wheels"
echo Checking cache dir: !CACHE_DIR!

if not exist "!CACHE_DIR!\*" (
    echo Cache is empty!
) else (
    echo Cache is populated!
)
