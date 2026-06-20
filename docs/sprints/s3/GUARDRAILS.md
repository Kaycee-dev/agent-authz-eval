# S3 — Guardrails

S3 produces artifacts; it does not change the data those artifacts are
derived from.

- DO NOT modify any `results/raw/*.jsonl` files. They are immutable.
- DO NOT modify existing summary CSVs in `results/`. They are inputs.
- DO NOT modify the runner, model adapters, or scenario corpus.
- DO NOT modify `docs/METHODOLOGY.md` except to add S3-specific subsections
  (e.g. provenance for new derived artifacts). Do not edit the
  Destructive-Action Precondition Handling section, the UCR handling rule,
  or any other locked methodology decision.
- DO NOT hand-type any numerical claim into figures or text. Every number
  must come from `s2_consolidated.csv` or `findings.json` via code.
- DO NOT draft writeup prose. That is S4's job.
- DO NOT tune the dataset, the metric definitions, or the classifier
  behavior. If a metric definition is ambiguous, propose the disambiguation
  in DECISIONS.md and wait for architect approval — do not just decide.
- DO NOT delete or modify any methodology evidence file:
    results/raw/validation_haiku45_n1.jsonl
    results/raw/s2_full_matrix_groq_context_only_t0_7_n5.jsonl
    results/openrouter_provenance_capture.txt
