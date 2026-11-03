# Agent workflow evaluations

This directory contains seven controlled scenarios and a shared scoring rubric for the specification workflows.

## What is automated

The repository CI validates Markdown formatting and local links.

## What is not automated

The seven scenarios are **behavioral evaluations**, not ordinary unit tests. They require an agent to read the instruction set and produce an answer and, where applicable, a proposed diff. The repository currently has no configured model/API runner, fixed model version, or trusted automated judge. CI therefore does not claim to execute these scenarios or certify agent behavior.

Run them manually using [`MANUAL_RUN.md`](MANUAL_RUN.md) and the [manual-behavioral-evaluation skill](../../skills/manual-behavioral-evaluation/SKILL.md). The skill defines a coordinator-led, SHA-pinned ChatGPT procedure: one fresh agent chat per scenario, the complete agent response returned to the coordinator, and rubric-based evaluation in the coordinator conversation. No separate evaluator chat, manually completed run-record template, or separate diff attachment is required. The coordinator instructions are in English; tested-agent prompt templates and scenario tasks remain in Russian. The scenario fixtures are in [`scenarios.md`](scenarios.md); score with [`rubric.md`](rubric.md). Keep the agent run blind to expected behavior and rubric. A future runner should pin the model and harness, capture outputs/diffs, and use the rubric; it should not replace semantic review with keyword matching.

## Keeping scenarios current

Review the affected scenarios whenever a change modifies or clarifies the normative contract, workflow instructions, documentation standards, skill routing, or a dependency that a scenario relies on. A review is also needed when a run exposes a misleading premise, an untestable expectation, or a gap not covered by the current scenarios. No calendar-based review is required in the absence of such changes.

For each affected scenario, check that:

- its premise and task are still possible and representative in the current repository;
- expected behavior and failure signals follow from the current canonical sources, rather than from the scenario's own wording or implementation observations;
- referenced files, workflow names, and setup instructions still exist;
- the scenario remains distinct and adds useful coverage; and
- its expected result can still be assessed with the shared rubric.

Do not weaken an expected result merely to make a failing run pass. First determine whether the run exposed an agent failure, a changed contract, or a defective fixture; record the evidence and update the scenario only when the canonical sources justify it.

### Scenario status

A scenario without a status annotation is **active**. Add `**Maintenance status:** review-needed` directly below its heading when a relevant change has occurred but its expected behavior has not yet been revalidated. Use `**Maintenance status:** stale` when its premise or expected behavior no longer matches the current sources; do not count it as active coverage until corrected. Use `**Maintenance status:** retired` when the scenario is intentionally no longer useful, and state the reason and replacement (if any). Remove the annotation once a review confirms the scenario is active again.

When changing or retiring a scenario, include in the PR description which canonical change prompted the review and why the fixture was updated. Keep the run record's repository SHA and fixture version so results from different snapshots are not conflated.
