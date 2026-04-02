import timeit
import json

def parse_old():
    # from log_export.py currently
    loads = json.loads
    lines = ['{"a": 1}\n', '  \n', '{"a": 2}\n']
    for line in lines:
        try:
            rec = loads(line)
        except json.JSONDecodeError:
            continue
        if type(rec) is not dict:
            continue

def parse_new():
    loads = json.loads
    lines = ['{"a": 1}\n', '  \n', '{"a": 2}\n']
    for line in lines:
        # short-circuit empty or space-only lines
        if not line or line.isspace():
            continue
        try:
            rec = loads(line)
        except json.JSONDecodeError:
            continue
        if type(rec) is not dict:
            continue

print("Old JSON parse:")
print(timeit.timeit("parse_old()", globals=globals(), number=1000000))

print("New JSON parse:")
print(timeit.timeit("parse_new()", globals=globals(), number=1000000))
