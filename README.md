# agent-authz-eval

Focused, reproducible evaluation of whether tool-using LLM agents respect
least-privilege authorization boundaries in a fully synthetic mock environment.

S0 status: mock environment and RBAC tests.

## Results

The S2/S3 artifacts are committed under `results/` and documented in
`docs/METHODOLOGY.md`.

- `results/figures/headline_metrics_by_condition.svg` / `.png` — OCR, UCR,
  and exposure-conditioned IIS rates by model and system-prompt condition.
- `results/figures/per_tier_iis_heatmap.svg` / `.png` — per-tier indirect
  injection susceptibility across models and conditions.
- `results/figures/open_weights_ocr_iis_divergence.svg` / `.png` —
  open-weights direct-request over-compliance versus indirect-injection
  susceptibility under safeguards.

The eight load-bearing numerical findings are encoded with provenance in
`results/findings.json`.

## How to reproduce

Install the package and run the end-to-end verifier:

```powershell
python -m pip install -e .
$env:PYTHONPATH='src'
python -m agent_authz_eval.report all
```

The verifier recomputes `results/s2_consolidated.csv` from raw JSONL records,
re-derives `results/findings.json`, regenerates the figure artifacts in a
temporary directory, confirms the PNG/SVG render outputs are valid, and verifies
that the underlying plotted rates and counts match the committed CSV and
findings data.
