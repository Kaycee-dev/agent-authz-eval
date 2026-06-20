# S3 — Decision Log

## D-S3-1 — Plotting dependency
- Choice: matplotlib (pinned version)
- Version: matplotlib==3.11.0
- Rationale: convention in empirical research artifacts; SVG and PNG output supported; reviewers expect to see matplotlib code; the alternatives (hand-generated SVG, plotly) introduce more surface area than the dependency saves.
- Risk: a new dep adds install friction; mitigated by pinning the version and listing it in pyproject.toml.

## D-S3-2 — Figure verification semantics
- Choice: verify figure renderability and underlying plotted data rather than PNG/SVG byte identity.
- Rationale: matplotlib raster/vector output can vary across operating systems, font stacks, Pillow, and freetype builds even when the plotted rates and counts are identical. Cross-platform reproduction should validate the empirical data and render health, not renderer-specific bytes.
- Risk: the verifier no longer proves exact image bytes; mitigated by regenerating all figures in a temporary directory, validating PNG/SVG outputs, and checking plotted values against the committed CSV and findings JSON.
