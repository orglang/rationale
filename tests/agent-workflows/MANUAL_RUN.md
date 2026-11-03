# Manual behavioral evaluation

This directory contains seven controlled scenarios and a shared scoring rubric for the specification workflows.

## Run procedure

Use the [manual-behavioral-evaluation skill](../../skills/manual-behavioral-evaluation/SKILL.md) as the coordinator procedure. It defines how to pin the repository SHA, prepare a blind copy-ready package, run one scenario in a fresh ChatGPT chat, return the complete agent response to the coordinator, and score the result in the coordinator conversation.

The coordinator instructions are in English. The prompt template for the tested agent and the scenario task statements remain in Russian.

The user only needs to copy the complete package into a new agent chat and then paste the agent's complete response back into the coordinator conversation. A separate evaluator chat, manually completed run-record template, and separate diff attachment are not required. Any proposed diff must be included in the agent's response.

## Test fixtures

- [Scenarios](scenarios.md) — seven Russian-language tasks, expected behavior, and failure signals. The tested agent must receive only the selected task, not the expected behavior or failure signals.
- [Scoring rubric](rubric.md) — five criteria scored from 0 to 2. Keep this hidden from the tested agent.
- [Coordinator skill](../../skills/manual-behavioral-evaluation/SKILL.md) — English instructions for preparing, running, and evaluating the manual tests.

## Automation boundary

Repository CI validates Markdown formatting and local links. The seven scenarios are manual behavioral evaluations, not ordinary unit tests. There is no configured model/API runner or trusted automated judge, so CI does not claim to execute these scenarios or certify agent behavior.

Keep the run's full commit SHA and scenario/rubric versions. Do not compare results from different snapshots as if they were identical conditions. Review scenarios whenever a canonical instruction, workflow, contract, or relevant dependency changes. Do not weaken an expected result merely to make a failing run pass; first determine whether the agent failed, the fixture became stale, or the premise is defective.
