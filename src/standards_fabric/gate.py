"""Acceptance gate — exit 0 only when every check passes. Each check ships with a mutation in tests/test_gate.py
that makes it fail; a check that has never said no does not count.

Checks:
  G1  site/index.html exists, embeds data (no '/*__DATA__*/null' left), and is < 16 MB
  G2  site/data/twin.json parses; every reality has ≥1 zone; every zone has counts for past/now/future
  G3  no reality reports missing topics
  G4  every curated ref used by a topic exists and declares three epochs
  G5  reports/weekly/LATEST.md exists and names its period; every finding in the latest findings.json has a source URL
  G6  numbers in README.md that describe the build (realities, topics, curated refs) equal the measured values
"""
from __future__ import annotations

import glob
import os
import re
import sys

from .twin import ROOT, load_json

SITE = os.path.join(ROOT, "site")


def _fail(msgs: list[str], m: str) -> None:
    msgs.append(m)


def run_gate(root: str = ROOT) -> int:
    fails: list[str] = []
    site = os.path.join(root, "site")
    idx = os.path.join(site, "index.html")
    # G1
    if not os.path.exists(idx):
        _fail(fails, "G1 site/index.html missing")
    else:
        html = open(idx, encoding="utf-8").read()
        if "/*__DATA__*/null" in html:
            _fail(fails, "G1 site/index.html has no embedded data")
        if os.path.getsize(idx) > 16 * 1024 * 1024:
            _fail(fails, "G1 site/index.html larger than 16 MB")
    # G2 / G3
    twin_p = os.path.join(site, "data", "twin.json")
    if not os.path.exists(twin_p):
        _fail(fails, "G2 site/data/twin.json missing")
        realities = {}
    else:
        payload = load_json(twin_p)
        realities = payload.get("realities", {})
        if not realities:
            _fail(fails, "G2 no realities in twin.json")
        for rid, r in realities.items():
            if not r.get("zones"):
                _fail(fails, f"G2 reality {rid} has no zones")
            for z in r.get("zones", []):
                if set(z.get("counts", {}).keys()) != {"past", "now", "future"}:
                    _fail(fails, f"G2 reality {rid} zone {z.get('id')} lacks epoch counts")
            if r.get("missing_topics"):
                _fail(fails, f"G3 reality {rid} has missing topics: {r['missing_topics']}")
    # G4
    topics = load_json(os.path.join(root, "data", "topics", "topics.json"))["topics"]
    curated = load_json(os.path.join(root, "data", "topics", "curated.json"))["refs"]
    for tid, t in topics.items():
        for rid in t.get("curated", []):
            if rid not in curated:
                _fail(fails, f"G4 topic {tid} cites unknown curated ref {rid}")
            elif set(curated[rid].get("epochs", {}).keys()) != {"past", "now", "future"}:
                _fail(fails, f"G4 curated ref {rid} lacks three epochs")
    # G5
    latest = os.path.join(root, "reports", "weekly", "LATEST.md")
    if not os.path.exists(latest):
        _fail(fails, "G5 reports/weekly/LATEST.md missing")
    else:
        head = open(latest, encoding="utf-8").read(400)
        if not re.search(r"weekly \d{4}-W\d{2}", head):
            _fail(fails, "G5 LATEST.md does not name its period")
        runs = sorted(glob.glob(os.path.join(root, "reports", "weekly", "*", "findings.json")))
        if runs:
            fj = load_json(runs[-1])
            for a in fj.get("agents", []):
                for f in a.get("findings", []):
                    if not str(f.get("source", "")).startswith(("http://", "https://", "C:", "/")):
                        _fail(fails, f"G5 finding without source URL in {a['name']}: {f.get('title')}")
                        break
    # G6 — README numbers are measured, never written
    readme = os.path.join(root, "README.md")
    if os.path.exists(readme):
        text = open(readme, encoding="utf-8").read()
        measured = {"realities": len(glob.glob(os.path.join(root, "data", "realities", "*.json"))),
                    "topics": len(topics), "curated refs": len(curated)}
        for label, n in measured.items():
            m = re.search(r"\*\*(\d+)\*\* " + re.escape(label), text)
            if m and int(m.group(1)) != n:
                _fail(fails, f"G6 README says {m.group(1)} {label}, measured {n}")
    for f in fails:
        print("FAIL", f)
    print("gate:", "GREEN" if not fails else f"RED ({len(fails)})")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(run_gate())
