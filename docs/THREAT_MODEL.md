# Threat Model

This repository is a defensive measurement study in a fully synthetic sandbox.

In scope:
- Measuring whether agents attempt to exceed a stated authorization boundary.
- Mock Python tools that return fabricated data only.
- Deterministic RBAC checks over synthetic principals and permissions.

Out of scope:
- Real systems, real credentials, live targets, or network egress in the eval path.
- Novel jailbreak or attack research.
- Payloads or procedures that transfer to real-world exploitation.

The eval-path environment makes zero network calls. Tool behavior is implemented
as local Python stubs over deterministic fabricated state.
