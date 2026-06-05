"""Generate condition-level pilot summaries from raw JSONL records."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from agent_authz_eval.metrics import (
    compute_metrics_by_condition,
    principal_distribution,
)


def load_records(paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    return records


def write_condition_summary(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metrics_by_condition = compute_metrics_by_condition(records)
    rows: list[dict[str, Any]] = []
    for condition, metrics in metrics_by_condition.items():
        condition_records = [
            record for record in records if record["condition"] == condition
        ]
        distribution = principal_distribution(condition_records)
        for metric, value in metrics.items():
            rows.append({"condition": condition, "metric": metric, "value": value})
        for principal, value in sorted(distribution.items()):
            rows.append(
                {
                    "condition": condition,
                    "metric": f"principal_{principal}_runs",
                    "value": value,
                }
            )

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["condition", "metric", "value"])
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize pilot raw JSONL files.")
    parser.add_argument("--output", default="results/summary.csv")
    parser.add_argument("raw_files", nargs="+")
    args = parser.parse_args(argv)

    records = load_records([Path(raw_file) for raw_file in args.raw_files])
    write_condition_summary(Path(args.output), records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
