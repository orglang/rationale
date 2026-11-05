# Instruction stress-test redesign

**Status:** sequential evaluation plan.  
**Purpose:** test whether repository instructions prevent specific, observable failures that appear without those instructions.

## Decisions

1. Keep the existing AWF scenarios in place as regression coverage and historical comparators. Do not delete or rewrite them, or reuse their IDs for new scenarios.
2. Add and validate any new scenario strictly **one at a time**. Do not draft or queue a batch of future scenarios.
3. Do not start a new scenario until the current one has a documented calibration result and an explicit keep/revise/retire decision.
4. Do not assign a stable AWF ID until the scenario fixture is complete, source-grounded, and passes setup validation.

The existing AWF-001, AWF-003, AWF-004, and AWF-007 results remain historical evidence. Their near-ceiling scores mean they are not useful primary stress tests, but they remain available as regression smoke tests.

## One-at-a-time workflow

For each candidate:

1. Choose one concrete failure mode and the one instruction mechanism that is supposed to prevent it.
2. Build one minimal fixture against a pinned repository snapshot. Keep the task prompt blind to evaluator-only expectations.
3. Validate the fixture before any tested-agent run: source facts, task completeness, prompt separation, objective scoring, and prohibited side effects.
4. Run the scenario under A first: optional project instructions are not explicitly activated.
5. Review the observed target behavior. If the model passes, decide whether the scenario is genuinely diagnostic or whether it disclosed the answer / did not create a meaningful decision boundary. If it fails, determine whether the failure is reproducible and whether the relevant instruction plausibly addresses it.
6. Record one of three decisions: **keep**, **revise and recalibrate**, or **retire**. A material fixture revision creates a new fixture version and restarts calibration.
7. Only after the scenario is accepted should the user and coordinator agree whether to run the instruction comparison (A/B/C) for that scenario.
8. Only after the current scenario is closed should work begin on the next candidate.

Do not create evaluation Issues or run a batch before the user agrees to the specific scenario and run matrix.

## What an independent pilot run means

A pilot run is one execution of the **same scenario** under condition A. Five pilot runs, if chosen, means:

- the exact same task prompt and pinned source materials are used five times;
- each execution starts in a genuinely fresh tested-agent context, with no conversation history or answer from another run;
- model, relevant settings, available tools, permissions, and instruction activation are kept the same;
- the agent receives the task once and is not coached or given follow-up clarification;
- each complete response and any actual side effects are captured separately.

These are five repetitions of one scenario, **not five different scenarios**, and not five messages in one chat. Separate GitHub Issues do not prove context independence. The operator must actually start a new context for each execution and record the available provenance.

Independent contexts do not make model outputs statistically independent in a strict scientific sense. They reduce direct carry-over between runs; shared model versions, infrastructure, hidden runtime state, and other uncontrolled factors may remain. Record these limitations rather than claiming perfect independence.

## Pilot size: adaptive, not automatic

Do not require five runs for every candidate by default. Start with one baseline run for the single scenario under consideration.

- If the first run reveals a severe, objectively verifiable boundary violation, preserve the evidence and replicate in fresh contexts before making a general claim. A single severe event can justify keeping the scenario for further investigation, but not a confident estimate of failure frequency.
- If the first run passes, inspect whether the fixture was diagnostic and whether the task accidentally disclosed the expected behavior. If the setup remains sound, use additional fresh-context repetitions to distinguish a stable pass from a chance pass.
- Use up to five baseline runs as a practical screening target when the decision remains uncertain. Stop earlier only when the keep/revise/retire decision is adequately supported; run more when outcomes are mixed.
- Report raw counts (for example, 1 failure in 3 runs), not a precise failure probability or a statistical equivalence claim.

The pilot is a screening procedure, not a statistical proof. Do not tune the task repeatedly against the same tested context.

## Candidate directions

Select only one direction when starting a new scenario. These are ideas, not approved fixtures or stable AWF IDs:

- conflicting authority and instruction precedence;
- a false factual premise that must be checked against a pinned source;
- materially ambiguous authorization requiring clarification;
- tempting scope expansion beyond the requested change;
- an explicit no-write boundary;
- incomplete or non-equivalent evidence requiring calibrated uncertainty;
- a workflow action whose required precondition or authorization is missing.

Do not combine several mechanisms merely to make a task difficult. A scenario should isolate one primary behavior so that a difference between conditions is interpretable.

## Fixture requirements

Every scenario proposed for calibration must contain:

1. A concise title and, only after acceptance, a stable scenario ID.
2. A Russian task prompt that states the requested outcome without revealing evaluator expectations.
3. A pinned, minimal, task-relevant source snapshot available identically across conditions.
4. One primary target behavior and objective evaluator-only acceptance checks.
5. Observable failure signals, including prohibited side effects where applicable.
6. Source-grounded reasoning for why the targeted instruction applies.
7. A setup verdict: Valid, Valid with limitations, or Invalid.
8. A targeted primary outcome separate from the common five-criterion rubric.

The prompt must not name the instruction under test, prescribe the expected process, or reproduce evaluator-only acceptance wording.

## Instruction comparison

After one scenario has passed calibration and been accepted, compare A/B/C only if that comparison is useful and the setup can be controlled.

- Use the same immutable fixture, prompt, source snapshot, model, and relevant settings.
- Use a fresh tested-agent context for every run.
- Record which instruction roots were explicitly activated and which files were actually resolved.
- Do not infer context isolation from separate Issues or different timestamps.
- Pre-register the expected behavioral change, primary outcome, critical boundary violations, repetitions, and stopping rule.
- Preserve all runs, including incomplete captures and regressions.
- If all conditions pass, report no demonstrated instruction effect on this fixture. If B/C perform worse, record the regression.

## Measurement

Keep these measures separate:

- **Primary target outcome:** whether the specific behavior under test occurred.
- **Critical boundary violations:** unauthorized writes, irreversible actions without preconditions, or unsupported claims of completed work.
- **Five-criterion rubric:** broad response quality.
- **Execution/provenance:** context independence, model/settings, activation, permissions, prompt identity, response capture, and actual side effects.

Do not collapse them into one average. A high rubric score must not mask a critical boundary violation. A capture failure is not automatically a behavioral failure.

## Completion record

For each scenario, preserve its pinned fixture, setup verdict, exact prompt, pilot count and outcomes, context/model/settings provenance (to the extent known), keep/revise/retire decision, and limitations.

No new scenario, Issue, score, or causal claim is created by this plan alone.
