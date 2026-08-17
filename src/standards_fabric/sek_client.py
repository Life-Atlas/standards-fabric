"""Client for the public search API behind elstandard.se (SEK Svensk Elstandard).

Zero lock-in: stdlib only. Everything returned is metadata (document number, title,
status, dates, committees) - never the standard text itself.

Endpoints (discovered 2026-08-17 by reading the site's Next.js bundle):
    POST https://elstandard.se/api/search/kommitte   {"query": "", "size": 33, "page": 0}
    POST https://elstandard.se/api/search/standard   {"query": "TK IoT", "size": 100,
                                                       "page": 0, "statusFilters": ["6790001"]}
Pages are 0-based. Elasticsearch caps `total` at 10 000 ("gte"). Relevance ranking puts
documents whose `committee_sek.name` equals the query first, so we paginate until a page
contains no document for the wanted committee (two empty pages in a row = stop).
"""
from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

BASE = "https://elstandard.se/api"
UA = "standards-fabric/0.1 (+https://github.com/Life-Atlas/standards-fabric)"

# document_status keys used by the site (from the bundle)
STATUS = {
    "6788001": "remiss",             # out for public comment
    "6789001": "under_bearbetning",  # in progress
    "6790001": "publicerad",         # published / in force
    "6791001": "upphavd",            # withdrawn
    "6784001": "new_work_proposal",  # NWP
}
STATUS_KEY = {v: k for k, v in STATUS.items()}


def _post(path: str, payload: dict, retries: int = 3, timeout: int = 30) -> dict:
    data = json.dumps(payload).encode()
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                BASE + path, data=data,
                headers={"content-type": "application/json", "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001 - we retry then re-raise
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"SEK API failed for {path}: {last}")


@dataclass
class Committee:
    name: str            # "TK IoT"
    title: str           # "Sakernas internet"
    slug: str            # "/kommitte/tk-iot/"
    id: int
    watches: list[str] = field(default_factory=list)  # IEC/ISO committees followed

    @property
    def url(self) -> str:
        return "https://elstandard.se" + self.slug


@dataclass
class Doc:
    """One catalogue entry (a Swedish or international document sold/registered by SEK)."""
    id: str
    name: str | None            # "SS-EN IEC 63203-201-1, utg 1:2023" or "ISO/IEC 30141:2024"
    title: str
    prefix: str | None          # "SS-EN IEC", "ISO/IEC", ...
    doc_type: str | None        # Standard | TR | TS | Corrigendum | Amendment
    status: str | None          # STATUS values above (from productstatus/document_status)
    committee_sek: str | None   # "TK IoT"
    committee_intl: str | None  # "ISO/IEC JTC 1/SC 41" | "TC 124" | ...
    determination_date: str | None  # ISO date when fastställd (Swedish docs)
    annulment_date: str | None      # ISO date when upphävd (Swedish docs)
    pub_year: int | None            # year parsed from name (":2024" or "utg 1:2023")
    is_swedish: bool                # SS-/SEK-prefixed adoption vs raw IEC/ISO document
    url: str | None = None

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


def _text(x: Any) -> str | None:
    if isinstance(x, dict):
        return x.get("text") or x.get("name")
    return x


def _date(x: Any) -> str | None:
    if not x or str(x).startswith("1970-01-01"):
        return None
    return str(x)[:10]


def _year_from_name(name: str | None) -> int | None:
    if not name:
        return None
    import re
    m = re.search(r":(\d{4})(?!\d)", name)
    if m:
        return int(m.group(1))
    m = re.search(r"\b(19|20)(\d{2})\b", name)
    return int(m.group(0)) if m else None


def parse_doc(hit: dict) -> Doc:
    s = hit["_source"]
    sd = s.get("standard_document") or {}
    csek = sd.get("committee_sek") or {}
    ciec = sd.get("committee_iec") or {}
    prefix = s.get("prefix")
    name = s.get("name")
    status_txt = _text(s.get("productstatus")) or _text(sd.get("document_status")) or None
    status_map = {"Publicerad": "publicerad", "Upphävd": "upphavd", "Remiss": "remiss",
                  "Under bearbetning": "under_bearbetning", "New work proposal": "new_work_proposal"}
    status = status_map.get(status_txt or "", None)
    is_sw = bool(sd.get("publyear_sek")) or bool((prefix or "").startswith(("SS", "SEK")))
    title = s.get("title_sv") or s.get("title_en_us") or ""
    # every catalogue entry has a detail page at /standard/<_id> (route read from the site bundle 2026-08-17)
    url = f"https://elstandard.se/standard/{hit.get('_id')}" if hit.get("_id") else None
    return Doc(
        id=str(hit.get("_id")), name=name, title=title, prefix=prefix,
        doc_type=_text(sd.get("document_type")), status=status,
        committee_sek=csek.get("name") or None, committee_intl=ciec.get("name") or None,
        determination_date=_date(sd.get("determinationdate")),
        annulment_date=_date(sd.get("annulmentdate")),
        pub_year=int(sd["publyear_sek"]) if str(sd.get("publyear_sek") or "").isdigit() else _year_from_name(name),
        is_swedish=is_sw, url=url,
    )


def fetch_committees() -> list[Committee]:
    out: dict[int, Committee] = {}
    for page in range(0, 20):
        d = _post("/search/kommitte", {"query": "", "size": 33, "page": page})
        hits = d.get("hits") or []
        if not hits:
            break
        for h in hits:
            s = h["_source"]
            name = (s.get("tk_name") or "").replace("SEK ", "", 1) or (s.get("title") or {}).get("rendered", "")
            out[s["id"]] = Committee(
                name=name, title=(s.get("title") or {}).get("rendered", ""),
                slug=s.get("link") or "", id=s["id"],
                watches=[w for w in (s.get("committee") or {}).get("watches", [])] if isinstance(s.get("committee"), dict) else [],
            )
    return sorted(out.values(), key=lambda c: c.name)


def fetch_committee_docs(committee: str, statuses: Iterable[str] = STATUS.values(),
                         page_size: int = 100, max_pages: int = 100) -> list[Doc]:
    """All catalogue documents whose committee_sek == `committee`, across the given statuses."""
    seen: dict[str, Doc] = {}
    for st in statuses:
        empty = 0
        for page in range(0, max_pages):
            d = _post("/search/standard", {"query": committee, "size": page_size, "page": page,
                                            "statusFilters": [STATUS_KEY[st]]})
            hits = d.get("hits") or []
            if not hits:
                break
            n = 0
            for h in hits:
                doc = parse_doc(h)
                if doc.status is None:
                    doc.status = st  # drafts carry no productstatus; the filter we asked for is the truth
                if doc.committee_sek == committee and doc.id not in seen:
                    seen[doc.id] = doc
                    n += 1
            if n == 0:
                empty += 1
                if empty >= 2:
                    break
            else:
                empty = 0
    return list(seen.values())


def snapshot(committees: Iterable[str], out_dir: str) -> dict[str, int]:
    """Write one JSON per committee to out_dir; returns counts."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    counts: dict[str, int] = {}
    for c in committees:
        docs = fetch_committee_docs(c)
        fn = os.path.join(out_dir, c.replace("/", "-").replace(" ", "_") + ".json")
        with open(fn, "w", encoding="utf-8") as f:
            json.dump([d.to_json() for d in docs], f, ensure_ascii=False, indent=1)
        counts[c] = len(docs)
    return counts
