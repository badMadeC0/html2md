import timeit

_DANGEROUS_PREFIXES = ("=", "+", "-", "@")

def sanitize_old(value: str) -> str:
    if not value or value[0] == "'":
        return value
    if value[0] in _DANGEROUS_PREFIXES or value.lstrip().startswith(_DANGEROUS_PREFIXES):
        return f"'{value}"
    return value

def sanitize_new(value: str) -> str:
    if not value or value[0] == "'":
        return value
    if value[0] in _DANGEROUS_PREFIXES:
        return f"'{value}"
    if value[0].isspace() and value.lstrip().startswith(_DANGEROUS_PREFIXES):
        return f"'{value}"
    return value

test_values = [
    "hello world",
    "   =dangerous",
    "=direct",
    "12345",
    "   safe",
    "'{safe",
    ""
]

print("Old:")
print(timeit.timeit("for v in test_values: sanitize_old(v)", globals=globals(), number=1000000))

print("New:")
print(timeit.timeit("for v in test_values: sanitize_new(v)", globals=globals(), number=1000000))
