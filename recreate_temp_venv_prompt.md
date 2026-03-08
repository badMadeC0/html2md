# How to Recreate the Temporary Virtual Environment Wrapper Scripts

This document serves as a prompt and logic guide to recreate the `run-*.bat` and `run-*.sh` scripts that manage a temporary Python virtual environment with offline caching.

## The Prompt

If you ever need to recreate this setup or apply it to another project, you can provide an AI assistant with the following prompt:

> "I need to modify my project's execution scripts (both `.bat` for Windows and `.sh` for macOS/Linux) so that the application runs entirely within a temporary Python virtual environment. It must not install dependencies persistently in my project folder or on my system.
>
> Please implement the following exact logic for the wrapper scripts:
>
> 1.  Locate the user's Downloads folder (e.g., `%USERPROFILE%\Downloads` on Windows or `~/Downloads` on Mac/Linux).
> 2.  Define a cache directory specifically for wheels (e.g., `Downloads/html2md-cache/wheels`).
> 3.  Define a temporary, unique virtual environment directory inside Downloads (e.g., `Downloads/html2md-venv-<random>`).
> 4.  Create the temporary virtual environment at that path and activate it.
> 5.  If the cache directory is empty, run `pip wheel . -w <cache-dir>` to download and build all dependencies from the internet into the cache folder.
> 6.  Run `pip install . --no-index --find-links <cache-dir>` to install the package and its dependencies purely offline from the local cache.
> 7.  Execute the application (e.g., the CLI tool or the GUI script).
> 8.  Delete the temporary virtual environment directory completely after the application exits, regardless of success or failure.
>
> Ensure all paths are safely quoted and platform-specific standard practices are used (like `trap EXIT` for cleanup in bash scripts)."

## Why this approach?

- **Zero Project Footprint:** By putting the `.venv` in the OS Downloads folder and deleting it, your project repository remains clean. No `.venv` folders or `.gitignore` entries are strictly necessary.
- **Offline Reliability:** By separating the "build wheels" (`pip wheel`) phase from the "install" (`pip install --no-index`) phase, the script can run completely offline after the very first execution, provided the cache remains intact.
- **Speed:** `pip install` from local wheels is significantly faster than querying PyPI on every execution.
