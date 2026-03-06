with open("src/html2md/log_export.py", "r") as f:
    content = f.read()

import re
old_str = """    with inp.open('r', encoding='utf-8') as fi, out.open('w', newline='', encoding='utf-8') as fo:
        w = csv.DictWriter(fo, fieldnames=fieldnames, extrasaction='ignore', restval='')
        w.writeheader()

        for line in fi:"""

new_str = """    with inp.open('r', encoding='utf-8') as fi, out.open('w', newline='', encoding='utf-8') as fo:
        w = csv.DictWriter(fo, fieldnames=fieldnames, extrasaction='ignore', restval='')
        w.writeheader()

        # Cache global references locally for inner loop speed
        _prefixes = _DANGEROUS_PREFIXES

        for line in fi:"""

new_content = content.replace(old_str, new_str)

old_str2 = """                    elif val.lstrip().startswith(_DANGEROUS_PREFIXES):"""
new_str2 = """                    elif val.lstrip().startswith(_prefixes):"""

new_content = new_content.replace(old_str2, new_str2)

with open("src/html2md/log_export.py", "w") as f:
    f.write(new_content)
