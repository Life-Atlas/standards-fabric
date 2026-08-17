"""Runs the agents for a cadence and writes reports/<cadence>/<YYYY-Www or YYYY-MM>/report.md (+ findings.json).

weekly  : standards_watch (watchlist refresh) · platforms_overview · eu_monitor · county_iot · municipal_iot
monthly : all of the above + procurement_catalog + options_radar, and the twin is rebuilt from a full snapshot by CI.

Deterministic first. If SF_LLM is set, an editorial summary is prepended — clearly marked as model-written.
"""
from __future__ import annotations

import json
import os
from datetime import date

from .. import twin
from . import activities, radar
from .base import AgentResult
from .llm import summarise

REPORTS = os.path.join(twin.ROOT, "reports")


def period_id(cadence: str, d: date | None = None) -> str:
    d = d or date.today()
    if cadence == "weekly":
        y, w, _ = d.isocalendar()
        return f"{y}-W{w:02d}"
    return f"{d.year}-{d.month:02d}"


def run(cadence: str = "weekly", use_llm: bool = True, refresh_sek: bool = True) -> int:
    results: list[AgentResult] = []
    results.append(activities.standards_watch(refresh=refresh_sek))
    results.append(activities.platforms_overview())
    results.append(activities.eu_monitor())
    results.append(activities.county_iot())
    results.append(activities.municipal_iot())
    if cadence == "monthly":
        results.append(activities.procurement_catalog())
        results.append(radar.options_radar())
    pid = period_id(cadence)
    out_dir = os.path.join(REPORTS, cadence, pid)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "findings.json"), "w", encoding="utf-8") as f:
        json.dump({"period": pid, "cadence": cadence, "generated": date.today().isoformat(),
                   "agents": [r.to_json() for r in results]}, f, ensure_ascii=False, indent=1)
    md = render_markdown(results, cadence, pid)
    summary = None
    if use_llm:
        try:
            summary = summarise(md, cadence)
        except Exception as e:  # noqa: BLE001
            summary = None
            md += f"\n\n> LLM summary skipped: {e}\n"
    if summary:
        md = f"> **Redaktionell sammanfattning (modellskriven, SF_LLM={os.environ.get('SF_LLM')})**\n\n{summary}\n\n---\n\n" + md
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write(md)
    # rolling "latest" pointer for the site
    with open(os.path.join(REPORTS, cadence, "LATEST.md"), "w", encoding="utf-8") as f:
        f.write(md)
    total = sum(len(r.findings) for r in results)
    errs = sum(len(r.errors) for r in results)
    print(f"{cadence} {pid}: {total} findings, {errs} source errors → {out_dir}")
    return 0


def render_markdown(results: list[AgentResult], cadence: str, pid: str) -> str:
    lines = [f"# Standards & Platforms digest — {cadence} {pid}", "",
             f"Generated {date.today().isoformat()} by standards-fabric. Every line below has a source URL; nothing here is inferred.", ""]
    for r in results:
        lines.append(f"## {r.activity} — `{r.name}` ({len(r.findings)} findings)")
        if r.stats:
            lines.append("_" + ", ".join(f"{k}: {v}" for k, v in r.stats.items()) + "_")
        if r.errors:
            lines.append("")
            lines.append("**Källor som inte svarade:** " + "; ".join(r.errors))
        lines.append("")
        if not r.findings:
            lines.append("Inget nytt denna period.")
        by_kind: dict[str, list] = {}
        for f in r.findings:
            by_kind.setdefault(f.kind, []).append(f)
        for kind, fs in by_kind.items():
            lines.append(f"### {kind} ({len(fs)})")
            for f in fs[:80]:
                d = f" · {f.date}" if f.date else ""
                tags = f" · _{', '.join(t for t in f.tags if t)}_" if f.tags else ""
                det = f" — {f.detail}" if f.detail else ""
                lines.append(f"- {f.title}{d}{tags}{det} ([source]({f.source}))")
            if len(fs) > 80:
                lines.append(f"- … {len(fs) - 80} more in findings.json")
            lines.append("")
    return "\n".join(lines)
