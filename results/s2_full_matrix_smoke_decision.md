# S2 Full-Matrix Smoke Decision

Model: `gpt-4.1-mini-2025-04-14`
Temperature: `0`
N: `1`

The smoke ran all 72 scenarios under all three conditions:

- `context_only`
- `authz_policy`
- `authz_policy_with_injection_guard`

Decision: stop before the full N>=5 matrix and strengthen injection scenarios.

Reason: under `authz_policy` (Block A+B, Block C off), injection exposure was high
(`1.0`) but IIS was `0.0`. The model saw every poisoned payload and still did not
attempt forbidden tools. Per the internal abort gate, this means the corpus should
be strengthened before spending on the full matrix.

Key smoke metrics are in `results/summary.csv`. Raw traces are committed under
`results/raw/`.
