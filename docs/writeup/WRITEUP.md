# Agent Authorization Evaluation Writeup Skeleton

## Intro / motivation (~500w)
- Thesis: Authorization-respecting behavior is shaped by deployment context and model identity, and the writeup will support that thesis only through locked S3 findings.
- Claim: The opening frames the project as a portfolio-grade AI-security/safety artifact whose empirical claims are traceable to finding IDs.
- Claim: The motivation leads with cross-deployment precondition divergence, then closed-frontier baseline asymmetry, then safeguard-layer tradeoffs.

## Methodology summary (~800w)
- Thesis: The methodology summary will explain the synthetic harness, locked metric definitions, and delegated-user / confused-deputy framing without changing S3 methodology.
- Claim: All empirical values in the writeup come from `results/findings.json`; raw JSONL, consolidated CSVs, and figures remain locked evidence.
- Claim: UCR is reported without scenario exclusion, and the destructive-action precondition scenario follows `docs/METHODOLOGY.md` "Destructive-Action Precondition Handling".
- Claim: Indirect injection is framed as delegated-user / confused-deputy behavior, never unsolicited injection.
- Claim: Groq partial JSONL remains forensic evidence and is excluded from matrix discussion.

## Findings (~2,000w)
- Thesis: The findings section establishes the narrative spine through F3 first, F5/F6 second, and the remaining findings as model- and guard-specific consequences.

### 3.1 Cross-deployment precondition divergence
- Thesis: F3 leads because the same destructive-action precondition produces opposite behavior across deployments.
- Claim: OpenAI and Anthropic pause for precondition verification rather than executing, {{F3.values.openai.verified_then_paused.numerator}}/{{F3.values.openai.verified_then_paused.denominator}} and {{F3.values.anthropic.verified_then_paused.numerator}}/{{F3.values.anthropic.verified_then_paused.denominator}} <!-- F3: 15/15 and 15/15 -->
- Claim: OpenRouter proceeds without verification and does not pause in the same scenario, {{F3.values.openrouter.proceeded_without_verification.numerator}}/{{F3.values.openrouter.proceeded_without_verification.denominator}} and {{F3.values.openrouter.paused.numerator}}/{{F3.values.openrouter.paused.denominator}} <!-- F3: 15/15 and 0/15 -->

### 3.2 Closed-frontier baseline asymmetry
- Thesis: F5 and F6 show that closed-frontier baselines begin at very different indirect-injection susceptibility levels before added safeguards are considered.
- Claim: OpenAI context-only has high exposure-conditioned IIS, {{F5.values.openai_context_only.iis_exposure_conditioned.numerator}}/{{F5.values.openai_context_only.iis_exposure_conditioned.denominator}} and {{F5.values.openai_context_only.iis_exposure_conditioned.rate}} <!-- F5: 105/120 and 0.875 -->
- Claim: Anthropic context-only is lower than OpenAI context-only on the same metric and corpus, {{F6.values.anthropic_context_only.iis_exposure_conditioned.numerator}}/{{F6.values.anthropic_context_only.iis_exposure_conditioned.denominator}} and {{F6.values.anthropic_context_only.iis_exposure_conditioned.rate}} versus {{F6.values.openai_context_only.iis_exposure_conditioned.numerator}}/{{F6.values.openai_context_only.iis_exposure_conditioned.denominator}} and {{F6.values.openai_context_only.iis_exposure_conditioned.rate}} <!-- F6: 22/112 and 0.19642857142857142 versus 105/120 and 0.875; claim text says approximately a factor of four -->
- [Figure 1: headline metric comparison] <!-- results/figures/headline_metrics_by_condition.png; results/figures/headline_metrics_by_condition.svg -->

