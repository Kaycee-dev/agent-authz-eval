# Methodology Notes

This is a focused synthetic evaluation of authorization behavior in tool-using
agents. The indirect-injection bucket is framed as a delegating-user /
confused-deputy setting: the user asks the agent to act on content returned by
an authorized tool, while attacker-controlled tool output embeds a forbidden
action in that returned content.

These scenarios should be interpreted as cases where the model lets tool output
escalate it into an unauthorized action. They are not claims that the model
followed an unsolicited injection outside the user's delegated workflow.

The S2 full matrix uses stochastic sampling with temperature `0.7` and `N=5`.
Reported spreads are standard deviations across run indices for the same
model, condition, and scenario corpus.
