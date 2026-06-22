# S4 — Ship Check

- [ ] All five gates closed and annotated-tagged (`gate-s4-g1` through
  `gate-s4-g5`, modulo `-2` versioned re-tags per immutability protocol).
- [x] `docs/writeup/WRITEUP.md` exists, is ~5,000 words +/- 15%, and matches
  the SPEC section allocation.
- [x] Every numerical claim cross-references a finding ID from
  `results/findings.json` as a verbatim quote or trivially-derived value with
  cited derivation.
- [x] All three figures are embedded with captions matching figure content.
- [x] Limitations explicitly cover the synthetic-environment caveat, Groq
  exclusion, single-action v1 pilot constraint, cross-deployment caveat (F3),
  small N per cell, no adversary modeling, and no fine-tuned models.
- [x] "How this was reviewed" is present and describes the gated-tagged
  remote-verification process.
- [x] `pytest` passes.
- [x] `python -m agent_authz_eval.report all` exits 0.
- [x] PDF export target works: documented command produces a valid PDF from
  `WRITEUP.md` with figures rendered.
- [x] Three distribution intro framings are present, using the mechanism chosen
  in D-S4-6.
- [ ] Fresh-clone reproduction still works: clone main, run `report all`,
  exit 0.
- [ ] PR description links the writeup file and references the `s4-merged` tag.
