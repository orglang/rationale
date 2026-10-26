# Specification review and alignment plan

> **Status: in progress.** This plan organizes a follow-up review of the three preliminary research documents. It does not itself decide unresolved language semantics or claim implementation conformance.

## Progress

| Work item | Status | Result so far |
|---|---|---|
| Cross-document ownership | Initial pass complete | Canonical ownership and cross-document summaries checked; updated pages link to the owning documents rather than duplicating call/selection semantics. |
| Pool and transaction model | Initial pass complete | Replaced broad TODOs with working definitions, explicit status/limitations, and a question table identifying affected behavior and evidence needed. |
| Process creation boundary | Contract summary added | Added a concise `ExternalCall`/`InternalCall` comparison covering incarnation creation, channel identity transfer, continuation eligibility, pool association, commit points, and pre-commit failures. The existing detailed operation contracts remain canonical. |
| `Fwd` transition gaps | Initial pass complete | Added a polarity/pending-interaction review matrix without inventing transition semantics. |
| Implementation evidence | Partial source review; completeness unproven | The user confirms multiple process/call implementation attempts are incomplete. Code observations are retained as examples of partial attempts, not as a prerequisite to infer intended semantics or as evidence of a complete implementation. Full execution-path and test validation is not required to establish the spec's motivation and remains separate from semantic decisions. |
| Final cross-document/link review | Complete (documentation pass) | Checked local links and anchors, canonical ownership, duplicate definitions, scope consistency, and the full changed-file set. Automated tests were not run; implementation conformance remains unverified. |

## Goal

Make the three documents mutually navigable and sufficiently precise to support deliberate semantic decisions, while preserving the repository's distinction between intended OrgLang behavior, publication claims, and implementation evidence.

## Scope and ownership

- [Processes and session types](../about-processes-and-session-types/README.md) remains canonical for process expressions, session types, and the intended language-level contracts of `ExternalCall`, `InternalCall`, and `Fwd`.
- [Process creation and pool selection](../about-spawn/README.md) remains canonical for pool eligibility, search order, process-incarnation creation, pool binding, servicing, and agreement-search timeout.
- [Pools and transaction types](../about-pools-and-transaction-types/README.md) remains canonical for pool and transaction terminology, transaction types, and the pool's public transaction channel and protocol.
- [Documentation review standards](../DOCUMENTATION_STANDARDS.md) and [the semantic-spec workflow](../skills/semantic-spec/SKILL.md) govern the review process.

Do not duplicate canonical definitions or turn preliminary research into normative rules without an explicit decision and appropriate evidence.

## Work plan

### 1. Establish the cross-document contract map

- Inventory claims that cross the three document boundaries: process calls, incarnation creation, `SpawnSpec`, pool selection, eligibility, transaction types, provider channels, and the pool's public transaction channel.
- For each consequential claim, record its canonical owner, status (`Confirmed`, `Inferred`, or `Open`), evidence, and any implementation-coverage status separately.
- Check cross-references and summaries for accidental changes in meaning.
- Resolve only clear documentation inconsistencies in this pass; record unresolved semantic decisions as questions.

**Exit criteria:** each shared concept has one canonical owner, and cross-document summaries link to it without overstating the evidence.

### 2. Define the minimum pool and transaction model

Work in `about-pools-and-transaction-types/README.md`, preserving its preliminary status.

- Establish definitions, or record focused questions for review, for pool, pool term, transaction, transaction identifier, transaction type, public transaction channel, and the distinction between a pool transaction protocol and a process provider channel.
- Describe the intended pool model and its state/boundaries only to the extent supported by current decisions and sources.
- Identify the transaction-type constructors and their syntax, constraints, and interpretation only where evidence supports them; otherwise list the specific decisions needed.
- Clarify what is currently known about `Up`, the continuation, and `Down`, including that resource disposition after `Down` remains unspecified.
- Keep pool selection and servicing rules in `about-spawn/README.md`; link to them rather than duplicating them.

**Exit criteria:** core terms are defined or have actionable open questions; established behavior is separated from hypotheses; no unsupported constructor or lifecycle rule is introduced.

### 3. Specify the process-creation boundary

Work primarily in `about-spawn/README.md`, referring to the canonical call contracts in `about-processes-and-session-types/README.md`. The canonical call section now has a compact comparison table; detailed rules remain in the operation-specific subsections.

