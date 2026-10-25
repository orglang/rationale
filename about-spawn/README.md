<!-- Canonical semantics: ../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls -->
# Process creation and pool selection

> **Status: preliminary semantic research.** This document explains the working model at the boundary between process creation and pool servicing. Its rules and rationale remain research findings pending a normative specification.

> **Canonical language contract:** the intended language-level semantics of `ExternalCall` and `InternalCall` are maintained in [Processes and session types, Section 7 — Intended semantics of named-process calls](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls). This document focuses on the process–pool boundary, its supporting evidence, and its open questions. The canonical document defines the language-level contracts.

## 1. Purpose and mental model

When a process invokes `ExternalCall`, the language-level operation requests service for a named process. The engine may need to perform two distinct tasks: create a fresh process incarnation and arrange for a pool to service the new incarnation's provider channel.

- **`ExternalCall`** creates a fresh incarnation and delivers its fresh provider channel outward to the caller.
- **`InternalCall`** creates a fresh incarnation in the same pool as the invoking incarnation and transfers the invoking incarnation's existing channels into it; it does not perform pool selection.
- **Process-incarnation creation** means creating a fresh instance of a process.
- **Pool selection and servicing** determine which pool is associated with the incarnation and which pool services its provider channel.

**Inferred:** `Spawn` is shorthand here for engine-level incarnation creation. Under the current model, creating a fresh incarnation is part of servicing either `ExternalCall` or `InternalCall`; a distinct source-language role for `Spawn` remains a question for authoritative language evidence.

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

**Agreed project decision:** the search selects the first suitable agreement encountered in the search order. The current matching criterion is the name of the called process; additional criteria may be introduced in the future. The order of traversal itself remains unspecified. No ranking or preference among matching agreements is defined beyond selecting the first one encountered.

If the initial search finds no suitable agreement, the search is escalated to a participant of the calling process's pool for manual intervention. The participant's possible actions and the details of that intervention remain unspecified.

### 4.4 Creation and start of servicing after selection

For `ExternalCall`, the current working sequence is:

1. The engine searches for a suitable agreement according to the current matching criterion and traversal rule in Section 4.3. The agreement-search timeout covers this search.
2. If the initial search finds no suitable agreement, the search is escalated to a participant of the calling process's pool for manual intervention; this escalation remains within the same timeout.
3. Only after a suitable agreement has been found, the engine creates a fresh process incarnation together with a fresh provider channel.
4. The engine associates the incarnation with the selected pool. The agreement automatically obliges that pool to service the call; there is no separate discretionary acceptance step.
5. The fresh provider channel is delivered to the caller. Delivery is the commit point.
6. Only after delivery may the selected pool begin servicing the provider channel. Servicing and the caller's continuation may then execute in either order or interleave, subject to protocol and linearity constraints.

The timeout-expiry outcome before a suitable agreement is found, including the pre-commit state, is specified in Section 4.5 below.

The observable result of a serviced call is constrained by the canonical channel-placeholder rule in [Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls).

### 4.5 Agreement-search timeout

**Agreed project decision:** for an `ExternalCall`, the agreement-search timeout starts when the search for a suitable agreement begins. It covers the search and any escalation to a participant of the calling process's pool for manual intervention.

Finding the first suitable agreement in the search order fixes the selection and ends the timeout's effect. No separate acceptance or confirmation step is required: the agreement automatically obliges the selected pool to service the matching call. If discovery and timeout expiry race, whichever event wins determines the outcome. If timeout expiry wins, the search for this call terminates definitively; an agreement discovered afterward cannot be selected for that call.

If the timeout expires before a suitable agreement is found, the search ends without selecting a servicing pool. Under the current working sequence, no incarnation has yet been created and no provider channel has been delivered. The supplied client channels remain with the caller, with their original identities and protocol states. Failure reporting and recovery remain unspecified.

Once a suitable agreement is found before timeout expiry, the timeout no longer governs the call. Subsequent engine work—including incarnation creation and provider-channel delivery—may be delayed without triggering this search timeout. Delivery remains the `ExternalCall` commit point, and the selected pool may begin servicing only after delivery. This is the intended process–pool contract, not a claim about implementation conformance.

The source of the timeout value, who supplies or configures it, its representation, and its valid range remain unspecified. The convention that a value of `0` means an infinite timeout has been proposed but is not yet an agreed rule.

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

This rule establishes the publication's cut/spawn semantics. Its correspondence to OrgLang, the role of OrgLang's `SpawnSpec`, and the lifecycle and scheduling guarantees remain **Open**.

### 5.3 Issue #85 discussion

The issue comments are the strongest current evidence for the conceptual separation, but remain provisional:

- `ExternalCall` inside a process is the trigger for requesting work identified by `qn`; it is distinguished from a separate `spawn` message.
- Creating a process incarnation is described as an internal engine operation that services `ExternalCall`.
- An agreement between pools may enable service. Process-incarnation creation is a separate engine operation.
- Resource provisioning, reservation, and the exact point of incarnation creation are unresolved.

Relevant comments: [Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893), [pool agreements and transactions](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290639), [transactional types and process creation](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290369), and [end-to-end service scenario](https://github.com/orglang/go-workspace/issues/85#issuecomment-6232198226).

## 6. Open questions and deferred topics

The following points remain **Open** or are explicitly deferred:

- **Pool binding:** must every incarnation always be bound to a pool, and can that binding change later?
- **Eligibility representation:** how exactly is a pool's ability to service a named process encoded in its transaction type?
- **Manual-intervention outcome:** what happens after the calling pool's participant has been asked to intervene remains unspecified.
- **Lifecycle and scheduling:** when is the incarnation's body ready to execute, and what further guarantees follow from the publication's cut/spawn rule, if any?
- **Resource provisioning and reservation:** what role do these play, and when do they occur?
- **Failures and abnormal termination:** how do they affect callers or held client channels?
- **Cancellation and progress:** what happens to calls that cannot be serviced or remain pending?

The current contract provides no progress guarantee for pending calls: it specifies neither eventual service nor a time bound.

Pool negotiation, transaction initiation, and resource reservation are outside the current phase except where needed to clarify how an incarnation is associated with the pool responsible for servicing it. Implementation structures, call paths, and mappings between AST/API representations are also deferred until the semantic model is sufficiently stable.

