<!-- Canonical semantics: ../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-operations -->
# Process creation and pool selection

> **Status: preliminary semantic research.** This document explains the working model at the boundary between process creation and pool servicing. It records current working rules and their rationale; it is not yet a normative specification.

> **Canonical language contract:** the intended language-level semantics of `Call` and `Link` are maintained in [Processes and session types, Section 7 — Intended semantics of named-process operations](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-operations). This document explains the process–pool boundary and the evidence and open questions around it; it does not duplicate those contracts.

## 1. Purpose and mental model

When a process invokes `Call`, the language-level operation requests service for a named process. The engine may need to create a fresh process incarnation and arrange for a pool to service the new incarnation's provider channel. These are related steps, but they are not the same thing:

- **`Call`** is a language-level operation with a contract defined in the canonical document.
- **Process-incarnation creation** means creating a fresh instance of a process.
- **Pool selection and servicing** determine which pool is associated with the incarnation and which pool services its provider channel.
- **`Spawn`** is used here as descriptive shorthand for engine-level incarnation creation, not as a separate source-language operation.

**Agreed working rule:** this model does not introduce a distinct semantic operation called `Spawn`. Creating a fresh incarnation is an internal step by which the engine services `Call`. This may be revisited only if later evidence establishes a separate semantic role for `Spawn`.

The purpose of this document is to make that boundary clear before studying implementation structures or call paths.

### How to read the status labels

- **Agreed** means an agreed working rule for this research phase, not necessarily a final normative specification.
- **Tentative** marks a proposed direction that may change.
- **Open** marks a question not yet resolved.
- **Evidence** identifies a source or observation that supports discussion; evidence does not automatically establish a language rule.

Issue comments are provisional discussion, not normative rules. A rule from the cited publication's calculus is not automatically an OrgLang rule.

## 2. The process–pool boundary

Three concepts are important to keep separate:

- **Process incarnation:** a particular instance of a process body.
- **Provider channel:** the channel through which the incarnation communicates with its client according to a session type.
- **Servicing pool:** the pool associated with the incarnation and responsible for servicing its provider channel.

For `Call`, the current working model says that creating the incarnation and creating its fresh provider channel happen together. The selected pool is associated with that incarnation and services the provider channel; the pool does not itself create the incarnation.

This is not a universal rule that channel creation and incarnation creation must always coincide. `Link` hands off an existing channel, so its target incarnation may be created after that channel already exists. The precise language-level distinction between `Call` and `Link` belongs in [Section 7 of the canonical document](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-operations).

**Agreed separation:** servicing a process through its provider channel is distinct from interacting with a pool through the pool's public transaction channel. A `Call` does not, by itself, require a transaction through the pool's public channel or entry into its critical section. Conversely, the pool's `Up … Down` protocol does not imply a `Call` or process-incarnation creation.

## 3. Working model of `Call` and `Link`

The detailed language-level contracts are defined only in the [canonical Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-operations). For the process–pool boundary, the working distinction is:

- **`Call`:** the engine searches for a suitable pool; after finding one, it creates a fresh process incarnation together with a fresh provider channel, associates the incarnation with the selected pool, and starts servicing the provider channel.
- **`Link`:** an existing channel is handed off to a target incarnation. The channel can therefore exist before the target incarnation is created.

These statements summarize the working model only; they do not replace the canonical contracts or settle implementation details.

## 4. Pool selection and servicing

### 4.1 Association with a pool

**Agreed working rule:** associating a new process incarnation with a servicing pool requires a separate mechanism. The servicing pool is not determined automatically from the caller's context.

**Tentative direction:** the mechanism selects the pool to which the new process incarnation itself is bound, rather than merely selecting a pool as a property of the `Call` request.

**Agreed working constraint:** an incarnation cannot be bound to multiple pools simultaneously; the mechanism selects at most one pool for an incarnation. It remains **Open** whether every incarnation must always have a pool binding or whether that binding can later change.

### 4.2 Eligibility and search order

Each pool has its own transaction type, which carries information about whether that pool can service a process with a given name. For the current semantic model, this type-level eligibility is sufficient; no separate acceptance step is required.

**Agreed working search rule:** for simplicity, pool selection searches for the first eligible pool, starting with the pool containing the caller and continuing through pools with which agreements are established. Agreements determine which further pools are considered; each candidate pool's own transaction type determines whether it is eligible.

The exact encoding of eligibility information remains **Open**. Performance shares or weights and the resulting load distribution are separate concerns outside the current scope.

### 4.3 Creation and start of servicing after selection

For `Call`, the current working sequence is:

1. The engine searches for the first eligible pool using the rule above.
2. Only after a suitable pool has been found, the engine creates a fresh process incarnation together with a fresh provider channel.
3. The engine associates the incarnation with the selected pool. The selected pool does not create the incarnation itself.
4. The selected pool begins servicing the provider channel immediately, without a separate readiness-wait stage.

The engine's message delivering the provider channel to the caller and the selected pool's start of servicing are **unordered**: neither event is required to precede the other. The precise point at which the new incarnation's body becomes ready to execute relative to these events is unspecified, because the current semantic model does not depend on that ordering.

If no eligible pool is found, the current model does not specify what happens next; failure and cancellation semantics remain deferred. Pool selection, agreements that guide the search, incarnation creation, channel delivery, and the start of servicing are conceptually distinct stages. This is separate from interacting with the pool through its public transaction channel.

