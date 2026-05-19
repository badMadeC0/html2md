import csv
import io

f = io.StringIO()
w = csv.writer(f)
w.writerow(x for x in [1, 2, 3])
print(f.getvalue())
