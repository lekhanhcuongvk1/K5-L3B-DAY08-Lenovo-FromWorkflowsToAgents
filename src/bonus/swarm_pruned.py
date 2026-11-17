"""Reference swarm with independently seeded 50% peer/parse call pruning.

Adapted from lab8.shapes.swarm_reference; retains its ticket override whenever
parse is kept. A dropped parse also drops parsing itself, not just its bill.
No benchmark label is consulted. Draft, host gates and investigator stay fixed.
"""

import hashlib

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace


def keep_call(seed, claim_id, purpose):
    key = f"B4-prune-v1|{seed}|{claim_id}|{purpose}".encode()
    return hashlib.sha256(key).digest()[0] < 128


def run_claim(claim_id, *, seed, store_path, crash_at=None):
    conn = connect(store_path)
    budget = Budget()
    shape = "swarm_pruned"
    trace = Trace(make_run_id(shape, claim_id, seed))

    def done(status, amount=0, reason=None):
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed,
                      status=status, proposal_amount=amount, budget=budget,
                      trace=trace, error_reason=reason)

    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        if not claim["found"]:
            trace.add("error", {"reason": "unknown_claim"})
            return done("failed", reason="unknown_claim")
        peer = keep_call(seed, claim_id, "peer")
        parse = keep_call(seed, claim_id, "parse")
        trace.add("pruning", {"peer_kept": peer, "parse_kept": parse})
        if peer:
            complete(budget, seed=seed, purpose="peer", prompt=claim["ticket"])
        parsed_delay = None
        if parse:
            parsed_delay = parse_delay_days(claim["ticket"])
            complete(budget, seed=seed, purpose="parse", prompt=claim["ticket"])
        if not claim.get("order_id"):
            complete(budget, seed=seed, purpose="draft", prompt="needs_info")
            trace.add("decision", {"status": "needs_info"})
            return done("needs_info", reason="missing_order_id")
        handoff = make_handoff(
            request_id=f"REQ-{claim_id}", claim_id=claim_id,
            task="check_applicable_policy", facts={},
            allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
        )
        trace.add("handoff", safe_dump(handoff))
        investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
        order_view = investigated["tools"].get("lookup_order", {})
        trace.add("investigator", {"lookup_order": order_view,
                  "policy_count": len((investigated["tools"].get("lookup_policy") or {}).get("policies") or [])})
        if not order_view.get("visible"):
            complete(budget, seed=seed, purpose="draft", prompt="escalated")
            return done("escalated", reason=order_view.get("reason"))
        order = dict(order_view["order"])
        # Preserve the reference weakness when parsing has not been pruned.
        if parsed_delay is not None and parsed_delay != int(order["delay_days"]) and seed % 5 == 0:
            order["delay_days"] = parsed_delay
            trace.add("model_override", {"delay_days": parsed_delay})
        quote = investigated["tools"]["compute_compensation"]
        if order["delay_days"] != order_view["order"]["delay_days"]:
            budget.add_tool(tool_cost())
            quote = compute_compensation(conn, order)
        proposal = int(quote["amount_vnd"])
        trace.add("quote", quote)
        complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
        if proposal <= 0:
            return done("denied", reason=quote.get("reason"))
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