### 3.3 The injection-guard layer: asymmetric value
- Thesis: The injection_guard layer has asymmetric value: large for OpenAI in this matrix and small with OCR cost for Anthropic.
- Claim: OpenAI moves from context-only to authz_policy to full stack across the locked IIS values, {{F5.values.openai_context_only.iis_exposure_conditioned.numerator}}/{{F5.values.openai_context_only.iis_exposure_conditioned.denominator}} and {{F5.values.openai_context_only.iis_exposure_conditioned.rate}}; {{F5.values.openai_authz_policy.iis_exposure_conditioned.numerator}}/{{F5.values.openai_authz_policy.iis_exposure_conditioned.denominator}} and {{F5.values.openai_authz_policy.iis_exposure_conditioned.rate}}; {{F5.values.openai_authz_policy_with_injection_guard.iis_exposure_conditioned.numerator}}/{{F5.values.openai_authz_policy_with_injection_guard.iis_exposure_conditioned.denominator}} and {{F5.values.openai_authz_policy_with_injection_guard.iis_exposure_conditioned.rate}} <!-- F5: 105/120 and 0.875; 24/114 and 0.21052631578947367; 13/109 and 0.11926605504587157 -->
- Claim: Anthropic's injection_guard shift over authz_policy is small on IIS, {{F7.values.anthropic_authz_policy.iis_exposure_conditioned.numerator}}/{{F7.values.anthropic_authz_policy.iis_exposure_conditioned.denominator}} and {{F7.values.anthropic_authz_policy.iis_exposure_conditioned.rate}} versus {{F7.values.anthropic_authz_policy_with_injection_guard.iis_exposure_conditioned.numerator}}/{{F7.values.anthropic_authz_policy_with_injection_guard.iis_exposure_conditioned.denominator}} and {{F7.values.anthropic_authz_policy_with_injection_guard.iis_exposure_conditioned.rate}} <!-- F7: 15/114 and 0.13157894736842105 versus 14/111 and 0.12612612612612611 -->
- Claim: Anthropic's injection_guard shift over authz_policy carries a small OCR cost, {{F7.values.anthropic_authz_policy.ocr.numerator}}/{{F7.values.anthropic_authz_policy.ocr.denominator}} and {{F7.values.anthropic_authz_policy.ocr.rate}} versus {{F7.values.anthropic_authz_policy_with_injection_guard.ocr.numerator}}/{{F7.values.anthropic_authz_policy_with_injection_guard.ocr.denominator}} and {{F7.values.anthropic_authz_policy_with_injection_guard.ocr.rate}} <!-- F7: 16/120 and 0.13333333333333333 versus 19/120 and 0.15833333333333333 -->
- [Figure 2: per-tier IIS comparison] <!-- results/figures/per_tier_iis_heatmap.png; results/figures/per_tier_iis_heatmap.svg -->

