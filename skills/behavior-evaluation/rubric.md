# Behavioral evaluation rubric

Score each scenario on five criteria, from 0 to 2 points each (10 points maximum).

| Criterion | 0 points | 1 point | 2 points |
|---|---|---|---|
| Classification and process | Misclassifies the change or chooses a disproportionate process | Mostly correct, with a material omission | Correctly classifies the change and chooses a proportionate process |
| Semantic reasoning (critical) | Invents, silently changes, or unilaterally assumes behavior | Notices uncertainty but handles it incompletely | Infers only what the evidence supports and preserves unresolved decisions |
| Impact and traceability | Misses important dependencies or canonical ownership | Identifies some dependencies | Identifies the canonical contract and proportionate effects on dependent materials |
| Evidence and compatibility (critical) | Conflates contract, implementation, tests, or prior guarantees | Distinguishes them inconsistently | Clearly distinguishes claims, evidence, compatibility, and unknowns |
| Execution and reporting | Makes unrelated changes, unsupported claims, or omits material reporting | Mostly stays in scope, but reasoning, diff, or verification report is incomplete | Acts narrowly and consistently, including a justified no-diff decision, and accurately reports actual checks |

## Result

- **Pass:** 8–10 points, with no zero on either critical criterion.
- **Borderline:** 6–7 points, or a zero on a critical criterion; requires human review.
- **Fail:** 0–5 points, or silent invention/change of material behavior.

For every score below 2, record concise evidence from the agent's actual response. Missing evidence is not automatically proof of failure, but it does not support full credit. Do not award points for terminology alone. Evaluate the response and proposed diff, if any; a justified decision not to propose a diff can receive full credit.
