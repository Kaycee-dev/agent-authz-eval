# S2 Runner Reliability Gate 2

Date: 2026-06-08

Controlled sticky-terminal-error dry run using the production append/resume path.

- first-pass model calls: 5
- first-pass raw records: 5
- first-pass terminal error records: 1
- completed OK keys before resume: 4
- resume model calls: 1
- records retried on resume: 1
- raw JSONL lines after resume: 6
- canonical run-unit keys after deduplication: 5
- canonical valid_runs: 5
- canonical error_runs: 0

The stale error line remains in append-only raw JSONL, but the successful retry
supersedes it for completed-key calculation and behavioral metrics.

Artifacts:

- `results/raw/s2_runner_reliability_sticky_error_dryrun.jsonl`
- `results/s2_runner_reliability_sticky_error_dryrun_summary.csv`
