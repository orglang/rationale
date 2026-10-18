# Spawn at the process–pool boundary

> **Status: preliminary semantic research.** This document records the current evidence, agreed working rules, and unresolved choices. It is not yet a normative specification.

## 1. Purpose and scope

Establish the semantics of process invocation and incarnation creation before studying implementation code. This phase uses the existing OrgLang rationale and [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85), including its comments. Implementation structures and call paths are out of scope.

Here, `spawn` is a candidate engine-level process-creation operation, not a claim that OrgLang has a source-language construct named `spawn`. Whether a distinct semantic operation called `Spawn` is needed remains open.

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
- A public structural channel as an offer/template, with a private linear channel per invocation, is proposed but not established.

Relevant comments: [Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893), [pool agreements and transactions](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290639), [transactional types and process creation](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290369), [offer channel proposal](https://github.com/orglang/go-workspace/issues/85#issuecomment-6231176672), and [end-to-end service scenario](https://github.com/orglang/go-workspace/issues/85#issuecomment-6232198226).

## 3. Current semantic contract

The following rules have been accepted in discussion. They define the working model, not yet a normative language specification.

### 3.1 Call lifecycle

A call has three conceptual stages:

1. **Initiated:** a process requests invocation of a named process and supplies the channel arguments required by the `Call` contract.
2. **Pending:** the engine has the request, but cannot yet service it. The caller remains suspended on the call; this does not stop the engine as a whole.
3. **Serviced:** the engine creates a fresh incarnation, establishes the required channel bindings, and reaches the point at which the callee is ready to execute.

**Agreed:** the call completes at stage 3. Merely accepting or recording the request is not completion. The caller does not wait for the callee's eventual termination.

**Agreed:** every successfully serviced call creates a fresh process incarnation. Reuse of an existing incarnation is not implicit and would require a separate rule.

### 3.2 Argument-channel custody while pending

**Agreed working rule:** when a call is initiated, the caller temporarily relinquishes the argument channels passed to it. The engine holds these channels while the call is pending, and the caller cannot use them during that interval. This is more than a reservation that still permits caller-side interaction.

The motivation is semantic stability: channel type or protocol state may change, so concurrent use by the caller could invalidate assumptions under which the eventual callee receives the channel. Upon successful service, the channels enter the new incarnation's environment.

This rule settles the caller's permission to use the channels, but not the engine's internal ownership representation or whether it may inspect or transform held channels.

## 4. Open design question: the callee's private communication channel

The callee's private communication channel is distinct from the argument channels passed to the call. The accepted custody rule for argument channels does **not** decide when this private channel is allocated.

Two designs remain possible:

### Option A — allocate at call initiation

The engine creates the private channel when it records the call, even if the callee cannot yet be created. The call remains pending. Semantics would need to say what it means for the channel to exist before its peer process does.

### Option B — allocate when the call is serviced

The engine keeps the call pending without creating the private channel. When service is possible, it creates the incarnation and channel, binds the endpoints, and completes the call.

Neither option has been selected. Both preserve the agreed completion boundary: the call completes only when a fresh incarnation exists, required channels are bound, and the callee is ready to execute.

The next useful question is whether process semantics needs to name, pass, or interact with the private channel before the callee is ready. Until evidence establishes that need, there is no reason to force a choice.

## 5. Explicitly deferred topics

The following topics are outside the current phase and should not be mixed into the decisions above:

- cancellation or permanently unserviceable calls;
- failure policy and the eventual fate of held argument channels in such cases;
- pool negotiation, transaction initiation, and resource reservation;
- implementation structures, call paths, and mappings between AST/API representations.

They can be revisited after the core successful-call semantics is clearer.

## 6. Next semantic questions

In order of dependency:

1. **Private-channel timing:** determine whether the private communication channel needs to exist or be observable before the callee is ready.
2. **Custody contract:** clarify what it means for the engine to hold argument channels, without revisiting the already agreed prohibition on caller-side use while pending.
3. **Observable result of a serviced call:** specify what the caller receives or can use after successful service, without conflating this with a pool API return value.
4. **Semantic identity of `Spawn`:** once the call contract is clearer, determine whether a distinct semantic operation called `Spawn` is needed.

Implementation study is a later phase, after the semantic model is sufficiently stable.
