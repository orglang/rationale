# Spawn at the process–pool boundary

> **Status: preliminary semantic research.** This document records the current evidence, agreed working rules, and unresolved choices. It is not yet a normative specification.

## 1. Purpose and scope

Establish the semantics of process invocation and incarnation creation before studying implementation code. This phase uses the existing OrgLang rationale and [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85), including its comments. Implementation structures and call paths are out of scope.

Here, `spawn` is descriptive shorthand for creating a process incarnation at the engine level, not a source-language construct. **Agreed working rule:** no distinct semantic operation called `Spawn` is introduced at this stage. Creation of a fresh incarnation is an internal step by which the engine services `Call`. This can be revisited only if a separate semantic role is established.

Claims below are marked **Evidence**, **Agreed**, or **Open**. Issue comments are provisional discussion, not normative rules. A rule from the publication's calculus is not automatically an OrgLang rule.

## 2. Evidence

### 2.1 Existing rationale: `Call`

**Evidence — [Processes and session types, Section 7](https://github.com/orglang/rationale/blob/main/about-processes-and-session-types/README.md).** `Call` is described as invocation of a named process. Its intended contract resolves the named process, maps declared channel parameters to existing channels, starts a fresh process incarnation with separate execution state and a channel environment, injects a distinct provider channel for communication with the caller, and allows the caller's continuation to proceed once the incarnation has started. Explicitly mapped channels are transferred to the new incarnation; distinct formal parameters must map to distinct channels under linearity.

The rationale notes that the authoritative language source and implementation mapping remain unverified. It does not establish that `Call` is implemented using `Spawn`.

### 2.2 Existing rationale: publication cut/spawn rule

**Evidence — [Section 8](https://github.com/orglang/rationale/blob/main/about-processes-and-session-types/README.md).** The publication's rule `x ← P ; Q` allocates a fresh channel, starts a process running `P` with that channel substituted for `x`, and continues the original process as `Q` with the same channel substituted.

**Limit.** This is a rule from a particular calculus. It does not establish that OrgLang uses the same rule or requires channel allocation and process creation to happen at the same moment.

### 2.3 Issue #85 discussion

The issue comments are the strongest current evidence for the conceptual separation, but remain provisional:

- `Call` inside a process is the trigger for requesting work identified by `qn`; it is distinguished from a separate `spawn` message.
- Creating a process incarnation is described as an internal engine operation that services `Call`.
- An agreement between pools may make service possible, but the agreement itself does not create the process.
- Resource provisioning, reservation, and the exact point of incarnation creation are unresolved.
- The issue discussion concerns a public channel of the pool. It does not establish that individual processes have public channels; that remains an open design question.

Relevant comments: [Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893), [pool agreements and transactions](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290639), [transactional types and process creation](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290369), [offer channel proposal](https://github.com/orglang/go-workspace/issues/85#issuecomment-6231176672), and [end-to-end service scenario](https://github.com/orglang/go-workspace/issues/85#issuecomment-6232198226).

## 3. Current semantic contract

The following rules have been accepted in discussion. They define the working model, not yet a normative language specification.

### 3.1 Call lifecycle

A call has three conceptual stages:

1. **Initiated:** a process requests invocation of a named process and supplies the channel arguments required by the `Call` contract.
2. **Pending:** the engine has the request, but cannot yet service it. The caller remains suspended on the call; this does not stop the engine as a whole.
3. **Serviced:** the engine creates a fresh incarnation, establishes the required channel bindings, and reaches the point at which the callee is ready to execute.

**Agreed:** the call completes at stage 3. Merely accepting or recording the request is not completion. The caller does not wait for the callee's eventual termination. “Ready to execute” means the callee's body can be executed; it does not require that the body has already begun or completed its first instruction. The caller's continuation becomes eligible to execute when the caller receives a message containing the new incarnation's provider channel. Thus, the caller behaves as if subscribed to the delivery of that channel; creation of the incarnation alone does not resume the caller. The callee's body and caller's continuation may execute in either order or interleave, including when they depend on communication over transferred channels; channel protocol and linearity constraints still apply. A process may wait for a required action by the other. This rule does not prescribe a scheduling priority or strict execution order.

**Agreed:** every successfully serviced call creates a fresh process incarnation. Reuse of an existing incarnation is not implicit and would require a separate rule. **Linearity consequence:** one existing incarnation cannot be reused to service multiple calls by reusing the same channel bindings. Each call that is successfully serviced has its own fresh incarnation, and its argument channels are transferred into that incarnation's environment rather than shared across incarnations.

### 3.2 Argument-channel custody while pending

**Agreed working rule:** when a call is initiated, the caller temporarily relinquishes the argument channels passed to it. The engine holds these channels while the call is pending, and the caller cannot use them during that interval. This is more than a reservation that still permits caller-side interaction.

The motivation is semantic stability: channel type or protocol state may change, so concurrent use by the caller could invalidate assumptions under which the eventual callee receives the channel. Upon successful service, the channels enter the new incarnation's environment.

**Agreed clarification — escrow/depository model:** while the call is pending, the engine is a custodian of the argument channels, not a participant in their protocols. It preserves the channels for later transfer; it does not interact over them, inspect their protocol state, or change that state. The caller cannot use them during custody. Once the call is serviced, the channels are bound into the fresh incarnation's environment and the pending-call custody ends. The analogy is limited to safekeeping and separation of control; it does not import additional legal or transactional obligations from real-world escrow.

### 3.3 Result of a serviced call

**Agreed working rule:** the relevant endpoint is designated in the call itself by a channel placeholder. Once the new incarnation and its provider channel have been created, the engine sends the caller a message containing that provider channel. The caller resumes its continuation (`ContExp`) upon receiving the message. The engine is responsible for this delivery because it creates the incarnation and provider channel; the selected pool services the channel but does not create it or deliver it to the caller. This is not a conventional return value from `Call`; it is delivery of the channel associated with the placeholder.

The placeholder is a name in the call's semantic environment, not the channel or endpoint resource itself. The exact message mechanism and binding details are outside this phase.

## 4. Pool public channel and callee's private communication channel

**Agreed separation:** servicing a `Call` and interacting through the pool's public channel are unrelated mechanisms. A `Call` does not, by itself, require a transaction through the pool's public channel or entry into its critical section; conversely, the pool's `Up … Down` protocol does not imply a `Call` or process-incarnation creation.

### 4.1 Public channel of the pool

**Agreed clarification:** the public channel discussed in issue #85 is the pool's public channel, not a public channel belonging to each process. Whether individual processes should have public channels remains open.

The pool's public channel has a transaction type of the form `Up` followed by some continuation that ultimately ends in `Down`. **Agreed working interpretation:** access through the pool's public channel gives the client a private channel for the duration of the critical section. Exclusivity is scoped to this private channel and the interaction conducted through it; it does not, by itself, imply a global lock that prevents all other clients from interacting with the pool. Reaching `Down` marks the end of this protocol-bounded critical section, and the client can no longer continue the interaction along that channel continuation after that point. This must be understood in light of channel identity: each interaction generates a new channel identifier for continuing the interaction, and this succession of identifiers is reflected in the channel's type. Thus, in one sense, the channel is continually changing; unavailability after `Down` does not by itself specify whether some underlying channel resource is closed, returned to the pool, or otherwise handled. Further guarantees should be derived from the exact `Up` / continuation / `Down` semantics, not assumed from the analogy alone.

This pool-level protocol is conceptually distinct from the process's provider channel and from the argument channels passed to `Call`. The provider channel is the sole channel associated with the new process incarnation for communication with its client; the current model introduces no separate callee-private communication channel.

## 5. Explicitly deferred topics

The following topics are outside the current phase and should not be mixed into the decisions above:

- failures and abnormal termination, including their effect on callers or held argument channels;
- cancellation or permanently unserviceable calls;
- pool negotiation, transaction initiation, and resource reservation, except where needed to clarify how a process incarnation is associated with the pool responsible for servicing it;
- implementation structures, call paths, and mappings between AST/API representations.

Failure behavior is not being considered at this stage. It can be revisited after the successful-call semantics is clearer.

The current contract makes no progress guarantee for pending calls: it does not promise that every pending call will eventually be serviced, nor impose a time bound on service. This is an omission of a guarantee at the current stage, not a claim that calls are intended to remain pending indefinitely.

## 6. Next semantic questions

The next question is how a new process incarnation is associated with the pool responsible for servicing it. **Agreed working rule:** this association requires a separate mechanism; the servicing pool is not determined automatically from the caller's context. **Tentative direction:** the mechanism selects the pool to which the new process incarnation itself is bound, rather than merely selecting a pool as a property of the `Call` request. **Agreed working constraint:** an incarnation cannot be bound to multiple pools simultaneously; the mechanism selects at most one pool for an incarnation. This does not yet establish whether every incarnation must always have a pool binding or whether that binding can later change.

**Meaning of servicing:** the pool services the process's provider channel by interacting with the client according to that channel's session type. **Agreed working rules:** each process incarnation has exactly one provider channel, and that channel is created at the same time as the incarnation. The pool association identifies who provides and services that channel. This does not, by itself, mean that the pool controls the process incarnation's execution or entire lifecycle.

**Pool eligibility and search:** each pool has its own transaction type, which carries information about whether that pool can service a process with a given name. For the current semantic model, this type-level eligibility is sufficient; no separate acceptance step is required. For simplicity, pool selection searches for the first eligible pool, starting with the pool containing the caller and continuing through pools with which agreements are established. Thus, agreements determine which further pools are considered, while each candidate pool's own transaction type determines whether it is eligible. The exact encoding of this information remains open. Performance shares/weights and the resulting load distribution are a separate concern and are outside the current scope.

**Creation and start of servicing after pool selection:** the engine searches for the first eligible pool using the pool-search rule above. Only after a suitable pool has been found does the engine create the new process incarnation together with its provider channel; the selected pool does not create the incarnation itself. The selected pool is associated with the incarnation and begins servicing its provider channel immediately, without a separate readiness-wait stage. The engine's message delivering the provider channel to the caller and the selected pool's start of servicing are unordered: neither event is required to precede the other. The precise point at which the new incarnation's body becomes ready to execute relative to these events is left unspecified, since the current semantic model does not depend on that ordering. If no eligible pool is found, the current model does not specify what happens next; failure and cancellation semantics remain deferred. Pool selection, any agreements that guide the search, incarnation creation, delivery of the provider channel, and the start of servicing are conceptually distinct stages, with no ordering imposed between channel delivery and servicing start. This is distinct from interacting with the pool through its public transaction channel, which has been agreed to be unrelated to `Call` itself.

The observable result of a serviced call is constrained by the channel-placeholder rule in §3.3 and by the provider-channel delivery rule above. A separate `Spawn` operation should be reconsidered only if later semantic evidence establishes a role not covered by `Call` and its servicing transition.

Implementation study is a later phase, after the semantic model is sufficiently stable.
