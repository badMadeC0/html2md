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
    if value[0] in _DANGEROUS_PREFIXES or (value[0].isspace() and value.lstrip().startswith(_DANGEROUS_PREFIXES)):
        return f"'{value}"
    return value

# Mostly normal strings without leading spaces
test_values = [
    "normal value",
    "another normal value",
    "123",
    "https://example.com",
    "   =dangerous",
    "=direct",
    "   safe",
    "'{safe",
    ""
] * 100

print("Old sanitize:")
print(timeit.timeit("for v in test_values: sanitize_old(v)", globals=globals(), number=10000))

print("New sanitize:")
print(timeit.timeit("for v in test_values: sanitize_new(v)", globals=globals(), number=10000))
