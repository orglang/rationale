<!-- Canonical semantics: common matching principle and process–pool selection boundary -->
# Matching and spawn

> **Status: preliminary semantic research.** This document describes the process-creation and pool-servicing boundary.

> **Document scope:** this document owns the general paired-interaction matching principle and the process–pool selection boundary. The constructor-specific language contracts for `ExternalCall` and `InternalCall` remain in [Processes and session types, Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls); pool transaction-type details remain in [Pools and transaction types](../about-pools-and-transaction-types/README.md).

> **Implementation status:** The process and call mechanisms discussed here have had multiple implementation attempts. The implementation observations below describe those attempts; the intended language behavior is specified independently.


## 1. Purpose and mental model

When a process invokes `ExternalCall`, the language-level operation requests service for a named process. The engine may need to perform two distinct tasks: create a fresh process incarnation and arrange for a pool to service the new incarnation's provider channel.

- **`ExternalCall`** creates a fresh incarnation and delivers its fresh provider channel outward to the caller.
- **`InternalCall`** creates a fresh incarnation in the same pool as the invoking incarnation and transfers the invoking incarnation's existing channels into it; it does not perform pool selection.
- **Process-incarnation creation** means creating a fresh instance of a process.
- **Pool selection and servicing** determine which pool is associated with the incarnation and which pool services its provider channel.

`SpawnSpec` is an unfinished implementation attempt for process spawning; it is not an established source-language operation.

**Implementation evidence:** the repository contains several similarly named representations that must be kept distinct. The process-expression `SpawnSpec` has no execution branch in the inspected process executor; an older `SpawnSpecOld` branch remains commented out. Separately, the pool API's `Spawn` method creates a new process-execution record, but the inspected implementation does not instantiate or attach a process body there. These observations support the status “incomplete implementation attempt”; they do not define the intended replacement semantics.

