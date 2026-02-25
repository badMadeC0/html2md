import logging
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import html2md.cli

def test_reproduce_exceptions():
    print("Starting tests...")

    # Setup mocks
    mock_requests = MagicMock()

    # We need a proper exception class for RequestException so 'except requests.RequestException' works
    class MockRequestException(Exception):
        pass
    mock_requests.RequestException = MockRequestException

    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session

    # Mock other deps
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab = MagicMock()

    # Patch dictionary for sys.modules
    patch_modules = {
        'requests': mock_requests,
        'markdownify': mock_markdownify,
        'bs4': mock_bs4,
        'reportlab.platypus': mock_reportlab,
        'reportlab.lib.styles': mock_reportlab,
    }

    # --- Test 1: Network Error ---
    print("\n--- Test 1: Simulating Network Error ---")
    mock_session.get.side_effect = MockRequestException("Simulated Network Error")

    with patch.dict(sys.modules, patch_modules):
        with patch('logging.error') as mock_log_error:
            html2md.cli.main(['--url', 'http://example.com/network-fail'])

            if mock_log_error.called:
                args, _ = mock_log_error.call_args
                msg = args[0] % args[1]
                print(f"Log message caught: {msg}")
                if "Network error: Simulated Network Error" in msg:
                     print("SUCCESS: Confirmed specific network error caught.")
                else:
                     print(f"FAILURE: Expected 'Network error...', got '{msg}'")
            else:
                print("FAILURE: logging.error was not called.")

    # --- Test 2: File Error ---
    print("\n--- Test 2: Simulating File Error ---")

    # Reset mocks
    mock_session.get.side_effect = None
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_session.get.return_value = mock_response

    # Mock open to raise OSError
    with patch('builtins.open', side_effect=OSError("Simulated File Permission Error")):
        with patch.dict(sys.modules, patch_modules):
            with patch('logging.error') as mock_log_error:
                with patch('os.path.exists', return_value=False):
                    with patch('os.makedirs'):
                         html2md.cli.main(['--url', 'http://example.com/file-fail', '--outdir', 'output'])

                if mock_log_error.called:
                    args, _ = mock_log_error.call_args
                    msg = args[0] % args[1]
                    print(f"Log message caught: {msg}")
                    if "File error: Simulated File Permission Error" in msg:
                        print("SUCCESS: Confirmed specific file error caught.")
                    else:
                        print(f"FAILURE: Expected 'File error...', got '{msg}'")
                else:
                    print("FAILURE: logging.error was not called.")

    # --- Test 3: Unexpected Error ---
    print("\n--- Test 3: Simulating Unexpected Error ---")

    mock_session.get.side_effect = Exception("Some Random Error")

    with patch.dict(sys.modules, patch_modules):
        with patch('logging.error') as mock_log_error:
             html2md.cli.main(['--url', 'http://example.com/unexpected-fail'])

             if mock_log_error.called:
                args, _ = mock_log_error.call_args
                msg = args[0] % args[1]
                print(f"Log message caught: {msg}")
                if "Unexpected conversion error: Some Random Error" in msg:
                    print("SUCCESS: Confirmed unexpected error caught.")
                else:
                    print(f"FAILURE: Expected 'Unexpected conversion error...', got '{msg}'")

if __name__ == "__main__":
    test_reproduce_exceptions()
