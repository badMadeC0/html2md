import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _extract_gemini_settings(workflow_text):
    name_pos = workflow_text.find("name: Gemini Code Assist")
    # Search for the settings block specifically after the Gemini name
    marker = "settings: |-"
    try:
        marker_pos = workflow_text.index(marker, name_pos if name_pos != -1 else 0)
        start = workflow_text.find("\n", marker_pos) + 1
    except ValueError:
        raise ValueError("Could not find 'settings: |-' after Gemini name")

    settings_lines = []
    for line in workflow_text[start:].splitlines():
        # Stop if we hit a non-empty line with less indentation than the JSON block
        if line.strip() and not line.startswith("            "):
            break
        settings_lines.append(line[12:] if len(line) >= 12 else "")
    return json.loads("\n".join(settings_lines))


def test_gemini_code_assist_yolo_run_disables_core_tools():
    workflow_text = (REPO_ROOT / ".github/workflows/gemini-code-assist.yml").read_text()

    assert "name: Gemini Code Assist" in workflow_text
    settings = _extract_gemini_settings(workflow_text)

    assert settings["tools"]["core"] == []
