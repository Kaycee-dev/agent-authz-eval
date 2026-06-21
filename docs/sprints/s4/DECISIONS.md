# S4 — Decision Log

## D-S4-1 — Deliverable format
- Choice: markdown source at `docs/writeup/WRITEUP.md` plus PDF export via
  pandoc.
- Rationale: GitHub-linkable canonical URL plus polished email-attachable
  artifact. HTML-only is rejected for low polish return; PDF-only is rejected
  because it loses the GitHub link surface.
- Risk: pandoc export adds tooling surface; mitigated by deferring exact target
  mechanics to G3/G4 and requiring the target to pass before G5.

## D-S4-2 — Length target
- Choice: ~5,000 words with the section allocation in SPEC.
- Rationale: below ~3k crowds the methodology-of-review story; above ~8k pads
  an 8-finding empirical study.
- Risk: the draft may drift from allocation; mitigated by making section
  allocation part of the G5 ship check.

## D-S4-3 — Narrative spine
- Choice: lead with F3 (cross-deployment precondition divergence) and F5/F6
  (closed-frontier baseline asymmetry, ~4x).
- Rationale: F3 is the most novel finding; F5/F6 is the most viscerally
  surprising number. Together they support the thesis that deployment context
  and model identity both shape authorization-respecting behavior, and the
  differences are larger than common framing suggests.
- Risk: the lead findings may crowd out the rest of F1-F8; mitigated by the
  G2 claim-provenance skeleton.

## D-S4-4 — Review methodology section
- Choice: "How this was reviewed" is load-bearing and non-optional.
- Rationale: AI-safety role targeting benefits from showing not only results
  but also infrastructure for verifying the author's own claims.
- Risk: it consumes limited word budget; mitigated by assigning it an explicit
  ~500-word allocation.

## D-S4-5 — Framing constraints
- Choice: no vendor-bashing and no extrapolation beyond the synthetic test
  harness.
- Rationale: the writeup should stay analytical. F5 reads as "OpenAI baseline
  highly susceptible; injection_guard layer highly effective," and F7 reads as
  "Anthropic baseline absorbs most of what the guard would add; guard has small
  OCR cost."
- Risk: tone can drift during prose drafting; mitigated by encoding these
  constraints in GUARDRAILS.md.

## D-S4-6 — Distribution variants
- Choice: blog, README link, and outreach PDF variants share the writeup body;
  intro framing varies per channel.
- Rationale: one empirical body avoids claim drift while still matching the
  distribution context.
- Risk: variant mechanics can become unnecessary process; mitigated by
  deferring the exact mechanism to G2.
