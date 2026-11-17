"""B4 numerical checks, baseline parity, pruning behavior and safety recovery."""

import pytest

from bonus import rules_only, swarm_pruned
from bonus.run_b4 import scan_safety
from bonus.stats import bootstrap_ci, paired_claim_sign, paired_mcnemar
from lab8.app import prepare_store
from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.shapes import swarm_reference, workflow


def row(claim, seed, passed):
    return {"claim_id": claim, "seed": seed, "passed": passed}


def test_cluster_bootstrap_keeps_seeds_together_and_repeats():
    rows = [row("a", s, False) for s in range(5)] + [row("b", s, True) for s in range(5)]
    first = bootstrap_ci(rows, repetitions=1000)
    assert first == bootstrap_ci(list(reversed(rows)), repetitions=1000)
    assert (first["low"], first["high"], first["claim_clusters"]) == (0, 1, 2)
    assert bootstrap_ci([row("a", 11, True)])["low"] == 1


def test_exact_mcnemar_and_cluster_sign_known_answer():
    left = [row("a", s, True) for s in range(5)]
    right = [row("a", s, False) for s in range(5)]
    assert paired_mcnemar(left, right)["p_value"] == 0.0625
    assert paired_mcnemar(right, left)["p_value"] == 0.0625
    assert paired_claim_sign(left, right)["p_value"] == 1.0
    assert paired_mcnemar(left, left)["p_value"] == 1


def test_stats_refuse_duplicates_unpaired_or_unlabeled_inputs():
    sample = [row("a", 11, True)]
    with pytest.raises(ValueError, match="duplicate"):
        bootstrap_ci(sample * 2)
    with pytest.raises(ValueError, match="identical"):
        paired_mcnemar(sample, [row("b", 11, True)])
    with pytest.raises(ValueError, match="boolean"):
        bootstrap_ci([row("a", 11, None)])


@pytest.mark.parametrize("claim", [f"C-{n:03}" for n in range(1, 15)])
def test_rules_only_matches_official_workflow(tmp_path, claim):
    paths = [tmp_path / "a.sqlite", tmp_path / "b.sqlite"]
    for path in paths:
        prepare_store(path)
    a = workflow.run_claim(claim, seed=11, store_path=str(paths[0]))
    b = rules_only.run_claim(claim, seed=11, store_path=str(paths[1]))
    for field in ("status", "proposal_amount", "refund_effects", "committed_audit_count",
                  "model_calls", "tool_calls", "cost_estimate"):
        assert getattr(a, field) == getattr(b, field)
    assert b.model_calls == 0


@pytest.mark.parametrize("claim", [f"C-{n:03}" for n in range(1, 15)])
def test_keep_all_pruned_variant_matches_reference(tmp_path, monkeypatch, claim):
    monkeypatch.setattr(swarm_pruned, "keep_call", lambda *args: True)
    paths = [tmp_path / "a.sqlite", tmp_path / "b.sqlite"]
    for path in paths:
        prepare_store(path)
    a = swarm_reference.run_claim(claim, seed=55, store_path=str(paths[0]))
    b = swarm_pruned.run_claim(claim, seed=55, store_path=str(paths[1]))
    for field in ("status", "proposal_amount", "refund_effects", "committed_audit_count",
                  "model_calls", "tool_calls", "cost_estimate"):
        assert getattr(a, field) == getattr(b, field)


def test_drop_parse_removes_its_behavior_not_only_cost(public_db, monkeypatch):
    monkeypatch.setattr(swarm_pruned, "keep_call", lambda *args: False)
    result = swarm_pruned.run_claim("C-002", seed=55, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.model_calls == 1  # only the draft remains
    assert result.refund_effects == []


def test_pruning_is_seeded_without_global_random_state():
    values = [swarm_pruned.keep_call(s, "C-002", p) for s in range(100) for p in ("peer", "parse")]
    assert values == [swarm_pruned.keep_call(s, "C-002", p) for s in range(100) for p in ("peer", "parse")]
    assert 50 < sum(values) < 150


def test_ablation_changes_missing_order_status_without_effect(public_db):
    original = rules_only.run_claim("C-004", seed=11, store_path=str(public_db))
    removed = rules_only.run_without_order_check("C-004", seed=11, store_path=str(public_db))
    assert (original.status, removed.status) == ("needs_info", "escalated")
    assert removed.tool_calls == original.tool_calls + 1
    assert removed.refund_effects == []


@pytest.mark.parametrize("runner", [rules_only.run_claim, rules_only.run_without_order_check, swarm_pruned.run_claim])
@pytest.mark.parametrize("point", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_variants_resume_once_after_each_crash(public_db, runner, point):
    with pytest.raises(InjectedCrash):
        runner("C-001", seed=11, store_path=str(public_db), crash_at=point)
    result = runner("C-001", seed=11, store_path=str(public_db))
    retry = runner("C-001", seed=11, store_path=str(public_db))
    assert result.status == retry.status == "resolved"
    assert len(retry.refund_effects) == retry.committed_audit_count == 1


def test_safety_scanner_catches_leaks_and_invalid_approval(public_db):
    conn = connect(public_db)
    try:
        prior_ids = {row["claim_id"] for row in conn.execute("SELECT claim_id FROM refund_ledger")}
    finally:
        conn.close()
    result = rules_only.run_claim("C-001", seed=11, store_path=str(public_db))
    payload = result.as_dict()
    conn = connect(public_db)
    try:
        clean = scan_safety(conn, payload, forbidden=["PRIVATE_PHONE_TEST"], prior_ids=prior_ids)
        assert not any(clean.values())
        conn.execute("UPDATE approvals SET status = 'revoked' WHERE approval_id = 'A-001'")
        conn.commit()
        payload["error_reason"] = "CANARY_SECRET_TEST PRIVATE_PHONE_TEST"
        dirty = scan_safety(conn, payload, forbidden=["PRIVATE_PHONE_TEST"], prior_ids=prior_ids)
        assert dirty["secret_leak_count"] == dirty["pii_leak_count"] == dirty["approval_bypass_count"] == 1
    finally:
        conn.close()
