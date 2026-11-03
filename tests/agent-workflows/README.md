# Local Codex behavioral evaluations

This directory contains seven scenarios in `scenarios.jsonl` and the shared scoring rubric in `rubric.md`. The harness runs the **local Codex CLI** against the actual repository instructions; it does not call the Responses API directly and does not require an API key in environment variables.

## Prerequisites

- Git and Python 3.10+
- Codex CLI installed and authenticated on the local machine
- A working Git checkout of this repository

Check the CLI with `codex --version`. Authenticate using the Codex sign-in flow supported by your installation. The runner uses `codex exec --json --full-auto` for the agent and a separate read-only `codex exec` for rubric grading.

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

Optionally select models exposed by your Codex CLI configuration:

~~~sh
python tests/agent-workflows/run_eval.py --model <agent-model> --grader-model <grader-model>
~~~

The default timeout is one hour per Codex invocation; override it with `--timeout SECONDS`.

## Execution model and isolation

For each scenario, the runner creates a detached Git worktree at the current `HEAD`. Codex receives the task and can inspect the real instruction files, use its available local tools, edit files, and run checks. It is explicitly instructed not to commit or push. The runner captures the CLI JSONL event trace, final response, Git status, patch, and untracked-file contents.

Each scenario starts from a clean copy of the same commit, so one scenario cannot contaminate another. Changes are never applied to the user's active checkout. The worktree is removed after its patch and evidence have been collected. Uncommitted changes in the active checkout are not included; commit or otherwise preserve the snapshot you want to evaluate before running.

The grader runs as a separate Codex invocation with read-only sandbox permissions and receives the rubric plus execution evidence. Unless `--grader-model` selects another model, Codex may use the same configured model for agent and grader. Model-based scoring is advisory, not an independent proof; review critical findings and the saved evidence manually.

## Reports

By default, reports are written to `eval-results/`:

- `report.md` and `report.json`: summary and per-scenario scores;
- `scenario-N-agent.jsonl`: complete Codex agent event stream;
- `scenario-N-grader.jsonl`: grader event stream;
- the JSON report also includes final responses, Git status, and captured patches.

The runner returns a non-zero exit code if any scenario fails, is borderline, errors, or the Codex agent exits unsuccessfully. A passing score does not replace human review.

## Scenario data format

`scenarios.jsonl` is the source of truth: one JSON object per line, with `input`, `expected_output`, and `additional_metadata` containing a stable unique integer `id`, a `title`, and a non-empty list of `failure_signals`. Optional maintenance fields belong in `additional_metadata`: omit `maintenance_status` (or set it to `active`) for current scenarios; use `review-needed`, `stale`, or `retired` when appropriate. For retired scenarios, add `maintenance_reason`. Keep shared scoring dimensions and score descriptions in `rubric.md`.

## Keeping scenarios current

Review affected scenarios whenever a change modifies or clarifies the normative contract, workflow instructions, documentation standards, skill routing, or a dependency that a scenario relies on. Also review when a run exposes a misleading premise, an untestable expectation, or an uncovered gap. No calendar-based review is required in the absence of such changes.

For each affected scenario, verify that its premise remains possible and representative; expected behavior and failure signals follow from canonical sources; referenced files and setup instructions still exist; the scenario is distinct; and its outcome can be assessed with the shared rubric.

Do not weaken an expected result merely to make a failing run pass. Determine whether the run exposed an agent failure, a changed contract, or a defective fixture. When changing or retiring a scenario, record the canonical change and rationale in the PR description. Keep the repository SHA and fixture version with each run so results from different snapshots are not conflated.
