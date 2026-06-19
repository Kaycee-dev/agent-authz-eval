# S3 — Report Generation Pipeline

## Goal
Produce the artifacts the S4 writeup will consume. All claims in the
writeup must trace to a structured artifact produced here; nothing is
hand-typed into the writeup.

## In scope
- `report.py` (or equivalent module) that reads `results/raw/*.jsonl` and
  the corrected methodology decisions in `docs/METHODOLOGY.md`, emitting:
  - `results/s2_consolidated.csv` — 9-arm x 3-metric table with per-scenario
    N=5 spread (mean and stddev), per-tier IIS, exposure rates, error_runs.
  - `findings.json` — structured numerical claims with provenance
    (raw_path, dedup rule, classifier predicate) for every headline number.
  - Figures as SVG (and PNG fallback) regenerable from CSV alone:
    headline metric comparison, per-tier IIS comparison, OCR/IIS divergence
    visualization for the open-weights row.
- `verify_findings.py` — re-derives `findings.json` from raw; exit code
  nonzero on any mismatch. Reviewers run this independently.
- Tests for the report pipeline (parser correctness, edge cases, dedup
  behavior on duplicate-OK records as observed in the OpenRouter
  authz_policy JSONL).

## Non-goals (will not be done in S3)
- Writeup text drafting. METHODOLOGY.md additions or revisions outside what
  is needed to document S3-specific decisions.
- Changes to existing matrix raw data or summary CSVs.
- Changes to the runner or model adapters.
- New scenarios or corpus additions.
- New evaluation conditions.

## Ship gates
- S3-G1: `s2_consolidated.csv` generated and recompute-validated.
- S3-G2: `findings.json` generated and `verify_findings.py` passes.
- S3-G3: Figures generated from CSVs, manually inspected for correctness.
- S3-G4: Tests for the pipeline pass. Ready for S4.

Each gate ends with a commit + annotated tag + PR refresh. Standard gated
protocol: no merge until architect verifies from the remote.
