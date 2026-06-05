# Limitations

Version 1 uses single-action scenarios. The runner will score whether an agent
attempts the target tool or a forbidden tool under the principal's initial
permission set; it will not update effective permissions after a successful
`grant_role` call. Multi-step confused-deputy escalation is deferred to a later
version so the first study can keep the authorization metric simple and
auditable.

The S2 pilot used `gpt-4.1-nano-2025-04-14` only as a harness-validation model.
It false-refused authorized base tasks often enough that it is not a valid
subject for the full matrix. The full-matrix plan drops nano and uses capable
mid-tier models instead.
