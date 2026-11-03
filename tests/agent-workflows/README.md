# Agent workflow evaluations

This directory contains seven controlled behavioral scenarios in `scenarios.jsonl` and a shared human-readable scoring rubric in `rubric.md`.

## What is automated

The repository CI validates Markdown formatting, local links, and Python syntax. A separate, manually dispatched GitHub Actions workflow runs the scenarios against an OpenAI model and evaluates each rubric criterion with DeepEval G-Eval using a second, different model.

## Run locally

Install the pinned evaluation dependencies:

~~~sh
python -m pip install -r tests/agent-workflows/requirements-eval.txt
~~~

Configure credentials and model IDs, then run:

~~~sh
export OPENAI_API_KEY="..."
export OPENAI_EVAL_MODEL="model-id-for-agent"
export OPENAI_EVAL_GRADER_MODEL="different-model-id-for-grader"
export DEEPEVAL_TELEMETRY_OPT_OUT="YES"

python tests/agent-workflows/run_eval.py
~~~

Run one scenario with --scenario 7. Reports are written to eval-results/report.json and eval-results/report.md.

The runner sends the tracked Markdown documentation in the checked-out repository and the selected scenario to the agent model through the OpenAI Responses API. DeepEval then scores each of the five rubric criteria independently with G-Eval. The grader model ID must differ from the agent model ID. A full seven-scenario run makes one agent request and five judge evaluations per scenario; judge calls and cost are therefore higher than the previous single-call grader.

## Configure GitHub Actions

1. In repository **Settings → Environments**, create an environment named behavioral-evals.
2. Add OPENAI_API_KEY as an environment secret. Do not add it as a general repository secret.
3. Configure at least one required reviewer for this environment before storing the key. The workflow checks out and runs code from the selected ref, so the approval gate is the trust boundary for evaluating branches that are not yet trusted.
4. Open **Actions → Agent workflow evaluations → Run workflow**.
5. Supply distinct agent and grader model IDs and the branch, tag, or commit SHA to evaluate.
6. Download the agent-workflow-evaluation artifact to inspect the JSON and Markdown reports.

The workflow is manual by design: it does not expose the API key to arbitrary pull-request code through a pull_request trigger. GitHub makes workflow_dispatch available only after the workflow file exists on the default branch, so this action becomes available after the PR is merged. Do not approve a run until the selected ref and its workflow/runner changes have been reviewed.

## Evaluation limits

The runner is a first, text-only harness. It gives the tested model the repository's Markdown snapshot and asks for a response or proposed diff. It does not expose GitHub, shell, filesystem-write, or other tools to the model; proposed diffs are not applied and tests are not run.

DeepEval G-Eval is used for subjective, criterion-specific assessment, not as a deterministic proof. The runner maps normalized G-Eval scores to the rubric's 0/1/2 scale and applies the existing pass/borderline/fail thresholds, including critical-failure gates. G-Eval is nondeterministic; scores can vary between runs. The complete response, per-criterion evidence, model IDs, repository SHA, and framework version must be reviewed together. A passing score is advisory and does not replace human review.

The runner fails closed when an API call or grading step fails. It does not depend on a Confident AI account; DeepEval runs locally with the configured LLM provider key. Telemetry is disabled in the provided workflow.

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

A scenario without a status annotation is **active**. Add **Maintenance status: review-needed** directly below its heading when a relevant change has occurred but its expected behavior has not yet been revalidated. Use **Maintenance status: stale** when its premise or expected behavior no longer matches the current sources; do not count it as active coverage until corrected. Use **Maintenance status: retired** when the scenario is intentionally no longer useful, and state the reason and replacement (if any). Remove the annotation once a review confirms the scenario is active again.

When changing or retiring a scenario, include in the PR description which canonical change prompted the review and why the fixture was updated. Keep the run record's repository SHA and fixture version so results from different snapshots are not conflated.
