"""Facility standards twin: reality (zones × systems) × topics × epochs.

Class = facility. Instances = whatever JSON sits in data/realities/. Zero code changes per new instance.

Output layout (site/data/twin.json — one payload shared by all realities, de-duplicated):
  {
    "epochs": {"past": 2016, "now": 2026, "future": 2036},
    "docs": {doc_id: {compact SEK doc}},                       # every catalogue doc referenced anywhere, once
    "curated": {ref_id: {curated ref}},                        # every curated ref, once
    "topics": {topic_id: {"label", "sek", "intl", "epochs": {e: {"sek": [doc_id, ...], "curated": [ref_id, ...]}}}},
    "realities": {reality_id: {"id","name","kind","reality_basis","smile_phase","zones":[...],"systems":[...],"totals":{}}}
  }
"""
from __future__ import annotations

import glob
import json
import os
from typing import Any

from .sek_client import Doc
from .timeslice import slice_docs

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
SNAP = os.path.join(DATA, "snapshots", "sek")
SITE_DATA = os.path.join(ROOT, "site", "data")

EPOCHS = {"past": 2016, "now": 2026, "future": 2036}
CURATED_VISIBLE = ("in-force", "draft", "aging", "expected", "superseded")


def load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_topics() -> tuple[dict, dict]:
    topics = load_json(os.path.join(DATA, "topics", "topics.json"))["topics"]
    curated = load_json(os.path.join(DATA, "topics", "curated.json"))["refs"]
    return topics, curated


def load_realities() -> list[dict]:
    return [load_json(p) for p in sorted(glob.glob(os.path.join(DATA, "realities", "*.json")))]


def committees_needed(topics: dict) -> list[str]:
    s: set[str] = set()
    for t in topics.values():
        s.update(t.get("sek", []))
    return sorted(s)


def snapshot_path(committee: str) -> str:
    return os.path.join(SNAP, committee.replace("/", "-").replace(" ", "_") + ".json")


def load_committee_docs(committee: str) -> list[Doc]:
    p = snapshot_path(committee)
    if not os.path.exists(p):
        return []
    return [Doc(**d) for d in load_json(p)]


def compact(d: dict) -> dict:
    return {"n": d["name"], "t": d["title"], "p": d["prefix"], "ty": d["doc_type"], "s": d["status"],
            "c": d["committee_sek"], "i": d["committee_intl"], "y": d["pub_year"], "sw": d["is_swedish"],
            "u": d.get("url"), "det": d.get("determination_date"), "ann": d.get("annulment_date")}


def build_topic_bundles(topics: dict, curated: dict) -> tuple[dict, dict]:
    """Slice every committee once; return (topic_bundles, docs)."""
    docs: dict[str, dict] = {}
    committee_slices: dict[str, dict[str, list[dict]]] = {}
    for c in committees_needed(topics):
        committee_slices[c] = slice_docs(load_committee_docs(c), EPOCHS["past"], EPOCHS["now"], EPOCHS["future"])
    bundles: dict[str, dict] = {}
    for tid, t in topics.items():
        b = {"label": t["label"], "sek": t.get("sek", []), "intl": t.get("intl", []),
             "epochs": {e: {"sek": [], "curated": []} for e in EPOCHS}}
        for c in t.get("sek", []):
            sl = committee_slices.get(c, {e: [] for e in EPOCHS})
            for e in EPOCHS:
                for d in sl[e]:
                    if d["id"] not in docs:
                        docs[d["id"]] = compact(d)
                    # per-epoch flags live on the doc (basis/pipeline/aging are epoch-dependent only for future)
                    docs[d["id"]].setdefault("b", {})[e] = d["basis"]
                    if e == "future":
                        docs[d["id"]]["pipe"] = bool(d.get("pipeline"))
                        docs[d["id"]]["age"] = bool(d.get("aging"))
                    if d["id"] not in b["epochs"][e]["sek"]:
                        b["epochs"][e]["sek"].append(d["id"])
        for rid in t.get("curated", []):
            ref = curated.get(rid)
            if not ref:
                continue
            for e in EPOCHS:
                if ref["epochs"].get(e) in CURATED_VISIBLE:
                    b["epochs"][e]["curated"].append(rid)
        bundles[tid] = b
    return bundles, docs


def counts_for(topic_ids: list[str], bundles: dict, docs: dict) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for e in EPOCHS:
        sek: set[str] = set()
        cur: set[str] = set()
        for tid in topic_ids:
            b = bundles.get(tid)
            if not b:
                continue
            sek.update(b["epochs"][e]["sek"])
            cur.update(b["epochs"][e]["curated"])
        pipeline = sum(1 for i in sek if docs[i].get("pipe")) if e == "future" else 0
        swedish = sum(1 for i in sek if docs[i].get("sw"))
        out[e] = {"sek": len(sek), "swedish": swedish, "curated": len(cur), "pipeline": pipeline, "total": len(sek) + len(cur)}
    return out


def build_all(out_dir: str = SITE_DATA) -> dict:
    topics, curated = load_topics()
    bundles, docs = build_topic_bundles(topics, curated)
    realities: dict[str, dict] = {}
    for r in load_realities():
        used = sorted({t for z in r["zones"] + r["systems"] for t in z.get("topics", [])})
        realities[r["id"]] = {
            "id": r["id"], "name": r["name"], "kind": r["kind"], "class": r.get("class", "facility"),
            "reality_basis": r.get("reality_basis", ""), "smile_phase": r.get("smile_phase"),
            "zones": [{**z, "counts": counts_for(z.get("topics", []), bundles, docs)} for z in r["zones"]],
            "systems": [{**s, "counts": counts_for(s.get("topics", []), bundles, docs)} for s in r["systems"]],
            "totals": counts_for(used, bundles, docs),
            "missing_topics": [t for t in used if t not in bundles],
        }
    payload = {"epochs": EPOCHS, "docs": docs, "curated": curated, "topics": bundles, "realities": realities,
               "generated_from": {"sek_snapshot_dir": os.path.relpath(SNAP, ROOT).replace("\\", "/"),
                                  "topics_file": "data/topics/topics.json"}}
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "twin.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"epochs": EPOCHS, "docs": len(docs), "curated": len(curated),
                   "realities": [{"id": p["id"], "name": p["name"], "kind": p["kind"], "totals": p["totals"]} for p in realities.values()]},
                  f, ensure_ascii=False, indent=1)
    return payload
