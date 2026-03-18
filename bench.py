import json
import time
import os

from html2md.log_export import main

def run_bench():
    # generate a large jsonl file
    data = []
    for i in range(100000):
        data.append({"ts": str(i), "input": "input" + str(i), "output": "output" + str(i), "status": "ok", "reason": "none", "extra": "extra" + str(i)})

    with open("bench.jsonl", "w") as f:
        for row in data:
            f.write(json.dumps(row) + "\n")

    start = time.time()
    main(["--in", "bench.jsonl", "--out", "bench.csv", "--fields", "ts,input,output,status,reason"])
    end = time.time()

    print(f"Time taken: {end - start:.4f}s")
    os.remove("bench.jsonl")
    os.remove("bench.csv")

if __name__ == "__main__":
    run_bench()