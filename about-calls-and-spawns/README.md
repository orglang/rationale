# Calls and spawns

> **Status: preliminary semantic research.** This document owns named-process invocation and the creation of process incarnations. It records intended OrgLang behavior separately from publication rules and implementation observations.

**Scope and document boundaries**

- This document owns `ExternalCall`, `InternalCall`, their channel-transfer and lifecycle contracts, and the generic semantics of creating a process incarnation.
- [Processes and session types](../about-processes-and-session-types/README.md) owns process declarations and definitions, process expressions, session types, process-channel protocols, and implementation evidence from the process AST/type-checker/executor.
- [Pools and transaction types](../about-pools-and-transaction-types/README.md) owns pool selection and servicing agreements, transaction protocols, and the `spawn` admissibility condition and its place in the transaction protocol.
- [Incarnations and channels](../about-incarnations-and-channels/README.md) owns the abstract incarnation, identifier, channel, endpoint, and substitution mechanisms used by these operations.

**Shared terminology:** see the [OrgLang glossary](../GLOSSARY.md).

## 1. Intended semantics of named-process calls

The following contract is the canonical statement of intended language-level behavior. Process declaration and definition interfaces are described in [Processes and session types, Section 4](../about-processes-and-session-types/README.md#4-process-declarations-and-definitions). The shared distinction between static obligations, runtime preconditions, and transition invariants is also defined there.

**This is the canonical statement of the intended language-level behavior.** Implementation field names are not OrgLang keywords; their correspondence to language-level roles is documented in Section 9.

#### Contract summary: creation, channel ownership, and commit

The rules below are the **working OrgLang contract adopted for this research draft**, independent of any current implementation. The detailed preconditions and commit-boundary rules follow in the operation-specific sections. This summary makes the shared model and the distinction between the two call forms explicit.

A call is not merely a jump to a named body. It resolves a process definition, creates a fresh incarnation on success, and establishes which existing channel identities that incarnation owns. A channel's identity and residual protocol state are preserved when its binding is transferred; the transition changes which incarnation owns a binding, not the identity of the channel itself.

| Property | `ExternalCall` | `InternalCall` |
|---|---|---|
| New incarnation | Creates a fresh incarnation of the named process. | Creates a fresh incarnation of the named process. |
| Provider channel of target | Allocates a new, fresh provider channel. | Reuses the invoking incarnation's existing provider channel `X`. |
| Target client channels | Reuses supplied existing channels in declaration order. | Reuses supplied existing channels `Ys` in declaration order. |
| Source incarnation after success | Remains live; its continuation becomes eligible after it receives the new provider channel. | Terminates semantically; there is no language-level continuation for the old incarnation. |
| Pool association | Selects a suitable pool agreement for the named process. | Uses the invoking incarnation's pool; no pool selection occurs. |
| Commit point | Delivery of the new provider channel to the caller. Before delivery, no target servicing or call-associated protocol action/effect is allowed. | The single atomic transition at which the complete post-state becomes observable. |
| Pre-commit precondition failure | No partial incarnation or channel transfer is observable. If the search-and-negotiation procedure times out or exhausts all candidate pools before a suitable existing agreement is found or a new agreement is successfully reached, no incarnation/provider channel is created and supplied client channels remain with the caller unchanged. | No partial transfer; the invoking incarnation and its bindings remain unchanged and no new live incarnation is exposed. |
| Cancellation after commit | The search-and-negotiation timeout cannot cancel the call after a suitable existing agreement is found or a new agreement is successfully reached; post-delivery failure/recovery is outside this contract. | No cancellation that restores the old incarnation's channel environment; runtime failure during/after commit is outside this contract. |

**Shared invariants on successful calls**

1. **Fresh incarnation identity:** every created incarnation receives an identity never allocated before; identities are never reused.
2. **Positional binding:** formal client-channel placeholders of the target are bound to the supplied channels in declaration order. The target provider placeholder is bound as described for the relevant call form.
3. **Linearity and no aliasing:** distinct formal channel parameters map to distinct channel identities. For `InternalCall`, `X` and `Ys` together account for the invoking incarnation's complete channel environment.
4. **Channel preservation:** transferred channels keep their identities and current residual protocol states; a call does not silently reset or advance a protocol.
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
- The caller's designated placeholder for the new provider channel must have a type compatible with the target process's provider protocol, accounting for the caller's client role.
- At execution time, the operation must be able to create a fresh incarnation with an identity that has never previously been allocated, and allocate a provider-channel identity that is fresh and distinct from all existing channels, including the supplied client channels.

**Static validation:** The shared rule in [Processes and session types, Section 4](../about-processes-and-session-types/README.md#4-process-declarations-and-definitions) applies. A channel/type mismatch, repeated channel identity, or invalid positional mapping is a static error when decidable from the program version and its channel-identity information at admission. Runtime allocation and freshness are runtime requirements, not static checks. The implementation's conformance remains unverified.

**Intended transition:**

1. Resolve the named callee process and map each formal client-channel parameter to the corresponding existing channel supplied by the call, in declaration order.
2. Ensure the static obligations listed above have been checked at the admission boundary, including strict session-type equality at both the target's client parameters and the caller's client-role placeholder for the new provider channel, under the applicable provider/client role convention. Session-type subtyping is out of scope for now. Check runtime preconditions when the relevant execution state and resources are available; they are not static validation.
3. Before creating the incarnation, search for a previously established agreement suitable for the named process. If none is found, proceed to negotiation with a candidate pool according to the applicable transaction type. The criterion for finding an existing agreement, first-match selection, traversal order, escalation to manual negotiation, and the shared search-and-negotiation timeout are specified as the process–pool boundary contract in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement).
4. Once a suitable existing agreement has been found or a new agreement has been successfully negotiated with a selected pool, create a fresh incarnation with its own execution state and a separate fresh provider channel, and associate the incarnation with that pool. Bind the new incarnation's client placeholders to the supplied channel identities and its provider placeholder to the fresh provider channel; designate that same fresh channel for delivery to the caller. The successful agreement establishes the terms under which the selected pool services the call; the shared search-and-negotiation timeout and its boundary are specified in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement). Until delivery, the supplied channels are held for the target and their protocol states remain unchanged, and the target cannot service the call or perform protocol actions or external effects on its behalf. The engine atomically transfers all channels involved in the call to both sides: the fresh provider channel to the caller and the corresponding channel endpoints/bindings to the selected pool and new incarnation. This is one indivisible operation; partial delivery is impossible. Delivery is the commit point and is required for successful completion of the call.

**After (intended):** the supplied client-channel identities and protocol states are preserved, and their use transfers to the new incarnation; the caller's continuation relinquishes those channel identities. The caller may retain channels not supplied to the call. Its continuation becomes eligible when it receives the fresh provider channel through the designated placeholder, and then uses that channel's client endpoint according to its protocol. The call produces no separate result value; the fresh provider channel is the only call-specific value delivered to the caller. The fresh provider channel is distinct from all supplied channels. General linearity and process-completion constraints from Section 2 still apply.

**Lifecycle and implementation status:** initiation, incarnation creation, atomic channel delivery, and servicing are distinct events. **Agreed project decisions:** in one indivisible operation, the engine transfers the fresh provider channel to the caller and the corresponding channel endpoints/bindings to the selected pool and new incarnation. This atomic delivery is the commit point and completes the protocol-level call. Once delivery occurs, both sides may proceed: the selected pool may begin servicing immediately, and the caller's continuation may use the fresh provider channel—including sending its first protocol action before the pool takes its first action. The two sides may execute in either order or interleave, subject to protocol and linearity constraints. The call's only call-specific outcome is delivery of the fresh provider channel; it has no separate result value. The pre-delivery phase preserves the supplied channels' identities and protocol states and permits no call-associated protocol action or external effect; actions that cannot be fully undone are excluded from this phase. The search-and-negotiation timeout boundary is specified in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement).

**Failure before commitment:** Delivery of the fresh provider channel to the caller remains the `ExternalCall` commit point. If the search-and-negotiation procedure times out or exhausts all candidate pools before a suitable existing agreement is found or a new agreement is successfully reached, no servicing pool is selected, no incarnation or provider channel is created, and the supplied client channels remain with the caller with their original identities and protocol states. This failure occurs before incarnation creation. Failure reporting and recovery remain unspecified. The timeout boundary and post-discovery behavior are specified in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement). This is the intended language-level contract; implementation conformance remains unverified.

