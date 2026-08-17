"""Rewrite the measured numbers in README.md from the repo itself (gate check G6 verifies them).

python scripts/sync_readme_numbers.py
"""
import glob
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def measure() -> dict:
    topics = json.load(open(os.path.join(ROOT, "data", "topics", "topics.json"), encoding="utf-8"))["topics"]
    curated = json.load(open(os.path.join(ROOT, "data", "topics", "curated.json"), encoding="utf-8"))["refs"]
    committees = [f for f in glob.glob(os.path.join(ROOT, "data", "snapshots", "sek", "*.json"))
                  if not os.path.basename(f).startswith("_")]
    idx = json.load(open(os.path.join(ROOT, "site", "data", "index.json"), encoding="utf-8"))
    return {"realities": len(glob.glob(os.path.join(ROOT, "data", "realities", "*.json"))),
            "topics": len(topics), "curated refs": len(curated),
            "SEK committees snapshotted": len(committees),
            "catalogue documents time-sliced": idx["docs"]}


def main() -> None:
    m = measure()
    p = os.path.join(ROOT, "README.md")
    s = open(p, encoding="utf-8").read()
    for label, n in m.items():
        s = re.sub(r"\*\*\d+\*\* " + re.escape(label), f"**{n}** {label}", s)
    open(p, "w", encoding="utf-8").write(s)
    print(" · ".join(f"{v} {k}" for k, v in m.items()))


if __name__ == "__main__":
    main()
