# Spawn at the process–pool boundary

> **Status: preliminary semantic research.** This document develops the intended contract at the boundary between process invocation and a future pool model. It distinguishes source evidence, provisional interpretation, decisions accepted during discussion, and unresolved choices. It is not yet a normative specification.

## Purpose and scope

The immediate goal is to establish semantics before studying implementation code. The investigation therefore uses the existing OrgLang rationale and the discussion in [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85), including its comments. Implementation structures and call paths are explicitly out of scope for this phase.

For this document, `spawn` means a candidate engine-level process-creation operation, not a source-language construct. The current hypothesis is that `Call` is the process-level request and that the engine creates a fresh process incarnation when it can service that request. Whether OrgLang needs a distinct semantic operation called `Spawn` remains open.

## Sources and evidential method

Primary sources:

- [Processes and session types](https://github.com/orglang/rationale/blob/main/about-processes-and-session-types/README.md), especially Section 7 on `Call` and `Link`, and Section 8 on the publication's cut/spawn rule.
- [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85), including comments transferred from #84 that discuss `Call`, process creation, pool agreements, and resource provisioning.
- [Grilling method](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md), used to structure clarification of semantic uncertainties. This document is a research note, not a Q&A transcript.

Claims are labelled **Observed**, **Working interpretation**, **Agreed**, or **Open**. Issue comments are provisional discussion, not normative rules. A rule from the publication's calculus is not automatically an OrgLang rule.

## Evidence from the existing rationale

### The intended contract of `Call`

**Observed — rationale, Section 7.** `Call` is described as invocation of a named process. The intended contract resolves the named process, maps declared channel parameters to existing channels, starts a fresh process incarnation with separate execution state and a channel environment, injects a distinct provider channel for communication with the caller, and allows the caller's continuation to proceed once the incarnation has started. Explicitly mapped channels are transferred to the new incarnation; distinct formal parameters must map to distinct channels under linearity.

The same section says that the authoritative language source and implementation mapping remain unverified. It also avoids assuming that `Call` is implemented using `Spawn`.

**Implication.** `Call` already expresses process invocation at the language level. A separate engine-level creation operation may be needed to fulfil a call, but this does not establish that `Call` and `Spawn` are equivalent or that the latter is a separate source-language operation.

### The publication's cut/spawn rule

**Observed — rationale, Section 8.** The publication's rule `x ← P ; Q` allocates a fresh channel, starts a process running `P` with that channel substituted for `x`, and continues the original process as `Q` with the same channel substituted.

**Limitation.** This rule combines channel allocation, process creation, and continuation in a particular calculus. It does not establish that OrgLang has the same rule or that the creation and channel-allocation events must be atomic in OrgLang.

## Evidence from issue #85

The issue discussion provides the strongest current evidence for the intended conceptual separation, while explicitly remaining provisional:

- `Call` inside a process is described as the trigger for requesting work identified by `qn`; it is distinguished from a separate `spawn` message.
- Creating a process incarnation is described as an internal engine operation that services `Call`.
- An agreement between pools may make service possible under specified conditions, but the agreement itself does not create the process.
- Resource provisioning, reservation, and the point at which the incarnation is created remain unresolved.
- If no existing agreement enables service, the caller might wait for an agreement to change, or the engine might initiate a transaction to change it. The discussion does not select either behavior as final semantics.
- A public structural channel might act as an offer/template, with a private linear channel for each invocation. This is a proposal, not an established rule.

Relevant comments: [Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893), [pool agreements and transactions](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290639), [transactional types and process creation](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290369), [offer channel proposal](https://github.com/orglang/go-workspace/issues/85#issuecomment-6231176672), and [end-to-end service scenario](https://github.com/orglang/go-workspace/issues/85#issuecomment-6232198226).

## Working semantic model

The current working model separates three concepts:

1. **Call initiation.** A process requests invocation of a named process and supplies the channel arguments required by the `Call` contract.
2. **Call pending / service not yet possible.** The engine has accepted a request that cannot yet be fulfilled. The request must remain pending if the chosen semantics permit delayed service; it must not be confused with a successfully completed call.
3. **Call serviced.** The engine creates a fresh incarnation, establishes the required channel bindings, and reaches the point at which the rationale says the caller's continuation may proceed.

The pool layer may affect when a pending call can be serviced, but pool agreements and transactions are separate mechanisms. Their detailed semantics are out of scope here.

This model is provisional except where the following choices have been explicitly accepted in discussion.

## Decisions accepted so far

### Completion and caller continuation

**Agreed.** A call is complete when a new process incarnation has been created, the required channels have been bound, and the callee is ready to execute. Merely accepting or recording a request is not enough to count as a completed call.

**Agreed.** The caller does not wait for the callee's eventual termination as part of call completion. The call's completion boundary is startup and channel binding, not the whole lifetime of the callee.

### Delayed service

**Agreed.** If the engine cannot yet service a call, the caller remains suspended with the call pending. This suspension must not imply that the entire engine stops. The policy for eventual wake-up, cancellation, or terminal failure remains to be specified.

### Fresh incarnation

**Agreed.** Every successfully serviced call creates a fresh process incarnation. Reusing an existing incarnation would change identity and shared-state semantics and therefore requires a separate, explicit rule; it is not implicit in `Call`.

**Important consequence.** Fresh incarnation per successful call does not, by itself, decide when its communication channel is allocated, nor does it settle whether a caller can attempt channel interaction while the call is pending.

## Central unresolved question: call waiting versus channel waiting

A potentially long delay before service makes the distinction between the **call** and the **channel used to communicate with the callee** central. These are separate possible waiting points, and the semantics must say which one a process is waiting on.

At least two designs remain possible:

### Option A — channel allocated when the call is initiated

The engine allocates a fresh private channel when it records the call, even if the callee incarnation cannot yet be created. The call itself remains pending until service conditions are met. The channel exists as a pending rendezvous point, but the specification must still define whether interaction on it blocks, buffers, or is otherwise constrained before the callee starts.

**Benefit:** channel identity can be established early and retained across a long service delay.

**Cost:** this introduces semantics for a channel whose peer process does not yet exist, and requires careful rules for cancellation, failure, and channel ownership during the pending interval.

### Option B — channel allocated only when the call is serviced

The engine keeps the call pending without creating the callee's private communication channel. Once service is possible, it creates the incarnation and channel, binds the endpoints, and completes the call as one logical transition.

**Benefit:** a successfully returned call always has an established callee incarnation and channel binding; there is no live call channel without a callee.

**Cost:** any interaction through the callee's channel necessarily occurs after the call has completed, so a caller waiting for service is blocked on the call itself rather than on a not-yet-serviced channel.

These are design alternatives, not claims about current OrgLang behavior. A hybrid is possible, but it would need to explain why channel identity exists before service and what guarantees that identity provides.

### Question that must be resolved

When service may be delayed for a long time, should the caller:

- remain blocked on the **call** until a fresh incarnation and its communication channel are established; or
- receive/hold a channel earlier and potentially block on **interaction with that channel** while the callee does not yet exist?

The key semantic distinction is not simply whether the process blocks, but **what operation is pending**, what resource exists during that interval, and which event releases the caller. The specification should avoid an accidental design in which a call appears complete even though the caller's continuation is unable to use the channel it was promised.

## Design constraints

1. Establish process and engine semantics before inspecting implementation code.
2. Treat `Call` as the current process-level request baseline; treat internal incarnation creation as a candidate engine operation.
3. Keep call completion distinct from callee termination.
4. Create a fresh incarnation for every successfully serviced call; do not infer reuse.
5. Distinguish pending call service from channel interaction. Decide explicitly when the private channel is allocated and when the caller may proceed.
6. Do not treat a pool agreement as a process-creation event.
7. Defer pool negotiation, transaction initiation, resource reservation, cancellation, and failure policy except where a minimal rule is necessary to state the call contract.
8. Do not use implementation details to settle semantic questions in this phase.

## Remaining semantic agenda

In order of dependency:

1. **Channel allocation and call completion:** choose between early channel allocation and allocation as part of successful service; define exactly when the caller's continuation resumes.
2. **Pending-call lifecycle:** define what keeps a pending call alive, and whether it can be cancelled or fail permanently.
3. **Unavailable service:** decide whether the engine only waits for conditions to change or may initiate a transaction; this may belong to pool semantics, but the call contract must state what the caller observes.
4. **Communication before callee startup:** if a channel can exist before the callee, define whether interaction blocks, buffers, or is disallowed.
5. **Observable result:** specify what a serviced call gives the caller (for example, access to a private linear endpoint) without conflating that with a pool API's return value.
6. **Semantic identity of `Spawn`:** after the above contract is clearer, determine whether a distinct semantic operation named `Spawn` is needed at all.

Conclusions should be promoted to normative rules only when they are explicitly agreed or supported by authoritative rationale. Implementation study is a later phase, after this semantic model is sufficiently stable.