The pre-commit failure and delivery contract preserves these invariants:

- **Channel-state integrity:** if the search-and-negotiation procedure times out or exhausts all candidate pools before finding or establishing a suitable agreement, supplied channel identities and protocol states remain unchanged with the caller.
- **Continuation eligibility:** the caller's continuation becomes eligible upon receipt of the fresh provider channel, as specified by the successful-call contract.
- **Commit boundary:** delivery is the commit point. The search-and-negotiation timeout cannot cancel a call after a suitable existing agreement has been found or a new agreement has been successfully reached, even if delivery is delayed.

General process/pool failure handling, recovery after a servicing incarnation fails, restart guarantees, and retry policy are outside the scope of this ExternalCall contract. The agreed protocol-level contract excludes failure after successful atomic channel delivery; behavior of external infrastructure outside this protocol-level contract is not specified here.

**Timeout configuration and scope:** The search-and-negotiation timeout applies to `ExternalCall`; its boundary and unresolved configuration questions are documented in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement). The timeout policy does not guarantee eventual success or completion within a bounded time.

The inspected executor has no `ExternalCall` branch. The exact AST/runtime mapping among `CommChnlPH`, `ValChnlPHs`, and `NewChnlPH` remains open; see [Processes and session types, Part III](../about-processes-and-session-types/README.md#part-iii-implementation-evidence-and-open-questions). This is an implementation-mapping question, not an unresolved choice about the intended positional channel contract.

#### `InternalCall`

**Before:** the invoking process provides a service on an existing channel (AST field `X`). The target process also receives a list of channels it will use as a client (AST field `Ys`). The terms *provider channel* and *client channels* describe the channel roles relative to the process being discussed. Both refer to the same underlying kind of channel resource. The role descriptions are explanatory labels. Runtime field resolution is documented separately in the implementation analysis.

**Static obligations and runtime preconditions:**

- At the admission boundary, the target definition must be resolvable in the program version being checked.
- The supplied channels must match the types and positions of the target's corresponding placeholders.
- The supplied channel identities must be pairwise distinct, including no overlap between `X` and `Ys`.
- `X` and `Ys` must account for **all channel identities bound in the invoking incarnation `P`**. After a successful call, no channel binding may remain attached to `P`.
- The binding environment of `P` follows the model-wide no-alias invariant: distinct bindings refer to distinct channel identities. This is not an `InternalCall`-specific condition.
**Static validation:** The shared rule in [Section 4](#4-process-declarations-and-definitions) applies. A channel/type mismatch, positional or arity mismatch, or repeated supplied channel identity (including overlap between `X` and `Ys`) is a static error when decidable at admission. The model-wide no-alias invariant applies here; it is not an additional `InternalCall` precondition. Set equality alone is not sufficient to establish that every binding in the environment has been transferred. The implementation's conformance remains unverified.

**Agreed channel-transfer and lifecycle decision:** On a successful transition, create a fresh incarnation `Q` at the start of the target definition, bind its provider placeholder to `X` and its client placeholders to `Ys` in declaration order, and remove those bindings from `P`. Because `X` and `Ys` account for the complete channel environment of `P`, the old incarnation semantically terminates without a language-level continuation. The precise atomicity, freshness, failure, and preservation invariants are consolidated below. This is the intended OrgLang behavior for this research document; conformance with the publication and current implementation is tracked separately.

**Commit and pool association:** The atomic transition is `InternalCall`'s commit point: once its complete post-state is observable, `P` has terminated and the transferred channels belong to `Q`. `Q` uses the same pool as `P`; no pool selection occurs. Unlike `ExternalCall`, `InternalCall` has no timeout-driven cancellation phase or post-commit restoration of `P`'s environment. A failed precondition leaves the pre-state intact; runtime failure during or after commit remains outside this decision.

**Mini-example (schematic, not OrgLang syntax):** suppose process `Old` has provider placeholder `x` bound to channel `c`, and client placeholder `y` bound to channel `d`. `Old` performs `InternalCall` to process `New`, passing `c` as `X` and `d` in `Ys`. The transition unbinds both placeholders in `Old` and binds `New`'s corresponding placeholders to `c` and `d`; the channel identities are preserved.

The atomicity and failure contract is stated precisely below. Pool association and selection are specified separately in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement): `ExternalCall` selects a pool, while `InternalCall` uses the invoking incarnation's existing pool and does not select another one. Implementation questions are collected in [Processes and session types, Section 14](../about-processes-and-session-types/README.md#14-open-questions-and-next-tests).

**Atomicity boundary and failure behavior (intended contract):**

Treat the transition as a single state transition from a pre-state to a post-state, not as a sequence of externally observable mutations. Let the pre-state contain the live incarnation `P`, its complete channel environment, and the target definition. A successful transition produces a fresh `Q` whose provider placeholder is bound to `X` and whose client placeholders are bound to `Ys` in declaration order; `P` is no longer live and owns no channel bindings. Every transferred channel retains its identity and protocol state. No other incarnation's bindings or channel state change as a side effect of the transition.

The atomicity guarantee is about semantic observability, not a requirement that the implementation use a particular lock, transaction, or storage primitive. An implementation may perform internal preparation before committing the transition, provided that preparation is not observable as a live incarnation or as changed channel ownership. The commit point is the single point at which the complete post-state becomes observable.

If a precondition fails before the transition commits—for example, the target cannot be resolved, the channel arity or positional mapping is invalid, channel identities are duplicated, or a type obligation fails—the operation does not partially transfer ownership: `P` remains live with its original bindings and no new live `Q` is exposed. Error reporting and recovery after failures that occur during runtime execution are not yet specified; this contract must not be read as claiming crash consistency or rollback across process or machine failure.

**Required invariants (intended contract):**

- **Freshness:** `Q`'s incarnation identity has never been allocated to any incarnation in the execution history, including terminated incarnations. Incarnation identities are never reused.
- **Total transfer:** the invoking environment is injective, and the set of channel identities referenced by `P`'s bindings is exactly the set supplied by `X` and `Ys`; after commit, `P` has no channel bindings.
- **Exact rebinding:** each target placeholder is bound to the corresponding supplied channel identity, with `X` mapped to the provider placeholder and `Ys[i]` mapped to the i-th client placeholder.
- **Identity and protocol preservation:** transfer changes ownership/bindings, not channel identity or current session-protocol state.
- **Binding ownership:** after commit, none of the transferred bindings remain attached to `P`; each transferred identity is bound to exactly its designated placeholder in `Q`. This does not remove the peer endpoint's ordinary binding to the same channel.
- **All-or-nothing visibility:** observers see either the complete pre-state or the complete post-state, never a partial combination.

**Focused conformance tests to add:** The following are test obligations for the implementation, not claims that current tests already pass.

1. **Complete transfer:** use a target with one provider placeholder and multiple client placeholders; assert the target receives the exact channel identities in declaration order and the old incarnation is no longer live.
2. **Protocol-state preservation:** give each supplied channel a non-initial residual session state; assert the transition does not reset, advance, or replace that state.
3. **Fresh identity and non-reuse:** assert `Q` receives an identity never previously allocated, including identities of terminated incarnations; repeat transitions after termination to verify that no identity is reused.
4. **Duplicate identity rejection:** supply the same channel identity twice, including the `X`/`Ys` overlap case; assert rejection leaves the pre-state unchanged.
5. **Missing or extra channels:** mismatch the target's client-placeholder count; assert no partial binding and no live target incarnation.
6. **Atomic observation:** pause or instrument execution around the implementation's commit boundary; assert no observer can see `Q` with a subset of bindings or see both `P` and `Q` live with transferred ownership.
7. **Failure before commit:** force target resolution or validation to fail; assert `P` retains all original bindings and no partially initialized `Q` is observable.
8. **Unrelated-state isolation:** keep a separate incarnation and channel active; assert its bindings and protocol state are unchanged by the transition.

These tests should exercise the adapter, type checker, executor, and persistence/scheduling path together where those layers participate. A unit test of the AST constructor alone is insufficient evidence of conformance.
**Implementation status:** the inspected dispatcher has no `InternalCall` execution branch; execution and type-checking are unverified. See Section 14 for the unresolved lifecycle and representation questions.

#### Boundary with pool semantics

Process invocation and incarnation creation are distinct from the pool mechanism that services a provider channel. Calls describe named-process and channel effects, while the pool's `Up … Down` protocol describes interaction through the pool's public channel. The pool's public channel belongs to the pool. Pool association, selection, and eligibility are pool-level concerns documented in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement) and [Section 5](../about-pools-and-transaction-types/README.md#5-the-pools-public-transaction-channel). The discovery of an existing agreement and negotiation of a new one are described in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement); the detailed negotiation protocol, reservation semantics, failure behavior when no eligible pool exists, and resource provisioning remain underspecified.

## 2. Process spawning and the pool protocol

The word **spawn** appears in the pool transaction-type model and in several implementation representations. These must not be conflated with the two named-process call forms.

**Pool-level contract:** the transaction-type constructor for `spawn` admits spawning process `q` on logical transaction channel `c` only when the current allocation function satisfies `Q(q) > 0`. The operation does not itself change `Q`; its continuation retains the stated allocation state. The grammar, state-indexed rule, and typing condition are owned by [Pools and transaction types, Formal grammar and state-indexed rules](../about-pools-and-transaction-types/README.md#formal-grammar-and-state-indexed-rules).

**Boundary with incarnation creation:** this condition establishes when the pool protocol permits the spawn request. It does not, by itself, specify the complete runtime procedure for allocating an incarnation, constructing its execution state, binding its channel environment, attaching a process body, or making the resulting state observable. Those generic creation mechanics belong to this document and must be specified without duplicating the pool's eligibility rule.

**Current semantic status:** the generic runtime transition for pool-level `spawn` remains open. The available material distinguishes:
- the pool transaction-type constructor, whose admissibility condition is specified by `Q(q) > 0`;
- the process-expression AST constructor `SpawnSpec`, which is an unfinished implementation attempt and is not an established user-facing call form;
- the pool API operation `Spawn`, which creates an execution record but does not by itself establish the complete process-body and channel-wiring transition;
- the separate `proto/rast2` prototype reduction, which is not evidence of current OrgLang runtime behavior.

No equivalence among these representations is assumed. The process AST, adapter, type-checker, and executor findings are documented in [Processes and session types, Part III](../about-processes-and-session-types/README.md#part-iii-implementation-evidence-and-open-questions). The pool API and transaction protocol evidence remain in [Pools and transaction types](../about-pools-and-transaction-types/README.md).

## 3. Open questions

1. What is the complete generic runtime transition for creating a fresh process incarnation, including execution-state initialization and process-body attachment?
2. How does pool-level `spawn` supply and bind the new incarnation's provider and client channel environment?
3. What is the relationship, if any, between pool-level `spawn` and process-expression `ExternalCall` / `InternalCall` beyond their shared concern with incarnation creation?
4. Which implementation representation, if any, will replace the unfinished process-expression `SpawnSpec` attempt?
5. What are the required atomicity and failure guarantees for pool-level spawning, and which component owns each boundary?
