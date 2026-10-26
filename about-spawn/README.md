<!-- Canonical semantics: ../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls -->
# Process creation and pool selection

> **Status: preliminary semantic research.** This document explains the working model at the boundary between process creation and pool servicing. Its rules and rationale remain research findings pending a normative specification.

> **Canonical language contract:** the intended language-level semantics of `ExternalCall` and `InternalCall` are maintained in [Processes and session types, Section 7 — Intended semantics of named-process calls](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls). This document focuses on the process–pool boundary, its supporting evidence, and its open questions. The canonical document defines the language-level contracts.

> **Implementation status and purpose of this specification:** The process and call mechanisms discussed here have had multiple implementation attempts; none is known to be complete. This is why the project is writing a specification: to establish the intended behavior independently of any partial AST, adapter, executor, prototype, or test path. Implementation observations below are evidence about those attempts, not a claim that the language contract is already implemented. Do not infer intended semantics from whichever attempt happens to exist in code.


## 1. Purpose and mental model

When a process invokes `ExternalCall`, the language-level operation requests service for a named process. The engine may need to perform two distinct tasks: create a fresh process incarnation and arrange for a pool to service the new incarnation's provider channel.

- **`ExternalCall`** creates a fresh incarnation and delivers its fresh provider channel outward to the caller.
- **`InternalCall`** creates a fresh incarnation in the same pool as the invoking incarnation and transfers the invoking incarnation's existing channels into it; it does not perform pool selection.
- **Process-incarnation creation** means creating a fresh instance of a process.
- **Pool selection and servicing** determine which pool is associated with the incarnation and which pool services its provider channel.

**Project clarification:** `SpawnSpec` is an unfinished implementation attempt for process spawning, not evidence of a separate, established source-language operation. It should not be used to define OrgLang semantics.

**Implementation evidence:** the repository contains several similarly named representations that must be kept distinct. The process-expression `SpawnSpec` has no execution branch in the inspected process executor; an older `SpawnSpecOld` branch remains commented out. Separately, the pool API's `Spawn` method creates a new process-execution record, but the inspected implementation does not instantiate or attach a process body there. These observations support the status “incomplete implementation attempt”; they do not define the intended replacement semantics.

