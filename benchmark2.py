import timeit

setup = """
strings = [
    "hello world",
    "  normal string",
    "=1+1",
    "  @bad"
] * 1000

_DANGEROUS_PREFIXES = ("=", "+", "-", "@")

def _sanitize_formula_orig(value: str) -> str:
    if not value or value[0] == "'":
        return value
    if value[0] in _DANGEROUS_PREFIXES or value.lstrip().startswith(_DANGEROUS_PREFIXES):
        return f"'{value}"
    return value

def _sanitize_formula_new(value: str) -> str:
    if not value or value[0] == "'":
        return value
    if value[0] in ("=", "+", "-", "@"):
        return f"'{value}"
    # only lstrip if the first character is whitespace
    if value[0].isspace() and value.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value

def _sanitize_formula_new2(value: str) -> str:
    if not value or value[0] == "'":
        return value
    if value[0] in ("=", "+", "-", "@"):
        return f"'{value}"
    stripped = value.lstrip()
    if stripped and stripped[0] in ("=", "+", "-", "@"):
        return f"'{value}"
    return value
"""

code_orig = """
for s in strings:
    _sanitize_formula_orig(s)
"""

code_new = """
for s in strings:
    _sanitize_formula_new(s)
"""

code_new2 = """
for s in strings:
    _sanitize_formula_new2(s)
"""


print("Original:", timeit.timeit(code_orig, setup=setup, number=1000))
print("New:", timeit.timeit(code_new, setup=setup, number=1000))
print("New 2:", timeit.timeit(code_new2, setup=setup, number=1000))
