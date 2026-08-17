"""Agent = collector(s) + optional writer. Deterministic first; the LLM only summarises what was collected.

Every agent returns Findings. A Finding is a fact with a source URL and a fetched-at date, never a guess.
"""
from __future__ import annotations

import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Iterable

UA = "standards-fabric/0.1 (+https://github.com/Life-Atlas/standards-fabric)"


@dataclass
class Finding:
    agent: str
    kind: str                # new-doc | withdrawn | remiss | nwp | eu-act | eu-consultation | funding-call | market | note
    title: str
    source: str              # URL
    date: str | None = None  # ISO date of the item itself if known
    detail: str = ""
    tags: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        return asdict(self)


@dataclass
class AgentResult:
    name: str
    activity: str            # which consortium activity this serves
    findings: list[Finding]
    stats: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def to_json(self) -> dict:
        return {"name": self.name, "activity": self.activity, "stats": self.stats, "errors": self.errors,
                "findings": [f.to_json() for f in self.findings]}


def http_get(url: str, timeout: int = 40) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def strip_html(s: str) -> str:
    import html as _html
    import re as _re
    return _re.sub(r"\s+", " ", _html.unescape(_re.sub(r"<[^>]+>", " ", s or ""))).strip()


def rss_items(url: str, limit: int = 50) -> list[dict]:
    """Minimal RSS/Atom reader → [{title, link, date, summary}]. Raises if the URL is not XML."""
    raw = http_get(url)
    if raw.lstrip()[:1] == b"<" and b"<html" in raw[:400].lower():
        raise ValueError(f"{url} returned HTML, not a feed")
    root = ET.fromstring(raw)
    ns = {"a": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}
    items = []
    for it in root.iter("item"):
        items.append({
            "title": (it.findtext("title") or "").strip(),
            "link": (it.findtext("link") or "").strip(),
            "date": (it.findtext("pubDate") or it.findtext("dc:date", namespaces=ns) or "").strip(),
            "summary": strip_html(it.findtext("description") or "")[:500],
        })
    if not items:
        for e in root.findall("a:entry", ns):
            link = e.find("a:link", ns)
            items.append({
                "title": (e.findtext("a:title", namespaces=ns) or "").strip(),
                "link": link.get("href") if link is not None else "",
                "date": (e.findtext("a:updated", namespaces=ns) or e.findtext("a:published", namespaces=ns) or "").strip(),
                "summary": strip_html(e.findtext("a:summary", namespaces=ns) or e.findtext("a:content", namespaces=ns) or "")[:500],
            })
    return items[:limit]


def load_state(path: str) -> dict:
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(path: str, state: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)


def today() -> str:
    return date.today().isoformat()


def keyword_hit(text: str, keywords: Iterable[str]) -> list[str]:
    t = (text or "").lower()
    return [k for k in keywords if k.lower() in t]
