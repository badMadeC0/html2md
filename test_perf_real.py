import json
import csv
import time
import os
from pathlib import Path
from html2md.log_export import main

data = {
    "ts": "123456789",
    "input": "https://example.com",
    "output": "# Example\n\nThis is an example domain.",
    "status": "ok",
    "reason": "",
    "extra_field_1": "123",
    "extra_field_2": "456",
    "extra_field_3": "789",
}

with open("test.jsonl", "w") as f:
    for _ in range(200000):
        f.write(json.dumps(data) + "\n")

t0 = time.time()
main(['--in', 'test.jsonl', '--out', 'test.csv', '--fields', 'ts,input,output,status,reason'])
print(f"Original Time: {time.time() - t0:.3f}s")
os.remove('test.jsonl')
os.remove('test.csv')
