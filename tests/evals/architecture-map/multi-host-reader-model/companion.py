import json
import subprocess


INDEX_PATH = "vault/papers.json"


def set_status(paper_id, status):
    with open(INDEX_PATH, encoding="utf-8") as handle:
        index = json.load(handle)
    index[paper_id]["status"] = status
    with open(INDEX_PATH, "w", encoding="utf-8") as handle:
        json.dump(index, handle)


def run_today():
    return subprocess.run(["reader-map", "run", "--today"], check=False).returncode