Under the current language-level working model, creating a fresh incarnation is part of servicing either `ExternalCall` or `InternalCall`; pool selection is specific to `ExternalCall`. See the implementation evidence in [Processes and session types, Section 13](../about-processes-and-session-types/README.md#13-what-the-execution-path-establishes) and the [pool executor implementation](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go) and [process executor implementation](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go).

`Call` is the umbrella term for the two named-process call forms, `ExternalCall` and `InternalCall`.

### How to read status labels

Use the same claim-status vocabulary as the canonical [Processes and session types](../about-processes-and-session-types/README.md#1-scope-and-evidence) document:

- **Confirmed** means the claim is directly supported by an appropriate source. State exactly what that source establishes; a claim confirmed by one source requires separate support before it is treated as confirmed for OrgLang.
- **Inferred** means the claim is a working interpretation or rule derived from available evidence; its status as a language rule remains unestablished.
- **Open** means the available evidence does not settle the claim or verification remains incomplete.

Use **Evidence** to identify the source or observation supporting a claim; use **Confirmed**, **Inferred**, and **Open** for claim status. Keep implementation coverage separate from claim status. Treat issue comments as provisional discussion. A rule from the cited publication's calculus requires separate evidence before it can be treated as an OrgLang rule.

## Common matching principle

**Language-level principle shared by process channels and pool transaction channels:** each participant performs its own protocol-permitted operation. An operation performed by only one side remains pending; it does not by itself complete the interaction or advance the shared protocol state. The interaction takes effect when the corresponding peer operations match. Matching establishes one shared channel identity and the protocol-state effect for both endpoints. Each participant may then proceed through its own continuation where the operation defines one; the continuation expressions need not be textually identical, and matching does not imply simultaneous execution.

For a pool-to-pool transaction, the two pools likewise use **one shared transaction channel**, not a pair of linked channels. Each pool has its own endpoint of that channel: the provider pool has the **provider endpoint**, and the consumer pool has the **consumer endpoint**. These roles identify the two endpoints of the shared channel. The channel's allocation state belongs to that shared channel. This endpoint and matching principle follows the same pattern as for process channels, whose corresponding roles are called provider and client; pool interactions use provider and consumer terminology to name the participants.

Operation matching and pool suitability are separate decisions. Pool suitability determines whether a discoverable transaction channel can service a requested process. As specified in Section 4.2, suitability requires a match with the called process name and positive allocation weight for that process in the dependent agreement state indexed by the channel's transaction type, `Q(q) > 0`. The map `Q` is the complete agreement state for that channel; the transaction type is the protocol governing its negotiation and modification, not an independent compatibility mechanism. The subsequent matched `Up` is the access transition for the corresponding private channel: it re-enters that channel with its retained `Q` when the established agreement/channel is available, or creates a new private channel and initializes `Q` when no corresponding agreement exists. This access rule is distinct from `ExternalCall`'s discovery/negotiation procedure; a pool pair alone does not identify a unique agreement because multiple channels may carry distinct agreements.

Concrete state transitions, channel-identity changes, and continuation typing are constructor- and context-specific: pool `One`/`Up`/`Down` rules are recorded in [Pools and transaction types](../about-pools-and-transaction-types/README.md), while process-channel constructors and their typing rules are recorded in [Processes and session types, Sections 6–7](../about-processes-and-session-types/README.md#6-session-types-the-protocol-for-a-channel). Cancellation, failure, and implementation linearization remain open.

## 2. The process–pool boundary

Three concepts are important to keep separate:

- **Process incarnation:** a particular instance of a process body.
- **Provider endpoint:** the side of a channel belonging to the process that provides the service.
- **Client endpoint:** the side of that channel belonging to the process that uses the service.
- **Provider channel:** a channel viewed from the process that provides on it; its endpoint in that process is the provider endpoint.
- **Client channel:** a channel viewed from the process that uses it; its endpoint in that process is the client endpoint. The same channel is the provider channel for one process and a client channel for the other; these labels describe relative roles of a single channel resource.
- **Servicing pool:** the pool associated with the incarnation and responsible for servicing its provider channel.

For `ExternalCall`, the current working model searches discoverable transaction channels for a suitable dependent agreement state and, if needed, negotiates over a candidate channel before creating a fresh incarnation. Only after a suitable transaction channel has been found or the parties have successfully negotiated its dependent agreement state does the engine create the fresh incarnation together with its fresh provider channel and associate it with the selected servicing pool. The engine creates the incarnation; the selected pool services its provider channel. The pool-selection mechanism and transaction-type model are documented in [Pools and transaction types](../about-pools-and-transaction-types/README.md) and Section 4 below.

The relevant boundary detail is channel provenance and pool association: `ExternalCall` uses a fresh provider channel and selects an eligible pool, while `InternalCall` transfers existing channels and keeps the invoking incarnation's pool. The language-level contracts for both forms are maintained in [Section 7 of the canonical document](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls).

## 3. Working model of `ExternalCall` and `InternalCall`

The language-level contracts and the distinction between `ExternalCall` and `InternalCall` are defined in the [canonical Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls). This section records only the pool-related consequences: `ExternalCall` invokes pool selection before a fresh incarnation is created and serviced; `InternalCall` creates the new incarnation in the invoking incarnation's existing pool, without pool selection. The `ExternalCall` selection and servicing sequence is specified as a working model in Section 4 below.

## 4. Pool selection and servicing

### 4.1 Association with a pool

**Inferred:** associating a new process incarnation with a servicing pool requires a separate pool-selection mechanism.

**Inferred (tentative direction):** the mechanism selects the pool to which the new process incarnation is bound.

**Inferred:** an incarnation is associated with at most one servicing pool at a time. Whether every incarnation requires a pool binding and whether that binding can change later remain **Open**.

### 4.2 Agreement-suitability criterion

**Agreed project decision:** a transaction channel `c` is suitable for a call of process `q` when its dependent agreement state has positive allocation weight for that process, `Q(q) > 0`, and the process name matches the call. `Q` is the complete agreement state indexed by the transaction type for channel `c`. This criterion is applied when searching discoverable transaction channels; the process-name match does not itself establish or modify the state. If no suitable channel is found, the call may proceed to negotiation with a candidate pool. The transaction type defines the protocol by which the parties establish or modify `Q`. See [Pools and transaction types, Section 2](../about-pools-and-transaction-types/README.md#2-core-concepts-and-terminology) for terminology and Section 4 for the transaction-type model.

### 4.3 Search and agreement negotiation

**Agreed project decisions:** `ExternalCall` supports both discovery of a suitable dependent agreement state on an existing transaction channel and negotiation of a new state. Automatic search examines discoverable transaction channels and selects the first suitable channel encountered in the existing selection order. The rules defining that order remain open. Suitability is determined by the criterion in Section 4.2.

If automatic search finds no suitable transaction channel, manual intervention always follows. A participant of the calling process's pool may select a candidate pool with which to negotiate a new dependent agreement state; selecting a candidate does not itself establish that state. The parties interact over the candidate transaction channel according to its applicable transaction type, which defines the negotiation protocol. If negotiation fails, the participant may select a different candidate before the shared timeout expires. A candidate already tried unsuccessfully cannot be selected again during the same call. The precise negotiation rules remain in the transaction-type model and are not fully specified here.

### 4.4 Creation and start of servicing after selection

After Section 4.3 either finds a suitable transaction channel or successfully negotiates its dependent agreement state, `ExternalCall` proceeds as follows:

1. The engine creates a fresh process incarnation together with a fresh provider channel and associates the incarnation with the selected servicing pool.
2. The engine atomically transfers all channels involved in the call: the fresh provider channel to the caller and the corresponding channel endpoints/bindings to the selected pool and new incarnation. Partial delivery is not an observable state; this delivery is mandatory for successful completion.
3. Once delivery succeeds, the protocol-level call is complete. The caller may resume its continuation and use the fresh provider channel immediately, including sending its first protocol action before the selected pool takes its first action. The selected pool may also begin servicing immediately. Their execution may proceed in either order or interleave, subject to protocol and linearity constraints.

The search-and-negotiation timeout and its pre-commit outcome are specified in Section 4.5.

### 4.5 Search-and-negotiation timeout

**Agreed project decisions:** the timeout belongs to the `ExternalCall` search-and-negotiation mechanism, not to the transaction type. The calling pool supplies one shared timeout setting for all agreement searches and negotiations initiated by calls from that pool. It starts when automatic search begins and covers the complete procedure in Section 4.3, including manual intervention and candidate negotiations. Selecting another candidate does not restart it.

Expiry is an outcome of the overall search-and-negotiation operation, not a type-compatibility judgment; it does not establish that no suitable agreement exists. If automatic search has found no suitable transaction channel and negotiation has not successfully established a dependent agreement state before expiry, the call terminates without a result: no servicing pool is selected, no incarnation or provider channel has been created, and the caller's supplied client channels remain with their original identities and protocol states. A later channel state cannot be applied to the terminated call; another attempt requires a new call. Failure-reporting details remain unspecified.

Once either a suitable transaction channel has been found or negotiation has successfully established its dependent agreement state, the timeout no longer governs subsequent engine work. The call proceeds to the incarnation-creation and atomic channel-delivery sequence in Section 4.4. The successful call returns the fresh provider channel.

This is the intended process–pool contract, not a claim about implementation conformance.

**Open:** the convention that a value of `0` means an infinite timeout has been proposed but is not yet an agreed rule.

## 5. Evidence and rationale

This section records the evidence and reasoning behind the working model. Claim status and implementation coverage remain distinct, as defined in Section 1.

### 5.1 Existing rationale for `ExternalCall`

**Evidence:** [Processes and session types, Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls) records the current project contract for `ExternalCall`. Pool selection is specified separately in Section 4.

### 5.2 Publication's cut/spawn rule

<a id="22-existing-rationale-publication-cutspawn-rule"></a>

The supplied calculus gives the following cut/spawn rule:

    proc(x ← P ; Q) 7→ proc([a/x]P), proc([a/x]Q) (a fresh)
    cut: allocate channel & spawn

Here `P` is the body of the process being spawned and `Q` is the original process's continuation. The rule allocates a fresh channel `a`, substitutes it for `x` in both expressions, and runs the two resulting processes so they can communicate over that shared channel. It therefore combines fresh-channel allocation and process spawning in this particular calculus.

This rule establishes the publication's cut/spawn semantics. Its correspondence to OrgLang, and the lifecycle and scheduling guarantees remain **Open**. The process `SpawnSpec` is an unfinished implementation attempt, not the source of an OrgLang language rule. In the transaction-type model, lowercase `spawn` is a protocol value/constructor whose application is permitted only when the named process has positive allocation weight `Q(q) > 0` on that transaction channel; it leaves `Q` unchanged. It must not be conflated with `ExternalCall`, which is the higher-level process-call operation that performs channel discovery or negotiation, creates a fresh incarnation, and delivers its provider channel. Nor is it the same as the unfinished process `SpawnSpec` or the pool API method `Spawn`. The precise correspondence, if any, between the publication's cut/spawn rule and OrgLang's transaction-level `spawn` remains **Open**.

## 6. Open questions and deferred topics

The current contract provides no progress guarantee for pending calls: it specifies neither eventual service nor a time bound. The following questions remain open because their answers can change observable behavior or resource ownership.

| Open question | Behavior/decision affected | Evidence or decision needed |
|---|---|---|
| Must every incarnation be bound to a servicing pool, and can the binding change? | Which pool is responsible for service and whether responsibility can migrate. | Explicit lifecycle/ownership decision; then verify the corresponding runtime transition. |
| What is the intended, complete process-creation path in the implementation after the unfinished `SpawnSpec` attempt? | How fresh process incarnations are actually created and connected to their provider/client channels; whether the current `ExternalCall`/`InternalCall` working model has a complete executable path. | Trace the current AST, checker, adapter, executor, and runtime path; identify focused tests with observable assertions. Do not treat the unfinished `SpawnSpec` as a language contract. |
| How is negotiation with a manually selected candidate pool defined by the transaction-type model? | Which parties participate, how terms are negotiated, and what constitutes agreement at the type level. | Transaction-type semantics and examples of successful and unsuccessful negotiation. |
| What happens if all available candidate pools have been tried unsuccessfully but the shared timeout has not expired? | Whether manual intervention waits for more candidates or the call terminates earlier. | An explicit project decision; do not infer this from timeout expiry or atomicity. |
| When are resources provisioned or reserved? | Whether selection reserves capacity and whether provisioning occurs before or after the call's commit point. | Pool/transaction model plus an explicit ordering rule relative to the commit point. |

Pool negotiation, transaction initiation, and resource reservation remain outside the current specification except where needed to define pool association and servicing. Implementation structures, call paths, and AST/API mappings should be inspected to answer these specific questions, not treated as semantic definitions in their own right.

