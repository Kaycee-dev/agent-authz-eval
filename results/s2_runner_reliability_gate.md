# S2 Runner Reliability Gate

Date: 2026-06-08

## Automated verification

The reliability tests cover:

- mid-run interruption followed by idempotent resume;
- truncated trailing JSONL repair;
- connection-level retry;
- HTTP 5xx retry;
- non-retryable HTTP 400 fail-fast behavior;
- terminal API failures recorded as error records;
- exclusion of error records from OCR, UCR, exposure, and IIS denominators.

## Live interruption dry run

Configuration:

- provider: `openai`
- model: `gpt-4.1-mini-2025-04-14`
- condition: `context_only`
- temperature: `0.7`
- scenarios: first 5 corpus scenarios
- N: `1`

The first process was forcibly stopped after two JSONL records had been flushed.
The identical command was restarted against the same path.

Observed:

- records before interruption: 2
- unique keys before interruption: 2
- final records after resume: 5
- final unique keys: 5
- occurrences of each pre-interruption key after resume: 1
- terminal API error records: 0

Artifacts:

- `results/raw/s2_runner_reliability_live_dryrun.jsonl`
- `results/s2_runner_reliability_live_dryrun_summary.csv`
- `results/s2_runner_reliability_live_dryrun_transcripts.md`
