# Interim semantic decisions: calls and forwarding

> **Status: proposed decision record.** This file records decisions reached during an initial semantic review. It is not a substitute for the normative language specification. Once accepted, these decisions should be incorporated into the appropriate normative section.

## Scope and evidence

These are language-level decisions, not claims that the current `orglang/go-engine` implementation already satisfies them. Keep intended semantics and implementation coverage separate, as described in the [research draft](README.md#1-scope-and-evidence).

## ExternalCall

- The calling process suspends at the call.
- Creating the provider process alone does not complete the call. The call completes for the caller when it obtains a fresh provider channel.
- The caller's continuation becomes eligible to execute only after that channel has been obtained.
- The call contract must specify the required arguments and channel mappings, as well as the type of the provider channel returned to the caller.

## InternalCall

- `InternalCall` transfers an existing provider channel to a new incarnation of the process.
- The old incarnation terminates as part of the operation; its continuation is not executed.
- The handoff is logically atomic: the placeholder is unbound in the old incarnation `P` and bound in the new incarnation `Q`. The semantics must not expose an intermediate state in which both incarnations can use the transferred binding or neither can.
- The call contract must specify the required arguments and channel mappings.

## Fwd

- `Fwd` connects interactions across two existing channels by redirecting pending actions and their continuations. It is not equivalent to `InternalCall`: it does not create a new process incarnation or transfer provider responsibility.
- If a suitable action is already pending when forwarding is established, the action and its continuation are redirected. If no suitable action is pending, forwarding is deferred until a compatible action appears.
- Type checking must guarantee compatibility of the actions and polarities being connected, and preserve the type correctness of both continuations after redirection.
- This is a type-safety guarantee, not a liveness guarantee: typing `Fwd` does not guarantee that the interaction will eventually complete.

## Specification and implementation status

The normative specification should define the contracts of `ExternalCall` and `InternalCall`, including their argument/channel requirements and result channel types. It should define `Fwd`'s interaction and typing contract at the language level.

Implementation coverage remains a separate question and must be supported by execution-path inspection or tests. The decisions above do not claim that any of these behaviors are fully implemented in `orglang/go-engine`.

## Explicitly out of scope for this interim record

- Runtime error behavior for invalid or inconsistent execution states.
- Detailed operational rules beyond the decisions stated above.
- A guarantee that forwarding or a call will terminate.
