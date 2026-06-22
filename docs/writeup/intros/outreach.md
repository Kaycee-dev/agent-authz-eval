# Outreach Intro

This artifact is an empirical writeup of a synthetic authorization evaluation for tool-using LLM agents. It is designed for AI-security and safety hiring contexts: it shows not only the findings, but also the infrastructure used to keep the claims reviewable. The study asks whether agents respect authorization boundaries under direct unauthorized requests, indirect injection in a delegated-user workflow, and destructive-action requests with user-specified preconditions.

The work demonstrates three things. First, the author can build and preserve a reproducible evaluation pipeline from raw JSONL through consolidated metrics, structured findings, and figures. Second, the analysis is willing to keep inconvenient details visible, including a locked finding whose claim text conflicted with its verified values object. Third, the final narrative is constrained by the evidence: claims remain inside the synthetic harness, avoid vendor-bashing, and distinguish model behavior from prompt-layer effects.

For reviewers, the artifact is meant to show judgment under evidence constraints: not just generating results, but keeping them traceable, bounded, and ready for independent verification.
