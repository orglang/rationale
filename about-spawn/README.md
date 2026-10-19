<!-- Canonical semantics: ../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls -->
# Process creation and pool selection

> **Status: preliminary semantic research.** This document explains the working model at the boundary between process creation and pool servicing. It records current working rules and their rationale; it is not yet a normative specification.

> **Canonical language contract:** the intended language-level semantics of `ExternalCall` and `InternalCall` are maintained in [Processes and session types, Section 7 — Intended semantics of named-process calls](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls). This document explains the process–pool boundary and the evidence and open questions around it; it does not duplicate those contracts.

## 1. Purpose and mental model

When a process invokes `ExternalCall`, the language-level operation requests service for a named process. The engine may need to create a fresh process incarnation and arrange for a pool to service the new incarnation's provider channel. These are related steps, but they are not the same thing:

- **`ExternalCall`** creates a fresh incarnation and delivers its fresh provider channel outward to the caller.
- **`InternalCall`** creates a fresh incarnation and injects an existing channel inward into it.
- **Process-incarnation creation** means creating a fresh instance of a process.
- **Pool selection and servicing** determine which pool is associated with the incarnation and which pool services its provider channel.

**Inferred:** `Spawn` is shorthand here for engine-level incarnation creation. Under the current model, creating a fresh incarnation is part of servicing either `ExternalCall` or `InternalCall`; a distinct source-language role for `Spawn` remains a question for authoritative language evidence.

The purpose of this document is to clarify the process–pool boundary before examining implementation structures or call paths. `Call` is the umbrella term for the two named-process call forms, `ExternalCall` and `InternalCall`.

### How to read status labels