- Preserve the distinction between `ExternalCall`, `InternalCall`, engine-level incarnation creation, and pool servicing.
- Treat process-expression `SpawnSpec` as an unfinished implementation attempt, per the user's clarification; do not derive OrgLang semantics from it. Trace the intended complete process-spawning path separately from the publication's cut/spawn rule.
- Keep the agreed pool-selection sequence, first-suitable-agreement rule, timeout boundary, and delivery commit point intact unless new evidence reveals a conflict.
- Clarify only the state and ordering guarantees that are part of the agreed call contract, especially the pre-/post-delivery boundary. Do not specify error reporting, recovery, retries, or abnormal-termination semantics in this pass.
- Keep timeout configuration and the proposed `0 = infinite` convention open unless explicitly decided.

**Exit criteria:** the call/creation/servicing boundary is explicit; publication semantics are not presented as OrgLang semantics; pre-/post-commit state invariants are explicit. Error reporting, recovery, retry, and abnormal-termination semantics remain out of scope. The call contracts must state the created incarnation, channel bindings and identity preservation, source-incarnation lifecycle, pool association, commit point, and pre-commit failure behavior.

### 4. Specify process/session transition gaps

Work in `about-processes-and-session-types/README.md`.

- Formalize the reachable `Fwd` cases by polarity and pending-interaction state, including continuation behavior and one-shot linear endpoint consumption.
- Preserve the agreed `InternalCall` channel-transfer and incarnation-identity contracts; distinguish their intended meaning from unverified implementation behavior.
- Review linear-context invariants and branch-local `Case` typing decisions for clear preconditions, per-branch residual contexts, and completion obligations.
- Keep the contracts of `Acqure`, `Accept`, `Detach`, and `Release` open until their semantics have evidence or an explicit decision.
- Do not use AST presence or checker behavior alone as proof of language semantics.

**Exit criteria:** agreed transitions are stated in checkable terms; unresolved transitions specify reachable cases and expected evidence/tests.

### 5. Validate implementation evidence selectively

Inspect implementation only to answer concrete hypotheses raised by the semantic review.

- Trace relevant AST, type-checker, adapter, executor, and scheduling paths for `ExternalCall`, `InternalCall`, `Fwd`, `SpawnSpec`, and transaction/pool operations.
- Add or identify focused tests for reachable transitions, linearity, branch-local contexts, timeout races, and adapter/executor reachability where relevant.
- Record source paths, test names/results, and limitations. Distinguish missing coverage from a semantic decision.
- Avoid claiming end-to-end conformance unless the complete path and behavior are demonstrated.

**Exit criteria:** each implementation claim has specific source/test evidence or is explicitly marked unverified.

### 6. Final documentation review

- Verify links and heading anchors changed by the work.
- Check terminology, status labels, canonical ownership, duplicate definitions, contradictions, and examples affected by any decision.
- Review the complete diff against the branch base and remove unrelated changes.
- Run available relevant checks; report checks that could not be run.
- Keep semantic decisions, edits, commits, and validation results distinct.

**Exit criteria:** the diff is limited to the reviewed specifications and directly related references; unresolved decisions remain visible; no unsupported completion or conformance claim is made.

## Dependencies and decision gates

1. The contract map in Step 1 informs all subsequent edits.
2. The pool/transaction model in Step 2 is a prerequisite for fully specifying pool eligibility and transaction protocol behavior in Step 3.
3. Semantic questions that materially change behavior must be asked and resolved with the user rather than guessed. Independent evidence gathering may continue while a decision is open.
4. Do not make a document normative merely because its TODOs have been rewritten or its implementation has partial support.

## Initial priority

1. Define the minimum vocabulary and protocol boundaries in `about-pools-and-transaction-types/README.md`.
2. Trace the intended complete process-spawning path and identify what must replace or complete the unfinished `SpawnSpec` attempt, without conflating it with the publication's cut/spawn rule.
3. Specify the remaining `Fwd` transition cases and tests.
4. Validate pre-commit atomicity and implementation reachability, then perform the cross-document consistency pass.

## Out of scope

- Declaring a complete normative language specification in one pass.
- Inventing transaction-type constructors, pool lifecycle rules, timeout defaults, or failure semantics without an explicit decision or supporting evidence.
- Reworking unrelated documentation or implementation.
- Claiming tests or checks passed before running them.
