# S3 — Decision Log

## D-S3-1 — Plotting dependency
- Choice: matplotlib (pinned version)
- Version: matplotlib==3.11.0
- Rationale: convention in empirical research artifacts; SVG and PNG output supported; reviewers expect to see matplotlib code; the alternatives (hand-generated SVG, plotly) introduce more surface area than the dependency saves.
- Risk: a new dep adds install friction; mitigated by pinning the version and listing it in pyproject.toml.
