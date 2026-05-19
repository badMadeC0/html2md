import timeit

setup = """
import json

def _sanitize_formula(value: str) -> str:
    if not value or value[0] == "'":
        return value
    if value[0] in ("=", "+", "-", "@") or value.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value

def _sanitize_value(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, str):
        return _sanitize_formula(value)
    return value

input_names = ["ts", "input", "output", "status", "reason", "extra1", "extra2"]
records = [
    {"ts": "123", "input": "test", "output": "ok", "status": "200", "reason": "none", "extra1": "=A1+1", "extra2": "  normal"},
    {"ts": "124", "input": "test2", "output": "fail", "status": "500", "reason": "error"},
] * 1000

class DummyWriter:
    def writerow(self, row):
        pass
w = DummyWriter()
writerow = w.writerow
sanitize = _sanitize_value
"""

code_list = """
for rec in records:
    writerow([
        sanitize(rec.get(name, ""))
        for name in input_names
    ])
"""

code_gen = """
for rec in records:
    writerow(
        sanitize(rec.get(name, ""))
        for name in input_names
    )
"""

code_map = """
for rec in records:
    get = rec.get
    writerow(map(sanitize, (get(name, "") for name in input_names)))
"""

code_tuple = """
for rec in records:
    writerow(tuple(
        sanitize(rec.get(name, ""))
        for name in input_names
    ))
"""

print("List comp:", timeit.timeit(code_list, setup=setup, number=1000))
print("Generator:", timeit.timeit(code_gen, setup=setup, number=1000))
print("Map:", timeit.timeit(code_map, setup=setup, number=1000))
print("Tuple comp:", timeit.timeit(code_tuple, setup=setup, number=1000))
