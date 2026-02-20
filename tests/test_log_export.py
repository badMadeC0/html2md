import json
import csv
import tempfile
from pathlib import Path
from html2md.log_export import main

        with inp.open('w', encoding='utf-8') as f:
            for d in data:
                f.write(json.dumps(d) + '\n')
            # Test cases for malformed and non-dict JSON lines
            f.write('not valid json\n')
            f.write('[1, 2, 3]\n')
            f.write('"string"\n')
