# Local OpenCode behavioral evaluations

This directory contains seven scenarios in `scenarios.jsonl` and the shared scoring rubric in `rubric.md`. The harness runs the **local OpenCode CLI** against the actual repository instructions. It does not call a model API directly and does not require a separate API key in the runner environment; provider credentials and model selection are managed by your OpenCode installation.

## Prerequisites

- Git and Python 3.10+
- OpenCode CLI installed
- At least one provider configured and authenticated in OpenCode
- A working Git checkout of this repository

Check the CLI and configured models:

~~~sh
opencode --version
opencode auth list
opencode models
~~~

OpenCode documents `opencode run --format json` as its non-interactive, machine-readable command. The scenario agent runs with `--auto` so approved local tools can be used without interactive prompts. The grader uses the `plan` agent by default and receives a temporary project config that disables its tools; it scores only the supplied evidence.

## Run

From the repository root:

~~~sh
python tests/agent-workflows/run_eval.py
~~~

Run one scenario or a selected set:

~~~sh
python tests/agent-workflows/run_eval.py --scenario 7
python tests/agent-workflows/run_eval.py --scenario 2 --scenario 5
~~~

Optionally select models in OpenCode's `provider/model` format and agent names:

~~~sh
python tests/agent-workflows/run_eval.py --model <provider/model> --grader-model <provider/model>
python tests/agent-workflows/run_eval.py --agent build --grader-agent plan
~~~

The default timeout is one hour per scenario-agent invocation (`--timeout SECONDS`) and 10 minutes per grader invocation (`--grader-timeout SECONDS`). The grader receives the captured evidence in an empty temporary workspace rather than the repository, so it should score the evidence instead of exploring project files. A timeout is reported as an error and the runner continues to the next scenario. The runner prints each scenario and its current phase, streams OpenCode stderr, reports tool-related events when available, and emits a 15-second heartbeat while either agent or grader is running.

## Execution model and isolation

For each scenario, the runner creates a detached Git worktree at the current `HEAD`. OpenCode receives the task and can inspect the real instruction files, use its configured local tools, edit files, and run checks. It is explicitly instructed not to commit or push. The runner captures the CLI JSONL event trace, final response, Git status, patch, and untracked-file contents.

Each scenario starts from a clean copy of the same commit, so one scenario cannot contaminate another. Changes are never applied to the user's active checkout. The worktree is removed after its patch and evidence have been collected. Uncommitted changes in the active checkout are not included; commit or otherwise preserve the snapshot you want to evaluate before running.

The grader runs as a separate OpenCode invocation using the `plan` agent by default. In its temporary workspace, the runner explicitly denies shell, file, search, task, and network tools for the selected grader agent; grading is based only on the supplied rubric and evidence. You can select another grader agent with `--grader-agent`; the same tool restrictions are applied to that agent for this invocation. Unless `--grader-model` selects another model, the agent and grader may use the same configured model. Model-based scoring is advisory, not an independent proof; review critical findings and saved evidence manually.

## Reports

By default, reports are written to `eval-results/`:

- `report.md` and `report.json`: summary and per-scenario scores;
- `scenario-N-agent.jsonl`: complete OpenCode agent event stream;
- `scenario-N-grader.jsonl`: grader event stream;
- the JSON report also includes final responses, Git status, and captured patches.

The runner returns a non-zero exit code if any scenario fails, is borderline, errors, or the agent exits unsuccessfully. A passing score does not replace human review.

## Scenario data format

`scenarios.jsonl` is the source of truth: one JSON object per line, with `input`, `expected_output`, and `additional_metadata` containing a stable unique integer `id`, a `title`, and a non-empty list of `failure_signals`. Optional maintenance fields belong in `additional_metadata`: omit `maintenance_status` (or set it to `active`) for current scenarios; use `review-needed`, `stale`, or `retired` when appropriate. For retired scenarios, add `maintenance_reason`. Keep shared scoring dimensions and score descriptions in `rubric.md`.

## Keeping scenarios current

Review affected scenarios whenever a change modifies or clarifies the normative contract, workflow instructions, documentation standards, skill routing, or a dependency that a scenario relies on. Also review when a run exposes a misleading premise, an untestable expectation, or an uncovered gap. No calendar-based review is required in the absence of such changes.

For each affected scenario, verify that its premise remains possible and representative; expected behavior and failure signals follow from canonical sources; referenced files and setup instructions still exist; the scenario is distinct; and its outcome can be assessed with the shared rubric.

Do not weaken an expected result merely to make a failing run pass. Determine whether the run exposed an agent failure, a changed contract, or a defective fixture. When changing or retiring a scenario, record the canonical change and rationale in the PR description. Keep the repository SHA and fixture version with each run so results from different snapshots are not conflated.
