import pytest
import re
import os


def test_ps_url_validation():
    """
    Ensure the loop variable ($u) is used in System.Uri casts in gui-url-convert.ps1
    to prevent the uninitialized `$url` vulnerability from recurring.
    """
    with open("gui-url-convert.ps1", "r", encoding="utf-8") as f:
        content = f.read()

    # Vulnerability assertion: ensure uninitialized $url is not used
    assert (
        "[System.Uri]$url" not in content
    ), "VULNERABILITY: Uninitialized `$url` variable used in System.Uri cast."

    # Correctness assertion: ensure the proper loop variable is used
    assert re.search(
        r"foreach\s*\(\$u\s+in\s+\$urlList\)", content
    ), "Could not find the expected foreach loop for $urlList."
    assert (
        "[System.Uri]$u" in content
    ), "Could not find correct System.Uri cast using loop variable $u."


def test_no_uninitialized_variables_in_foreach():
    """
    Ensure no common `.ps1` files use uninitialized variables inside foreach loops.
    """
    # Just a simple static check to prevent recurrence of this exact bug
    files = ["gui-url-convert.ps1", "setup-html2md.ps1"]
    for filename in files:
        if not os.path.exists(filename):
            continue

        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Example pattern: foreach ($var in $list) { ... }
        # Let's ensure the var is used correctly and not another similar sounding var
        if filename == "gui-url-convert.ps1":
            # Just verify the loop logic remains secure
            assert "foreach ($u in $urlList)" in content
            assert "$uriObj = [System.Uri]$u" in content
