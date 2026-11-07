# Calls and spawns

> **Status: preliminary semantic research.** This document owns named-process invocation and the creation of process Computation aggregates. It records intended OrgLang behavior separately from publication rules and implementation observations.

**Scope and document boundaries**

- This document owns `ExternalCall`, `InternalCall`, their channel-transfer and lifecycle contracts, and the generic semantics of creating a process Computation aggregate and its Execution.
- [Processes and session types](../about-processes-and-session-types/README.md) owns process declarations and definitions, process expressions, session types, process-channel protocols, and implementation evidence from the process AST/type-checker/executor.
- [Pools and transaction types](../about-pools-and-transaction-types/README.md) owns pool selection and servicing agreements, transaction types, and the `spawn` admissibility condition and its place in the transaction type.
- [Computations and channels](../about-incarnations-and-channels/README.md) owns the abstract computation, identifier, channel, endpoint, and substitution mechanisms used by these operations.

**Shared terminology:** see the [OrgLang glossary](../GLOSSARY.md).

## 1. Intended semantics of named-process calls

The following contract is the canonical statement of intended language-level behavior. Process declaration and definition interfaces are described in [Processes and session types, Section 4](../about-processes-and-session-types/README.md#4-process-declarations-and-definitions). The shared distinction between static obligations, runtime preconditions, and transition invariants is also defined there.

**This is the canonical statement of the intended language-level behavior.** Implementation field names are not OrgLang keywords; their correspondence to language-level roles is documented in Section 9.

#### Contract summary: creation, channel ownership, and commit

The rules below are the **working OrgLang contract adopted for this research draft**, independent of any current implementation. The detailed preconditions and commit-boundary rules follow in the operation-specific sections. This summary makes the shared model and the distinction between the two call forms explicit.

A call is not merely a jump to a named body. It resolves a process definition and, on success, creates a fresh **Computation** aggregate rooted at a fresh **Execution**. It also establishes which existing channel identities are bound in the target execution. A channel's identity and **type continuation** are preserved when its ownership is transferred; the transition changes the owning execution, not the identity of the channel itself.

| Property | `ExternalCall` | `InternalCall` |
|---|---|---|
| New Computation | Creates a fresh Computation aggregate rooted at a fresh Execution for the named process. | Creates a fresh Computation aggregate rooted at a fresh Execution for the named process. |
| Provider channel of target | Allocates a new, fresh provider channel. | Reuses the invoking execution's existing provider channel `X`. |
| Target client channels | Reuses supplied existing channels in declaration order. | Reuses supplied existing channels `Ys` in declaration order. |
| Source computation after success | Remains live; its continuation becomes eligible after it receives the new provider channel. | Terminates semantically; there is no language-level continuation for the old computation. |
| Pool association | Selects a suitable pool agreement for the named process. | Uses the invoking Computation aggregate's pool; no pool selection occurs. |
| Commit point | Delivery of the new provider channel to the caller. Before delivery, no target servicing or call-associated interaction or effect is allowed. | The single atomic transition at which the complete post-state becomes observable. |
| Pre-commit precondition failure | No partial Computation aggregate or channel transfer is observable. If the search-and-negotiation procedure times out or exhausts all candidate pools before a suitable existing agreement is found or a new agreement is successfully reached, no Computation aggregate or provider channel is created; the supplied client channels remain with the caller unchanged. | No partial transfer; the invoking Computation aggregate and its Execution bindings remain unchanged and no new live Computation aggregate is exposed. |
| Cancellation after commit | The search-and-negotiation timeout cannot cancel the call after a suitable existing agreement is found or a new agreement is successfully reached; post-delivery failure/recovery is outside this contract. | No cancellation that restores the old Execution's channel environment; runtime failure during/after commit is outside this contract. |

**Shared invariants on successful calls**

1. **Fresh aggregate-root identity:** every new Computation aggregate is rooted at an Execution whose identifier has never been allocated before; Execution root identifiers are never reused.
2. **Positional binding:** formal client-channel placeholders of the target are bound to the supplied channels in declaration order. The target provider placeholder is bound as described for the relevant call form.
3. **Linearity and no aliasing:** distinct formal channel parameters map to distinct channel identities. For `InternalCall`, `X` and `Ys` together account for the invoking Execution's complete channel environment.
4. **Channel preservation:** transferred channels keep their identities and type continuations; a call does not silently reset, replace, or advance a type continuation.
5. **No partial visible transition:** observers see the pre-state or the specified committed post-state, not partially changed channel ownership.
6. **Implementation independence:** these are intended language-level rules, not a claim that any existing implementation attempt completes them.

**Out of scope:** error reporting or propagation, recovery or retries after commit, and crash consistency.

The remaining uncertainty concerns two areas:

- **Intended but underspecified:** the broad behavior is stated here, but its precise rule, conditions, or edge cases still need to be written down and checked.
- **Design question:** the available evidence does not settle which behavior or mechanism OrgLang should choose. Resolving it requires an explicit design decision.

The operation-specific sections below provide the complete contracts for `ExternalCall` and `InternalCall`, including their distinct provider-channel behavior, commit points, and pre-commit failure guarantees. The table and shared invariants above are the concise cross-operation summary; avoid restating them here.

#### `ExternalCall`

**Before:** the caller is executing an `ExternalCall` expression, with its current channel environment and a continuation `ContExp` (the implementation field for the expression the caller should continue with).

**Agreed project contract:** This section records the intended OrgLang contract agreed for this research. Correspondence with a published language specification and conformance with the current implementation are tracked separately.

**Static obligations and runtime preconditions:**

- At the admission boundary, the callee definition must be resolvable in the program version being checked.
- Each supplied client channel must match the type and position of the callee's corresponding client placeholder.
- Distinct formal client parameters must map to pairwise distinct existing channel identities.
- The caller's designated placeholder for the new provider channel must have a type compatible with the target process's provider session type, accounting for the caller's client role.
- At execution time, the operation must be able to create a fresh Computation aggregate whose Execution root has an identifier that has never previously been allocated, and allocate a provider-channel identity that is fresh and distinct from all existing channels, including the supplied client channels.

**Static validation:** The shared rule in [Processes and session types, Section 4](../about-processes-and-session-types/README.md#4-process-declarations-and-definitions) applies. A channel/type mismatch, repeated channel identity, or invalid positional mapping is a static error when decidable from the program version and its channel-identity information at admission. Runtime allocation and freshness are runtime requirements, not static checks. The implementation's conformance remains unverified.

**Intended transition:**

1. Resolve the named callee process and map each formal client-channel parameter to the corresponding existing channel supplied by the call, in declaration order.
2. Ensure the static obligations listed above have been checked at the admission boundary, including strict session-type equality at both the target's client parameters and the caller's client-role placeholder for the new provider channel, under the applicable provider/client role convention. Session-type subtyping is out of scope for now. Check runtime preconditions when the relevant execution state and resources are available; they are not static validation.
3. Before creating the computation, search for a previously established agreement suitable for the named process. If none is found, proceed to negotiation with a candidate pool according to the applicable transaction type. The criterion for finding an existing agreement, first-match selection, traversal order, escalation to manual negotiation, and the shared search-and-negotiation timeout are specified as the process–pool boundary contract in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement).
4. Once a suitable existing agreement has been found or a new agreement has been successfully negotiated with a selected pool, create a fresh Computation aggregate rooted at a fresh Execution with its own execution state, together with a separate fresh provider channel, and associate the Computation aggregate with that pool. Bind the new Execution's client placeholders to the supplied channel identities and its provider placeholder to the fresh provider channel; designate that same fresh channel for delivery to the caller. The successful agreement establishes the terms under which the selected pool services the call; the shared search-and-negotiation timeout and its boundary are specified in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement). Until delivery, the supplied channels are held for the target and their type continuations remain unchanged, and the target cannot service the call or perform interactions or external effects on its behalf. The engine atomically transfers ownership and bindings for all channels involved in the call: the fresh provider channel to the caller and the corresponding channel bindings in the selected pool and new Execution. This is one indivisible operation; partial delivery is impossible. Delivery is the commit point and is required for successful completion of the call.

**After (intended):** the supplied client-channel identities and type continuations are preserved, and their use transfers to the new Execution; the caller's continuation relinquishes those channel identities. The caller may retain channels not supplied to the call. Its continuation becomes eligible when it receives the fresh provider channel through the designated placeholder, and then uses that channel's client endpoint according to its session type. The call produces no separate result value; the fresh provider channel is the only call-specific value delivered to the caller. The fresh provider channel is distinct from all supplied channels. General linearity and process-completion constraints from Section 2 still apply.

**Lifecycle and implementation status:** initiation, computation creation, atomic channel delivery, and servicing are distinct events. **Agreed project decisions:** in one indivisible operation, the engine transfers the fresh provider channel to the caller and the corresponding channel bindings in the selected pool and new computation. This atomic delivery is the commit point and completes the call. Once delivery occurs, both sides may proceed: the selected pool may begin servicing immediately, and the caller's continuation may use the fresh provider channel—including sending its first interaction before the pool takes its first action. The two sides may execute in either order or interleave, subject to session-type and linearity constraints. The call's only call-specific outcome is delivery of the fresh provider channel; it has no separate result value. The pre-delivery phase preserves the supplied channels' identities and type continuations and permits no call-associated interaction or external effect; actions that cannot be fully undone are excluded from this phase. The search-and-negotiation timeout boundary is specified in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement).

**Failure before commitment:** Delivery of the fresh provider channel to the caller remains the `ExternalCall` commit point. If the search-and-negotiation procedure times out or exhausts all candidate pools before a suitable existing agreement is found or a new agreement is successfully reached, no servicing pool is selected, neither a Computation aggregate nor a provider channel is created, and the supplied client channels remain with the caller with their original identities and type continuations. This failure occurs before Computation aggregate creation. Failure reporting and recovery remain unspecified. The timeout boundary and post-discovery behavior are specified in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement). This is the intended language-level contract; implementation conformance remains unverified.