Under the current language-level working model, creating a fresh incarnation is part of servicing either `ExternalCall` or `InternalCall`; pool selection is specific to `ExternalCall`. See the implementation evidence in [Processes and session types, Section 13](../about-processes-and-session-types/README.md#13-what-the-execution-path-establishes) and the [pool executor implementation](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go) and [process executor implementation](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go).

The purpose of this document is to clarify the process–pool boundary before examining implementation structures or call paths. `Call` is the umbrella term for the two named-process call forms, `ExternalCall` and `InternalCall`.

### How to read status labels

Use the same claim-status vocabulary as the canonical [Processes and session types](../about-processes-and-session-types/README.md#1-scope-and-evidence) document:

- **Confirmed** means the claim is directly supported by an appropriate source. State exactly what that source establishes; a claim confirmed by one source requires separate support before it is treated as confirmed for OrgLang.
- **Inferred** means the claim is a working interpretation or rule derived from available evidence; its status as a language rule remains unestablished.
- **Open** means the available evidence does not settle the claim or verification remains incomplete.

Use **Evidence** to identify the source or observation supporting a claim; use **Confirmed**, **Inferred**, and **Open** for claim status. Keep implementation coverage separate from claim status. Treat issue comments as provisional discussion. A rule from the cited publication's calculus requires separate evidence before it can be treated as an OrgLang rule.

## 2. The process–pool boundary

Three concepts are important to keep separate:

- **Process incarnation:** a particular instance of a process body.
- **Provider endpoint:** the side of a channel belonging to the process that provides the service.
- **Client endpoint:** the side of that channel belonging to the process that uses the service.
- **Provider channel:** a channel viewed from the process that provides on it; its endpoint in that process is the provider endpoint.
- **Client channel:** a channel viewed from the process that uses it; its endpoint in that process is the client endpoint. The same channel is the provider channel for one process and a client channel for the other; these labels describe relative roles of a single channel resource.
- **Servicing pool:** the pool associated with the incarnation and responsible for servicing its provider channel.

For `ExternalCall`, the current working model says that the engine creates a fresh incarnation together with a fresh provider channel, then associates the incarnation with a selected pool for servicing. The engine creates the incarnation; the selected pool services its provider channel. The pool-selection mechanism and transaction-type model are documented in [Pools and transaction types](../about-pools-and-transaction-types/README.md) and Section 4 below.

The relevant boundary detail is channel provenance and pool association: `ExternalCall` uses a fresh provider channel and selects an eligible pool, while `InternalCall` transfers existing channels and keeps the invoking incarnation's pool. The language-level contracts for both forms are maintained in [Section 7 of the canonical document](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls).

## 3. Working model of `ExternalCall` and `InternalCall`

The language-level contracts and the distinction between `ExternalCall` and `InternalCall` are defined in the [canonical Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls). This section records only the pool-related consequences: `ExternalCall` invokes pool selection before a fresh incarnation is created and serviced; `InternalCall` creates the new incarnation in the invoking incarnation's existing pool, without pool selection. The `ExternalCall` selection and servicing sequence is specified as a working model in Section 4 below.

## 4. Pool selection and servicing

### 4.1 Association with a pool

**Inferred:** associating a new process incarnation with a servicing pool requires a separate pool-selection mechanism.

**Inferred (tentative direction):** the mechanism selects the pool to which the new process incarnation is bound.

**Inferred:** an incarnation is associated with at most one servicing pool at a time. Whether every incarnation requires a pool binding and whether that binding can change later remain **Open**.

### 4.2 Matching criterion

**Agreed project decision:** the current criterion for a suitable agreement is a match with the name of the called process. Additional matching criteria may be introduced in the future; they are not specified here. The role of transaction types in pool agreements remains a separate open question, documented in [Pools and transaction types, Section 4](../about-pools-and-transaction-types/README.md#4-transaction-types).

### 4.3 Search order

**Agreed project decisions:** automatic search looks among previously established agreements and selects the first suitable agreement encountered in an existing selection order. The rules defining that order remain open.

If automatic search finds no suitable previously established agreement, manual intervention always follows. A participant of the calling process's pool can select a candidate pool to begin negotiation of a new agreement; selecting a pool does not itself establish a completed agreement. If negotiation with that candidate does not succeed, the participant may select a different candidate before the shared timeout expires. A candidate that has already been tried unsuccessfully cannot be selected again during the same call. The negotiation participants and detailed negotiation semantics remain unspecified here because they belong to the transaction-type model.

### 4.4 Creation and start of servicing after selection

For `ExternalCall`, the current working sequence is:

1. The engine searches among previously established agreements for a suitable agreement, using the matching criterion and selection order described in Section 4.3.
2. If automatic search finds no suitable established agreement, manual intervention always follows. A participant of the calling process's pool may select a candidate pool.
3. Selecting a candidate pool begins negotiation of a new agreement; it does not itself complete the agreement. The negotiation's participant roles and detailed rules belong to the transaction-type model and are not defined here.
4. If negotiation with a candidate does not succeed, the participant may select a different candidate before timeout expiry, but may not retry a candidate already tried during this call. Selecting another candidate does not restart the timeout.
5. The same overall timeout covers automatic search, manual intervention, candidate selection, and agreement negotiation. If no candidate is selected before expiry, the call terminates without a result. If candidates have all been tried unsuccessfully while time remains, what happens next remains open.
6. Only after the parties agree on the terms before timeout expiry does the call proceed to creation of a fresh process incarnation together with a fresh provider channel.
7. The engine atomically transfers all channels involved in the call to both sides: the fresh provider channel to the caller and the corresponding channel endpoints/bindings to the selected pool and new incarnation. This is one indivisible delivery operation; partial delivery is not a possible state. Delivery is mandatory for successful completion of the call.
8. Once this atomic transfer succeeds, the protocol-level call is successfully complete. The selected pool may begin servicing immediately without waiting for the caller's continuation to resume; the selected pool and caller may execute in either order or interleave, subject to protocol and linearity constraints. The call produces no separate result value beyond delivery of the fresh provider channel. A protocol-level failure after successful delivery is not a possible outcome.

The timeout-expiry outcome when an agreement has not been successfully negotiated, including the pre-commit state, is specified in Section 4.5 below.

A successful `ExternalCall` produces no separate result value: its call-specific outcome is delivery of the fresh provider channel, as specified by the canonical channel-placeholder contract in [Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls).

### 4.5 Agreement-search timeout

**Agreed project decisions:** for an `ExternalCall`, the agreement-search timeout belongs to the search mechanism, not to the transaction type. The calling pool supplies one shared timeout setting for all agreement searches initiated by calls from that pool. The timeout starts when automatic search begins and covers searching previously established agreements, escalation to a participant of the calling process's pool, manual selection of candidate pools, and negotiation of new agreements with those candidates. Selecting another candidate does not restart the timeout.

Timeout expiry is an outcome of the overall search-and-negotiation operation, not a type-compatibility judgment; it does not establish that no suitable agreement exists. If automatic search finds no suitable previously established agreement, manual intervention always follows. Selecting a candidate pool begins negotiation of a new agreement and is not itself a completed agreement. If negotiation with a candidate does not succeed, a different candidate may be selected before timeout expiry; a candidate already tried unsuccessfully cannot be selected again during the same call. The parties must agree on the terms for the agreement to be considered successfully negotiated. The participants and detailed negotiation rules belong to the transaction-type model and remain outside this section.

If the parties agree on the terms before timeout expiry, the call proceeds to the incarnation-creation and atomic channel-delivery sequence in Section 4.4. The successful call has no separate result value beyond delivery of the fresh provider channel. Once agreement negotiation succeeds, this timeout no longer governs subsequent engine work.

If timeout expiry occurs before the agreement is successfully negotiated, the call terminates without a result; there is no alternative outcome. No servicing pool is selected for the call, no incarnation has yet been created, and no provider channel has been delivered. The caller's supplied client channels remain with the caller, with their original identities and protocol states, as required by the call's atomicity. A later agreement cannot be applied to the terminated call; another attempt requires a new call. Failure reporting details remain unspecified.

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

This rule establishes the publication's cut/spawn semantics. Its correspondence to OrgLang, and the lifecycle and scheduling guarantees remain **Open**. The process `SpawnSpec` is an unfinished implementation attempt, not the source of an OrgLang language rule.

### 5.3 Issue #85 discussion

The issue comments are the strongest current evidence for the conceptual separation, but remain provisional:

- `ExternalCall` inside a process is the trigger for requesting work identified by `qn`; it is distinguished from a separate `spawn` message.
- Creating a process incarnation is described as an internal engine operation that services `ExternalCall`.
- An agreement between pools may enable service. Process-incarnation creation is a separate engine operation.
- Resource provisioning, reservation, and the exact point of incarnation creation are unresolved.

Relevant comments: [Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893), [pool agreements and transactions](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290639), [transactional types and process creation](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290369), and [end-to-end service scenario](https://github.com/orglang/go-workspace/issues/85#issuecomment-6232198226).

## 6. Open questions and deferred topics

The current contract provides no progress guarantee for pending calls: it specifies neither eventual service nor a time bound. The following questions remain open because their answers can change observable behavior or resource ownership.

| Open question | Behavior/decision affected | Evidence or decision needed |
|---|---|---|
| Must every incarnation be bound to a servicing pool, and can the binding change? | Which pool is responsible for service and whether responsibility can migrate. | Explicit lifecycle/ownership decision; then verify the corresponding runtime transition. |
| How is eligibility represented in a pool's transaction type? | Whether a matching agreement is sufficient for selection and whether additional validation can reject it. | A transaction-type/agreement contract in [Pools and transaction types, Section 4](../about-pools-and-transaction-types/README.md#4-transaction-types), with positive and negative examples. |
| What is the intended, complete process-creation path in the implementation after the unfinished `SpawnSpec` attempt? | How fresh process incarnations are actually created and connected to their provider/client channels; whether the current `ExternalCall`/`InternalCall` working model has a complete executable path. | Trace the current AST, checker, adapter, executor, and runtime path; identify focused tests with observable assertions. Do not treat the unfinished `SpawnSpec` as a language contract. |
| How is negotiation with a manually selected candidate pool defined by the transaction-type model? | Which parties participate, how terms are negotiated, and what constitutes agreement at the type level. | Transaction-type semantics and examples of successful and unsuccessful negotiation. |
| What happens if all available candidate pools have been tried unsuccessfully but the shared timeout has not expired? | Whether manual intervention waits for more candidates or the call terminates earlier. | An explicit project decision; do not infer this from timeout expiry or atomicity. |
| When may the new incarnation's body execute relative to channel delivery and the caller's continuation? | Observable scheduling and whether servicing can race with caller behavior. | Explicit scheduling contract and concurrency tests. The publication's cut/spawn rule does not establish OrgLang scheduling guarantees. |
| When are resources provisioned or reserved? | Whether selection reserves capacity and whether provisioning occurs before or after the call's commit point. | Pool/transaction model plus an explicit ordering rule relative to the commit point. |
| What state is observable on each side of the `ExternalCall` delivery commit point? | Whether a call can expose a partial incarnation/channel transfer or begin servicing before delivery. | Preserve the pre-commit invariants in Section 4.5 and test them; error reporting, recovery, retry, and abnormal-termination semantics are out of scope. |
| What guarantees exist for a call that remains pending? | Whether callers can rely on eventual service or a time bound. | An explicit progress guarantee or an explicit statement that no such guarantee is provided. The current model provides none. |

Pool negotiation, transaction initiation, and resource reservation remain outside the current specification except where needed to define pool association and servicing. Implementation structures, call paths, and AST/API mappings should be inspected to answer these specific questions, not treated as semantic definitions in their own right.

