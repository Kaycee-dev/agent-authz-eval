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

## Findings writeup

The empirical writeup turns the S2/S3 report artifacts into a portfolio-ready
narrative about authorization behavior in tool-using LLM agents. It covers
direct over-compliance, exposure-conditioned indirect injection susceptibility,
destructive-action precondition handling, and the review process used to keep
claims tied to locked findings. The central result is that deployment context
and model identity both shape authorization-respecting behavior: the same
safeguard layer can be highly effective in one model row, marginal in another,
and paired with different tradeoffs in the open-weights row. The writeup stays
inside the synthetic harness boundary, links every numerical claim to finding
IDs, embeds the committed figures, and documents the F8 wording correction as an
example of the gated review process. Use this as the canonical narrative
companion to `results/findings.json`, `results/s2_consolidated.csv`, and the
committed figures. It is the best starting point for readers who want the
findings before the raw artifacts:
[Do Tool-Using LLM Agents Respect Authorization Boundaries?](docs/writeup/WRITEUP.md)

## How to reproduce

Install the package and run the end-to-end verifier:

```text
python -m pip install -e ".[dev]"
python -m agent_authz_eval.report all
```

The verifier recomputes `results/s2_consolidated.csv` from raw JSONL records,
re-derives `results/findings.json`, regenerates the figure artifacts in a
temporary directory, confirms the PNG/SVG render outputs are valid, and verifies
that the underlying plotted rates and counts match the committed CSV and
findings data.

Build the PDF version of the writeup with:

```text
python scripts/build_writeup_pdf.py
```
