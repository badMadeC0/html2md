import timeit

setup = """
from html2md.log_export import _sanitize_formula
strings = [
    "hello world",
    "  normal string",
    "=1+1",
    "  @bad"
] * 1000
"""

code = """
for s in strings:
    _sanitize_formula(s)
"""

print("Original:", timeit.timeit(code, setup=setup, number=1000))
