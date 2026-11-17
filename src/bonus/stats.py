"""Claim-cluster percentile bootstrap and exact paired McNemar (stdlib only)."""

import math
import random
from collections import defaultdict


def _index(rows):
    result = {}
    for row in rows:
        key = (row["claim_id"], row["seed"])
        if key in result:
            raise ValueError(f"duplicate pair {key}")
        if not isinstance(row.get("passed"), bool):
            raise ValueError("statistics require labeled boolean outcomes")
        result[key] = int(row["passed"])
    if not result:
        raise ValueError("empty sample")
    return result


def bootstrap_ci(rows, *, repetitions=10000, seed=20261117):
    if repetitions < 100:
        raise ValueError("at least 100 bootstrap repetitions required")
    indexed = _index(rows)
    grouped = defaultdict(list)
    for (claim, _), passed in indexed.items():
        grouped[claim].append(passed)
    groups = [grouped[key] for key in sorted(grouped)]
    rng = random.Random(seed)
    samples = []
    for _ in range(repetitions):
        selected = [rng.choice(groups) for _ in groups]
        samples.append(sum(map(sum, selected)) / sum(map(len, selected)))
    samples.sort()
    return {
        "low": samples[math.floor(0.025 * (repetitions - 1))],
        "high": samples[math.ceil(0.975 * (repetitions - 1))],
        "method": "percentile_claim_cluster_bootstrap", "repetitions": repetitions,
        "seed": seed, "claim_clusters": len(groups),
    }


def paired_mcnemar(left, right):
    a, b = _index(left), _index(right)
    if a.keys() != b.keys():
        raise ValueError("paired samples must have identical claim/seed keys")
    wins = sum(a[key] > b[key] for key in a)
    losses = sum(a[key] < b[key] for key in a)
    n = wins + losses
    p = min(1.0, 2 * sum(math.comb(n, k) for k in range(min(wins, losses) + 1)) / 2**n) if n else 1.0
    return {"pairs": len(a), "left_only_pass": wins, "right_only_pass": losses,
            "discordant_pairs": n, "p_value": p, "method": "exact_two_sided_mcnemar",
            "caution": "seed outcomes within a claim may be dependent; use claim-cluster sensitivity too"}


def paired_claim_sign(left, right):
    a, b = _index(left), _index(right)
    if a.keys() != b.keys():
        raise ValueError("paired samples must have identical claim/seed keys")
    diffs = defaultdict(int)
    for key in a:
        diffs[key[0]] += a[key] - b[key]
    wins, losses = sum(v > 0 for v in diffs.values()), sum(v < 0 for v in diffs.values())
    n = wins + losses
    p = min(1.0, 2 * sum(math.comb(n, k) for k in range(min(wins, losses) + 1)) / 2**n) if n else 1.0
    return {"claim_clusters": len(diffs), "left_better": wins, "right_better": losses,
            "ties": len(diffs) - n, "p_value": p, "method": "exact_two_sided_claim_sign"}
