
import csv
    command = ["html2md-log-export", "--in", str(infile), "--out", str(outfile)]
    subprocess.run(command, check=True)

    with open(outfile, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader)

    # Verify values are prepended with a single quote
    assert row["input"] == "'=1+1"
    assert row["output"] == "'+cmd"
    assert row["status"] == "'-risk"
    assert row["reason"] == "'@sum"
