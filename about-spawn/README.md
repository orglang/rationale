<!-- Canonical semantics: ../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-operations -->
# Spawn at the process–pool boundary

> **Status: preliminary semantic research.** This document records the current evidence, agreed working rules, and unresolved choices. It is not yet a normative specification.

> **Canonical intended semantics:** the language-level contracts for `Call` and `Link` are linked from [Section 3 below](#3-canonical-semantics). This document retains the supporting rationale, detailed working rules, evidence links, and unresolved pool-boundary questions.

## 1. Purpose and scope

Establish the semantics of process invocation and incarnation creation before studying implementation code. This phase uses the existing OrgLang rationale and [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85), including its comments. Implementation structures and call paths are out of scope.

Here, `spawn` is descriptive shorthand for creating a process incarnation at the engine level, not a source-language construct. **Agreed working rule:** no distinct semantic operation called `Spawn` is introduced at this stage. Creation of a fresh incarnation is an internal step by which the engine services `Call`. This can be revisited only if a separate semantic role is established.

Claims below are marked **Evidence**, **Agreed**, or **Open**. Issue comments are provisional discussion, not normative rules. A rule from the publication's calculus is not automatically an OrgLang rule.

## 2. Evidence

### 2.1 Existing rationale: `Call`

**Evidence — canonical contract (see Section 3).** The canonical document records the current intended `Call` contract. Its authoritative language source and implementation mapping remain unverified; this evidence does not establish that `Call` is implemented using `Spawn`, nor does it settle the pool-selection mechanism described in Section 6.

### 2.2 Existing rationale: publication cut/spawn rule

**Publication rule.** The supplied calculus gives the cut/spawn rule:

    proc(x ← P ; Q) 7→ proc([a/x]P), proc([a/x]Q) (a fresh)
    cut: allocate channel & spawn

Here `P` is the body of the process being spawned and `Q` is the original process's continuation. The rule allocates a fresh channel `a`, substitutes it for `x` in both expressions, and runs the two resulting processes so they can communicate over that shared channel. It therefore combines fresh-channel allocation and process spawning in this particular calculus.

**Limit as OrgLang evidence.** This clarifies the publication's rule only. It does not establish that OrgLang uses the same rule, that channel allocation and process creation must happen at the same moment, or how OrgLang's `SpawnSpec` represents the body and continuation. Lifecycle and scheduling behavior remain open.

### 2.3 Issue #85 discussion

The issue comments are the strongest current evidence for the conceptual separation, but remain provisional:

- `Call` inside a process is the trigger for requesting work identified by `qn`; it is distinguished from a separate `spawn` message.
- Creating a process incarnation is described as an internal engine operation that services `Call`.
- An agreement between pools may make service possible, but the agreement itself does not create the process.
- Resource provisioning, reservation, and the exact point of incarnation creation are unresolved.
- The issue discussion concerns a public channel of the pool. It does not establish that individual processes have public channels; that remains an open design question.

Relevant comments: [Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893), [pool agreements and transactions](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290639), [transactional types and process creation](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290369), [offer channel proposal](https://github.com/orglang/go-workspace/issues/85#issuecomment-6231176672), and [end-to-end service scenario](https://github.com/orglang/go-workspace/issues/85#issuecomment-6232198226).

## 3. Canonical semantics

The intended language-level semantics of `Call` and `Link` are maintained in one place: [Processes and session types, Section 7 — Intended semantics of named-process operations](../about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-operations).

This document does not restate those contracts. Use Section 2 above for the supporting evidence and its limitations; use Sections 4–6 below for pool-boundary context, deferred topics, and open research questions. In particular, the detailed channel-transfer rules, `Call` lifecycle, `Link` handoff, and their shared pool-selection rule should be edited in the canonical document only when they are part of the language-level contract.

## 4. Pool public channel and callee's private communication channel

**Agreed separation:** servicing a `Call` and interacting through the pool's public channel are unrelated mechanisms. A `Call` does not, by itself, require a transaction through the pool's public channel or entry into its critical section; conversely, the pool's `Up … Down` protocol does not imply a `Call` or process-incarnation creation.

### 4.1 Public channel of the pool

**Agreed clarification:** the public channel discussed in issue #85 is the pool's public channel, not a public channel belonging to each process. Whether individual processes should have public channels remains open.

The pool's public channel has a transaction type of the form `Up` followed by some continuation that ultimately ends in `Down`. **Agreed working interpretation:** access through the pool's public channel gives the client a private channel for the duration of the critical section. Exclusivity is scoped to this private channel and the interaction conducted through it; it does not, by itself, imply a global lock that prevents all other clients from interacting with the pool. Reaching `Down` marks the end of this protocol-bounded critical section, and the client can no longer continue the interaction along that channel continuation after that point. This must be understood in light of channel identity: each interaction generates a new channel identifier for continuing the interaction, and this succession of identifiers is reflected in the channel's type. Thus, in one sense, the channel is continually changing; unavailability after `Down` does not by itself specify whether some underlying channel resource is closed, returned to the pool, or otherwise handled. Further guarantees should be derived from the exact `Up` / continuation / `Down` semantics, not assumed from the analogy alone.

**TODO:** Decide whether the detailed `Up … Down` protocol explanation belongs in `about-transaction/README.md`, then move the protocol mechanics there and keep only the process/pool boundary distinction here.

This pool-level protocol is conceptually distinct from the process's provider channel and from the client channels passed to `Call`. The provider channel is the sole channel associated with the new process incarnation for communication with its client; the current model introduces no separate callee-private communication channel.

## 5. Explicitly deferred topics

The following topics are outside the current phase and should not be mixed into the decisions above:

- failures and abnormal termination, including their effect on callers or held client channels;
- cancellation or permanently unserviceable calls;
- pool negotiation, transaction initiation, and resource reservation, except where needed to clarify how a process incarnation is associated with the pool responsible for servicing it;
- implementation structures, call paths, and mappings between AST/API representations.

Failure behavior is not being considered at this stage. It can be revisited after the successful-call semantics is clearer.

The current contract makes no progress guarantee for pending calls: it does not promise that every pending call will eventually be serviced, nor impose a time bound on service. This is an omission of a guarantee at the current stage, not a claim that calls are intended to remain pending indefinitely.

## 6. Next semantic questions

The next question is how a new process incarnation is associated with the pool responsible for servicing it. **Agreed working rule:** this association requires a separate mechanism; the servicing pool is not determined automatically from the caller's context. **Tentative direction:** the mechanism selects the pool to which the new process incarnation itself is bound, rather than merely selecting a pool as a property of the `Call` request. **Agreed working constraint:** an incarnation cannot be bound to multiple pools simultaneously; the mechanism selects at most one pool for an incarnation. This does not yet establish whether every incarnation must always have a pool binding or whether that binding can later change.

**Meaning of servicing:** the pool services the process's provider channel by interacting with the client according to that channel's session type. **Agreed working rules for `Call`:** each newly created process incarnation has exactly one provider channel, and `Call` creates that channel together with the incarnation. The pool association identifies who provides and services that channel. This does not, by itself, mean that the pool controls the process incarnation's execution or entire lifecycle. **Clarification for `Link`:** the provider channel may already exist before the target incarnation is created, because `Link` hands off an existing channel. Therefore, channel creation and incarnation creation are not universally simultaneous; the simultaneous-creation rule applies to `Call`, not to `Link`.

**Pool eligibility and search:** each pool has its own transaction type, which carries information about whether that pool can service a process with a given name. For the current semantic model, this type-level eligibility is sufficient; no separate acceptance step is required. For simplicity, pool selection searches for the first eligible pool, starting with the pool containing the caller and continuing through pools with which agreements are established. Thus, agreements determine which further pools are considered, while each candidate pool's own transaction type determines whether it is eligible. The exact encoding of this information remains open. Performance shares/weights and the resulting load distribution are a separate concern and are outside the current scope.

**Creation and start of servicing after pool selection (`Call`):** the engine searches for the first eligible pool using the pool-search rule above. Only after a suitable pool has been found does the engine create the new process incarnation together with a fresh provider channel; the selected pool does not create the incarnation itself. The canonical distinction between `Call` and `Link` is specified in Section 7 of the linked document in Section 3. The selected pool is associated with the incarnation and begins servicing its provider channel immediately, without a separate readiness-wait stage. The engine's message delivering the provider channel to the caller and the selected pool's start of servicing are unordered: neither event is required to precede the other. The precise point at which the new incarnation's body becomes ready to execute relative to these events is left unspecified, since the current semantic model does not depend on that ordering. If no eligible pool is found, the current model does not specify what happens next; failure and cancellation semantics remain deferred. For `Call`, pool selection, any agreements that guide the search, incarnation creation, delivery of the fresh provider channel, and the start of servicing are conceptually distinct stages, with no ordering imposed between channel delivery and servicing start. This is distinct from interacting with the pool through its public transaction channel, which has been agreed to be unrelated to `Call` itself.

The observable result of a serviced call is constrained by the canonical channel-placeholder rule in Section 7 of the linked document in Section 3. A separate `Spawn` operation should be reconsidered only if later semantic evidence establishes a role not covered by `Call` and its servicing transition.

Implementation study is a later phase, after the semantic model is sufficiently stable.
