"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    budget = Budget()
    trace = Trace(make_run_id("single", claim_id, seed))

    def done(status: str, amount: int = 0, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": amount, "reason": reason})
        return finish(conn, shape="single", claim_id=claim_id, seed=seed,
                      status=status, proposal_amount=amount, budget=budget,
                      trace=trace, error_reason=reason)

    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        if not claim["found"]:
            return done("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return done("needs_info", reason="missing_order_id")

        phase = 0

        def decide(observation: dict) -> dict:
            nonlocal phase
            # The model accounts for the agent's decisions; tool arguments and
            # monetary decisions come only from scoped, structured observations.
            complete(budget, seed=seed, purpose="decide", prompt=f"step={phase}")
            if phase == 0:
                phase = 1
                return {"tool": "lookup_order", "args": {
                    "order_id": claim["order_id"], "principal_id": claim["principal_id"]}}
            if phase == 1:
                order_view = observation["last_result"]
                trace.add("lookup_order", {"visible": order_view["visible"], "reason": order_view["reason"]})
                if not order_view["visible"]:
                    return {"final": {"status": "escalated", "reason": order_view["reason"]}}
                phase = 2
                return {"tool": "compute_compensation", "args": {"order": order_view["order"]}}
            quote = observation["last_result"]
            trace.add("quote", quote)
            return {"final": {"status": "quoted", "quote": quote}}

        result = run_react(conn, budget, observation={"claim": {
            "claim_id": claim_id, "order_id": claim["order_id"]}},
            decide=decide, max_steps=8)
        final = result["final"]
        if final["status"] != "quoted":
            return done(final["status"], reason=final.get("reason") or final.get("error_reason"))
        quote = final["quote"]
        proposal = int(quote["amount_vnd"])
        if proposal <= 0:
            return done("denied", reason=quote["reason"])
        # CP3: forward crash_at to the host and let InjectedCrash propagate.
        # The ledger row keyed refund:{claim_id} makes the resume a no-op replay.
        try:
            outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        except InjectedCrash:
            trace.add("crash", {"at": crash_at})
            trace.write()
            raise
        if not outcome["ok"]:
            return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
        return done("resolved", proposal)
    finally:
        conn.close()
