from html2md.log_export import _sanitize_formula

print(_sanitize_formula("hello"))
print(_sanitize_formula("=1+2"))
print(_sanitize_formula("  +3+4"))
print(_sanitize_formula("  \t@bad"))
print(_sanitize_formula(""))
print(_sanitize_formula("'safe"))
