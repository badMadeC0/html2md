import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _extract_gemini_settings(workflow_text):
    marker = "          settings: |-\n"
    start = workflow_text.index(marker) + len(marker)
    settings_lines = []
    for line in workflow_text[start:].splitlines():
        if not line.startswith("            "):
            break
        settings_lines.append(line[12:])
    return json.loads("\n".join(settings_lines))


def test_gemini_code_assist_yolo_run_disables_core_tools():
    workflow_text = (REPO_ROOT / ".github/workflows/gemini-code-assist.yml").read_text()

    assert "name: Gemini Code Assist" in workflow_text
    settings = _extract_gemini_settings(workflow_text)

    assert settings["tools"]["core"] == []
