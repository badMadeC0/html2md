## 2024-05-18 - [Python Chunked Downloads]
**Learning:** In Python, doing `bytes += chunk` in a loop has O(N^2) memory reallocation overhead because bytes are immutable. This is extremely inefficient for streaming large HTTP responses.
**Action:** Always use `bytearray().extend(chunk)` and convert to `bytes()` at the end for amortized O(1) appends.
