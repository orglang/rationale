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

For every score below 2, record concise evidence from the agent's actual response comment. Missing evidence is not automatically proof of failure, but it does not support full credit. Do not award points for terminology alone. Evaluate the response and proposed diff, if any; a justified decision not to propose a diff can receive full credit.

## Run and grading completeness

These statuses are independent of the numeric rubric result:

- **Run completeness** concerns whether the planned one-shot attempt was executed with the intended prompt/context and its complete final response was captured verbatim in a new comment on the correct Run Issue by the tested agent. Record the comment permalink, author, and timestamp. A refusal or incorrect answer is still a complete run if the complete answer was successfully published. An interrupted attempt, wrong prompt/context, missing final answer, absent comment, wrong Issue, or truncated/corrupted comment makes the run incomplete.
- **Grading completeness** concerns whether the coordinator completed all five criterion scores with evidence, all applicable scenario-specific and cross-scenario checks, and the result/critical-failure rules. It is incomplete while any of that assessment remains outstanding.

Do not assign a behavioral **Fail** or zero score merely because execution or response-comment capture failed. If an incomplete run prevents a defensible assessment, report **not evaluable** and explain why; do not manufacture a rubric result. Conversely, missing evidence in an otherwise complete response is assessed as received: use **not verifiable** for checks that cannot be established and score the demonstrated omission under the relevant criterion. It does not make the run incomplete.

GitHub Issue comments are editable/deletable by users with sufficient repository permissions and are not immutable evidence. Record the provenance observed at verification time and note any subsequent edit/deletion. The coordinator must not publish or rewrite the tested agent's response comment on its behalf. After all responses in the evaluation batch have been captured, publish the coordinator assessment as a separate top-level comment on the same Run Issue. Label it `Coordinator assessment — RUN-XX`; include the response comment permalink and keep the two comments distinct. Do not publish assessments before the batch is closed, because visible assessments can influence later runs. Coordinator assessment comments are visible to repository collaborators and are not confidential.
