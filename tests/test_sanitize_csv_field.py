"""Tests for sanitize_csv_field function."""

import pytest
from html2md.log_export import sanitize_csv_field

@pytest.mark.parametrize("value, expected", [
    # Dangerous prefixes
    ("=SUM(1,2)", "'=SUM(1,2)"),
    ("+1", "'+1"),
    ("-1", "'-1"),
    ("@SUM(1,2)", "'@SUM(1,2)"),
    ("\t", "'\t"),
    ("\r", "'\r"),
    # With leading whitespace
    ("  =SUM(1,2)", "'  =SUM(1,2)"),
    ("\t=SUM(1,2)", "'\t=SUM(1,2)"),
    # Already quoted - should be safe
    ("'=SUM(1,2)", "'=SUM(1,2)"),
    ("'+1", "'+1"),
    # Safe strings
    ("hello", "hello"),
    ("123", "123"),
    # Non-string values
    (123, 123),
    (None, None),
    # Empty string
    ("", ""),
    # Leading whitespace but safe content
    ("  hello", "  hello"),
    # Leading whitespace but quoted formula
    ("  '=SUM", "  '=SUM"),
])
def test_sanitize_csv_field(value, expected):
    """Test sanitize_csv_field handles various inputs correctly."""
    assert sanitize_csv_field(value) == expected

def test_sanitize_csv_field_handles_tab_injection():
    """Specific test for tab injection."""
    value = "\tmalicious"
    expected = "'\tmalicious"
    assert sanitize_csv_field(value) == expected

def test_sanitize_csv_field_handles_carriage_return_injection():
    """Specific test for carriage return injection."""
    value = "\rmalicious"
    expected = "'\rmalicious"
    assert sanitize_csv_field(value) == expected
