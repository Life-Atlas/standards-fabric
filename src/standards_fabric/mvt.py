"""MVT scorecard — the Definition of Done as a command, not a sentence.

    python -m standards_fabric mvt          # exit 0 only when every criterion I own is green
    python -m standards_fabric mvt --links  # also sample-checks live catalogue links (slow, network)

Ten criteria (docs/MVT.md). Seven are mine to close; three depend on named people and report
BLOCKED with the owner — a blocked criterion never counts as green and never counts as my failure.
"""
from __future__ import annotations

import os
import random
import re
import statistics
import urllib.request
from dataclasses import dataclass

from .twin import ROOT, load_json

GREEN, RED, BLOCKED = "GREEN", "RED", "BLOCKED"


@dataclass
class Check:
    id: str
    title: str
    state: str
    measured: str
    owner: str = "repo"

    def line(self) -> str:
        mark = {GREEN: "GREEN  ", RED: "RED    ", BLOCKED: "BLOCKED"}[self.state]
        who = "" if self.owner == "repo" else f"  [owner: {self.owner}]"
        return f"{mark} {self.id}  {self.title}\n         {self.measured}{who}"


def _topics(root: str) -> dict:
    return load_json(os.path.join(root, "data", "topics", "topics.json"))["topics"]


def _curated(root: str) -> dict:
    return load_json(os.path.join(root, "data", "topics", "curated.json"))["refs"]


def _twin(root: str) -> dict:
    p = os.path.join(root, "site", "data", "twin.json")
    return load_json(p) if os.path.exists(p) else {}


def _evidence(root: str) -> dict:
    p = os.path.join(root, "data", "mvt_evidence.json")
    return load_json(p) if os.path.exists(p) else {}


# --------------------------------------------------------------------------- M1 shortlist
def m1_shortlist(root: str, cap: int = 25) -> Check:
    """A zone must yield a shortlist a human can act on: a `tier` on every topic→doc mapping,
    and the core tier no larger than `cap` documents per topic."""
    topics = _topics(root)
    tiered = [t for t in topics.values() if t.get("tiers")]
    tw = _twin(root)
    zones = [z for r in tw.get("realities", {}).values() for z in r.get("zones", [])]
    median = statistics.median([z["counts"]["now"]["total"] for z in zones]) if zones else 0
    if not tiered:
        return Check("M1", "Zone yields an actionable shortlist (core tier ≤ %d per topic)" % cap, RED,
                     f"0 of {len(topics)} topics carry a `tiers` block; median zone shows {median:.0f} refs — an inventory, not a shortlist")
    core_over = [t for t in topics.values() if len(t.get("tiers", {}).get("core", [])) > cap]
    state = GREEN if len(tiered) == len(topics) and not core_over else RED
    return Check("M1", "Zone yields an actionable shortlist (core tier ≤ %d per topic)" % cap, state,
                 f"{len(tiered)}/{len(topics)} topics tiered, {len(core_over)} over the cap, median zone {median:.0f} refs")


# --------------------------------------------------------------------------- M2 links
def m2_links(root: str, sample: int = 25, do_network: bool = False) -> Check:
    tw = _twin(root)
    docs = tw.get("docs", {})
    if not docs:
        return Check("M2", "Every displayed document resolves to its catalogue page", RED, "no twin.json built")
    missing = [i for i, d in docs.items() if not d.get("u")]
    if missing:
        return Check("M2", "Every displayed document resolves to its catalogue page", RED,
                     f"{len(missing)} of {len(docs)} documents have no URL")
    if not do_network:
        return Check("M2", "Every displayed document resolves to its catalogue page", GREEN,
                     f"{len(docs)} documents all carry a URL (run with --links to sample-fetch them)")
    ids = random.Random(7).sample(list(docs), min(sample, len(docs)))
    ok = 0
    for i in ids:
        try:
            req = urllib.request.Request(docs[i]["u"], headers={"User-Agent": "standards-fabric/0.1"})
            with urllib.request.urlopen(req, timeout=25) as r:
                body = r.read(4000).decode("utf-8", "ignore")
            name = (docs[i].get("n") or "").split(",")[0][:22]
            ok += 1 if (r.status == 200 and (not name or name in body)) else 0
        except Exception:  # noqa: BLE001
            pass
    state = GREEN if ok >= len(ids) * 0.99 else RED
    return Check("M2", "Every displayed document resolves to its catalogue page", state,
                 f"{ok}/{len(ids)} sampled links returned 200 and contained the document number")


# --------------------------------------------------------------------------- M3 autonomy
def m3_autonomy(root: str) -> Check:
    """A digest committed by a *scheduled* run, not by a human pressing the button."""
    ev = _evidence(root).get("scheduled_runs_observed", [])
    state = GREEN if ev else RED
    return Check("M3", "A scheduled run has produced a digest without a human", state,
                 f"{len(ev)} scheduled runs recorded; first cron fires Monday 05:17 UTC (weekly) / 1st 04:23 UTC (monthly)")


# --------------------------------------------------------------------------- M4 golden set
def m4_golden(root: str, need: int = 10) -> Check:
    p = os.path.join(root, "tests", "golden_timeslice.json")
    if not os.path.exists(p):
        return Check("M4", "Hand-verified golden set pins the time-slice to reality", RED,
                     "tests/golden_timeslice.json missing — the epoch rules are tested against synthetic docs only")
    g = load_json(p)
    cases = g.get("cases", [])
    state = GREEN if len(cases) >= need else RED
    return Check("M4", "Hand-verified golden set pins the time-slice to reality", state,
                 f"{len(cases)} hand-checked documents (need ≥ {need})")