The pre-commit failure and delivery contract preserves these invariants:

- **Channel-state integrity:** if the search-and-negotiation procedure times out or exhausts all candidate pools before finding or establishing a suitable agreement, supplied channel identities and type continuations remain unchanged with the caller.
- **Continuation eligibility:** the caller's continuation becomes eligible upon receipt of the fresh provider channel, as specified by the successful-call contract.
- **Commit boundary:** delivery is the commit point. The search-and-negotiation timeout cannot cancel a call after a suitable existing agreement has been found or a new agreement has been successfully reached, even if delivery is delayed.

General process/pool failure handling, recovery after a servicing computation fails, restart guarantees, and retry policy are outside the scope of this ExternalCall contract. The agreed contract excludes failure after successful atomic channel delivery; behavior of external infrastructure outside this agreed contract is not specified here.

**Timeout configuration and scope:** The search-and-negotiation timeout applies to `ExternalCall`; its boundary and unresolved configuration questions are documented in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement). The timeout policy does not guarantee eventual success or completion within a bounded time.

The inspected executor has no `ExternalCall` branch. The exact AST/runtime mapping among `CommChnlPH`, `ValChnlPHs`, and `NewChnlPH` remains open; see [Processes and session types, Part III](../about-processes-and-session-types/README.md#part-iii-implementation-evidence-and-open-questions). This is an implementation-mapping question, not an unresolved choice about the intended positional channel contract.

#### `InternalCall`

**Before:** the invoking process provides a service on an existing channel (AST field `X`). The target process also receives a list of channels it will use as a client (AST field `Ys`). The terms *provider channel* and *client channels* describe the channel roles relative to the process being discussed. Both refer to the same underlying kind of channel resource. The role descriptions are explanatory labels. Runtime field resolution is documented separately in the implementation analysis.

**Static obligations and runtime preconditions:**

- At the admission boundary, the target definition must be resolvable in the program version being checked.
- The supplied channels must match the types and positions of the target's corresponding placeholders.
- The supplied channel identities must be pairwise distinct, including no overlap between `X` and `Ys`.
- `X` and `Ys` must account for **all channel identities bound in the invoking Execution within Computation `P`**. After a successful call, no channel binding may remain attached to `P`.
- The binding environment of `P` follows the model-wide no-alias invariant: distinct bindings refer to distinct channel identities. This is not an `InternalCall`-specific condition.
**Static validation:** The shared rule in [Processes and session types, Section 4](../about-processes-and-session-types/README.md#4-process-declarations-and-definitions) applies. A channel/type mismatch, positional or arity mismatch, or repeated supplied channel identity (including overlap between `X` and `Ys`) is a static error when decidable at admission. The model-wide no-alias invariant applies here; it is not an additional `InternalCall` precondition. Set equality alone is not sufficient to establish that every binding in the environment has been transferred. The implementation's conformance remains unverified.

**Agreed channel-transfer and lifecycle decision:** On a successful transition, create a fresh Computation aggregate `Q`, rooted at a fresh Execution, at the start of the target definition, bind its provider placeholder to `X` and its client placeholders to `Ys` in declaration order, and record negative bindings for those channels in `P`. Because `X` and `Ys` account for the complete channel environment of the Execution within `P`, the old Computation aggregate semantically terminates without a language-level continuation. The precise atomicity, freshness, failure, and preservation invariants are consolidated below. This is the intended OrgLang behavior for this research document; conformance with the publication and current implementation is tracked separately.

**Commit and pool association:** The atomic transition is `InternalCall`'s commit point: once its complete post-state is observable, `P` has terminated and the transferred channels are positively bound in the target execution. `Q` uses the same pool as `P`; no pool selection occurs. Unlike `ExternalCall`, `InternalCall` has no timeout-driven cancellation phase or post-commit restoration of `P`'s environment. A failed precondition leaves the pre-state intact; runtime failure during or after commit remains outside this decision.

**Mini-example (schematic, not OrgLang syntax):** suppose process `Old` has provider placeholder `x` bound to channel `c`, and client placeholder `y` bound to channel `d`. `Old` performs `InternalCall` to process `New`, passing `c` as `X` and `d` in `Ys`. The transition unbinds both placeholders in `Old` and binds `New`'s corresponding placeholders to `c` and `d`; the channel identities are preserved.

The atomicity and failure contract is stated precisely below. Pool association and selection are specified separately in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement): `ExternalCall` selects a pool, while `InternalCall` uses the invoking computation's existing pool and does not select another one. Implementation questions are collected in [Processes and session types, Section 14](../about-processes-and-session-types/README.md#14-open-questions-and-next-tests).

**Atomicity boundary and failure behavior (intended contract):**

Treat the transition as a single state transition from a pre-state to a post-state, not as a sequence of externally observable mutations. Let the pre-state contain the live Computation aggregate `P`, its Execution and complete channel environment, and the target definition. A successful transition produces a fresh `Q` whose provider placeholder is bound to `X` and whose client placeholders are bound to `Ys` in declaration order; `P` is no longer live and has negative bindings for the transferred channels. Every transferred channel retains its identity and type continuation. No other Execution's bindings or channel state change as a side effect of the transition.

The atomicity guarantee is about semantic observability, not a requirement that the implementation use a particular lock, transaction, or storage primitive. An implementation may perform internal preparation before committing the transition, provided that preparation is not observable as a live computation or as changed channel ownership. The commit point is the single point at which the complete post-state becomes observable.

If a precondition fails before the transition commits—for example, the target cannot be resolved, the channel arity or positional mapping is invalid, channel identities are duplicated, or a type obligation fails—the operation does not partially transfer ownership: `P` remains live with its original bindings and no new live `Q` is exposed. Error reporting and recovery after failures that occur during runtime execution are not yet specified; this contract must not be read as claiming crash consistency or rollback across process or machine failure.

**Required invariants (intended contract):**

- **Freshness:** `Q`'s Execution root identifier has never been allocated to any Computation aggregate in the execution history, including terminated aggregates. Execution root identifiers are never reused.
- **Total transfer:** the invoking environment is injective, and the set of channel identities referenced by `P`'s bindings is exactly the set supplied by `X` and `Ys`; after commit, `P` has negative bindings for all transferred channels.
- **Exact rebinding:** each target placeholder is bound to the corresponding supplied channel identity, with `X` mapped to the provider placeholder and `Ys[i]` mapped to the i-th client placeholder.
- **Identity and type-continuation preservation:** transfer changes ownership/bindings, not channel identity or type continuation.
- **Binding ownership:** after commit, none of the transferred bindings remain attached to `P`; each transferred identity is bound to exactly its designated placeholder in `Q`. This does not remove the peer participant's binding to the same channel.
- **All-or-nothing visibility:** observers see either the complete pre-state or the complete post-state, never a partial combination.

**Focused conformance tests to add:** The following are test obligations for the implementation, not claims that current tests already pass.

1. **Complete transfer:** use a target with one provider placeholder and multiple client placeholders; assert the target receives the exact channel identities in declaration order and the old computation is no longer live.
2. **Type-continuation preservation:** give each supplied channel a non-initial type continuation; assert the transition does not reset, advance, or replace that state.
3. **Fresh identity and non-reuse:** assert `Q` receives an identity never previously allocated, including identities of terminated computations; repeat transitions after termination to verify that no identity is reused.
4. **Duplicate identity rejection:** supply the same channel identity twice, including the `X`/`Ys` overlap case; assert rejection leaves the pre-state unchanged.
5. **Missing or extra channels:** mismatch the target's client-placeholder count; assert no partial binding and no live target computation.
6. **Atomic observation:** pause or instrument execution around the implementation's commit boundary; assert no observer can see `Q` with a subset of bindings or see both `P` and `Q` live with transferred ownership.
7. **Failure before commit:** force target resolution or validation to fail; assert `P` retains all original bindings and no partially initialized `Q` is observable.
8. **Unrelated-state isolation:** keep a separate computation and channel active; assert its bindings and type continuation are unchanged by the transition.

These tests should exercise the adapter, type checker, executor, and persistence/scheduling path together where those layers participate. A unit test of the AST constructor alone is insufficient evidence of conformance.
**Implementation status:** the inspected dispatcher has no `InternalCall` execution branch; execution and type-checking are unverified. See Section 14 for the unresolved lifecycle and representation questions.

#### Boundary with pool semantics

Process invocation and computation creation are distinct from the pool mechanism that services a provider channel. Calls describe named-process and channel effects, while the pool's `Up … Down` transaction type describes interaction through the pool's public channel. The pool's public channel belongs to the pool. Pool association, selection, and eligibility are pool-level concerns documented in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement) and [Section 5](../about-pools-and-transaction-types/README.md#5-the-pools-public-transaction-channel). The discovery of an existing agreement and negotiation of a new one are described in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement); the detailed negotiation rules, reservation semantics, failure behavior when no eligible pool exists, and resource provisioning remain underspecified.

#### Abstract `ExternalCall` state at the process–pool boundary

This representation-independent view makes the state boundaries of `ExternalCall` explicit. It complements, and does not replace, the canonical call, ownership, and delivery contract above or the pool-selection and negotiation rules in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement).

