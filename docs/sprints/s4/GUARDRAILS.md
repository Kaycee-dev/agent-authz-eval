# S4 — Guardrails

S4 writes the empirical narrative; it does not change the evidence the
narrative depends on.

- DO NOT edit `results/findings.json`. All findings F1-F8 are locked. Quote
  verbatim when load-bearing, and cite findings by finding ID.
- DO NOT re-derive numbers in prose. Every numerical claim must trace to a
  finding ID in `results/findings.json`. At G2/G3, cite finding IDs in source
  comments next to each value or placeholder.
- DO NOT report UCR with scenario exclusion. UCR is reported without scenario
  exclusion.
- DO document the cross-deployment finding according to
  `docs/METHODOLOGY.md` "Destructive-Action Precondition Handling".
- DO frame indirect injection as delegating-user / confused-deputy behavior.
  Never call it "unsolicited injection."
- DO NOT tune the corpus, tune metric definitions post-hoc, run new
  experiments, add new model runs, add new tiers, or expand scope. If something
  feels missing, log it as "future work" for S5+.
- DO NOT regenerate or replace the three committed visuals in
  `results/figures/*.png` and `results/figures/*.svg`.
- DO keep Groq partial JSONL as forensic evidence, excluded from matrix
  discussion.
- DO keep framing analytical:
  - F5 reads as "OpenAI baseline highly susceptible; injection_guard layer
    highly effective," not "OpenAI bad."
  - F7 reads as "Anthropic baseline absorbs most of what the guard would add;
    guard has small OCR cost," not "Anthropic guard useless."
  - Claims characterize behavior in a specific reproducible synthetic test
    environment, not production behavior. The limitations section must own
    this directly.
- DO NOT modify or delete immutable S4 inputs:
    `results/raw/*.jsonl`
    `results/openrouter_provenance_capture.txt`
    `results/s2_full_matrix_*_summary.csv`
    `results/s2_consolidated.csv`
    `results/findings.json`
    `results/figures/*.png`
    `results/figures/*.svg`
    `docs/METHODOLOGY.md`
    `docs/sprints/s1/`
    `docs/sprints/s2/`
    `docs/sprints/s3/`
    `src/agent_authz_eval/report.py`
- DO put any writeup-side helpers in a new module. The report pipeline is
  locked.
