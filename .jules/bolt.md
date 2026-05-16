## 2024-05-16 - [Fast CSV Sanitization]
**Learning:** Checking for `.isspace()` on the first character before executing an expensive `.lstrip().startswith()` is an effective performance optimization in tight loops, such as parsing rows and fields.
**Action:** Always prefer checking conditions via individual characters rather than creating copies of entire strings (e.g. `lstrip()`) when dealing with large volumes of text.