| Phase | State represented | Observable boundary |
|---|---|---|
| Admission | The caller's live computation and current channel bindings; the resolved target process and validated client-channel mapping. | Admission creates neither a target computation nor a fresh provider channel. A failed admission leaves the caller's bindings unchanged. |
| Agreement search | The target process name and the logical transaction channels eligible for discovery. | Search reads only the latest committed allocation state for each logical transaction channel. It does not mutate that state or create a Computation aggregate or provider channel. |
| Candidate negotiation | The candidate pool and the active private attempt for its logical transaction channel, including its uncommitted allocation state. | The preceding committed private channel remains the search basis. The active attempt is not an established agreement before matched `Down`. Its initialization, commit, cancellation, and rollback rules are owned by [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement). |
| Agreement ready | A suitable existing committed agreement, or a newly committed agreement after matched `Down`, and the selected servicing pool. | The search-and-negotiation timeout no longer governs the call. Computation preparation and delivery follow; the call has not yet committed by delivery. |
| Delivery committed | The fresh computation, fresh provider channel, selected servicing pool, and transferred channel bindings. | One indivisible delivery gives the provider channel to the caller and the corresponding bindings to the pool and computation. This delivery is the `ExternalCall` commit point; partial delivery is not observable. |
| Servicing | The live computation associated with the selected pool and the provider channel received by the caller. | The caller's continuation and pool servicing may proceed in either order or interleave, subject to channel protocols and linearity. |

