"""Data-driven integrity: every topic a reality uses exists; every curated id a topic cites exists; no domain nouns
leak into shared code; every curated ref declares all three epochs and a confidence."""
import glob
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def test_realities_reference_defined_topics():
    topics = load(os.path.join(ROOT, "data", "topics", "topics.json"))["topics"]
    for p in glob.glob(os.path.join(ROOT, "data", "realities", "*.json")):
        r = load(p)
        for z in r["zones"] + r["systems"]:
            for t in z["topics"]:
                assert t in topics, f"{os.path.basename(p)} zone {z['id']} uses undefined topic {t}"


def test_topics_reference_defined_curated_refs():
    topics = load(os.path.join(ROOT, "data", "topics", "topics.json"))["topics"]
    curated = load(os.path.join(ROOT, "data", "topics", "curated.json"))["refs"]
    for tid, t in topics.items():
        for rid in t.get("curated", []):
            assert rid in curated, f"topic {tid} cites undefined curated ref {rid}"


def test_curated_refs_declare_epochs_and_confidence():
    curated = load(os.path.join(ROOT, "data", "topics", "curated.json"))["refs"]
    allowed = {"absent", "draft", "in-force", "superseded", "expected", "aging"}
    for rid, ref in curated.items():
        assert set(ref["epochs"]) == {"past", "now", "future"}, rid
        assert set(ref["epochs"].values()) <= allowed, rid
        assert ref.get("confidence"), rid


def test_shared_code_has_no_domain_nouns():
    """The class is 'facility'. Instance nouns belong in data/, never in src/."""
    banned = re.compile(r"\b(steel|welding portal|datacenter|hyres|apartment|tunnel|VSAB|Hagerbach)\b", re.I)
    for p in glob.glob(os.path.join(ROOT, "src", "standards_fabric", "**", "*.py"), recursive=True):
        text = open(p, encoding="utf-8").read()
        # docstrings may mention examples; code lines may not
        code = "\n".join(ln for ln in text.splitlines() if not ln.strip().startswith(("#", '"', "'")))
        assert not banned.search(code), f"domain noun in shared code: {p}"


def test_zone_layouts_do_not_overlap():
    for p in glob.glob(os.path.join(ROOT, "data", "realities", "*.json")):
        r = load(p)
        cells = {}
        for z in r["zones"]:
            for x in range(z["x"], z["x"] + z["w"]):
                for y in range(z["y"], z["y"] + z["h"]):
                    assert (x, y) not in cells, f"{os.path.basename(p)}: {z['id']} overlaps {cells[(x, y)]} at {(x, y)}"
                    cells[(x, y)] = z["id"]
