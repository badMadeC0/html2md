with open("src/html2md/log_export.py", "r") as f:
    content = f.read()

import re
old_str = """            row = {
                output_name: _sanitize_value(rec.get(input_name, ""))
                for input_name, output_name in mapping
            }
            w.writerow(row)"""

new_str = """            for input_name, output_name in mapping:
                val = rec.get(input_name)
                if val is None:
                    rec[output_name] = ""
                elif isinstance(val, str):
                    if val.startswith("'"):
                        if input_name != output_name:
                            rec[output_name] = val
                    elif val.lstrip().startswith(_DANGEROUS_PREFIXES):
                        rec[output_name] = f"'{val}"
                    elif input_name != output_name:
                        rec[output_name] = val
                elif input_name != output_name:
                    rec[output_name] = val
            w.writerow(rec)"""

new_content = content.replace(old_str, new_str)

with open("src/html2md/log_export.py", "w") as f:
    f.write(new_content)
