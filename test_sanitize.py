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

cases = [
    "hello",
    "=danger",
    " =danger",
    "\t=danger",
    "\n=danger",
    "  safe",
    " safe",
    "123",
    "-1",
    " -1",
    "'safe"
]

for c in cases:
    o = sanitize_old(c)
    n = sanitize_new(c)
    assert o == n, f"Failed on {repr(c)}: {repr(o)} != {repr(n)}"
print("All pass")