The observable result of a serviced call is constrained by the canonical channel-placeholder rule in [Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-operations). A separate `Spawn` operation should be reconsidered only if later semantic evidence establishes a role not covered by `Call` and its servicing transition.

## 5. The pool's public channel

<a id="4-pool-public-channel-and-callees-private-communication-channel"></a>

**Agreed clarification:** the public channel discussed in [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85) is the pool's public channel, not a public channel belonging to each process. Whether individual processes should have public channels remains **Open**.

The pool's public channel has a transaction type of the form `Up` followed by a continuation that ultimately ends in `Down`.

**Agreed working interpretation:** access through the pool's public channel gives the client a private channel for the duration of the critical section. Exclusivity is scoped to this private channel and the interaction conducted through it; it does not, by itself, imply a global lock that prevents all other clients from interacting with the pool. Reaching `Down` marks the end of this protocol-bounded critical section, and the client can no longer continue the interaction along that channel continuation after that point.

This must be understood in light of channel identity: each interaction generates a new channel identifier for continuing the interaction, and this succession of identifiers is reflected in the channel's type. Thus, in one sense, the channel is continually changing. Unavailability after `Down` does not by itself specify whether an underlying channel resource is closed, returned to the pool, or otherwise handled. Further guarantees should be derived from the exact `Up` / continuation / `Down` semantics, not assumed from the analogy alone.

**TODO:** Decide whether the detailed `Up … Down` protocol explanation belongs in `about-transaction/README.md`. If so, move the protocol mechanics there and keep only the process/pool boundary distinction here.

This pool-level protocol is conceptually distinct from the process's provider channel and from the client channels passed to `Call`. The provider channel is the sole channel associated with the new process incarnation for communication with its client; the current model introduces no separate callee-private communication channel.

## 6. Evidence and rationale

This section records why the working model is being considered. These sources inform the research but do not, by themselves, establish OrgLang's normative semantics or implementation.

### 6.1 Existing rationale for `Call`

**Evidence — canonical contract.** [Processes and session types, Section 7](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-operations) records the current intended `Call` contract. Its authoritative language source and implementation mapping remain unverified. This does not establish that `Call` is implemented using `Spawn`, nor does it settle the pool-selection mechanism described in Section 4.

### 6.2 Publication's cut/spawn rule

<a id="22-existing-rationale-publication-cutspawn-rule"></a>

The supplied calculus gives the following cut/spawn rule:

    proc(x ← P ; Q) 7→ proc([a/x]P), proc([a/x]Q) (a fresh)
    cut: allocate channel & spawn

Here `P` is the body of the process being spawned and `Q` is the original process's continuation. The rule allocates a fresh channel `a`, substitutes it for `x` in both expressions, and runs the two resulting processes so they can communicate over that shared channel. It therefore combines fresh-channel allocation and process spawning in this particular calculus.

**Limit as OrgLang evidence:** this clarifies the publication's rule only. It does not establish that OrgLang uses the same rule, that channel allocation and process creation must happen at the same moment, or how OrgLang's `SpawnSpec` represents the body and continuation. Lifecycle and scheduling behavior remain **Open**.

### 6.3 Issue #85 discussion

The issue comments are the strongest current evidence for the conceptual separation, but remain provisional:

- `Call` inside a process is the trigger for requesting work identified by `qn`; it is distinguished from a separate `spawn` message.
- Creating a process incarnation is described as an internal engine operation that services `Call`.
- An agreement between pools may make service possible, but the agreement itself does not create the process.
- Resource provisioning, reservation, and the exact point of incarnation creation are unresolved.
- The discussion concerns a public channel of the pool. It does not establish that individual processes have public channels; that remains an open design question.

Relevant comments: [Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893), [pool agreements and transactions](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290639), [transactional types and process creation](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290369), [offer channel proposal](https://github.com/orglang/go-workspace/issues/85#issuecomment-6231176672), and [end-to-end service scenario](https://github.com/orglang/go-workspace/issues/85#issuecomment-6232198226).

## 7. Open questions and deferred topics

<a id="6-next-semantic-questions"></a>

The following points remain **Open** or are explicitly deferred. They should not be inferred from the working rules above.

- **Pool binding:** must every incarnation always be bound to a pool, and can that binding change later?
- **Eligibility representation:** how exactly is a pool's ability to service a named process encoded in its transaction type?
- **No eligible pool:** what happens if the search finds no suitable pool?
- **Lifecycle and scheduling:** when is the incarnation's body ready to execute, and what further guarantees follow from the publication's cut/spawn rule, if any?
- **Resource provisioning and reservation:** what role do these play, and when do they occur?
- **Public channels for individual processes:** should they exist at all?
- **Failures and abnormal termination:** how do they affect callers or held client channels?
- **Cancellation and progress:** what happens to calls that cannot be serviced or remain pending?

The current contract makes no progress guarantee for pending calls: it does not promise that every pending call will eventually be serviced, nor impose a time bound on service. This is an omission of a guarantee at the current stage, not a claim that calls are intended to remain pending indefinitely.

Pool negotiation, transaction initiation, and resource reservation are outside the current phase except where needed to clarify how an incarnation is associated with the pool responsible for servicing it. Implementation structures, call paths, and mappings between AST/API representations are also deferred until the semantic model is sufficiently stable.

Implementation study is a later phase, after the semantic model is sufficiently stable.