The transitions preserve these boundaries:

1. **Admission → search:** resolve the target and validate the supplied channel mapping. Failure leaves the caller's existing bindings unchanged.
2. **Search → agreement ready:** select a suitable committed agreement if one is found. Search alone does not create a Computation aggregate or provider channel.
3. **Search → candidate negotiation:** if no suitable committed agreement is found, try candidate pools under the single timeout. A matched `Up` starts a fresh private attempt initialized from that candidate pool's `Q⁰`; it does not copy the previous committed allocation state. The previous committed private channel remains current for search until matched `Down`.
4. **Candidate negotiation → agreement ready:** only matched `Down` commits the prepared allocation state and makes the negotiated agreement current. Cancellation, candidate exhaustion, or timeout before this point ends the attempt/call without creating either the target Computation aggregate (rooted at its Execution) or a fresh provider channel. Supplied client channels remain with the caller.
5. **Agreement ready → delivery committed:** prepare the fresh Computation aggregate rooted at its Execution, and provider channel, then atomically deliver the provider channel to the caller together with the corresponding channel bindings to the selected pool and Execution. Delivery, not agreement readiness or computation preparation, commits the call.
6. **Delivery committed → servicing:** both caller and selected pool may take their first interactions without waiting for the other side's first action.

**Required state separation:** the active uncommitted negotiation attempt, the latest committed agreement, the prepared-but-not-delivered computation, and the delivered live computation are distinct states. An active attempt cannot be used as an established agreement; a prepared computation is not yet a successfully delivered call.

