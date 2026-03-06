
## 2024-05-19 - Fast CSV DictWriter Formatting
**Learning:** For extremely large JSONL/CSV pipelines, Python dictionary comprehensions combined with per-field function calls (e.g. `_sanitize_value`) in hot inner loops become a major bottleneck.
**Action:** Inline string operations like `.startswith()` directly into the generator loop rather than calling external helper functions for every row/field. Caching globals (`_DANGEROUS_PREFIXES`) into local loop scope also shaves off execution time by reducing dictionary lookups. When mutating a dictionary in place during a mapping loop, always pre-fetch values to a tuple first to prevent cascading overwrite collisions (e.g., when output names match subsequent input names).
