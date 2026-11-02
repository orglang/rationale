# Agent workflow evaluations

This directory contains six controlled scenarios and a shared scoring rubric for the specification workflows.

## What is automated

The repository CI validates Markdown formatting and local links.

## What is not automated

The six scenarios are **behavioral evaluations**, not ordinary unit tests. They require an agent to read the instruction set and produce an answer and, where applicable, a proposed diff. The repository currently has no configured model/API runner, fixed model version, or trusted automated judge. CI therefore does not claim to execute these scenarios or certify agent behavior.

Run them manually using the procedure in [`scenarios.md`](scenarios.md), score with [`rubric.md`](rubric.md), and retain the run record. A future runner should pin the model and harness, capture outputs/diffs, and use the rubric; it should not replace semantic review with keyword matching.
