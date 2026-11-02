<!-- Canonical semantics: pool and transaction-type model; shared participant/channel and process/pool selection rules are in ../about-incarnations-and-channels/README.md -->

# Pools and transaction types

> **Status: preliminary semantic research.** This document is a technical companion to [What is a transaction?](../about-transaction/README.md). It collects the language-level model of pools and transaction types, distinguishes intended semantics from publication rules and implementation observations, and records unresolved questions. Its conclusions remain research findings pending a normative specification.

**Scope and document boundaries**

- This document owns the technical model of pools and transaction types, including the pool's public transaction channel and its protocol.
- [Incarnations and channels](../about-incarnations-and-channels/README.md) owns the shared participant/channel model, pool eligibility, search order, process-incarnation creation, pool binding, and the start of servicing.
- [What is a transaction?](../about-transaction/README.md) provides the accessible introduction.
- [Processes and session types](../about-processes-and-session-types/README.md) owns process expressions and the intended semantics of `ExternalCall` and `InternalCall`.

## 1. Scope, evidence, and status

This research draft keeps language-level intended semantics, claims made by the supplied publication, and implementation observations separate. A normative language specification remains future work.

Use the claim-status vocabulary from [Processes and session types, Section 1](../about-processes-and-session-types/README.md#1-scope-and-evidence): **Confirmed**, **Inferred**, and **Open**. Record the source and what it establishes for substantial or disputed claims. Implementation coverage is a separate dimension and should be recorded only when the relevant code path or test has been inspected.

## 2. Core concepts and terminology

The following working definitions are inferred from the current model described in [What is a transaction?](../about-transaction/README.md).

| Term | Working meaning | Status and limitation |
|---|---|---|
| Pool | A participant that can communicate with other pools and may service a process incarnation under an agreement. | **Inferred** from the explanatory model and the current process–pool model. Pool lifecycle, internal state, and whether every incarnation must always be bound to one pool remain **Open**. |
| Pool term | An executable expression describing a pool's communication or state transition. | **Inferred** from the companion model's distinction between terms, values, and continuations. Its runtime representation in OrgLang is **Open**. |
| Logical transaction channel | The pool-to-pool communication relationship between a fixed provider/client pair. It has one logical identity and one transaction type, and is represented by distinct public and private physical channels. | **Agreed project decision:** public and private channels are physically distinct representations of the same logical transaction channel; they share its transaction type and logical identity. Their physical identities are distinct. The matching and representation-switching principle is defined in [Incarnations and channels](../about-incarnations-and-channels/README.md#2-common-matching-principle). |
| Public transaction channel | The physical channel representation used while private access is inactive; it exposes the provider and client endpoints for the logical transaction channel. | **Agreed project decision:** physically distinct from the private channel, while representing the same logical transaction channel and carrying the same transaction type. |
| Private channel | A physical channel representation created by a matched `Up` for the logical transaction channel; the access cycle ends with either matched `Down` or `Rollback`. | **Agreed project decision:** each matched `Up` creates a new private physical channel. It represents the same logical transaction channel, with the same logical identity and transaction type, but has its own physical identity. |
| Agreement | The current allocation map `Q` associated with a logical transaction channel for a provider/client pair. | **Agreed working model:** agreement identity is the logical transaction channel identity, not either physical representation's identity. The current `Q` is determined by that logical channel's latest committed private channel. `Q'` denotes the in-progress value of the same map during an uncommitted private-channel access, not a separate map or stored field. |
| Transaction identifier | An identifier used to refer to a pool transaction or its channel in the pool model. | **Inferred**. Its concrete representation and allocation/uniqueness guarantees are **Open**; the agreement state itself is identified by the transaction channel `c`. |
| Transaction type | The protocol by which pools interact to establish and modify the agreement state; it governs permitted messages and transitions. | **Agreed project direction:** the public channel type does not use refinements; the private channel type may use refinement session types. Exact OrgLang syntax, checking rules, and runtime enforcement remain **Open**. |
| Provider/client endpoint roles | The provider and client own their respective endpoints of one shared transaction channel. | **Agreed project decision** for endpoint ownership; lifecycle and failure rules remain **Open**. |
| Process provider channel | The channel on which a process incarnation provides its named-process service. | Defined in [Incarnations and channels, Section 2](../about-incarnations-and-channels/README.md#2-participants-and-channels). It is distinct from the pool's public transaction channel. |

A transaction identifier and a process channel identity refer to distinct resources. Their precise mapping remains **Open** pending evidence from the language contract or a verified execution path.

A **transaction** is the pool-to-pool interaction; its **transaction type** is the governing protocol; the **agreement** is the dependent state `Q` of the logical transaction channel. A **transaction identifier** refers to the transaction or its channel. The logical channel identity is stable across the public/private representation switch; the two physical channel identities remain distinct.

## 2.1 Negotiation protocol and established agreement

The current model has three related concepts:

1. **Transaction type:** the protocol that governs how pools interact while establishing or modifying an agreement. It describes permitted messages, choices, constraints, and continuations.
2. **Negotiation interaction:** the pool-to-pool exchange governed by that protocol over the shared transaction channel. Its detailed operational representation remains unspecified.
3. **Agreement:** the complete allocation map `Q` for the shared transaction channel `c`, accepted by the participating pools. Once established, this state can be found and reused by a later `ExternalCall`; finding it is distinct from negotiating or modifying it.

For the discovery and negotiation sequence, including the point at which incarnation creation may begin, see [Incarnations and channels, Sections 5.3–5.4](../about-incarnations-and-channels/README.md#43-search-and-agreement-negotiation).

### What the formal transaction-type model establishes

The grammar in the [transaction introduction](../about-transaction/README.md) gives evidence for a **state-indexed protocol**:

- The type constructors describe interactions such as `grant`, `revoke`, `choice`, `coop`, `isol`, and `spawn`.
- The `Coop` and `Isol` constructors change the allocation-map value during the current private-channel access; `Q'` and `Q''` denote the values before and after an operation. They are not separate maps or stored fields. The current value becomes committed when the matching `Down` occurs.
- The spawn constructor requires positive allocation weight for the named process on that channel: `Q(q) > 0`; its continuation retains the stated `Q`.
- The type grammar also places a continuation `A` after these state constraints and transitions.

`Q` is the current allocation map associated with the logical transaction channel. Its current value is determined by that channel's latest committed private channel. `Q'` denotes the value of the same map during an uncommitted private-channel access; it is not a separate map or stored field. Search uses the `Q` associated with the latest committed private channel only to check suitability conditions and select candidates; it does not modify `Q` or the committed channel. How search obtains `Q`—for example, by copying it, referring to it, or another mechanism—remains **Open**. An uncommitted private channel does not replace the current committed channel until its matching `Down`. The map's interpretation and transition rules are defined canonically in [What is a transaction?](../about-transaction/README.md#типы-ограничения-уточнения).

**Agreed working model:** the public channel type has no refinements; the private channel type may express refinements, with `Q` as the runtime value providing evidence for a relevant condition (for example, `Q(q) > 0`). `Q` exists in the context of private channels and changes with the corresponding channel's allocation-map value. `Q'` is only notation for that value during an uncommitted private-channel access, not a separate map or stored field. How `Q` is physically stored or associated with a private channel remains **Open**.

### Agreement lifecycle: current contract and missing rules

| Stage | Current project contract | Still unspecified |
|---|---|---|
| Existing-agreement discovery | Search uses the `Q` associated with the latest committed private channel for each logical transaction channel, only to check conditions such as `Q(q) > 0` and select candidates. Search does not modify `Q` or the committed channel. | How search obtains `Q`; how committed private channels are made discoverable; visibility/ownership and selection among suitable channels belonging to different provider/client pairs. |
| Candidate selection | If discovery finds no suitable channel, manual intervention selects a candidate pool. Selection does not itself establish an agreement. | Authorization, candidate presentation, and whether candidates can be rejected before negotiation starts. |
| Private-channel access | Each matched `Up` creates a new private physical channel for the same logical transaction channel and gives it that logical channel's current `Q` (or the common initial value `Q⁰` if no private channel has yet been committed). At most one uncommitted private channel may exist for a logical channel. | The relationship between the common `Q⁰` and the provider-specific competence domain `C`; failure handling is addressed separately. |
| Negotiation | After matched `Up`, the candidate pools interact over that pair's private channel according to the applicable transaction type. Any number of `Coop` and `Isol` operations may change the channel's current allocation-map value; `Q'` denotes its in-progress value. The previously committed private channel remains current for search until `Down` or `Rollback`. Negotiation does not create a second concurrent private channel or a per-process agreement. A failed candidate may be replaced before the shared timeout expires. | The exact protocol steps, proposal/acceptance rules, and candidate-switch behavior while preserving the committed agreement. |
| Commit | When provider `detach` and client `release` match at `Down`, the current private channel's allocation-map value is committed, and that channel replaces the previous committed private channel as the current one for the logical transaction channel. `Down` itself does not modify `Q`. | Whether the superseded private channel is physically destroyed or retained. |
| Rollback | `Rollback` cancels the current private-channel access, discards its uncommitted state including changes to `Q`, and restores the active binding to the public channel. The preceding committed private channel remains current and continues to supply `Q` for search and the next `Up`. Timeout during an active negotiation is one trigger for rollback. | The explicit initiation mechanism and triggers other than timeout; physical disposition of the uncommitted private channel. |
| Service activation | Only after a suitable existing agreement is found or a new one is successfully established does the engine create the incarnation and deliver the provider channel. | Resource reservation/consumption semantics and failure handling between agreement establishment and channel delivery. |


### Questions required to complete the agreement model

- How is `Q` physically represented or associated with a private channel? The current model does not decide whether it is stored within the channel or represented separately.
- What exact formal syntax and typing judgment express the transaction type's protocol and its dependent state index `Q`?
- What operation or judgment distinguishes a negotiation that is still in progress from one whose agreement has been accepted by both parties?
- How do channel discovery and `ExternalCall` search interact with protocol-state transitions and channel linearity, and what determines which channels are visible to a searching pool?



## 3. Pool model

**Inferred working model:** a pool is represented by a pool term/state and exposes a public transaction channel through which other pools interact according to a transaction type. The provider/client endpoints and matching principle are defined in [Incarnations and channels](../about-incarnations-and-channels/README.md#2-common-matching-principle); the channel-local allocation map is defined in [What is a transaction?](../about-transaction/README.md#типы-ограничения-уточнения). The process's provider channel is a distinct resource. Pool lifecycle and behavior when a pool cannot service a request remain **Open**.

## 4. Transaction types

The companion [transaction introduction](../about-transaction/README.md) presents the candidate transaction-type grammar, including termination, directional `Up` and `Down`, choice, `Coop`, `Isol`, and process spawning. The formal representation and transitions of the per-channel allocation map `Q` are defined there; this document focuses on pool roles, negotiation, and agreements.

| Question | Current status | Why it matters | Evidence needed |
|---|---|---|---|
| Which constructors belong to the OrgLang transaction-type language, and what is their exact syntax? | **Open** | Determines what specifications and programs may express. | An adopted language grammar or an explicit project decision; compare with the companion model and implementation parser/type definitions. |
| What are the remaining exact transition rules for `One`, `Up`, and `Down`, including type-state progression, ownership, and observable boundaries? | **Partly decided; partly Open** | Matching is the transition point; the remaining state progression and observability details govern conformance. | Preserve the adopted decisions in Section 6.2; specify remaining obligations, then test permitted and prohibited transitions. |
| Are constraints on pool state part of type checking, runtime validation, or both? | **Open** | Determines which constraints expressed by the transaction-type agreement are checked statically and which require runtime validation. | A typing/validation rule and implementation-path evidence, with negative examples. |


### Per-channel allocation state

The transaction-type grammar is state-indexed: `Coop` and `Isol` transition the allocation map associated with the shared transaction channel, while `spawn` requires a positive allocation weight for the requested process. The canonical definition of the map, its initialization, allocation weights, and transition side conditions are in [What is a transaction?](../about-transaction/README.md#типы-ограничения-уточнения).

The map `Q` is the current agreement state associated with each logical transaction channel, not with the client pool globally. Each logical transaction channel has its own current `Q`, determined by its latest committed private channel; `Up` gives the new private channel the current `Q` of that same logical channel. A matched `Down` commits the new value and replaces the preceding committed private channel as the current one. A pool may participate in logical transaction channels with different counterpart pools. No cross-channel summation rule is currently imposed.

For a fixed provider/client pair, the working model permits only one established agreement, regardless of which process name is called. Consequently, that pair does not require a choice among several agreements or channels. Discovery may still select among suitable agreements offered by different provider/client pairs; the discovery and negotiation procedure is specified in [Incarnations and channels, Sections 5.3–5.5](../about-incarnations-and-channels/README.md#43-search-and-agreement-negotiation).

## 5. The pool's public transaction channel

**Inferred:** the pool's public transaction channel is part of the current explanatory pool model. Whether individual processes should have public channels remains **Open**.

The public transaction channel and private channels are physically distinct representations of one logical transaction channel. They have distinct physical identities, share one logical identity, and use the same transaction type. The provider and client pools each have their respective endpoint in these representations. Each matched `Up` creates a new private physical channel and makes it the active representation; matched `Down` commits that private channel's current allocation-map value and restores the public channel as the active representation, while `Rollback` restores the public channel and discards the uncommitted private-channel state. The latest committed private channel is the current committed channel for the logical transaction channel and supplies the `Q` used by search. Restoring the active binding to the public channel does not make the public channel the search target. The public channel type itself has no refinements. The exact matching points, participant continuations, and channel-identity rules are specified canonically in [Incarnations and channels](../about-incarnations-and-channels/README.md#2-common-matching-principle) and [Section 6.2](#62-matched-transitions-continuations-and-channel-identity); this section does not restate those rules.

The lifecycle of `Q`, including initialization, updates during private-channel access, and commit at matched `Down`, is defined in [Section 2.1](#21-negotiation-protocol-and-established-agreement). The logical/physical identity switch and participant-continuation rules are defined in [Section 6.2](#62-matched-transitions-continuations-and-channel-identity).

This pool-level protocol is distinct from a process's provider channel and from channels mapped to a new incarnation's client-role parameters in `ExternalCall`. Process creation, pool selection, and the start of servicing are described in [Incarnations and channels](../about-incarnations-and-channels/README.md).

## 6. Intended semantics and formal rules

This section records the agreed minimal language-level decisions for matching and continuation behavior, while leaving a complete operational semantics unfinished. The decisions below specify when the protocol transition counts as occurring; they do not establish implementation correctness, complete typing rules, failure semantics, or every state transition.

### 6.1 Minimal transaction-type constructors

**Status: Project semantic decisions, with formalization still open.** The matching points, shared channel-identity rules, and participant-specific continuation obligations recorded below are adopted language-level requirements. Their complete typing judgments, operational rules, and implementation conformance are not yet established; this research document is not itself the normative language specification.

A transaction type describes the protocol exposed by a pool through its public transaction channel. A client's interactions must conform to this provider-side protocol, evaluated against the current protocol state. No separately declared client-side transaction type is required by this model.

| Constructor | Provider-side operation | Client-side operation | Minimal intended meaning | Further detail |
|---|---|---|---|---|
| `One` | `close` | `wait` | Terminal provider interaction and corresponding client wait. The client's enclosing expression may continue after `wait`; provider-side `close` has no executable continuation of its own. | Matching and shared-identity rule: Section 6.2. `One` does not itself imply process termination. |
| `Up A` | `accept` | `acquire` | Provider accepts access; client acquires access. | Matching, private identity, and participant continuation rules: Section 6.2. Formal typing remains open; `dual(A)` is provisional explanatory notation only. |
| `Down A` | `detach` | `release` | Provider detaches access; client releases access. | Matching, restoration of the original public identity, and mandatory participant-specific `ContExp` on both operations: Section 6.2. Formal typing and resource disposition remain open. |

The operation names above are implementation identifiers, not proposed surface syntax. The pool-side operation declarations are in [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core/core.go); the process-side declarations are in [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go). These declarations support the provider/client operation mapping, but by themselves do not establish the runtime transition order or full language semantics.

### 6.2 Matched transitions, continuations, and channel identity

The general paired-interaction principle is defined in [Incarnations and channels](../about-incarnations-and-channels/README.md#2-common-matching-principle). This section specifies its pool-specific consequences:

- **`One`:** provider `close` matches client `wait`. Only the matched pair completes the transaction interaction and establishes one channel identity shared by both sides. Client-side `wait` may continue in its enclosing expression; provider-side `close` is terminal and has no executable continuation of its own.
- **`Up A`:** provider `accept` matches client `acquire`. Access becomes active and both participants' logical channel bindings resolve to a newly created private physical channel. This channel has its own identity, distinct from the public channel and from any earlier private channel, while representing the same logical transaction channel and carrying the same transaction type. Allocation-state initialization and negotiation are defined in [Section 2.1](#21-negotiation-protocol-and-established-agreement).
- **`Down A`:** provider `detach` matches client `release`. The current private channel's allocation-map value is committed, and both participants' logical channel bindings resolve back to the public physical channel. The current private channel replaces the previous committed private channel for that logical transaction channel and becomes the source of its current `Q` for subsequent search. `Down` itself does not modify `Q`. It does not imply physical destruction of the superseded private channel; its physical lifetime remains open. The logical identity and transaction type are unchanged. The allocation-state commit is defined in [Section 2.1](#21-negotiation-protocol-and-established-agreement).
- **`Rollback`:** rollback cancels the current private-channel access. The uncommitted private-channel state, including changes to `Q`, is discarded, and both participants' active bindings return to the public physical channel. The preceding committed private channel remains current and continues to provide the `Q` used by search and the next `Up`. Timeout during an active negotiation is one trigger for rollback. The explicit initiation mechanism and other triggers remain open; the physical disposition of the uncommitted private channel is unspecified.

Each side of `Up A` and `Down A` carries its own participant-specific continuation; the expressions need not be textually identical and become eligible only after the corresponding pair matches. After `Up`, each uses the shared private identity; after `Down`, each uses the restored public identity. `Rollback` also restores the public identity; its continuation and notification behavior remain unspecified. Provider continuations are checked against `A`, and client continuations against the corresponding client-side protocol type (provisionally `dual(A)`); the endpoint typing qualification is defined below.

The logical placeholder persists across the public/private transition: matched `Up` binds it to a newly created private physical channel, and either matched `Down` or `Rollback` restores the public physical binding. The logical identity and shared transaction type remain unchanged; every private channel has its own physical identity. `One` has a separate shared-identity rule. Matching imposes no additional ordering between participant continuations. Search uses the `Q` associated with the latest committed private channel and does not modify it; how search obtains `Q` remains **Open**. A later `Down` replaces that channel as the current committed private channel. Whether the superseded physical channel is retained or destroyed remains **Open**. The initialization and update rules for `Q` and `Q'` are defined in [Section 2.1](#21-negotiation-protocol-and-established-agreement).

#### Continuation correspondence: dual endpoint views

**Decision recorded from semantic review:** `A` describes the provider-side continuation protocol; the client-side continuation must be checked against the corresponding client-side protocol type. For brevity, this document uses `dual(A)` as a provisional notation for that client-side type. This notation is introduced here for explanatory purposes only: it is not an established OrgLang grammar constructor or operation, and no definition or derivation rule for it is assumed. The participant-specific continuation expressions need not be textually identical, but each must satisfy the typing obligation for its own endpoint. Matching the operation pair and binding the appropriate shared channel identity do not, by themselves, make arbitrary `ContExp` values valid.

This decision establishes the intended endpoint relationship, not the complete typing judgment. The formal representation of the client-side type, the typing rules, and how the continuation channel identity is substituted into each participant's continuation remain to be specified and tested.

#### Initial conformance examples

These examples translate the decisions in Section 6.2 into acceptance criteria for future tests; they are not claims that tests already exist or pass:

1. **`One`:** a client waiting for the provider's `close` may proceed to its own continuation only after the close/wait pair matches; matching establishes one channel identity shared by both sides. The close interaction does not itself terminate the enclosing client process.
2. **`Up`:** a client cannot treat access as acquired unless the provider-side protocol permits and matches the acquisition; both participants continue according to the continuation associated with `Up`.
3. **`Down`:** after a valid detach/release match, the current private channel's allocation-map value is committed, both sides regain the public channel identity, and the current private channel replaces the preceding committed private channel for that logical transaction channel. A subsequent matched `Up` must create a different private physical channel identity. Tests should verify that suitability checks use the `Q` associated with the preceding committed private channel until `Down`, then use the `Q` associated with the newly committed channel, without requiring `Down` itself to modify `Q` or destroy the superseded physical channel.
4. **`Rollback`:** during an uncommitted private-channel access, rollback discards the private channel's uncommitted state, including changes to `Q`, restores both active bindings to the public channel, and leaves the preceding committed private channel and its `Q` current for search and the next `Up`. Verify these postconditions when rollback is triggered by timeout.
5. **Protocol conformance:** an operation that contradicts the current provider-side protocol state is rejected or otherwise prevented according to a separately specified checking/enforcement rule; that enforcement mechanism is currently open.

For each rule adopted in this section, record:

1. **Preconditions:** the participant roles, channel/type state, and any agreement or resource prerequisites.
2. **Action:** which participant sends, receives, selects, or applies a continuation.
3. **Result:** the next protocol state, the identity and ownership of any channel/resource, and any change to pool state.
4. **Observable state at a transition boundary:** where relevant, state the pre-state/post-state and ordering constraints needed to preserve protocol and resource invariants. Detailed error reporting, recovery, retries, and abnormal-termination semantics are outside this specification pass.
5. **Evidence:** the source for the intended language rule, plus separate implementation-path/test evidence where conformance is claimed.

Until these points are settled, keep only the corresponding unresolved detail explicitly **Open** and link to the relevant question in Section 9. Do not downgrade the adopted matching, identity, or continuation requirements recorded in Section 6.2.

## 7. Publication correspondence

The [transaction introduction](../about-transaction/README.md) presents the OrgLang working transaction model. Its Table 4 assigns `grant`-send behavior to `↑ A` and `revoke`-receive behavior to `↓ A`, with continuation as `A`. This table is part of the project's model; it is not a table reproduced from the publication. The publication supplies the process-channel session-type framework and the corresponding continuation/application ideas: its continuation grammar and the definition of `V ▷ K` explain how a received value selects a continuation and substitutes an identifier for a placeholder.

The project uses those ideas as the basis for its transaction-type interpretation. The correspondence between the publication's channel actions and OrgLang's transaction operations is therefore a model-level analogy, not a rule stated directly by the publication. The OrgLang language-level operation model additionally requires each side of `Down`—provider-side `detach` and client-side `release`—to carry its own participant-specific `ContExp`. These expressions need not be identical: the provider continuation is checked against `A`, and the client continuation against the corresponding client-side protocol type. This is a language-level requirement, not a claim that the current runtime operation structs already expose those fields. The publication table's send/accept wording also should not be equated mechanically with the current runtime operation names (`accept`/`acquire`, `detach`/`release`) without an explicit role and polarity mapping.

### Initial constructor/role correspondence table

The table below separates the publication model's token polarity from OrgLang's current provider/client operation names. It is a working correspondence, not a claim that the runtime implementation already conforms.

| Type constructor | Publication-level action | Provider-side OrgLang operation | Client-side OrgLang operation | Established minimum | Still open |
|---|---|---|---|---|---|
| `One` (`𝟏`) | The provider-side type sends `close`; the client-side dual action receives/waits for it. | `close` | `wait` | The pair must match before the interaction counts as complete; matching establishes one shared channel identity. The client's enclosing expression may continue after `wait`; provider-side `close` is terminal for this interaction and has no executable continuation of its own. | The precise correspondence between the publication's terminal `close` case and OrgLang's enclosing-expression behavior, plus the formal typing of the shared identity for this terminal case. |
| `Up A` (`↑ A`) | The provider-side type sends `grant`, then continues as `A`; the client performs the complementary receive/acquire action. | `accept` | `acquire` | Access starts only when the pair matches; both participants use the shared new private channel identity. The provider continuation is checked against `A`, and the client continuation against its corresponding client-side protocol type (provisionally `dual(A)`). | The exact correspondence between the publication's actions and OrgLang's runtime operations, plus formal typing judgments and runtime conformance. |
| `Down A` (`↓ A`) | The provider-side type accepts/receives `revoke`, then continues as `A`; the client performs the complementary send/release action. | `detach` | `release` | Access ends only when the pair matches; both operations must carry their own participant-specific `ContExp`. After matching, each continuation may proceed with the restored original public channel identity. The provider continuation is checked against `A`, and the client continuation against its corresponding client-side protocol type (provisionally `dual(A)`). | The exact correspondence between the publication's actions and OrgLang's runtime operations, formal typing judgments, and runtime conformance. |

**Polarity rule for this comparison:** the transaction type is the protocol exposed by the provider. Accordingly, this project's analogy reads the action from the provider endpoint: `↑ A` sends `grant`, while `↓ A` receives `revoke`; the client endpoint performs the complementary action. This is the project's interpretation of the type table and provider role, not a direct statement about OrgLang in the publication or proof of the exact runtime implementation. The runtime names `accept`, `acquire`, `detach`, and `release` must still be checked against their code paths and tests, not matched by English verb similarity alone.

The initial comparison should cover:
- the grammar and reduction/application operation for values, continuations, and pool terms;
- the transaction-type constructors and their side conditions;
- the relationship between a type's constraints and the pool-state set used by the model;
- the spawn-form rule and its relationship, if any, to OrgLang's `SpawnSpec`.

**Open:** whether these publication constructs correspond one-to-one to OrgLang constructs. Similar names or matching notation are not sufficient evidence.

## 8. Implementation evidence

Implementation conformance has not been established by this document. The following are **implementation observations only** from the inspected source snapshot; they do not establish that the language contract must have identical semantics.

| Path / symbol | Observed behavior | What this establishes | What remains unverified |
|---|---|---|---|
| [`pool/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go), `take` cases for `AcceptSpec` and `AcquireSpec` | If `commSnap.NextTurn()` is empty, the executor records a `SubRec` containing the operation and continuation, logs `taking half done`, and returns without binding either continuation. When the matching opposite operation is already registered, it creates one new channel ID, binds both participants' continuation channels to it, advances the exchange offset, and schedules non-nil continuations. | The inspected implementation permits a first-arriving operation to remain pending and performs continuation binding when the opposite operation is matched. | Whether the pending registration is externally observable, the intended atomicity/linearization point, cancellation/interleaving behavior, and whether this path is complete for all runtime cases. |
| [`pool/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go), `take` cases for `DetachSpec` and `ReleaseSpec` | The same pending-subscription pattern is used. On matching, the implementation creates a channel ID and binds both continuation channels; these cases do not schedule participant-specific `ContExp` expressions. The bound runtime continuation channels should not be confused with the language-level `ContExp` expressions required on both operations. The inspected code path alone does not establish how this ID relates to the original public channel identity at the language level. | The current implementation models `detach`/`release` as a paired interaction with a continuation channel after matching. | Resource disposition after the interaction and any broader lifecycle contract. |
| [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/core/core.go) and [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go), operation-spec declarations | In both packages, `DetachSpec` and `ReleaseSpec` contain only `CommChnlPH`; neither declares a `ContExp` field. By contrast, `AcceptSpec` and `AcquireSpec` declare `ContExp`. In the process package, `CloseSpec` has no `ContExp`, while `WaitSpec` does. | The inspected runtime operation-spec structures do **not** satisfy the language-level `Down` requirement recorded here: both `detach` and `release` must carry participant-specific `ContExp` values. `Up` already has continuation fields on both operations. | The runtime AST/specs, typing, adapters, executor, and tests must be brought into alignment with the `Down` contract. This is a documented conformance gap, not a reason to weaken the language-level requirement. |
| [`proc/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go), `takeWith` cases for `CloseSpec` and `WaitSpec` | If no opposite operation is registered, the executor records a pending subscription and returns. On matching `close`/`wait`, it creates a new channel ID and binds both sides to the `One` continuation type; the wait-side continuation is scheduled when non-nil. | The inspected process executor uses the same pending-then-match pattern for `One`. | Whether the language contract requires this exact scheduling/observability behavior, and abnormal termination/error behavior. |
| [`pool/termexp/adapter/tc.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/adapter/tc.go) | The adapter maps the core operation specifications to SDK operation variants with corresponding names. | The operation names are carried through the adapter. | An adapter mapping alone does not establish protocol correctness or type conformance. |
| [`test/e2e/pool_test.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/test/e2e/pool_test.go), `TestPool` / `waitClose` | The test builds an `Up`/`With`/`Down` pool type and exercises some pool acquisition/acceptance steps. The `close`/`wait` process interaction and final outcome assertion are commented out; the test contains a TODO for an assertion. | This file provides an example of intended test setup and partial execution coverage. | It does not currently establish an asserted end-to-end `One` outcome or full conformance for `Up`/`Down`. The test was inspected, not run in this task. |

These paths suggest that the implementation has a **pending registration** stage followed by a **matching/continuation-binding** stage. In the inspected `detach`/`release` path, the executor creates a channel ID and binds runtime continuation channels, but does not schedule participant-specific `ContExp` expressions (and the operation specs do not expose those fields). Runtime continuation-channel binding is distinct from the language-level continuation expressions required on both operations. This source-level observation does not tell us how that ID maps to the logical channel placeholder or to the original public identity described by the language-level model. The internal mechanism for preserving and restoring that identity is an implementation detail and is not specified here. Do not call the whole interaction atomic without defining the relevant observable boundary: the database mutation and broker scheduling path, and concurrent interleavings, would need to be traced to settle that question.

The [`TestPool` / `waitClose` example](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/test/e2e/pool_test.go) defines the type-level continuation as `Down { ContExp: Link{TypeQN: poolTypeQN} }`, but its runtime `ReleaseSpec` and `DetachSpec` literals supply only `CommChnlPH`. This is consistent with the operation-spec declarations above and exposes the same implementation gap: the example does not encode the two required participant-specific `ContExp` values. The test's final `close`/`wait` sequence and outcome assertion are commented out, so it is partial evidence only; it does not validate the complete lifecycle.

## 9. Open questions and next tests

| Open question | Behavior/decision affected | Evidence or test needed |
|---|---|---|
| Which transaction-type constructors and syntax are part of OrgLang, rather than only the companion model? | Grammar, type checking, and compatibility of programs. | Adopted grammar/project decision; compare parser and type-checker support separately. |
| What formal rules remain for `One`, `Up`, and `Down`? | Matching points, shared-identity rules, and the requirement for participant-specific `ContExp` on both `Down` operations are decided. Formal typing, type-state progression, ownership, and observable boundaries remain open. | Define the typing and state-transition judgments; add positive and negative tests without reopening the adopted decisions. |
| How is continuation typing formalized? | **Decision:** the provider-side continuation is checked against `A`, and the client-side continuation against the corresponding client-side protocol type, provisionally denoted `dual(A)`. This notation is not an established grammar construct. The formal judgments and channel-identity substitution remain open. | Define the typing judgments and client-side protocol type representation; test valid and invalid continuation pairs, including channel-identity substitution. |
| How do the publication's continuation notation and actions map to OrgLang's participant-specific continuations and runtime operations? | The OrgLang endpoint obligations are adopted; the correspondence between the publication's notation/actions and OrgLang's runtime operations remains open. | Verify provider/client polarity and action correspondence against language rules and runtime paths; do not infer runtime semantics from publication wording alone. |
| What is the physical lifetime of a private channel after `Down` commits it? | `Down` does not imply destruction; the latest committed private channel remains the search target until a later `Down` commits a newer one. Whether older private channels are retained, and for how long, remains **Open**. | Specify resource retention and reclamation separately from the agreed commit and search-target behavior. |
| How are the logical identity, public/private physical identities, and shared transaction type represented? | The logical identity is shared; the public and private physical channel identities are distinct; both physical representations use the same transaction type. The concrete identity mapping and physical representation of `Q`/`Q'` remain open. | Specify the identity/substitution representation and verify that `Up`/`Down` switch only the active physical binding while preserving logical identity and transaction type. |
| How do cancellation, failure, and concurrency affect pending or matching `Up`/`Down` interactions? | Whether a pending participant can withdraw, how peer absence or failure is handled, and which interleavings are permitted around a matched transition. | Specify cancellation and failure semantics without weakening the adopted rule that the public protocol transition occurs only when the corresponding operations match; add interleaving and peer-absence tests. |
| Can individual processes expose public transaction channels, or is this pool-only? | Public API and which entity owns the public protocol endpoint. | Project decision grounded in language examples or source rules; inspect implementation only as conformance evidence. |

| How are agreement parameters and timeout values represented? | Who supplies timeout, how it is checked, and whether it is static or dynamic. | Project decision; do not assume the proposed `0 = infinite` convention. |
| How are transaction identifiers allocated and related to process channel identities? | Identity uniqueness, resource ownership, and safe continuation substitution. | Identity contract and source/test evidence for allocation and substitution. |
| Which implementation paths establish conformance? | Confidence that intended protocol rules are executable. | Source-level trace and tests with observable assertions for each agreed rule. |

### Minimum conformance test matrix

The following is an acceptance target for the adopted semantics, not a description of tests already present. Each pending case should be tested with both endpoint arrival orders, and each matched case should assert the observable post-state rather than only the absence of an API error.

- **Pending boundary:** after only `accept` or `acquire` (and separately only `detach` or `release`), assert that no protocol transition has occurred, no continuation has become eligible, and no participant can observe a partially changed channel state.
- **`Up` match:** after both `accept` and `acquire` match, assert one shared fresh private channel identity, the expected residual protocol state, and exactly one eligibility event for each non-null participant continuation. Use different provider/client continuation expressions to ensure they are not accidentally conflated.
- **`Down` match:** after both `detach` and `release` match, assert restoration of the original public channel identity (not a newly allocated public identity), the expected residual protocol state, and exactly one eligibility event for each participant-specific continuation. Include distinct continuation expressions and positive/negative typing cases for each endpoint.
- **`One` match:** assert that a lone `close` or `wait` remains pending; after the pair matches, assert completion with one shared channel identity, no provider-side executable continuation, and eligibility of the client's enclosing continuation when present.
- **Representation path:** round-trip every operation and continuation through AST, adapter, persistence, and executor representations. In particular, `Down` cannot pass the language-level continuation tests until both operation specs and their conversion paths can carry the required `ContExp` values.
- **Linearity and isolation:** reject duplicate/aliased channel identities and invalid endpoint continuation types; verify that a pending or matched operation does not mutate unrelated channels or another participant's bindings.

The current inspected `go-engine` paths provide useful pending/matching implementation observations, but the existing end-to-end scenarios include missing result assertions, and the `Down` operation representation does not yet expose the adopted language-level continuation expressions. These are implementation gaps to address, not reasons to weaken the acceptance criteria.
