"""The six consortium activities as agents (+ the options radar in radar.py).

Each agent: collect deterministically → Findings with source URLs. No agent invents a fact; when a source fails,
the failure is recorded in AgentResult.errors and shown in the report ("Källa X svarade inte").
"""
from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request

from .. import twin
from .base import AgentResult, Finding, http_get, keyword_hit, load_state, rss_items, save_state, today

SOURCES = twin.load_json(os.path.join(twin.DATA, "sources", "sources.json"))
STATE_DIR = os.path.join(twin.ROOT, "reports", "state")
KW = SOURCES["keywords"]["iot"]


# ---------------------------------------------------------------- 1. Standardisation ---------------------------
def standards_watch(refresh: bool = True) -> AgentResult:
    """Diff the SEK catalogue for the watchlist committees against the last run."""
    from ..sek_client import fetch_committee_docs
    name = "standards_watch"
    state_path = os.path.join(STATE_DIR, "sek_baseline.json")
    baseline = load_state(state_path)  # {doc_id: {"status":..., "name":..., "committee":...}}
    findings: list[Finding] = []
    errors: list[str] = []
    current: dict[str, dict] = {}
    for c in SOURCES["sek_watchlist"]:
        try:
            docs = fetch_committee_docs(c) if refresh else twin.load_committee_docs(c)
        except Exception as e:  # noqa: BLE001
            errors.append(f"SEK API failed for {c}: {e}")
            continue
        for d in docs:
            current[d.id] = {"status": d.status, "name": d.name, "committee": d.committee_sek, "title": d.title,
                             "url": d.url, "intl": d.committee_intl}
    first_run = not baseline
    for did, d in current.items():
        old = baseline.get(did)
        label = d["name"] or f"(draft) {d['title']}"
        src = d["url"] or "https://elstandard.se/sok?query=" + urllib.parse.quote(d["committee"] or "")
        if old is None:
            if first_run:
                continue  # baseline run: nothing is "new"
            kind = {"remiss": "remiss", "new_work_proposal": "nwp", "publicerad": "new-doc"}.get(d["status"] or "", "new-doc")
            findings.append(Finding(name, kind, f"{label} — {d['status']}", src, today(), d["title"] or "", [d["committee"] or "", d["intl"] or ""]))
        elif old.get("status") != d["status"]:
            findings.append(Finding(name, "status-change", f"{label}: {old.get('status')} → {d['status']}", src, today(), d["title"] or "", [d["committee"] or ""]))
    for did, old in baseline.items():
        if did not in current and old.get("committee") in SOURCES["sek_watchlist"]:
            findings.append(Finding(name, "withdrawn", f"{old.get('name') or old.get('title')} — no longer in catalogue", "https://elstandard.se/", today(), "", [old.get("committee") or ""]))
    # SEK newsroom
    for f in SOURCES["feeds"]:
        if f["activity"] != "standardisation" or f.get("disabled"):
            continue
        try:
            seen = load_state(os.path.join(STATE_DIR, f"feed_{f['id']}.json"))
            for it in rss_items(f["url"]):
                if it["link"] in seen:
                    continue
                seen[it["link"]] = today()
                findings.append(Finding(name, "news", it["title"], it["link"], it["date"], it["summary"][:240], ["SEK"]))
            save_state(os.path.join(STATE_DIR, f"feed_{f['id']}.json"), seen)
        except Exception as e:  # noqa: BLE001
            errors.append(f"feed {f['id']} failed: {e}")
    if current:
        save_state(state_path, current)
    stats = {"watchlist": len(SOURCES["sek_watchlist"]), "docs_tracked": len(current), "baseline_run": first_run,
             "pipeline_open": sum(1 for d in current.values() if d["status"] in ("remiss", "new_work_proposal", "under_bearbetning"))}
    return AgentResult(name, "Standardisation", findings, stats, errors)


# ---------------------------------------------------------------- 2. Standards & Platforms working group ------
def platforms_overview() -> AgentResult:
    name = "platforms_overview"
    findings: list[Finding] = []
    errors: list[str] = []
    seen_path = os.path.join(STATE_DIR, "github_releases.json")
    seen = load_state(seen_path)
    for g in SOURCES["github_releases"]:
        url = f"https://github.com/{g['repo']}/releases.atom"
        try:
            items = rss_items(url, limit=5)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{g['repo']}: {e}")
            continue
        for it in items:
            if it["link"] in seen:
                continue
            seen[it["link"]] = today()
            findings.append(Finding(name, "market", f"{g['repo']} — {it['title']}", it["link"], it["date"], g.get("note", ""), ["platform"]))
    save_state(seen_path, seen)
    return AgentResult(name, "Standards & Platforms working group", findings, {"repos": len(SOURCES["github_releases"])}, errors)


