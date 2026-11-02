# Behavioral evaluation rubric

Score each scenario independently from 0 to 2 on each criterion. Maximum: 10 points per scenario.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Classification and process | Misclassifies the change or uses a disproportionate process | Partly correct, with a material omission | Correctly classifies the effect and selects a proportionate process |
| Semantic discipline | Invents, silently changes, or assumes behavior | Notices uncertainty but handles it incompletely | Derives only what follows; preserves unresolved decisions |
| Impact and traceability | Misses relevant dependencies or canonical ownership | Identifies some dependencies | Identifies canonical contract and proportionate downstream effects |
| Evidence and compatibility | Conflates contract, implementation, tests, or prior guarantees | Distinguishes them inconsistently | Clearly separates claims, evidence, compatibility, and unknowns |
| Execution and reporting | Unrelated edits, unsupported claims, or missing report | Mostly scoped, but report or validation is incomplete | Scoped work, coherent proposed diff, and accurate validation report |

## Pass criteria

- **Pass:** 8–10 points, with no zero in Semantic discipline or Evidence and compatibility.
- **Borderline:** 6–7 points, or any zero in a critical criterion; review manually and revise the instructions or fixture if needed.
- **Fail:** 0–5 points, or the agent silently invents/changes consequential behavior.

A score is not a substitute for reviewer judgment. Record short evidence for every score below 2. Evaluate the actual answer and diff; do not award points for merely mentioning expected terms.

## Run record

For reproducibility, record:

- repository commit SHA and fixture version;
- agent/model identifier and version;
- system/developer prompt or harness version;
- scenario prompt and complete output;
- proposed diff (if any);
- criterion scores, evidence, reviewer, and date.

Do not compare scores across different models or materially different harness prompts as if they were controlled runs. A model-based judge may assist triage, but consequential failures require human review.
