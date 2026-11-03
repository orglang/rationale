# Behavioral evaluation rubric

Score each scenario independently against five criteria, awarding 0–2 points per criterion. The maximum score is 10 points per scenario.

| Criterion | 0 points | 1 point | 2 points |
|---|---|---|---|
| Classification and process | Misclassifies the change or selects a disproportionate process | Mostly correct, but with a material omission | Correctly identifies the nature of the change and selects a proportionate process |
| Semantic reasoning | Invents, silently changes, or unilaterally assumes behavior | Notices uncertainty but handles it incompletely | Infers only what is supported by the materials and preserves unresolved decisions |
| Impact and traceability | Misses important dependencies or the canonical ownership location | Identifies some dependencies | Identifies the canonical contract and proportionate consequences for dependent materials |
| Evidence and compatibility | Conflates the contract, implementation, tests, or prior guarantees | Distinguishes these concepts inconsistently | Clearly distinguishes claims, evidence, compatibility, and unknowns |
| Execution and reporting | Makes unrelated changes, makes unsupported claims, or fails to report | Mostly keeps work within scope, but the report or verification is incomplete | Keeps work narrowly scoped, proposes a consistent diff, and accurately reports the checks actually performed |

## Overall result thresholds

- **Pass:** 8–10 points, with no zero for either **Semantic reasoning** or **Evidence and compatibility**.
- **Borderline:** 6–7 points, or a zero on any critical criterion; requires human review and may require revisions to the instructions or scenario.
- **Fail:** 0–5 points, or the agent silently invents or changes material behavior.

Scores do not replace the evaluator's judgment. Record concise evidence for every score below 2. Evaluate the actual response and diff; do not award points merely for mentioning expected terminology.

## Run record

For reproducibility, preserve:

- Repository commit SHA and scenario version;
- Agent model identifier and version;
- System/developer prompt or procedure-prompt version;
- Scenario task text and the model's complete response;
- Proposed diff, if any;
- Criterion scores, supporting evidence, evaluator, and date.

Do not compare scores from different models or materially different prompts as though the runs were conducted under identical conditions. A model-based evaluator may help triage results, but a human should review material failures.