# ---------------------------------------------------------------- 3. EU engagement and monitoring -------------
def eu_monitor() -> AgentResult:
    name = "eu_monitor"
    findings: list[Finding] = []
    errors: list[str] = []
    for f in SOURCES["feeds"]:
        if f["activity"] != "eu":
            continue
        try:
            path = os.path.join(STATE_DIR, f"feed_{f['id']}.json")
            seen = load_state(path)
            for it in rss_items(f["url"], limit=60):
                if it["link"] in seen:
                    continue
                hits = keyword_hit(it["title"] + " " + it["summary"], KW)
                seen[it["link"]] = today()
                if hits:
                    findings.append(Finding(name, "eu-act", it["title"], it["link"], it["date"], it["summary"][:240], hits))
            save_state(path, seen)
        except Exception as e:  # noqa: BLE001
            errors.append(f"feed {f['id']} failed: {e}")
    # Funding & Tenders portal — open topics
    fund = SOURCES["eu_funding"]
    seen_path = os.path.join(STATE_DIR, "eu_funding.json")
    seen = load_state(seen_path)
    for q in fund["queries"]:
        try:
            url = fund["api"] + "&text=" + urllib.parse.quote(q) + "&pageSize=20&pageNumber=1"
            body = json.dumps({"bool": {"must": [{"terms": {"type": ["1", "2", "8"]}}, {"terms": {"status": ["31094501", "31094502"]}}]}}).encode()
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "standards-fabric/0.1"})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.load(r)
            for res in d.get("results", []):
                meta = res.get("metadata", {}) or {}
                ident = (meta.get("identifier") or [res.get("reference")])[0]
                if ident in seen:
                    continue
                seen[ident] = today()
                title = (meta.get("title") or [res.get("title") or ident])[0]
                deadline = (meta.get("deadlineDate") or [""])[0]
                status = (meta.get("status") or [""])[0]
                link = "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/" + str(ident).lower()
                findings.append(Finding(name, "funding-call", f"{ident}: {title}", link, deadline[:10] if deadline else None, f"status {status}; query '{q}'", ["funding"]))
        except Exception as e:  # noqa: BLE001
            errors.append(f"funding query '{q}' failed: {e}")
    save_state(seen_path, seen)
    return AgentResult(name, "EU engagement and monitoring", findings, {"queries": len(fund["queries"])}, errors)


# ---------------------------------------------------------------- 4. County-wide IoT --------------------------
def county_iot() -> AgentResult:
    name = "county_iot"
    findings: list[Finding] = []
    errors: list[str] = []
    ted = SOURCES["ted"]
    seen_path = os.path.join(STATE_DIR, "ted.json")
    seen = load_state(seen_path)
    try:
        terms = " OR ".join(f'"{t}"' for t in ted["terms"])
        q = f'buyer-country={ted["country"]} AND (notice-title ~ ({terms}) OR description-proc ~ ({terms}))'
        body = json.dumps({"query": q, "fields": ["publication-number", "notice-title", "publication-date", "buyer-name", "links"], "limit": 25, "scope": "ALL"}).encode()
        req = urllib.request.Request(ted["api"], data=body, headers={"Content-Type": "application/json", "User-Agent": "standards-fabric/0.1"})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
        for n in d.get("notices", []):
            pn = n.get("publication-number")
            if pn in seen:
                continue
            seen[pn] = today()
            t = n.get("notice-title") or {}
            title = t.get("swe") or t.get("eng") or next(iter(t.values()), pn) if isinstance(t, dict) else str(t)
            link = f"https://ted.europa.eu/en/notice/-/detail/{pn}"
            buyer = n.get("buyer-name")
            findings.append(Finding(name, "procurement", f"{title} — {buyer if isinstance(buyer, str) else ''}", link, n.get("publication-date"), "", ["TED", "SWE"]))
        stats = {"ted_total": d.get("totalNoticeCount", 0)}
    except Exception as e:  # noqa: BLE001
        errors.append(f"TED query failed: {e}")
        stats = {}
    save_state(seen_path, seen)
    for f in SOURCES["feeds"]:
        if f["activity"] != "county":
            continue
        try:
            path = os.path.join(STATE_DIR, f"feed_{f['id']}.json")
            s2 = load_state(path)
            for it in rss_items(f["url"], limit=40):
                if it["link"] in s2:
                    continue
                s2[it["link"]] = today()
                hits = keyword_hit(it["title"] + " " + it["summary"], KW + ["kommun", "region", "län"])
                if hits:
                    findings.append(Finding(name, "note", it["title"], it["link"], it["date"], it["summary"][:240], hits))
            save_state(path, s2)
        except Exception as e:  # noqa: BLE001
            errors.append(f"feed {f['id']} failed: {e}")
    return AgentResult(name, "County-wide IoT", findings, stats, errors)


