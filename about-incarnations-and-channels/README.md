<!-- Canonical semantics: participant/channel model, paired matching, incarnation and process–pool selection -->
# Incarnations and channels

> **Status: preliminary semantic research.** This document describes the shared participant, channel, and incarnation model for processes and pools, including paired matching and the process–pool servicing boundary.

> **Document scope:** this document owns the common model of participants, channels, endpoints, paired matching, process incarnations, and the process–pool selection and servicing boundary. Constructor-specific language contracts for `ExternalCall` and `InternalCall` remain in [Processes and session types, Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls); pool transaction-type details remain in [Pools and transaction types](../about-pools-and-transaction-types/README.md).

> **Implementation status:** The intended call and servicing behavior is specified independently of the incomplete implementation paths recorded in [Processes and session types, Part III](../about-processes-and-session-types/README.md#part-iii-implementation-evidence-and-open-questions).


## 1. Purpose and mental model

When a process invokes `ExternalCall`, the language-level operation requests service for a named process. The engine may need to perform two distinct tasks: create a fresh process incarnation and arrange for a pool to service the new incarnation's provider channel.

- **`ExternalCall`** creates a fresh incarnation and delivers its fresh provider channel outward to the caller.
- **`InternalCall`** creates a fresh incarnation in the same pool as the invoking incarnation and transfers the invoking incarnation's existing channels into it; it does not perform pool selection.
- **Process-incarnation creation** means creating a fresh instance of a process.
- **Pool selection and servicing** determine which pool is associated with the incarnation and which pool services its provider channel.

`SpawnSpec` is an unfinished process-expression implementation attempt, not an established source-language operation. The distinct process-AST, pool-API, and prototype representations—and the inspected execution gaps—are documented in [Processes and session types, Section 13](../about-processes-and-session-types/README.md#13-what-the-execution-path-establishes).

Under the current language-level working model, creating a fresh incarnation is part of servicing either `ExternalCall` or `InternalCall`; pool selection is specific to `ExternalCall`. See the implementation evidence in [Processes and session types, Section 13](../about-processes-and-session-types/README.md#13-what-the-execution-path-establishes) and the [pool executor implementation](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go) and [process executor implementation](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go).

`Call` is the umbrella term for the two named-process call forms, `ExternalCall` and `InternalCall`.

### How to read status labels

Use the same claim-status vocabulary as the canonical [Processes and session types](../about-processes-and-session-types/README.md#1-scope-and-evidence) document:

- **Confirmed** means the claim is directly supported by an appropriate source. State exactly what that source establishes; a claim confirmed by one source requires separate support before it is treated as confirmed for OrgLang.
- **Inferred** means the claim is a working interpretation or rule derived from available evidence; its status as a language rule remains unestablished.
- **Open** means the available evidence does not settle the claim or verification remains incomplete.

Use **Evidence** to identify the source or observation supporting a claim; use **Confirmed**, **Inferred**, and **Open** for claim status. Keep implementation coverage separate from claim status. Treat issue comments as provisional discussion. A rule from the cited publication's calculus requires separate evidence before it can be treated as an OrgLang rule.

## 2. Common matching principle

**Language-level principle shared by process channels and pool transaction channels:** each participant performs its own protocol-permitted operation. An operation performed by only one side remains pending; it does not by itself complete the interaction or advance the shared protocol state. The interaction takes effect when the corresponding peer operations match. Matching establishes one shared channel identity and the protocol-state effect for both endpoints. Each participant may then proceed through its own continuation where the operation defines one; the continuation expressions need not be textually identical, and matching does not imply simultaneous execution.

For ordinary process-to-process communication, the provider and client endpoints belong to one shared physical channel. Pool-to-pool transaction access uses distinct public and private physical channels for the same logical transaction channel; they share its logical identity and transaction type. A matched `Up` activates a new private channel. Matched `Down` commits it and restores the active binding to the public channel; `Rollback` also restores the public binding while discarding the uncommitted private-channel state. Neither outcome changes the logical identity or transaction type. The pool-specific lifecycle, process-allocation-function behavior, and continuation rules are defined in [Pools and transaction types](../about-pools-and-transaction-types/README.md).

Process-channel constructors and their typing rules are recorded in [Processes and session types, Sections 6–7](../about-processes-and-session-types/README.md#6-session-types-the-protocol-for-a-channel). The explicit initiation mechanism for `Rollback` and triggers other than timeout remain open; other failure handling and implementation linearization also remain open.

## 3. Participants and channels

A **participant** is a process incarnation or pool taking part in a channel interaction. Each participant has exactly one provider channel and may have any number of client channels. This cardinality rule applies to all channels in the model. Provider and client describe the participant's role on a channel: the same channel is the provider channel for one participant and a client channel for the other.

The following concepts distinguish participant and endpoint roles:

- **Process incarnation:** a particular instance of a process body.
- **Provider endpoint:** the side of a channel belonging to the participant that provides the service.
- **Client endpoint:** the side of that channel belonging to the participant that uses the service.
- **Provider channel:** a channel viewed from the participant that provides on it; its endpoint for that participant is the provider endpoint.
- **Client channel:** a channel viewed from the participant that uses it; its endpoint for that participant is the client endpoint. The same channel is the provider channel for one participant and a client channel for the other; these labels describe relative roles of a single channel resource.
- **Servicing pool:** the pool associated with the incarnation and responsible for servicing its provider channel.

### 3.1 The process–pool boundary

For `ExternalCall`, the current working model searches discoverable transaction channels for a suitable dependent agreement state and, if needed, negotiates over a candidate channel before creating a fresh incarnation. Only after a suitable transaction channel has been found or the parties have successfully negotiated its dependent agreement state does the engine create the fresh incarnation together with its fresh provider channel and associate it with the selected servicing pool. The engine creates the incarnation; the selected pool services its provider channel. The pool-selection mechanism and transaction-type model are documented in [Pools and transaction types](../about-pools-and-transaction-types/README.md) and Section 5 below.

The relevant boundary detail is channel provenance and pool association: `ExternalCall` uses a fresh provider channel and selects an eligible pool, while `InternalCall` transfers existing channels and keeps the invoking incarnation's pool. The language-level contracts for both forms are maintained in [Section 7 of the canonical document](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls).

## 4. Working model of `ExternalCall` and `InternalCall`

The language-level contracts and the distinction between `ExternalCall` and `InternalCall` are defined in the [canonical Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls). This section records only the pool-related consequences: `ExternalCall` invokes pool selection before a fresh incarnation is created and serviced; `InternalCall` creates the new incarnation in the invoking incarnation's existing pool, without pool selection. The `ExternalCall` selection and servicing sequence is specified as a working model in Section 5 below.

## 5. Pool selection and servicing

### 5.1 Association with a pool

**Inferred:** `ExternalCall` requires a pool-selection mechanism to identify the servicing pool for the new incarnation.

**Agreed working model:** the selected pool is the pool to which the new incarnation is bound.

**Agreed working model:** each process incarnation is bound to a specific servicing pool. Whether that binding can change later remains **Open**.

### 5.2 Agreement-suitability criterion

**Agreed project decision:** a transaction channel `c` is suitable for a call of process `q` when its process name matches the call and the `Q` of the latest committed private channel for that logical transaction channel satisfies `Q(q) > 0`. Search uses this `Q` only to check suitability and select candidates; it does not modify the function or the committed channel. How search obtains `Q` remains **Open**. If no suitable committed private channel is found, the call may proceed to negotiation with a candidate pool. The interpretation of `Q` and the public/private transaction-type distinction are defined in [Pools and transaction types](../about-pools-and-transaction-types/README.md).

### 5.3 Search and agreement negotiation

**Agreed project decisions:** `ExternalCall` supports discovery of a suitable committed private channel and negotiation that prepares an updated state on a newly created private channel. Automatic search examines discoverable logical transaction channels using, for each provider/client pair, the latest private channel committed through `Down`; it selects the first suitable logical channel encountered in the existing selection order. The rules defining that order remain open. An uncommitted newer private channel does not replace the current search target. Suitability is determined by the criterion in Section 5.2.

If automatic search finds no suitable committed private channel, manual intervention follows. A participant of the calling process's pool selects candidate pools for negotiation. The available candidates are tried in an unspecified order; selecting a candidate does not itself establish or modify an agreement. For each candidate, the selected provider/client pair performs matched `Up`, which creates a new private physical channel for the existing logical transaction channel and gives it the current `Q` of that same logical channel (or `Q⁰` if no private channel has yet been committed). If all available candidates are exhausted without success, negotiation terminates without a result, even if the shared timeout has not expired. The timeout remains an independent time limit for the overall search-and-negotiation procedure. The new private channel can change its own process-allocation-function value through any number of `Coop` and `Isol` operations; `Q'` denotes that in-progress value and is not a separate function or stored field. The previously committed `Q` remains effective for search throughout negotiation. Every `Up` has exactly one terminal outcome: matched `Down` commits the prepared value, or `Rollback` cancels the uncommitted access. There is no second uncommitted private channel for the same logical channel. Matched `Down` is the commit boundary: it commits the value prepared by the current private channel and makes that channel the current committed private channel, replacing the previous one for that logical channel. `Down` itself does not change the function, and it does not imply physical destruction of the superseded private channel. If the search-and-negotiation timeout expires while a private-channel negotiation is active, it triggers `Rollback`; the uncommitted state is discarded and the previously committed `Q` remains current. The call then terminates without a result. The explicit rollback initiation mechanism and triggers other than timeout remain open; candidate-switching details are also not fully specified here.

### 5.4 Creation and start of servicing after selection

After Section 5.3 either finds a suitable existing committed agreement or completes negotiation and matched `Down` has committed the prepared state with `Q(q) > 0`, `ExternalCall` proceeds as follows:

1. The engine creates a fresh process incarnation together with a fresh provider channel and associates the incarnation with the selected servicing pool.
2. The engine atomically transfers all channels involved in the call: the fresh provider channel to the caller and the corresponding channel endpoints/bindings to the selected pool and new incarnation. Partial delivery is not an observable state; this delivery is mandatory for successful completion.
3. Once delivery succeeds, the protocol-level call is complete. The caller may resume its continuation and use the fresh provider channel immediately, including sending its first protocol action before the selected pool takes its first action. The selected pool may also begin servicing immediately. Their execution may proceed in either order or interleave, subject to protocol and linearity constraints.

The search-and-negotiation timeout and its pre-commit outcome are specified in Section 5.5.

### 5.5 Search-and-negotiation timeout

**Agreed project decisions:** the timeout belongs to the `ExternalCall` search-and-negotiation mechanism, not to the transaction type. The calling pool supplies one shared timeout setting for all agreement searches and negotiations initiated by calls from that pool. It starts when automatic search begins and covers the complete procedure in Section 5.3, including candidate negotiations. Selecting another candidate does not restart it.

Expiry is an outcome of the overall search-and-negotiation operation, not a type-compatibility judgment; it does not establish that no suitable agreement exists. If automatic search has found no suitable committed private channel and negotiation has not reached a matched `Down` that commits a suitable state before expiry, the call terminates without a result: no servicing pool is selected, no incarnation or provider channel has been created, and the caller's supplied client channels remain with their original identities and protocol states. If expiry occurs during an active private-channel negotiation, it triggers `Rollback`: the uncommitted private-channel state, including changes to `Q`, is discarded and the active binding returns to the public channel. The previously committed private channel remains the search target and its `Q` remains current. A later channel state cannot be applied to the terminated call; another attempt requires a new call. Failure-reporting details remain unspecified.

Once either a suitable committed transaction channel has been found or negotiation has reached matched `Down` and committed a suitable agreement state, the timeout no longer governs subsequent engine work. The call proceeds to the incarnation-creation and atomic channel-delivery sequence in Section 5.4. The successful call returns the fresh provider channel.

This is the intended process–pool contract, not a claim about implementation conformance.

**Open:** the convention that a value of `0` means an infinite timeout has been proposed but is not yet an agreed rule.

## 6. Evidence and rationale

This section records the evidence and reasoning behind the working model. Claim status and implementation coverage remain distinct, as defined in Section 1.

### 6.1 Existing rationale for `ExternalCall`

**Evidence:** [Processes and session types, Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls) records the current project contract for `ExternalCall`. Pool selection is specified separately in Section 5.

### 6.2 Publication's cut/spawn rule

<a id="22-existing-rationale-publication-cutspawn-rule"></a>

The supplied calculus gives the following cut/spawn rule:

    proc(x ← P ; Q) 7→ proc([a/x]P), proc([a/x]Q) (a fresh)
    cut: allocate channel & spawn

Here `P` is the body of the process being spawned and `Q` is the original process's continuation. The rule allocates a fresh channel `a`, substitutes it for `x` in both expressions, and runs the two resulting processes so they can communicate over that shared channel. It therefore combines fresh-channel allocation and process spawning in this particular calculus.

This rule establishes only the publication's cut/spawn semantics; its correspondence to OrgLang, including lifecycle and scheduling guarantees, remains **Open**. OrgLang's lowercase transaction-type `spawn` is a distinct protocol constructor guarded by positive committed allocation weight `Q(q)` and leaves `Q` unchanged; see [Pools and transaction types](../about-pools-and-transaction-types/README.md). The higher-level `ExternalCall` contract, including discovery, negotiation, incarnation creation, and provider-channel delivery, is defined in [Processes and session types, Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls). The unfinished AST `SpawnSpec` and pool API `Spawn` are implementation representations, not substitutes for either language contract. Any correspondence between the publication's cut rule and transaction-level `spawn` remains **Open**.

## 7. Open questions and deferred topics

The current contract provides no progress guarantee for pending calls: it specifies neither eventual service nor a time bound. The following questions remain open because their answers can change observable behavior or resource ownership.

| Open question | Behavior/decision affected | Evidence or decision needed |
|---|---|---|
| Can an incarnation's servicing-pool binding change after it is established? | Whether servicing responsibility can migrate. | An explicit lifecycle/ownership decision; then verify the corresponding runtime transition. |
| What is the intended, complete process-creation path in the implementation after the unfinished `SpawnSpec` attempt? | How fresh process incarnations are actually created and connected to their provider/client channels; whether the current `ExternalCall`/`InternalCall` working model has a complete executable path. | Trace the current AST, checker, adapter, executor, and runtime path; identify focused tests with observable assertions. Do not treat the unfinished `SpawnSpec` as a language contract. |
| How is negotiation with a manually selected candidate pool defined by the transaction-type model? | Which parties participate, how terms are negotiated, and what constitutes agreement at the type level. | Transaction-type semantics and examples of successful and unsuccessful negotiation. |
| When are resources provisioned or reserved? | Whether selection reserves capacity and whether provisioning occurs before or after the call's commit point. | Deferred as an implementation detail; revisit only if it affects the semantic contract. |

Pool negotiation, transaction initiation, and resource reservation remain outside the current specification except where needed to define pool association and servicing. Implementation structures, call paths, and AST/API mappings should be inspected to answer these specific questions, not treated as semantic definitions in their own right.