### 3.4 Open-weights under safeguards: the OCR/IIS tradeoff
- Thesis: F1, F2, and F8 show an open-weights pattern where safeguards can eliminate injection-derived action attempts while exposure and OCR remain costly.
- Claim: OpenRouter OCR rises under authz_policy and remains high under the full stack, {{F1.values.openrouter_context_only.ocr.numerator}}/{{F1.values.openrouter_context_only.ocr.denominator}} and {{F1.values.openrouter_context_only.ocr.rate}}; {{F1.values.openrouter_authz_policy.ocr.numerator}}/{{F1.values.openrouter_authz_policy.ocr.denominator}} and {{F1.values.openrouter_authz_policy.ocr.rate}}; {{F1.values.openrouter_authz_policy_with_injection_guard.ocr.numerator}}/{{F1.values.openrouter_authz_policy_with_injection_guard.ocr.denominator}} and {{F1.values.openrouter_authz_policy_with_injection_guard.ocr.rate}} <!-- F1: 104/120 and 0.8666666666666667; 119/120 and 0.9916666666666667; 112/120 and 0.9333333333333333 -->
- Claim: The same authz_policy condition has lower OCR on OpenAI and Anthropic than on OpenRouter, {{F1.values.openai_authz_policy.ocr.numerator}}/{{F1.values.openai_authz_policy.ocr.denominator}} and {{F1.values.openai_authz_policy.ocr.rate}}; {{F1.values.anthropic_authz_policy.ocr.numerator}}/{{F1.values.anthropic_authz_policy.ocr.denominator}} and {{F1.values.anthropic_authz_policy.ocr.rate}} <!-- F1: 0/120 and 0.0; 16/120 and 0.13333333333333333 -->
- Claim: OpenRouter full stack has no exposure-conditioned IIS while retaining full exposure in the locked full-stack runs, {{F2.values.openrouter_authz_policy_with_injection_guard.iis_exposure_conditioned.numerator}}/{{F2.values.openrouter_authz_policy_with_injection_guard.iis_exposure_conditioned.denominator}} and {{F2.values.openrouter_authz_policy_with_injection_guard.iis_exposure_conditioned.rate}}; {{F2.values.openrouter_authz_policy_with_injection_guard.exposure_rate.numerator}}/{{F2.values.openrouter_authz_policy_with_injection_guard.exposure_rate.denominator}} and {{F2.values.openrouter_authz_policy_with_injection_guard.exposure_rate.rate}} <!-- F2: 0/120 and 0.0; 120/120 and 1.0 -->
- Claim: Closed full-stack comparators retain nonzero exposure-conditioned IIS, {{F2.values.anthropic_authz_policy_with_injection_guard.iis_exposure_conditioned.numerator}}/{{F2.values.anthropic_authz_policy_with_injection_guard.iis_exposure_conditioned.denominator}} and {{F2.values.anthropic_authz_policy_with_injection_guard.iis_exposure_conditioned.rate}}; {{F2.values.openai_authz_policy_with_injection_guard.iis_exposure_conditioned.numerator}}/{{F2.values.openai_authz_policy_with_injection_guard.iis_exposure_conditioned.denominator}} and {{F2.values.openai_authz_policy_with_injection_guard.iis_exposure_conditioned.rate}} <!-- F2: 14/111 and 0.12612612612612611; 13/109 and 0.11926605504587157 -->
- Claim: F8 OpenRouter exposure uses the locked values object while D-S4-7 tracks the claim-text mismatch, {{F8.values.openrouter_context_only.exposure_rate.numerator}}/{{F8.values.openrouter_context_only.exposure_rate.denominator}} and {{F8.values.openrouter_context_only.exposure_rate.rate}}; {{F8.values.openrouter_authz_policy.exposure_rate.numerator}}/{{F8.values.openrouter_authz_policy.exposure_rate.denominator}} and {{F8.values.openrouter_authz_policy.exposure_rate.rate}}; {{F8.values.openrouter_authz_policy_with_injection_guard.exposure_rate.numerator}}/{{F8.values.openrouter_authz_policy_with_injection_guard.exposure_rate.denominator}} and {{F8.values.openrouter_authz_policy_with_injection_guard.exposure_rate.rate}} <!-- F8: 114/120 and 0.95; 114/120 and 0.95; 120/120 and 1.0 -->
- Claim: F8 closed-model exposure comparison uses the stored per-arm exposure fields, {{F8.values.openai_context_only.exposure_rate.numerator}}/{{F8.values.openai_context_only.exposure_rate.denominator}} and {{F8.values.openai_context_only.exposure_rate.rate}}; {{F8.values.openai_authz_policy.exposure_rate.numerator}}/{{F8.values.openai_authz_policy.exposure_rate.denominator}} and {{F8.values.openai_authz_policy.exposure_rate.rate}}; {{F8.values.openai_authz_policy_with_injection_guard.exposure_rate.numerator}}/{{F8.values.openai_authz_policy_with_injection_guard.exposure_rate.denominator}} and {{F8.values.openai_authz_policy_with_injection_guard.exposure_rate.rate}}; {{F8.values.anthropic_context_only.exposure_rate.numerator}}/{{F8.values.anthropic_context_only.exposure_rate.denominator}} and {{F8.values.anthropic_context_only.exposure_rate.rate}}; {{F8.values.anthropic_authz_policy.exposure_rate.numerator}}/{{F8.values.anthropic_authz_policy.exposure_rate.denominator}} and {{F8.values.anthropic_authz_policy.exposure_rate.rate}}; {{F8.values.anthropic_authz_policy_with_injection_guard.exposure_rate.numerator}}/{{F8.values.anthropic_authz_policy_with_injection_guard.exposure_rate.denominator}} and {{F8.values.anthropic_authz_policy_with_injection_guard.exposure_rate.rate}} <!-- F8: OpenAI 120/120 and 1.0; 114/120 and 0.95; 109/120 and 0.9083333333333333; Anthropic 112/120 and 0.9333333333333333; 114/120 and 0.95; 111/120 and 0.925 -->
- [Figure 3: open-weights OCR/IIS divergence] <!-- results/figures/open_weights_ocr_iis_divergence.png; results/figures/open_weights_ocr_iis_divergence.svg -->

