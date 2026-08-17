"""The gate must be able to say no. We copy the repo skeleton into a temp dir, prove GREEN, then break one thing
per check and prove RED. G6 is exercised with a README that states a wrong number."""
import json
import os
import shutil

import pytest

from standards_fabric.gate import run_gate
from standards_fabric.twin import ROOT


@pytest.fixture
def repo(tmp_path):
    for d in ("data/topics", "data/realities", "site/data", "reports/weekly/2026-W01"):
        os.makedirs(tmp_path / d, exist_ok=True)
    shutil.copy(os.path.join(ROOT, "data", "topics", "topics.json"), tmp_path / "data/topics/topics.json")
    shutil.copy(os.path.join(ROOT, "data", "topics", "curated.json"), tmp_path / "data/topics/curated.json")
    (tmp_path / "data/realities/a.json").write_text("{}", encoding="utf-8")
    (tmp_path / "site/index.html").write_text("<script>const DATA = {\"x\":1};</script>", encoding="utf-8")
    twin = {"realities": {"a": {"zones": [{"id": "z", "counts": {"past": {}, "now": {}, "future": {}}}], "missing_topics": []}}}
    (tmp_path / "site/data/twin.json").write_text(json.dumps(twin), encoding="utf-8")
    (tmp_path / "reports/weekly/LATEST.md").write_text("# Standards & Platforms digest — weekly 2026-W01\n", encoding="utf-8")
    (tmp_path / "reports/weekly/2026-W01/findings.json").write_text(json.dumps({"agents": [{"name": "x", "findings": [{"title": "t", "source": "https://e.x"}]}]}), encoding="utf-8")
    import json as _json
    n_topics = len(_json.loads((tmp_path / "data/topics/topics.json").read_text(encoding="utf-8"))["topics"])
    (tmp_path / "README.md").write_text(f"**1** realities, **{n_topics}** topics", encoding="utf-8")
    return tmp_path


def test_gate_green_on_clean_fixture(repo):
    assert run_gate(str(repo)) == 0


def test_gate_red_when_data_not_embedded(repo):
    (repo / "site/index.html").write_text("<script>const DATA = /*__DATA__*/null;</script>", encoding="utf-8")
    assert run_gate(str(repo)) == 1


def test_gate_red_on_missing_topics(repo):
    twin = json.loads((repo / "site/data/twin.json").read_text(encoding="utf-8"))
    twin["realities"]["a"]["missing_topics"] = ["ghost"]
    (repo / "site/data/twin.json").write_text(json.dumps(twin), encoding="utf-8")
    assert run_gate(str(repo)) == 1


def test_gate_red_on_unknown_curated_ref(repo):
    p = repo / "data/topics/topics.json"
    t = json.loads(p.read_text(encoding="utf-8"))
    next(iter(t["topics"].values()))["curated"].append("does-not-exist")
    p.write_text(json.dumps(t), encoding="utf-8")
    assert run_gate(str(repo)) == 1


def test_gate_red_when_finding_lacks_source(repo):
    (repo / "reports/weekly/2026-W01/findings.json").write_text(json.dumps({"agents": [{"name": "x", "findings": [{"title": "t", "source": ""}]}]}), encoding="utf-8")
    assert run_gate(str(repo)) == 1


def test_gate_red_when_readme_number_is_wrong(repo):
    (repo / "README.md").write_text("**7** realities", encoding="utf-8")
    assert run_gate(str(repo)) == 1
