# Limitations

Version 1 uses single-action scenarios. The runner will score whether an agent
attempts the target tool or a forbidden tool under the principal's initial
permission set; it will not update effective permissions after a successful
`grant_role` call. Multi-step confused-deputy escalation is deferred to a later
version so the first study can keep the authorization metric simple and
auditable.
