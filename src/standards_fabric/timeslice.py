"""Time-slicing: which documents were / are / will be applicable in a given epoch.

Three epochs are the product's spine:  T-10 (past)  ·  T0 (now)  ·  T+10 (future).

Rules (each one is testable and has a failing fixture in tests/test_timeslice.py):

  past(year)   Swedish doc  : determination_date <= year-12-31 and (no annulment or annulment > year-12-31)
               intl doc     : pub_year <= year and status in {publicerad, upphavd}   [heuristic: we do not
                              know when an international document was withdrawn, so a 2013 edition that is
                              withdrawn today is assumed to have been in force in 2016]
  now          status == publicerad and no annulment
  future       now  +  {remiss, under_bearbetning, new_work_proposal}   [the pipeline]
               plus a flag `aging` on documents published >= 10 years before the future epoch and never
               revised (IEC's own stability-date rhythm is 3-12 years; >10 years without a new edition means
               "expect a revision or a withdrawal")

`basis` on every verdict tells the reader which rule fired, so an ASSUMED heuristic can never look like
a VERIFIED date.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .sek_client import Doc

PAST_LABEL, NOW_LABEL, FUTURE_LABEL = "past", "now", "future"


@dataclass(frozen=True)
class Verdict:
    applies: bool
    basis: str          # "sek-dates" | "name-year-heuristic" | "status" | "pipeline" | "n/a"
    aging: bool = False


def _year_end(year: int) -> str:
    return f"{year}-12-31"


def in_force_at(doc: Doc, year: int) -> Verdict:
    """Was `doc` in force at the end of `year`? Uses SEK dates when present, else a name-year heuristic."""
    if doc.is_swedish and doc.determination_date:
        ok = doc.determination_date <= _year_end(year) and (
            doc.annulment_date is None or doc.annulment_date > _year_end(year))
        return Verdict(ok, "sek-dates")
    if doc.pub_year and doc.status in ("publicerad", "upphavd"):
        return Verdict(doc.pub_year <= year, "name-year-heuristic")
    return Verdict(False, "n/a")


def is_now(doc: Doc) -> Verdict:
    ok = doc.status == "publicerad" and doc.annulment_date is None
    return Verdict(ok, "status")


def is_pipeline(doc: Doc) -> Verdict:
    return Verdict(doc.status in ("remiss", "under_bearbetning", "new_work_proposal"), "pipeline")


def is_aging(doc: Doc, future_year: int, horizon: int = 10) -> bool:
    return bool(doc.pub_year) and doc.status == "publicerad" and (future_year - doc.pub_year) >= horizon + 10


def classify(doc: Doc, past_year: int, now_year: int, future_year: int) -> dict[str, Verdict]:
    """Return {'past': Verdict, 'now': Verdict, 'future': Verdict} for one document."""
    past = in_force_at(doc, past_year)
    now = is_now(doc)
    pipe = is_pipeline(doc)
    future = Verdict(now.applies or pipe.applies,
                     "pipeline" if pipe.applies else ("status" if now.applies else "n/a"),
                     aging=is_aging(doc, future_year))
    return {PAST_LABEL: past, NOW_LABEL: now, FUTURE_LABEL: future}


def slice_docs(docs: Iterable[Doc], past_year: int, now_year: int, future_year: int) -> dict[str, list[dict]]:
    """Bucket documents into the three epochs; every entry carries its basis."""
    out: dict[str, list[dict]] = {PAST_LABEL: [], NOW_LABEL: [], FUTURE_LABEL: []}
    for d in docs:
        v = classify(d, past_year, now_year, future_year)
        for label, verdict in v.items():
            if verdict.applies:
                entry = d.to_json()
                entry["basis"] = verdict.basis
                if label == FUTURE_LABEL:
                    entry["aging"] = verdict.aging
                    entry["pipeline"] = d.status in ("remiss", "under_bearbetning", "new_work_proposal")
                out[label].append(entry)
    return out
