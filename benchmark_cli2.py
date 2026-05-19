import timeit

setup = """
_DANGEROUS_PREFIXES = ("=", "+", "-", "@")

def _sanitize_formula_orig(value: str) -> str:
    if not value or value[0] == "'":
        return value
    if value[0] in _DANGEROUS_PREFIXES or value.lstrip().startswith(_DANGEROUS_PREFIXES):
        return f"'{value}"
    return value

# Even faster lookup
_DANGEROUS_SET = {"=", "+", "-", "@"}

def _sanitize_formula_new(value: str) -> str:
    if not value or value[0] == "'":
        return value
    if value[0] in _DANGEROUS_SET:
        return f"'{value}"
    if value[0].isspace():
        stripped = value.lstrip()
        if stripped and stripped[0] in _DANGEROUS_SET:
            return f"'{value}"
    return value

strings = [
    "hello world",
    "  normal string",
    "=1+1",
    "  @bad",
    "test", "test2", "ok", "fail"
] * 1000
"""

code_orig = """
for s in strings:
    _sanitize_formula_orig(s)
"""

code_new = """
for s in strings:
    _sanitize_formula_new(s)
"""

print("Original sanitize:", timeit.timeit(code_orig, setup=setup, number=10000))
print("New sanitize:", timeit.timeit(code_new, setup=setup, number=10000))