# ---------------------------------------------------------------- 5. Framework agreement procurement ----------
def procurement_catalog() -> AgentResult:
    """Check every standard referenced by the requirements catalogue against the SEK snapshot."""
    name = "procurement_catalog"
    cat_path = os.path.join(twin.ROOT, "catalog", "requirements.json")
    cat = twin.load_json(cat_path)
    findings: list[Finding] = []
    errors: list[str] = []
    # index snapshot by normalised number ("SS-EN IEC 62443-3-3" → "62443-3-3")
    index: dict[str, list[dict]] = {}
    for c in twin.committees_needed(twin.load_topics()[0]):
        for d in twin.load_committee_docs(c):
            key = _num(d.name)
            if key:
                index.setdefault(key, []).append(d.to_json())
    checked = 0
    for req in cat["requirements"]:
        for ref in req.get("standards", []):
            key = _num(ref)
            checked += 1
            docs = index.get(key or "", [])
            if not docs:
                findings.append(Finding(name, "note", f"{req['id']}: {ref} not found in SEK catalogue snapshot (non-electrotechnical or check number)", cat_path, today(), req["text"], ["catalog", "unresolved"]))
                continue
            pub = [d for d in docs if d["status"] == "publicerad"]
            latest = max((d.get("pub_year") or 0) for d in docs)
            if not pub:
                findings.append(Finding(name, "withdrawn", f"{req['id']}: {ref} — every edition in the catalogue is withdrawn or draft", docs[0].get("url") or cat_path, today(), req["text"], ["catalog", "withdrawn"]))
            elif latest and (2026 - latest) >= 10:
                findings.append(Finding(name, "note", f"{req['id']}: {ref} — latest edition {latest}, older than 10 years", pub[0].get("url") or cat_path, today(), req["text"], ["catalog", "aging"]))
            pipeline = [d for d in docs if d["status"] in ("remiss", "new_work_proposal", "under_bearbetning")]
            if pipeline:
                findings.append(Finding(name, "remiss", f"{req['id']}: {ref} — a new edition is in the pipeline ({pipeline[0]['status']})", pipeline[0].get("url") or cat_path, today(), req["text"], ["catalog", "pipeline"]))
    return AgentResult(name, "Framework agreement procurement", findings, {"requirements": len(cat["requirements"]), "references_checked": checked}, errors)


def _num(name: str | None) -> str | None:
    if not name:
        return None
    m = re.search(r"(\d{4,5}(?:-\d+)*)", name)
    return m.group(1) if m else None


# ---------------------------------------------------------------- 6. Municipal IoT ----------------------------
def municipal_iot() -> AgentResult:
    name = "municipal_iot"
    findings: list[Finding] = []
    errors: list[str] = []
    for f in SOURCES["feeds"]:
        if f["activity"] != "municipal":
            continue
        try:
            path = os.path.join(STATE_DIR, f"feed_{f['id']}.json")
            seen = load_state(path)
            for it in rss_items(f["url"], limit=40):
                if it["link"] in seen:
                    continue
                seen[it["link"]] = today()
                findings.append(Finding(name, "note", it["title"], it["link"], it["date"], it["summary"][:240], ["OASC"]))
            save_state(path, seen)
        except Exception as e:  # noqa: BLE001
            errors.append(f"feed {f['id']} failed: {e}")
    # playbook link check: every URL in the municipal playbook must answer
    pb = os.path.join(twin.ROOT, "docs", "playbooks", "municipal-iot.md")
    if os.path.exists(pb):
        urls = sorted(set(re.findall(r"https?://[^\s)>\]]+", open(pb, encoding="utf-8").read())))
        dead = []
        for u in urls[:40]:
            try:
                http_get(u, timeout=20)
            except Exception:  # noqa: BLE001
                dead.append(u)
        for u in dead:
            findings.append(Finding(name, "note", f"Playbook link not answering: {u}", u, today(), "", ["playbook", "dead-link"]))
    return AgentResult(name, "Municipal IoT", findings, {}, errors)
