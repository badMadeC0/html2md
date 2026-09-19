import json
import os

filepath = 'package.json'
if os.path.exists(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
else:
    data = {
        "name": "html2md-cli",
        "version": "0.11.6",
        "private": True
    }

if 'scripts' not in data:
    data['scripts'] = {}

data['scripts'].update({
    "healthcheck": "node scripts/healthcheck.mjs",
    "self:heal": "node scripts/self-heal.mjs",
    "lint": "eslint .",
    "format": "prettier -w .",
    "typecheck": "tsc -b",
    "test": "vitest run"
})

with open(filepath, 'w') as f:
    json.dump(data, f, indent=2)