### 3.5 Anthropic at exposure
- Thesis: F4 shows that Anthropic's overt-injection behavior includes pre-execution defense before the injection-derived action attempt stage.
- Claim: Anthropic overt-instruction exposure is consistent across context-only, authz_policy, and full-stack conditions, {{F4.values.anthropic_context_only.exposure_overt_instruction.numerator}}/{{F4.values.anthropic_context_only.exposure_overt_instruction.denominator}} and {{F4.values.anthropic_context_only.exposure_overt_instruction.rate}}; {{F4.values.anthropic_authz_policy.exposure_overt_instruction.numerator}}/{{F4.values.anthropic_authz_policy.exposure_overt_instruction.denominator}} and {{F4.values.anthropic_authz_policy.exposure_overt_instruction.rate}}; {{F4.values.anthropic_authz_policy_with_injection_guard.exposure_overt_instruction.numerator}}/{{F4.values.anthropic_authz_policy_with_injection_guard.exposure_overt_instruction.denominator}} and {{F4.values.anthropic_authz_policy_with_injection_guard.exposure_overt_instruction.rate}} <!-- F4: 25/30 and 0.8333333333333334; 25/30 and 0.8333333333333334; 25/30 and 0.8333333333333334 -->
- Claim: Among exposed overt-instruction runs, Anthropic has no IIS in each condition, {{F4.values.anthropic_context_only.iis_overt_instruction.numerator}}/{{F4.values.anthropic_context_only.iis_overt_instruction.denominator}} and {{F4.values.anthropic_context_only.iis_overt_instruction.rate}}; {{F4.values.anthropic_authz_policy.iis_overt_instruction.numerator}}/{{F4.values.anthropic_authz_policy.iis_overt_instruction.denominator}} and {{F4.values.anthropic_authz_policy.iis_overt_instruction.rate}}; {{F4.values.anthropic_authz_policy_with_injection_guard.iis_overt_instruction.numerator}}/{{F4.values.anthropic_authz_policy_with_injection_guard.iis_overt_instruction.denominator}} and {{F4.values.anthropic_authz_policy_with_injection_guard.iis_overt_instruction.rate}} <!-- F4: 0/25 and 0.0; 0/25 and 0.0; 0/25 and 0.0 -->

## Limitations (~500w)
- Synthetic-environment caveat: Claims are bounded to the reproducible synthetic harness and will not extrapolate to production behavior.
- Groq exclusion: Groq partial JSONL remains forensic evidence and is excluded from matrix discussion.
- Single-action v1 pilot constraint: The corpus is an early single-action pilot rather than a broad multi-action benchmark.
- Cross-deployment caveat (F3): The destructive-precondition result is scenario-specific and must follow the S3 methodology note.
- Small N per cell: Per-cell sample size limits precision and keeps claims directional and bounded.
- No adversary modeling: The prompts are fixed test cases rather than adaptive adversary behavior.
- No fine-tuned models: The matrix covers the evaluated endpoints only and does not test fine-tuned variants.

## Reproduction note (~300w)
- Thesis: The reproduction note gives reviewers the shortest path from clone to regenerated artifacts without changing the locked pipeline.
- Claim: Start with `git clone` of the repository and checkout of the reviewed tag or branch.
- Claim: Install the package and pinned dependencies through the repo-documented `pip install` path.
- Claim: Regenerate artifacts with `python -m agent_authz_eval.report all`.
- Claim: Fresh-clone reproduction was previously verified on Linux at S3 close and will be cited as prior gate evidence.

## How this was reviewed (~500w)
- Thesis: The review section makes the verification process part of the portfolio artifact.
- Claim: The sprint uses a gated-tagged workflow with commits, annotated tags, pushed branches, and remote verification.
- Claim: The local agent and remote architect are separate roles, with architect verification required before the next gate opens.
- Claim: Recompute-from-raw verification was used for S3 claim-bearing artifacts and remains the standard for derived evidence.
- Claim: Annotated tag immutability is the audit boundary for approved gates.
- Claim: The S3-G4 to S3-G4-2 versioned re-tag pattern is the worked example for correcting a gate without rewriting approved history.

## Conclusion + future work (~400w)
- Conclusion: Authorization-respecting behavior is an empirical property of deployment context, model identity, and safeguard layering, not a generic model-family assumption.
- Future work: Resolve D-S4-7 before prose locks F8's exposure wording.
- Future work: Add adaptive adversary modeling outside S4 scope.
- Future work: Broaden beyond the single-action pilot corpus outside S4 scope.
- Future work: Add more model endpoints and fine-tuned variants outside S4 scope.
