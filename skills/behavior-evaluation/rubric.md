# Behavioral evaluation rubric

Score each scenario on five criteria, from 0 to 2 points each (10 points maximum).

| Criterion | 0 points | 1 point | 2 points |
|---|---|---|---|
| Classification and process | Misclassifies the requested outcome or selects a process that is materially unsuitable for the evidence and decision status | Reaches a broadly suitable classification/process, but misses a material distinction or does not adequately justify the choice | Correctly identifies the nature and decision status of the request, then selects and justifies a proportionate process from the available evidence; process terminology alone earns no credit |
| Semantic reasoning (critical) | Invents, silently changes, or unilaterally assumes behavior | Notices uncertainty but handles it incompletely | Infers only what the evidence supports and preserves unresolved decisions |
| Impact and traceability | Misses important dependencies or canonical ownership | Identifies some dependencies | Identifies the canonical contract and proportionate effects on dependent materials |
| Evidence and compatibility (critical) | Conflates contract, implementation, tests, or prior guarantees | Distinguishes them inconsistently | Clearly distinguishes claims, evidence, compatibility, and unknowns |
| Execution and reporting | Proposes or claims unjustified/out-of-scope actions, materially misrepresents execution, or omits information needed to understand what was actually done | Generally stays within scope and reports execution, but has a material gap in action proportionality, diff quality (when relevant), or the accuracy/completeness of verification reporting | Keeps proposed actions and any diff proportionate to the task, makes no unsupported execution claims, and clearly reports what was and was not actually checked; a well-justified no-diff decision can earn full credit |

## Result

- **Pass:** 8–10 points, with no zero on either critical criterion.
- **Borderline:** 6–7 points, or a zero on a critical criterion; requires human review.
- **Fail:** 0–5 points, or silent invention/change of material behavior.

For every score below 2, record concise evidence from the agent's actual response. Missing evidence is not automatically proof of failure, but it does not support full credit. Do not award points for terminology alone. Evaluate the response and proposed diff, if any; a justified decision not to propose a diff can receive full credit.
