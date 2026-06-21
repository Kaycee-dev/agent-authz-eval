# S4 — Empirical Writeup

## Goal
Produce the empirical writeup of `agent-authz-eval` findings, suitable as the
portfolio centerpiece for AI-security/safety role applications. The writeup is
distributed through a blog post, a repo README link, and an outreach PDF.

## In scope
- `docs/writeup/WRITEUP.md` — markdown source of truth and GitHub-linkable
  canonical URL.
- PDF export via pandoc, exposed as a build target (Makefile target or
  top-level script). Exact mechanism is decided at G3 or G4.
- Three distribution variants: blog, README link, outreach PDF. The same
  writeup body is used for all three; intro framing varies by channel. Exact
  mechanism (separate intro files vs. templated header vs. `variants/`
  subdirectory) is deferred to G2.
- Length target: ~5,000 words +/- 15%, allocated as:
  - Intro / motivation: ~500 words.
  - Methodology summary: ~800 words.
  - Findings with narrative spine: ~2,000 words, with figures embedded and no
    word cost.
  - Limitations: ~500 words.
  - Reproduction note: ~300 words.
  - How this was reviewed: ~500 words.
  - Conclusion + future work: ~400 words.
- Narrative spine: lead with F3 (cross-deployment precondition divergence) and
  F5/F6 (closed-frontier baseline asymmetry, ~4x). Thesis: deployment context
  and model identity both shape authorization-respecting behavior, and the
  differences are larger than common framing suggests.

## Non-goals (will not be done in S4)
- New experiments, model runs, tiers, scenarios, corpus tuning, or metric
  definition changes.
- Changes to raw data, findings, figures, or the locked report pipeline.
- Claims beyond the synthetic test harness.
- Vendor-bashing or production-behavior extrapolation.
- Hand-derivation of numerical claims outside the finding-ID provenance path.

## Ship gates
- S4-G1: Governance pack added under `docs/sprints/s4/`.
- S4-G2: Outline / skeleton with section headers, thesis sentences, and
  numerical placeholders pointing to finding IDs (for example,
  `{{F3.numerator}}/{{F3.denominator}}`). No prose body yet; the skeleton acts
  as a claim-provenance map.
- S4-G3: Full prose draft, figures embedded, claims cross-referenced to
  finding IDs, limitations covered.
- S4-G4: Final pass with link audit, "how this was reviewed" finalized,
  reproduction-claim audit, PDF export target working, and distribution-variant
  intros finalized.
- S4-G5: Merge PR to main and tag `s4-merged`.

At the end of G1, open a draft PR against main titled
`[WIP] S4 — Empirical writeup`.

Each gate ends with a commit + annotated tag + PR refresh. Standard gated
protocol: no merge until architect verifies from the remote.
