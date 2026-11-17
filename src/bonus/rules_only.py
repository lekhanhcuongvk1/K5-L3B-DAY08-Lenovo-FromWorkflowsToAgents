"""Workflow baseline and one-factor removal of the missing-order check.

Adapted from lab8.shapes.workflow. Host authorization is never removed.
"""

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.schemas import Budget, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace


def run_claim(claim_id, *, seed, store_path, crash_at=None):
    return _run(claim_id, seed, store_path, crash_at, check_order=True)


def run_without_order_check(claim_id, *, seed, store_path, crash_at=None):
    return _run(claim_id, seed, store_path, crash_at, check_order=False)


def _run(claim_id, seed, store_path, crash_at, *, check_order):
    shape = "rules_only" if check_order else "workflow_no_order_check"
    conn = connect(store_path)
    budget = Budget()
    trace = Trace(make_run_id(shape, claim_id, seed))

    def done(status, amount=0, reason=None):
        trace.add("decision", {"status": status, "proposal_amount": amount, "reason": reason})
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed,
                      status=status, proposal_amount=amount, budget=budget,
                      trace=trace, error_reason=reason)

    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        if not claim["found"]:
            return done("failed", reason="unknown_claim")
        if check_order and not claim.get("order_id"):
            return done("needs_info", reason="missing_order_id")
        budget.add_tool(tool_cost())
        order = lookup_order(conn, claim.get("order_id"), claim["principal_id"])
        trace.add("lookup_order", {"visible": order["visible"], "reason": order["reason"]})
        if not order["visible"]:
            return done("escalated", reason=order["reason"])
        budget.add_tool(tool_cost())
        quote = compute_compensation(conn, order["order"])
        proposal = int(quote["amount_vnd"])
        trace.add("quote", quote)
        if proposal <= 0:
            return done("denied", reason=quote["reason"])
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
