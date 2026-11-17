"""Check the ablation changes read work without changing the refund effect."""

import pytest

from bonus.investigator_ablation import run_claim
from lab8.app import prepare_store
from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.shapes import orchestrator


def test_second_investigator_preserves_decision_and_retry(tmp_path):
    baseline_store = tmp_path / "baseline.sqlite"
    variant_store = tmp_path / "variant.sqlite"
    prepare_store(baseline_store)
    prepare_store(variant_store)
    baseline = orchestrator.run_claim("C-001", seed=11, store_path=str(baseline_store))
    original_runner = orchestrator.run_readonly_investigators
    variant = run_claim("C-001", seed=11, store_path=str(variant_store))
    assert orchestrator.run_readonly_investigators is original_runner
    assert (variant.status, variant.proposal_amount) == (baseline.status, baseline.proposal_amount)
    assert variant.tool_calls == baseline.tool_calls + 4
    assert variant.cost_estimate == pytest.approx(baseline.cost_estimate + 40)
    assert variant.run_id != baseline.run_id
    run_claim("C-001", seed=11, store_path=str(variant_store))
    conn = connect(variant_store)
    try:
        assert get_refund(conn, "C-001")["amount_vnd"] == 35000
        assert committed_audit_count(conn, "C-001") == 1
    finally:
        conn.close()


def test_variant_propagates_crash_and_restores_runner(public_db):
    original_runner = orchestrator.run_readonly_investigators
    with pytest.raises(InjectedCrash):
        run_claim("C-001", seed=11, store_path=str(public_db), crash_at="after_effect_before_checkpoint")
    assert orchestrator.run_readonly_investigators is original_runner
    resumed = run_claim("C-001", seed=11, store_path=str(public_db))
    assert resumed.status == "resolved"
    assert resumed.committed_audit_count == 1
