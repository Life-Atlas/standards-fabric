"""Time-slice rules. Each rule has a fixture that passes AND a mutation that must make it fail
(see rules/kontroller-maste-kunna-saga-nej: a check that has never said no is not a check)."""
from standards_fabric.sek_client import Doc
from standards_fabric.timeslice import classify, in_force_at, is_aging, is_now, is_pipeline


def mk(**kw) -> Doc:
    base = dict(id="x", name="SS-EN 60974-6, utg 3:2016", title="t", prefix="SS-EN", doc_type="Standard",
                status="publicerad", committee_sek="TK 26", committee_intl="TC 26",
                determination_date="2016-05-01", annulment_date=None, pub_year=2016, is_swedish=True, url=None)
    base.update(kw)
    return Doc(**base)


def test_swedish_doc_in_force_at_past_year_uses_sek_dates():
    d = mk()
    v = in_force_at(d, 2016)
    assert v.applies and v.basis == "sek-dates"


def test_swedish_doc_determined_after_past_year_is_not_past():
    d = mk(determination_date="2017-03-01", pub_year=2017)
    assert not in_force_at(d, 2016).applies


def test_swedish_doc_withdrawn_before_past_year_end_is_not_past():
    d = mk(determination_date="2010-01-01", annulment_date="2015-06-01", status="upphavd")
    assert not in_force_at(d, 2016).applies
    # mutation: withdrawn AFTER the epoch → must be past
    assert in_force_at(mk(determination_date="2010-01-01", annulment_date="2018-06-01", status="upphavd"), 2016).applies


def test_international_doc_uses_name_year_heuristic():
    d = mk(name="ISO/IEC 30141:2018", prefix="ISO/IEC", is_swedish=False, determination_date=None, pub_year=2018)
    assert not in_force_at(d, 2016).applies
    v = in_force_at(mk(name="ISO/IEC 29182-1:2013", prefix="ISO/IEC", is_swedish=False, determination_date=None, pub_year=2013), 2016)
    assert v.applies and v.basis == "name-year-heuristic"


def test_now_requires_published_and_not_annulled():
    assert is_now(mk()).applies
    assert not is_now(mk(status="upphavd")).applies
    assert not is_now(mk(annulment_date="2025-01-01")).applies


def test_pipeline_statuses():
    for s in ("remiss", "under_bearbetning", "new_work_proposal"):
        assert is_pipeline(mk(status=s)).applies
    assert not is_pipeline(mk(status="publicerad")).applies


def test_future_is_now_plus_pipeline_and_flags_aging():
    v = classify(mk(status="remiss", pub_year=None), 2016, 2026, 2036)
    assert v["future"].applies and v["future"].basis == "pipeline"
    old = classify(mk(pub_year=2010, determination_date="2010-01-01"), 2016, 2026, 2036)
    assert old["future"].applies and old["future"].aging is True
    fresh = classify(mk(pub_year=2024, determination_date="2024-01-01"), 2016, 2026, 2036)
    assert fresh["future"].aging is False


def test_aging_threshold_is_twenty_years_before_future_epoch():
    assert is_aging(mk(pub_year=2016), 2036)
    assert not is_aging(mk(pub_year=2017), 2036)
