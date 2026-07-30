import ast
import os

def check_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'run' and hasattr(node.func.value, 'id') and node.func.value.id == 'app':
                        print(f"Found app.run() in {path}")
                        # Check for debug=True
                        for kw in node.keywords:
                            if kw.arg == 'debug' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                print(f"WARNING: app.run(debug=True) found in {path}")
    except Exception as e:
        print(f"Error checking {path}: {e}")

for root, _, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            check_file(os.path.join(root, file))
