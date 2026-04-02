import timeit
import json

def parse_old():
    loads = json.loads
    lines = ['{"a": 1}\n'] * 1000
    for line in lines:
        try:
            rec = loads(line)
        except json.JSONDecodeError:
            continue
        if type(rec) is not dict:
            continue

def parse_new():
    loads = json.loads
    lines = ['{"a": 1}\n'] * 1000
    for line in lines:
        if line.isspace():
            continue
        try:
            rec = loads(line)
        except json.JSONDecodeError:
            continue
        if type(rec) is not dict:
            continue

print("Old JSON parse (no empty lines):")
print(timeit.timeit("parse_old()", globals=globals(), number=10000))

print("New JSON parse (no empty lines):")
print(timeit.timeit("parse_new()", globals=globals(), number=10000))
