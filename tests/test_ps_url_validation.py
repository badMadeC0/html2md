import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GUI_URL_CONVERT_SCRIPT = REPO_ROOT / "gui-url-convert.ps1"
FOREACH_URL_LIST_PATTERN = re.compile(
    r"foreach\s*\(\s*\$u\s+in\s+\$urlList\s*\)",
    re.IGNORECASE,
)
VULNERABLE_URI_CAST_PATTERN = re.compile(
    r"\\[System\\.Uri\\]\\s*\\$url\\b",
    re.IGNORECASE,
)
SAFE_URI_CAST_PATTERN = re.compile(
    r"\\[System\\.Uri\\]\\s*\\$u\\b",
    re.IGNORECASE,
)


def test_ps_url_validation():
    """
    Ensure the loop variable ($u) is used in System.Uri casts in gui-url-convert.ps1
    to prevent the uninitialized `$url` vulnerability from recurring.
    """
    assert GUI_URL_CONVERT_SCRIPT.exists(), (
        f"Required file {GUI_URL_CONVERT_SCRIPT} not found for validation."
    )

    content = GUI_URL_CONVERT_SCRIPT.read_text(encoding="utf-8")

    # Vulnerability assertion: ensure uninitialized $url is not used in a Uri cast.
    assert not VULNERABLE_URI_CAST_PATTERN.search(content), (
        "VULNERABILITY: Uninitialized `$url` variable used in System.Uri cast."
    )

    # Correctness assertion: ensure the proper loop variable is used.
    assert FOREACH_URL_LIST_PATTERN.search(content), (
        "Could not find the expected foreach loop for $urlList."
    )
    assert SAFE_URI_CAST_PATTERN.search(content), (
        "Could not find correct System.Uri cast using loop variable $u."
    )