Use the same claim-status vocabulary as the canonical [Processes and session types](../about-processes-and-session-types/README.md#1-scope-and-evidence) document:

- **Confirmed** means the claim is directly supported by an appropriate source. State what that source establishes; confirmation by one source does not confirm the claim for OrgLang.
- **Inferred** means the claim is a working interpretation or rule derived from available evidence, not directly established as a language rule.
- **Open** means the available evidence does not settle the claim or verification remains incomplete.

Use **Evidence** to identify the source or observation supporting a claim, not as a claim-status label. Keep implementation coverage separate from claim status. Issue comments are provisional discussion, not normative rules; a rule from the cited publication's calculus is not automatically an OrgLang rule.

## 2. The process–pool boundary

Three concepts are important to keep separate:

- **Process incarnation:** a particular instance of a process body.
- **Provider endpoint:** the side of a channel belonging to the process that provides the service.
- **Client endpoint:** the side of that channel belonging to the process that uses the service.
- **Provider channel:** a channel viewed from the process that provides on it; its endpoint in that process is the provider endpoint.
- **Client channel:** a channel viewed from the process that uses it; its endpoint in that process is the client endpoint. The same channel is the provider channel for one process and a client channel for the other; these labels do not name separate channel resources.
- **Servicing pool:** the pool associated with the incarnation and responsible for servicing its provider channel.

For `ExternalCall`, the current working model says that creating the incarnation and creating its fresh provider channel happen together. The selected pool is associated with that incarnation and services the provider channel; the pool does not itself create the incarnation.

The two forms differ here: `ExternalCall` creates a fresh provider channel with the incarnation, while `InternalCall` injects an existing channel that may predate the new incarnation. The precise language-level distinction between `ExternalCall` and `InternalCall` belongs in [Section 7 of the canonical document](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls).

**Inferred:** process servicing through a provider channel and transactions through the pool's public channel are separate mechanisms. `ExternalCall` describes named-process invocation; the pool's `Up … Down` protocol describes interaction through the pool's public transaction channel.

## 3. Working model of `ExternalCall` and `InternalCall`

The detailed language-level contracts are defined only in the [canonical Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls). For the process–pool boundary, the working distinction is:

- **`ExternalCall`:** the engine searches for a suitable pool; after finding one, it creates a fresh process incarnation together with a fresh provider channel, associates the incarnation with the selected pool, and starts servicing the provider channel.
- **`InternalCall`:** an existing channel is handed off to a target incarnation. The channel can therefore exist before the target incarnation is created.

The shared concept is `Call`; `ExternalCall` and `InternalCall` are its two forms, distinguished by whether a channel is delivered outward from or injected inward into the new incarnation.

## 4. Pool selection and servicing

### 4.1 Association with a pool

**Inferred:** associating a new process incarnation with a servicing pool requires a separate pool-selection mechanism.

**Inferred (tentative direction):** the mechanism selects the pool to which the new process incarnation is bound.

**Inferred:** an incarnation is associated with at most one servicing pool at a time. Whether every incarnation requires a pool binding and whether that binding can change later remain **Open**.

### 4.2 Eligibility and search order

Each pool has its own transaction type, which carries information about whether that pool can service a process with a given name. The exact encoding of eligibility and any additional runtime validation remain **Open**.

**Inferred:** for simplicity, pool selection searches for the first eligible pool, starting with the pool containing the caller and continuing through pools with which agreements are established. Agreements determine which further pools are considered; each candidate pool's own transaction type determines whether it is eligible.

### 4.3 Creation and start of servicing after selection

For `ExternalCall`, the current working sequence is:

1. The engine searches for the first eligible pool using the rule above.
2. Only after a suitable pool has been found, the engine creates a fresh process incarnation together with a fresh provider channel.
3. The engine associates the incarnation with the selected pool.
4. The selected pool begins servicing the provider channel immediately, without a separate readiness-wait stage.

The engine's message delivering the provider channel to the caller and the selected pool's start of servicing are **unordered**. The new incarnation body's readiness relative to these events remains unspecified.

If no eligible pool is found, the current model does not specify what happens next; failure and cancellation semantics remain deferred. Pool selection, agreements that guide the search, incarnation creation, channel delivery, and the start of servicing are conceptually distinct stages. This is separate from interacting with the pool through its public transaction channel.

The observable result of a serviced call is constrained by the canonical channel-placeholder rule in [Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls).

## 5. The pool's public channel

**Inferred:** the public channel discussed in [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85) is the pool's public transaction channel. Whether individual processes should have public channels remains **Open**.

The pool's public transaction channel has a transaction type of the form `Up` followed by a continuation that ultimately ends in `Down`.

**Inferred:** access through the pool's public transaction channel gives the client a private channel for the duration of the critical section. Exclusivity is scoped to this private channel and its interaction, rather than to all clients of the pool. Reaching `Down` marks the end of this protocol-bounded critical section; the client interaction along that channel continuation ends there.

Each interaction generates a new channel identifier for its continuation, reflected in the channel's type. Resource lifecycle after `Down`—closure, return to the pool, or another disposition—remains unspecified pending a precise account of the `Up` / continuation / `Down` semantics.

**TODO:** Decide whether the detailed `Up … Down` protocol explanation belongs in `about-transaction/README.md`. If so, move the protocol mechanics there and keep only the process/pool boundary distinction here.

This pool-level protocol is conceptually distinct from the process's provider channel and from the channels mapped to the new incarnation's client-role parameters in `ExternalCall`. The provider channel is the channel through which the new process incarnation provides service; its provider endpoint belongs to that incarnation, and the caller uses the corresponding client endpoint.

## 6. Evidence and rationale

This section records the evidence and reasoning behind the working model. Claim status and implementation coverage remain distinct, as defined in Section 1.

### 6.1 Existing rationale for `ExternalCall`

**Evidence:** [Processes and session types, Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls) records the current project contract for `ExternalCall`. Pool selection is specified separately in Section 4.

### 6.2 Publication's cut/spawn rule

<a id="22-existing-rationale-publication-cutspawn-rule"></a>

The supplied calculus gives the following cut/spawn rule:

    proc(x ← P ; Q) 7→ proc([a/x]P), proc([a/x]Q) (a fresh)
    cut: allocate channel & spawn

Here `P` is the body of the process being spawned and `Q` is the original process's continuation. The rule allocates a fresh channel `a`, substitutes it for `x` in both expressions, and runs the two resulting processes so they can communicate over that shared channel. It therefore combines fresh-channel allocation and process spawning in this particular calculus.

This rule establishes the publication's cut/spawn semantics. Its correspondence to OrgLang, the role of OrgLang's `SpawnSpec`, and the lifecycle and scheduling guarantees remain **Open**.

### 6.3 Issue #85 discussion

The issue comments are the strongest current evidence for the conceptual separation, but remain provisional:

- `ExternalCall` inside a process is the trigger for requesting work identified by `qn`; it is distinguished from a separate `spawn` message.
- Creating a process incarnation is described as an internal engine operation that services `ExternalCall`.
- An agreement between pools may make service possible, but the agreement itself does not create the process.
- Resource provisioning, reservation, and the exact point of incarnation creation are unresolved.

Relevant comments: [Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893), [pool agreements and transactions](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290639), [transactional types and process creation](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290369), [offer channel proposal](https://github.com/orglang/go-workspace/issues/85#issuecomment-6231176672), and [end-to-end service scenario](https://github.com/orglang/go-workspace/issues/85#issuecomment-6232198226).

## 7. Open questions and deferred topics

The following points remain **Open** or are explicitly deferred:

- **Pool binding:** must every incarnation always be bound to a pool, and can that binding change later?
- **Eligibility representation:** how exactly is a pool's ability to service a named process encoded in its transaction type?
- **No eligible pool:** what happens if the search finds no suitable pool?
- **Lifecycle and scheduling:** when is the incarnation's body ready to execute, and what further guarantees follow from the publication's cut/spawn rule, if any?
- **Resource provisioning and reservation:** what role do these play, and when do they occur?
- **Public channels for individual processes:** should they exist at all?
- **Failures and abnormal termination:** how do they affect callers or held client channels?
- **Cancellation and progress:** what happens to calls that cannot be serviced or remain pending?

The current contract provides no progress guarantee for pending calls: it specifies neither eventual service nor a time bound.

Pool negotiation, transaction initiation, and resource reservation are outside the current phase except where needed to clarify how an incarnation is associated with the pool responsible for servicing it. Implementation structures, call paths, and mappings between AST/API representations are also deferred until the semantic model is sufficiently stable.

