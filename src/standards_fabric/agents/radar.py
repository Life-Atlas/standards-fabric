"""Options radar — monthly scan for the eight optional efforts (ways of working IoT+AI, national case bank,
national IoT device register, W3C, JTC 1, JTC 4, RefARK, Citiverse).

Sources are the same feeds; each option owns keywords in data/sources/options.json so a new option is data, not code.
"""
from __future__ import annotations

import os

from .. import twin
from .base import AgentResult, Finding, keyword_hit, load_state, rss_items, save_state, today

OPTIONS = twin.load_json(os.path.join(twin.DATA, "sources", "options.json"))
STATE_DIR = os.path.join(twin.ROOT, "reports", "state")


def options_radar() -> AgentResult:
    name = "options_radar"
    findings: list[Finding] = []
    errors: list[str] = []
    feeds = OPTIONS["feeds"]
    items_by_feed: dict[str, list[dict]] = {}
    for f in feeds:
        try:
            items_by_feed[f["id"]] = rss_items(f["url"], limit=60)
        except Exception as e:  # noqa: BLE001
            errors.append(f"feed {f['id']} failed: {e}")
    seen_path = os.path.join(STATE_DIR, "options_radar.json")
    seen = load_state(seen_path)
    for opt in OPTIONS["options"]:
        for fid, items in items_by_feed.items():
            for it in items:
                key = opt["id"] + "|" + it["link"]
                if key in seen:
                    continue
                hits = keyword_hit(it["title"] + " " + it["summary"], opt["keywords"])
                if hits:
                    seen[key] = today()
                    findings.append(Finding(name, "option", f"[{opt['label']}] {it['title']}", it["link"], it["date"], it["summary"][:240], [opt["id"], fid] + hits))
    save_state(seen_path, seen)
    return AgentResult(name, "Options radar (8 optional efforts)", findings, {"options": len(OPTIONS["options"]), "feeds": len(feeds)}, errors)
