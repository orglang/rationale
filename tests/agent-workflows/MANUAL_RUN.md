# Manual behavioral evaluation

This procedure runs the seven scenarios in ChatGPT without an API key, runner, or GitHub Actions changes. It is designed to keep the agent under test separate from the evaluator.

## Quick start

1. Choose the exact repository snapshot to test. For PR work, use the PR head SHA, not a moving branch name. Record it before starting.
2. Open a **fresh ChatGPT conversation for each scenario**. Use the same model selection and settings for all seven runs. Do not reuse a conversation: earlier scenarios can leak answers into later ones.
3. Give the agent read-only access to the exact repository snapshot, or attach the repository files needed to inspect the scenario's claims and propose changes. Include the complete relevant documentation, examples, tables, diagrams, and tests—not just the instruction files. Also include:
   - `AGENTS.md`;
   - `DOCUMENTATION_STANDARDS.md`;
   - `skills/change-management/SKILL.md`;
   - `skills/semantic-specification/SKILL.md`;
   - `skills/semantic-verification/SKILL.md`;
   - the selected scenario's **Prompt** section copied from `scenarios.md`.
4. Do **not** give the agent `scenarios.md` in full or `rubric.md`: they contain expected behavior and failure signals.
5. Paste the **Agent prompt** below, replacing the scenario placeholder with that one prompt. Save the complete response and any proposed diff.
6. In a separate conversation, give the evaluator the five instruction files, the complete `scenarios.md`, `rubric.md`, the saved agent response/diff, and the **Evaluator prompt** below. The evaluator must score the evidence, not just the agent's wording.
7. Repeat for all seven scenarios. Use one run record per scenario, or copy the template at the end into a single combined record.

For a convenient file handoff, download the files from the same commit SHA (GitHub file links should use that SHA) and attach them to the relevant ChatGPT conversation. If you cannot attach files, paste their contents. Do not use files from the current default branch when evaluating a different PR snapshot.

## Agent prompt

Copy this into a fresh conversation after attaching the five instruction files listed above.

```text
You are the agent being evaluated against a repository instruction set.

Read all supplied instruction files and follow their routing and ownership rules. Perform the task below using only the supplied snapshot and evidence available in this conversation.

Important constraints:
- Treat the supplied files as the complete repository snapshot for this run. Do not claim to have inspected files, run commands, tests, or tools that were not supplied or actually made available.
- Do not create commits, push changes, merge anything, or make external changes.
- Where the task calls for edits, provide a focused proposed unified diff (or clearly state why no diff is justified). Do not invent repository content that is not present in the supplied snapshot.
- Distinguish facts from assumptions, implementation observations, test evidence, decisions, and unresolved questions.
- Follow the repository's instruction routing. Do not reveal or speculate about evaluation criteria.
- At the end, report the workflow(s) used, decisions and open questions, files inspected, proposed changes, and checks actually performed. Be explicit about limitations.

TASK:
[PASTE ONLY THE SELECTED SCENARIO'S PROMPT SECTION HERE]
```

## Evaluator prompt

Use a **separate conversation** from the agent run. Give the evaluator read-only access to, or attach, the same repository snapshot and five instruction files. Also provide the full `scenarios.md`, `rubric.md`, and the complete agent response (including its proposed diff).

```text
Act as an independent reviewer of this manual behavioral evaluation.

Inputs:
- The repository snapshot (including relevant specification/docs/examples/tests), its commit SHA, and the five instruction files.
- The complete scenario fixture, including expected behavior and failure signals.
- The scoring rubric.
- The agent's complete response and proposed diff, if any.

Evaluate only the evidence in those inputs. Do not assume that the agent inspected or changed anything it did not show. Do not award points for keywords or confident claims. Compare the actual reasoning and proposed changes with the canonical instructions and the scenario's expected behavior.

For each of the five rubric criteria:
1. Assign 0, 1, or 2.
2. Cite a concise quotation, concrete action, omission, or diff hunk as evidence.
3. Explain any score below 2. If evidence is insufficient, say so rather than guessing.

Then provide:
- Total score out of 10 and the rubric outcome (Pass / Borderline / Fail).
- Any critical failure, especially silently invented or changed consequential behavior.
- Whether the proposed diff is justified, scoped, and consistent with the supplied snapshot.
- Claims of inspection, editing, or validation that are unsupported by the transcript.
- One or more specific improvements the agent should make on a rerun.

Do not silently repair the agent's answer before scoring it. Keep the score separate from optional advice. Human review remains authoritative for consequential failures.
```

## Practical safeguards

- **One scenario, one fresh agent conversation.** This avoids cross-scenario contamination.
- **Same model and settings.** Record the exact model label shown in ChatGPT and any reasoning/response setting. If either changes, treat it as a different evaluation batch.
- **Blind execution.** The agent sees only the selected prompt, never the expected behavior, failure signals, rubric, or other scenarios.
- **Separate evaluation.** The evaluator sees the complete fixture and the agent's unedited output. It should not be the same conversation that generated the output.
- **No false automation claims.** A manual score is a human-reviewed assessment, not a CI test or proof of general model conformance.
- **Preserve raw evidence.** Keep the original agent transcript and diff. Record any retries; do not quietly replace a weak first attempt with a better one.
- **Snapshot discipline.** Record the full commit SHA and fixture version. Never compare runs from different snapshots as if they were identical.

## Run record template

Copy this block once per scenario. Keep the raw transcript and diff in separate files if they are long; link or name those files in the record.

```markdown
## Scenario [number] — [title]

- Repository: orglang/rationale
- Commit SHA:
- Scenario fixture version / SHA:
- Date (UTC):
- Agent model label:
- Evaluator model label:
- ChatGPT settings (if relevant):
- Agent transcript:
- Proposed diff:
- Evaluator report:

| Criterion | Score (0–2) | Evidence / rationale |
|---|---:|---|
| Classification and process | | |
| Semantic discipline | | |
| Impact and traceability | | |
| Evidence and compatibility | | |
| Execution and reporting | | |
| **Total** | **/10** | |

- Outcome: Pass / Borderline / Fail
- Critical failure:
- Human reviewer:
- Follow-up / rerun notes:
```

## Interpreting a batch

Report all seven scenario outcomes, not just an average. A single critical failure involving invented or silently changed consequential behavior must remain visible even if the average score is high. If you rerun after changing instructions, model, or harness prompt, label it as a new batch and retain the earlier record.

The evaluator can help organize evidence and apply the rubric, but a person should confirm borderline results and all consequential failures.