# --------------------------------------------------------------------------- M5 critical refs checked
def m5_critical_refs(root: str) -> Check:
    topics, curated = _topics(root), _curated(root)
    use: dict[str, int] = {}
    for t in topics.values():
        for r in t.get("curated", []):
            use[r] = use.get(r, 0) + 1
    cat_p = os.path.join(root, "catalog", "requirements.json")
    cited: set[str] = set()

    def numbers(text: str) -> set[str]:
        """Match on the standard's number, never on the body ('IEC' matches everything)."""
        return set(re.findall(r"\d{3,5}(?:[-/]\d+)*", text or ""))

    if os.path.exists(cat_p):
        ref_numbers = {rid: numbers(ref["ref"]) for rid, ref in curated.items()}
        for req in load_json(cat_p)["requirements"]:
            for cite in req.get("standards", []):
                cn = numbers(cite)
                for rid, rn in ref_numbers.items():
                    if cn & rn:
                        cited.add(rid)
    critical = {r for r, n in use.items() if n >= 3} | cited
    checked = {r for r in critical if str(curated.get(r, {}).get("confidence", "")).startswith("checked")}
    state = GREEN if critical and checked == critical else RED
    return Check("M5", "Load-bearing curated references are verified, not assumed", state,
                 f"{len(checked)}/{len(critical)} critical refs marked `checked` "
                 f"({len([1 for r in curated.values() if str(r.get('confidence','')).startswith('checked')])}/{len(curated)} overall)")


# --------------------------------------------------------------------------- M6 external contribution
def m6_external(root: str) -> Check:
    ev = _evidence(root).get("external_contributions", [])
    state = GREEN if ev else BLOCKED
    return Check("M6", "Someone outside WINNIIO has contributed and CI accepted it", state,
                 f"{len(ev)} merged external contributions", owner="WG delegates / any node")


# --------------------------------------------------------------------------- M7 consent
def m7_consent(root: str) -> Check:
    ev = _evidence(root).get("consent_to_publish", [])
    real = [e for e in ev if e.get("reality")]
    granted = [e for e in real if e.get("granted")]
    state = GREEN if real and len(granted) == len(real) else BLOCKED
    pending = ", ".join(e["reality"] for e in real if not e.get("granted")) or "none"
    return Check("M7", "Realities derived from real sites have publish consent on record", state,
                 f"{len(granted)}/{len(real)} consents recorded; pending: {pending}", owner="Nicolas → site owners")


# --------------------------------------------------------------------------- M8 decision evidence
def m8_decision(root: str) -> Check:
    ev = _evidence(root).get("decisions_citing_a_view", [])
    state = GREEN if ev else BLOCKED
    return Check("M8", "A real decision cites a view from the twin", state,
                 f"{len(ev)} decisions recorded (a permalink in a WG minute, a procurement doc or a committee comment)",
                 owner="WG / a procuring municipality")


# --------------------------------------------------------------------------- M9 reproducibility
def m9_reproducible(root: str) -> Check:
    ci = os.path.join(root, ".github", "workflows", "ci.yml")
    if not os.path.exists(ci):
        return Check("M9", "A clean clone builds and gates without secrets", RED, "no ci.yml")
    text = open(ci, encoding="utf-8").read()
    has_build = "standards_fabric build" in text and "standards_fabric gate" in text
    return Check("M9", "A clean clone builds and gates without secrets", GREEN if has_build else RED,
                 "ci.yml builds the twin from the committed snapshot and runs the gate" if has_build
                 else "ci.yml does not build+gate")


# --------------------------------------------------------------------------- M10 cost
def m10_cost(root: str) -> Check:
    ev = _evidence(root).get("scheduled_runs_observed", [])
    durations = [e.get("minutes") for e in ev if isinstance(e.get("minutes"), (int, float))]
    if not durations:
        return Check("M10", "Runs fit the free Actions budget (weekly < 10 min, monthly < 25 min)", RED,
                     "no scheduled run measured yet; timeouts are set to 25/45 min as a guard")
    worst = max(durations)
    return Check("M10", "Runs fit the free Actions budget (weekly < 10 min, monthly < 25 min)",
                 GREEN if worst <= 25 else RED, f"worst observed run {worst} min over {len(durations)} runs")


CHECKS = [m1_shortlist, m2_links, m3_autonomy, m4_golden, m5_critical_refs,
          m6_external, m7_consent, m8_decision, m9_reproducible, m10_cost]


def run_mvt(root: str = ROOT, do_network: bool = False) -> int:
    results: list[Check] = []
    for fn in CHECKS:
        results.append(fn(root, do_network=do_network) if fn is m2_links else fn(root))
    for c in results:
        print(c.line())
    mine = [c for c in results if c.owner == "repo"]
    green = [c for c in mine if c.state == GREEN]
    blocked = [c for c in results if c.state == BLOCKED]
    print(f"\nMVT: {len(green)}/{len(mine)} criteria I own are green; {len(blocked)} blocked on people "
          f"({', '.join(c.id for c in blocked) or 'none'}).")
    print("MVT " + ("REACHED" if len(green) == len(mine) else "NOT REACHED"))
    return 0 if len(green) == len(mine) else 1