**Conformance scenarios:** implementation tests should inspect observable state at each boundary, not merely whether an operation returned successfully.

- If a suitable committed agreement already exists, search selects it without changing its allocation state or creating a negotiation attempt, computation, or provider channel.
- If `Coop` or `Isol` changes an active candidate's uncommitted state, that state remains invisible to agreement search until matched `Down`. Before that match, cancellation discards the attempt and preserves the preceding committed agreement.
- Matching provider `detach` with client `release` at `Down` commits the prepared allocation state and makes the candidate private channel the latest committed private channel.
- If no suitable agreement is found and negotiation is canceled, candidates are exhausted, or the shared timeout expires before agreement readiness, neither the target Computation aggregate (rooted at its Execution) nor a fresh provider channel is created; the caller retains the supplied client-channel identities and type continuations.
- Delivery exposes the fresh provider channel and corresponding pool/computation bindings as one atomic transition. After delivery, either side may perform its first interaction first.

**Deliberately unresolved interval:** the contract does not yet determine recovery if the engine fails after an agreement becomes ready but before delivery commits. The implementation may later choose discard, retry, or recovery semantics; this model does not assert one of those outcomes as language conformance.

## 2. Process spawning and the pool transaction type

The word **spawn** appears in the pool transaction-type model and in several implementation representations. These must not be conflated with the two named-process call forms.

