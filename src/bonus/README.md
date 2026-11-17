# B4 — Baselines and controlled ablation

Run commands from `src/`. No API key or network is required.

```powershell
python -m bonus.run_b4 --out reports/bonus_ablation.json
python -m pytest -q tests/test_bonus_b4.py
```

The first command registers variants with the official extra-shape mechanism,
runs all four official shapes and three variants through `lab8.benchmark`, scans
each result before its temporary database is removed, and computes statistics.
The JSON is generated evidence: do not edit it by hand. The runner restores the
shape registry even if a trial or benchmark fails. Run sequentially, not in threads.

To run the variants with the ordinary CLI, including an unlabeled student drop:

```powershell
python -m lab8.benchmark --shapes workflow,swarm,rules_only,swarm_pruned,workflow_no_order_check --extra-shape rules_only=bonus.rules_only:run_claim --extra-shape swarm_pruned=bonus.swarm_pruned:run_claim --extra-shape workflow_no_order_check=bonus.rules_only:run_without_order_check --cases data/public_claims.jsonl --world data/public_world_state.json --seeds 11,22,33,44,55 --out reports/bonus_variants.json
```

For an unlabeled self-check, change `--cases` and `--world` to the files under
`student_drop/`. No pass rate or statistical test is available without labels.
Do not use the deliberately ablated workflow as the team's chosen shape.

Files:

- `rules_only.py`: workflow parity baseline and removal of only the missing-order
  early return. Approval, ownership, compensation and durability stay enforced.
- `swarm_pruned.py`: adapted from `lab8/shapes/swarm_reference.py`, with a fixed
  50% keep decision for peer/parse calls. Removing parse removes its behavior too.
  Draft calls and the reference ticket weakness when parse survives are retained.
- `stats.py`: claim-cluster percentile bootstrap, exact paired McNemar, and a
  claim-level sign sensitivity check. Duplicate or unmatched samples are rejected.
- `run_b4.py`: official evaluator plus independent public safety diagnostics;
  original grader/config/data files are not modified.
- `investigator_ablation.py`: earlier CP5 research-card experiment, separate from B4.

Sources: the provided lab starter files and `docs/bonus_topics.md` (B4);
[Zhang et al., EMNLP 2026](https://aclanthology.org/2026.emnlp-main.798/);
[AgentArch](https://arxiv.org/abs/2509.10769v2).

Safety counts scan artifacts and every newly created ledger effect against its
approval and principal. Seeded historical refunds are excluded by their IDs.
Any exception before scanning is reported as an unscanned trial and makes this
runner return a nonzero exit code. These diagnostics are not official hidden grades.
