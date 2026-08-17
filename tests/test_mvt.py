"""The MVT scorecard must be able to say no — and must not say yes for the wrong reason.

Every criterion gets a fixture that makes it green and a mutation that makes it red/blocked.
"""
import json
import os

import pytest

from standards_fabric.mvt import BLOCKED, GREEN, RED, m1_shortlist, m4_golden, m5_critical_refs, m7_consent, run_mvt
from standards_fabric.twin import ROOT


@pytest.fixture
def repo(tmp_path):
    """A fixture where every criterion I own is green."""
    for d in ("data/topics", "site/data", "tests", ".github/workflows", "catalog"):
        os.makedirs(tmp_path / d, exist_ok=True)
    topics = {"topics": {"t1": {"label": "T1", "sek": [], "intl": [], "curated": ["r1"],
                                "tiers": {"core": ["a", "b"], "context": ["c"]}}}}
    (tmp_path / "data/topics/topics.json").write_text(json.dumps(topics), encoding="utf-8")
    curated = {"refs": {"r1": {"ref": "IEC 60909-0", "title": "t", "body": "b", "kind": "standard",
                               "epochs": {"past": "in-force", "now": "in-force", "future": "in-force"},
                               "confidence": "checked 2026-08-17"}}}
    (tmp_path / "data/topics/curated.json").write_text(json.dumps(curated), encoding="utf-8")
    (tmp_path / "catalog/requirements.json").write_text(json.dumps({"requirements": [
        {"id": "X-1", "text": "t", "standards": ["IEC 60909-0"]}]}), encoding="utf-8")
    twin = {"realities": {"a": {"zones": [{"id": "z", "counts": {"now": {"total": 12}}}]}},
            "docs": {"d1": {"n": "SS-EN 1", "u": "https://elstandard.se/standard/1"}}}
    (tmp_path / "site/data/twin.json").write_text(json.dumps(twin), encoding="utf-8")
    (tmp_path / "tests/golden_timeslice.json").write_text(json.dumps(
        {"cases": [{"id": str(i)} for i in range(10)]}), encoding="utf-8")
    (tmp_path / ".github/workflows/ci.yml").write_text(
        "run: python -m standards_fabric build && python -m standards_fabric gate", encoding="utf-8")
    (tmp_path / "data/mvt_evidence.json").write_text(json.dumps({
        "consent_to_publish": [{"reality": "a", "granted": "2026-08-18", "evidence": "mail"}],
        "external_contributions": [{"pr": 1}],
        "decisions_citing_a_view": [{"doc": "minute"}],
        "scheduled_runs_observed": [{"run": 1, "minutes": 6}]}), encoding="utf-8")
    return tmp_path


def test_mvt_reached_on_complete_fixture(repo):
    assert run_mvt(str(repo)) == 0


def test_m1_red_without_tiers(repo):
    t = json.loads((repo / "data/topics/topics.json").read_text(encoding="utf-8"))
    del t["topics"]["t1"]["tiers"]
    (repo / "data/topics/topics.json").write_text(json.dumps(t), encoding="utf-8")
    assert m1_shortlist(str(repo)).state == RED
    assert run_mvt(str(repo)) == 1


def test_m1_red_when_core_tier_too_big(repo):
    t = json.loads((repo / "data/topics/topics.json").read_text(encoding="utf-8"))
    t["topics"]["t1"]["tiers"]["core"] = [str(i) for i in range(40)]
    (repo / "data/topics/topics.json").write_text(json.dumps(t), encoding="utf-8")
    assert m1_shortlist(str(repo)).state == RED


def test_m4_red_when_golden_set_too_small(repo):
    (repo / "tests/golden_timeslice.json").write_text(json.dumps({"cases": [{"id": "1"}]}), encoding="utf-8")
    assert m4_golden(str(repo)).state == RED


def test_m5_red_when_a_cited_reference_is_only_assumed(repo):
    c = json.loads((repo / "data/topics/curated.json").read_text(encoding="utf-8"))
    c["refs"]["r1"]["confidence"] = "assumed"
    (repo / "data/topics/curated.json").write_text(json.dumps(c), encoding="utf-8")
    assert m5_critical_refs(str(repo)).state == RED


def test_m5_matches_on_the_number_not_the_body(repo):
    """'IEC' must not make every reference critical — the bug this check shipped with."""
    c = json.loads((repo / "data/topics/curated.json").read_text(encoding="utf-8"))
    c["refs"]["unrelated"] = {"ref": "IEC 12345678-9", "title": "t", "body": "b", "kind": "standard",
                              "epochs": {"past": "absent", "now": "in-force", "future": "in-force"},
                              "confidence": "assumed"}
    (repo / "data/topics/curated.json").write_text(json.dumps(c), encoding="utf-8")
    assert m5_critical_refs(str(repo)).state == GREEN  # the assumed one is not cited, so it is not critical


def test_m7_blocked_without_consent(repo):
    e = json.loads((repo / "data/mvt_evidence.json").read_text(encoding="utf-8"))
    e["consent_to_publish"][0]["granted"] = None
    (repo / "data/mvt_evidence.json").write_text(json.dumps(e), encoding="utf-8")
    assert m7_consent(str(repo)).state == BLOCKED


def test_blocked_criteria_do_not_fail_the_run(repo):
    """Blocked-on-humans criteria are reported, never counted as my failure."""
    e = json.loads((repo / "data/mvt_evidence.json").read_text(encoding="utf-8"))
    e["external_contributions"] = []
    e["decisions_citing_a_view"] = []
    (repo / "data/mvt_evidence.json").write_text(json.dumps(e), encoding="utf-8")
    assert run_mvt(str(repo)) == 0


def test_real_repo_is_not_mvt_yet():
    """Today's honest state — this test flips when the MVT is actually reached."""
    assert run_mvt(ROOT) == 1
