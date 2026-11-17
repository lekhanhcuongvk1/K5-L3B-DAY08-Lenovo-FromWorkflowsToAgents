"""CP5 controlled ablation: enable one extra, identical read-only investigation.

Uses the official orchestrator unchanged. Scoped patches are restored on exit;
run this variant sequentially, as the lab benchmark does (not in threads).
This is research-card evidence, not a claim for bonus marks.
"""

from dataclasses import replace
from unittest.mock import patch

from lab8.schemas import make_run_id
from lab8.shapes import orchestrator


def run_claim(claim_id, *, seed, store_path, crash_at=None):
    original = orchestrator.run_readonly_investigators

    def two_investigations(conn, budget, handoff, principal_id):
        first = original(conn, budget, handoff, principal_id)
        second = original(conn, budget, handoff, principal_id)
        if first != second:
            raise ValueError("read-only investigators disagreed on the same snapshot")
        return first

    variant = "orchestrator_two"
    with patch.object(orchestrator, "run_readonly_investigators", two_investigations), patch.object(
        orchestrator, "make_run_id", lambda shape, claim, value: make_run_id(variant, claim, value)
    ):
        result = orchestrator.run_claim(
            claim_id, seed=seed, store_path=store_path, crash_at=crash_at
        )
    return replace(result, shape=variant)
