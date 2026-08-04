import timeit

setup = """
_DANGEROUS_PREFIXES = ("=", "+", "-", "@")

def _sanitize_formula_old(value: str) -> str:
    if not value or value[0] == "'":
        return value
    if value[0] in _DANGEROUS_PREFIXES or value.lstrip().startswith(_DANGEROUS_PREFIXES):
        return f"'{value}"
    return value

def _sanitize_formula_new(value: str) -> str:
    if not value or value[0] == "'":
        return value
    c = value[0]
    if c in "=+-@":
        return f"'{value}"
    if c.isspace() and value.lstrip().startswith(_DANGEROUS_PREFIXES):
        return f"'{value}"
    return value
"""

print("Old (normal):", timeit.timeit("_sanitize_formula_old('normal string')", setup=setup, number=1000000))
print("New (normal):", timeit.timeit("_sanitize_formula_new('normal string')", setup=setup, number=1000000))