**Pool-level contract:** the transaction-type constructor for `spawn` admits spawning process `q` on logical transaction channel `c` only when the current allocation function satisfies `Q(q) > 0`. The operation does not itself change `Q`; its continuation retains the stated allocation state. The grammar, state-indexed rule, and typing condition are owned by [Pools and transaction types, Formal grammar and state-indexed rules](../about-pools-and-transaction-types/README.md#formal-grammar-and-state-indexed-rules).

**Boundary with computation creation:** this condition establishes when the pool transaction type permits the spawn request. It does not, by itself, specify the complete runtime procedure for allocating a Computation aggregate and its Execution, constructing the execution state, binding its channel environment, attaching a process body, or making the resulting state observable. Those generic creation mechanics belong to this document and must be specified without duplicating the pool's eligibility rule.

**Current semantic status:** the generic runtime transition for pool-level `spawn` remains open. The available material distinguishes:
- the pool transaction-type constructor, whose admissibility condition is specified by `Q(q) > 0`;
- the process-expression AST constructor `SpawnSpec`, which is an unfinished implementation attempt and is not an established user-facing call form;
- the pool API operation `Spawn`, which creates an execution record but does not by itself establish the complete process-body and channel-wiring transition;
- the separate `proto/rast2` prototype reduction, which is not evidence of current OrgLang runtime behavior.

No equivalence among these representations is assumed. The process AST, adapter, type-checker, and executor findings are documented in [Processes and session types, Part III](../about-processes-and-session-types/README.md#part-iii-implementation-evidence-and-open-questions). The pool API and transaction-type evidence remain in [Pools and transaction types](../about-pools-and-transaction-types/README.md).

## 3. Open questions

1. What is the complete generic runtime transition for creating a fresh process computation, including execution-state initialization and process-body attachment?
2. How does pool-level `spawn` supply and bind the new computation's provider and client channel environment?
3. What is the relationship, if any, between pool-level `spawn` and process-expression `ExternalCall` / `InternalCall` beyond their shared concern with computation creation?
4. Which implementation representation, if any, will replace the unfinished process-expression `SpawnSpec` attempt?
5. What are the required atomicity and failure guarantees for pool-level spawning, and which component owns each boundary?
