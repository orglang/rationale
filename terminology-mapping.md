# Terminology mapping: OrgLang model and go-engine

> **Status: working terminology inventory.** This document compares terms used in the current OrgLang research documents with names and structures found in the inspected `orglang/go-engine` source snapshot. It is a vocabulary-alignment aid, not a normative specification and not a claim of runtime conformance.

**Implementation snapshot:** `orglang/go-engine` commit [`8ef6983f7a112616ee3f78d4f98e615686931e6a`](https://github.com/orglang/go-engine/tree/8ef6983f7a112616ee3f78d4f98e615686931e6a).

**Canonical model documents:**

- [Pools and transaction types](about-pools-and-transaction-types/README.md)

- [Processes and session types](about-processes-and-session-types/README.md)

- [Incarnations and channels](about-incarnations-and-channels/README.md)

- [What is a transaction?](about-transaction/README.md)

## 1. Purpose and method

The goal is to converge on a shared vocabulary without mechanically replacing language-level concepts with Go identifiers. In particular, the shared conceptual vocabulary should use `Coop` and `Isol`; `Hire`/`Apply` and `Fire`/`Quit` are treated as implementation-side names to be aligned with those concepts, not as competing canonical terms. The mapping distinguishes:

1. **Language concept** — a term used by the OrgLang model.
2. **Implementation representation** — a Go type, field, or operation that may represent some or all of that concept.
3. **Correspondence status** — how strongly the available evidence supports the mapping.
4. **Mismatch or open question** — where the implementation's boundaries or behavior differ, or where evidence is incomplete.

A matching name is not sufficient evidence of matching semantics. An AST constructor establishes that a representation exists; it does not by itself establish a complete execution path.

### Mapping status

- **Confirmed** — the correspondence is supported for the specific aspect stated in the notes. This does not imply full semantic or runtime conformance.

- **Provisional** — the representation is a plausible or partial match, but its complete semantics or lifecycle has not been verified.

- **Unresolved** — no reliable correspondence has been established, or the available evidence leaves a material mismatch.

These labels describe terminology correspondence only. They do not replace the claim-evidence and implementation-coverage statuses used in the process and pool model documents.

For vocabulary convergence, distinguish **preferred language term**, **current implementation identifier**, and **semantic correspondence**. Use the language term as the shared conceptual name in cross-project discussion and documentation. Preserve Go identifiers when describing concrete code. Where semantics are not yet verified, record a target alignment rather than asserting equivalence.

## 2. Participant, definition, and execution terms

| OrgLang term | Implementation term(s) | Status | Correspondence and limits |
|---|---|---|---|
| **Pool** | `pool/termdef`, `pool/compexec` | Provisional | The implementation separates pool-term definitions from pool execution. Neither package alone should be treated as the complete language-level notion of a pool participant. |
| **Pool term / pool definition** | `pool/termdef.DefSpec`, `DefRec` | Provisional | Definition-level representation. It is distinct from an executing pool and from a reference to an execution. |
| **Pool incarnation / pool execution** | `pool/compexec.ExecRec`, `ExecSnap*` | Provisional | The executor maintains an execution record and snapshots/configurations. The language-level lifecycle and identity guarantees for a pool incarnation need separate confirmation. |
| **Process** | `proc/termdef`, `proc/termdec` | Provisional | The language model distinguishes a named process, its declaration/interface, and its definition/body. The implementation has corresponding packages, but their exact contract should be read at the declaration/definition boundary rather than collapsed into one type. |
| **Process declaration** | `proc/termdec` | Provisional | Candidate representation of the process interface and its channel parameters. |
| **Process definition** | `proc/termdef` | Provisional | Candidate representation of the named process body/term. |
| **Process incarnation** | `proc/compexec.ExecRec`, `ExecSnap`; `compsem.SemRef` | Provisional (fresh record identity confirmed; lifecycle incomplete) | `compsem.New()` allocates a fresh identity plus revision, and pool `Spawn` persists a process execution record. But that path does not install channel bindings, resolve the declaration, or start the body. `proc/compexec.RetrieveSnap` is a stub; the inspected PGX adapter's channel query hard-codes `proc_id = 'proc1'`. Full incarnation lifecycle and the model's never-reuse guarantee are not established. |
| **Execution reference** | `compsem.SemRef`, stored as `CompRef` | Confirmed (reference role) | This is the reference used by pool and process execution records and operations. It is a reference to an execution, not the execution's full state and not a channel identity. |
| **Term/type name** | `uniqsym.ADT` values such as `TermQN`, `ProcTermQN`, `TypeQN` | Confirmed (name role) | These are symbolic names used to look up definitions. They are not execution references or channel identities. |

Relevant source locations:

- [pool/termdef](https://github.com/orglang/go-engine/tree/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termdef)

- [pool/compexec](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go)

- [proc/termdef](https://github.com/orglang/go-engine/tree/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termdef)

- [proc/termdec](https://github.com/orglang/go-engine/tree/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termdec)

- [proc/compexec](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go)

## 3. Channels, identities, and bindings

The implementation exposes several distinct identifiers and binding fields. They must not be collapsed into one generic notion of “channel reference”.

| OrgLang term | Implementation term(s) | Status | Correspondence and limits |
|---|---|---|---|
| **Channel** | No single implementation type established | Unresolved | The model's channel is a resource with identity, endpoints, and protocol state. The inspected code distributes these aspects across identities, bindings, communication records, and type-state references. |
| **Channel identity** | `identity.ADT`, stored as `ChnlID` | Confirmed (identity role) | Identifies a channel in the inspected communication and binding records. It is not the local placeholder and is not the communication exchange reference. |
| **Channel placeholder** | `symbol.ADT`, stored as `ChnlPH` | Confirmed | A symbolic local name used to find a binding in an execution configuration. It is not the channel resource or its identity. |
| **Channel binding** | `compvar.LinearRec`, `compvar.StructRec` | Confirmed (binding role) | A binding associates an execution, communication, channel identity, placeholder, side, and type-state key. It represents a participant's local binding to a channel. |
| **Linear / structural binding mode** | `compvar.LinearRec` / `compvar.StructRec`; `LinearMode` / `StructMode` | Confirmed (implementation distinction) | The implementation distinguishes linear and structural channel-variable records. The precise correspondence between these modes and every language-level channel category should be stated where used. |
| **Provider / client endpoint role** | `LiabSide` / `AssetSide` (`compvar.Side`) | Confirmed in process type checking | Pool execution initialization assigns `LiabSide` to the liability variable and `AssetSide` to asset variables. Process type checking routes `LiabSide` bindings through `checkProvider` and all other sides through `checkClient`; the implementation's own checker therefore explicitly treats these sides as provider and client. Keep `LiabSide`/`AssetSide` as code identifiers, but use Provider/Client in the model prose. |
| **Communication exchange** | `commexch.ExchRec`, `CommRef`, `ExchSnap` | Provisional | The exchange record tracks communication-level state and turns. It is distinct from an individual channel identity. |
| **Execution identity/reference** | `CompRef` (`compsem.SemRef`) | Confirmed (reference role) | Identifies the participating execution in binding and pending-turn records. It must not be confused with `ChnlID`. |
| **Residual protocol state** | `valkey.ADT`, stored as `ExpVK` | Provisional | The key points to a protocol/type expression state. Its role resembles a residual type, but a full correspondence requires tracing type-expression evaluation and channel-state updates. |

The shared binding fields are visible in [adt/compvar/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/adt/compvar/core.go). The pool and process packages alias or use these records in their respective execution configurations.

**Working vocabulary recommendation:** use **channel**, **channel identity**, **channel placeholder**, and **channel binding** as four distinct terms. Use **execution reference** for `CompRef` and **communication reference** for `CommRef`. Do not call all three “channel references”.

## 4. Transaction and session protocols

The model deliberately distinguishes pool-level transaction protocols from process-level session protocols.

| OrgLang term | Implementation term(s) | Status | Correspondence and limits |
|---|---|---|---|
| **Transaction type** | `pool/typeexp.ExpSpec`, `ExpRec` | Confirmed (type-expression role) | Pool type expressions represent a protocol over pool communication. Their current constructor set is not identical to the full transaction grammar in the OrgLang research model. |
| **Session type** | `proc/typeexp.ExpSpec`, `ExpRec` | Confirmed (type-expression role) | Process type expressions represent protocols on process channels. This is separate from pool transaction types. |
| **Type definition** | `pool/typedef.DefRec`, `proc/typedef.DefRec` | Confirmed (definition role) | Definition records associate type names with type-expression keys. |
| **Type-expression state / residual type** | `valkey.ADT`, `ExpVK`, and `Next()` in type records | Provisional | The executor advances to a continuation type key. This resembles residual protocol state, but the complete language-level substitution and duality rules remain separate concerns. |
| **Transaction constructors** | `pool/typeexp.OneRec`, `LinkRec`, `PlusRec`, `WithRec`, `UpRec`, `DownRec` | Confirmed (listed constructors) | The inspected pool type-expression package contains these constructors. The model's `Coop`, `Isol`, and `spawn` constructs are not represented as corresponding constructors in this package. |
| **Session constructors** | `proc/typeexp` records | Provisional | The process type-expression package has its own constructor family. Do not infer a one-to-one mapping from pool constructors or assume the two grammars are interchangeable. |

Sources:

- [pool/typeexp/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/typeexp/core/core.go)

- [proc/typeexp](https://github.com/orglang/go-engine/tree/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/typeexp)

- [pool/typedef](https://github.com/orglang/go-engine/tree/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/typedef)

- [proc/typedef](https://github.com/orglang/go-engine/tree/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/typedef)

### 4.1 Pool transaction operations

The pool expression package contains operational specifications including:

- `AcquireSpec` and `AcceptSpec`;

- `ReleaseSpec` and `DetachSpec`;

- `HireSpec` and `ApplySpec`;

- `FireSpec` and `QuitSpec`;

- `SpawnSpec` and `SpawnSpec2`.

The pool type-expression package separately contains `UpSpec` and `DownSpec`, each with a continuation expression. The inspected pool executor has paired handling for `Acquire`/`Accept`, `Hire`/`Apply`, and `Release`/`Detach`. Although `FireSpec` and `QuitSpec` are declared in `pool/termexp`, no corresponding `FireSpec` or `QuitSpec` cases were found in the inspected `pool/compexec` executor.

| Model operation / construct | Candidate implementation operation(s) | Status | Notes |
|---|---|---|---|
| `Up` / grant-access transition | Provider-side `AcceptSpec`; client-side `AcquireSpec` | Provisional | The pool type package has `UpSpec`/`UpRec`; the executor pairs `Accept` and `Acquire`. This is a strong operational candidate, but exact role/polarity and full conformance must be checked against the language contract. |
| `Down` / revoke-access transition | Provider-side `DetachSpec`; client-side `ReleaseSpec` | Provisional | The pool type package has `DownSpec`/`DownRec`; the executor pairs `Detach` and `Release`. In the inspected snapshot, these operation specs do not carry the participant-specific `ContExp` fields required by the current language-level contract. |
| `Coop` (one model operation, two participant sides) | `HireSpec` / `ApplySpec` | Vocabulary correspondence agreed; runtime semantics incomplete | `Hire` and `Apply` are the two participant-side forms of one model-level `Coop` operation, not two separate model operations. The inspected implementation has a paired negotiation path, but does not yet implement the model's allocation update: no weight parameter is present in these operation specifications, and no `Q` update is established. |
| `Isol` (one model operation, two participant sides) | `FireSpec` / `QuitSpec` | Vocabulary correspondence agreed; runtime path not implemented in inspected executor | `Fire` and `Quit` are the two participant-side forms of one model-level `Isol` operation, not two separate model operations. The AST/spec types and comments exist, but no matching executor cases were found in the inspected `pool/compexec` source. The implementation has no weight parameter or established decrement of `Q` / non-negativity guard. |
| Allocation transitions | `HireSpec` / `ApplySpec` implement the two sides of `Coop`; `FireSpec` / `QuitSpec` are the two sides of `Isol` | Vocabulary correspondence agreed; implementation incomplete | In the model, `Coop(q,w)` adds weight and `Isol(q,w)` subtracts weight subject to non-negativity. In the inspected implementation snapshot, the relevant operation specifications do not carry a weight, and the pool type representation has no allocation function or weight state. The `Hire`/`Apply` pair has an executor path; `Fire`/`Quit` has no matching cases in the inspected executor. Thus the names align conceptually, but the `Q` transitions, weight handling, and `Isol` execution remain to be implemented. |
| Model-level `spawn` in transaction grammar | `SpawnSpec`, `SpawnSpec2` in `pool/termexp`; no corresponding `pool/typeexp` constructor | Provisional (AST only) | Pool-expression spawn forms refer to process terms and/or process execution references, but no matching case was found in the inspected pool executor and no typed `spawn` constructor exists in the inspected pool type grammar. Correspondence to the model's `Q(q) > 0` rule and runtime process creation is not established. |

Sources:

- [pool/termexp/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/core/core.go)

- [pool/compexec/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go)

- [pool/typeexp/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/typeexp/core/core.go)

### 4.2 Pending interactions and matching

The implementation uses `commturn.PubRec` and `commturn.SubRec` records. Both contain a communication reference, an execution reference, and a channel identity; the records also carry a value or continuation expression. The pool executor can register a pending `SubRec` when no matching turn is available, then bind the two participants' continuation channels when the opposite operation arrives.

| Model term | Implementation term | Status | Notes |
|---|---|---|---|
| **Interaction** | Matching operation pair in the executor | Provisional | The executor implements a pending-then-matched pattern for inspected operation cases. The full language-level interaction abstraction is broader than a single record type. |
| **Pending interaction** | `commturn.SubRec` (and `PubRec` where used) | Confirmed (pending-record role) | These are pending turn records, not simply messages and not necessarily the whole interaction. |
| **Matching** | `ExchSnap.NextTurn()` plus executor operation cases | Provisional | The inspected code retrieves a next turn and branches on its concrete type. The exact atomicity, cancellation, and concurrency contract is not established by this observation. |
| **Continuation binding** | New `ChnlID` plus `LinearRec` entries | Confirmed (binding behavior in inspected cases) | The executor creates a channel identity and binds the two participant placeholders to it after a match. This is not the same as executing arbitrary language-level continuation expressions. |

Sources:

- [pool/commturn/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/commturn/core/core.go)

- [pool/commexch/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/commexch/core/core.go)

- [pool/compexec/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go)

## 5. Calls and incarnation creation

The OrgLang model distinguishes `ExternalCall` and `InternalCall`. Both create a fresh process incarnation, but their channel-transfer and pool-selection behavior differ. The implementation contains process-expression constructors such as `CallSpec`, `LinkSpec`, and `SpawnSpec`; their presence must not be treated as proof that the complete model-level call behavior is implemented.

| OrgLang term | Implementation term(s) | Status | Correspondence and limits |
|---|---|---|---|
| **ExternalCall** | `proc/termexp.CallSpec` | Provisional (AST only) | A named-process call AST candidate. The inspected field set includes a communication placeholder, a new channel placeholder, a process term name, channel placeholders, and a continuation. No matching `CallSpec` execution case was found in the inspected `proc/compexec` executor. An end-to-end test constructs a call but ends with `TODO add assertion`, so it does not establish successful runtime behavior. |
| **InternalCall** | `proc/termexp.LinkSpec` | Unresolved | A possible candidate based on its process-term name and identity fields, but the inspected process executor has no matching `LinkSpec` execution case. The field types and runtime path do not establish the intended complete channel-environment transfer. |
| **Process spawning** | `proc/termexp.SpawnSpec`; `pool/termexp.SpawnSpec`, `SpawnSpec2` | Provisional | Several spawn-related representations exist at different layers. The process model document explicitly treats the process-expression `SpawnSpec` as an unfinished implementation attempt, not an established source-language operation. |
| **Fresh process incarnation** | `proc/compexec.ExecRec`, process executor creation path | Provisional | Candidate runtime representation. The full call-to-creation lifecycle and identity guarantee require end-to-end path and test evidence. |
| **Servicing pool** | Pool execution references and pool/process executor interaction | Unresolved | No single inspected type establishes the model-level servicing-pool relationship and its lifecycle. |

Source: [proc/termexp/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go), [proc/compexec/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go), and [Incarnations and channels](about-incarnations-and-channels/README.md).

## 6. Recommended shared vocabulary

The following vocabulary is recommended for cross-document use. It intentionally prefers model-level terms over implementation-specific Go names.

| Preferred term | Use it for | Avoid using it as a synonym for |
|---|---|---|
| **Participant** | A pool or process incarnation taking part in an interaction | Definition, declaration, or execution reference |
| **Pool definition** | The named/defined pool term or behavior | Pool incarnation |
| **Pool incarnation** | One running pool participant | Pool term or `CompRef` |
| **Process definition** | The body/behavior of a named process | Process declaration or process incarnation |
| **Process declaration** | The process interface and channel parameters | Process definition |
| **Process incarnation** | One running instance of a process | Process name or execution reference |
| **Execution reference** | A reference identifying a pool or process execution (`CompRef`) | Channel identity |
| **Channel** | The channel resource in the language model | Placeholder or channel identity |
| **Channel identity** | The identifier of a channel (`ChnlID`) | Communication reference or execution reference |
| **Channel placeholder** | A symbolic name in an expression/interface (`ChnlPH`) | Channel or channel identity |
| **Channel binding** | A participant-local association between placeholder and channel, with its execution/communication/type context | Channel itself |
| **Provider endpoint / client endpoint** | The participant's role-specific endpoint of a channel | `LiabSide` / `AssetSide` without a verified mapping |
| **Transaction type** | Pool-level interaction protocol | Session type |
| **Session type** | Process-channel protocol | Transaction type |
| **Residual protocol state** | The remaining type/protocol after a transition | Type definition |
| **Interaction** | A matched participant-to-participant operation | Pending turn record alone |
| **Pending interaction** | An operation waiting for its counterpart | Completed interaction |
| **Continuation expression** | The language expression to execute after an operation | Channel binding created for a continuation |
| **Call** | Umbrella term for `ExternalCall` and `InternalCall` | Spawn, unless the language contract explicitly equates them |
| **Coop** | One model-level allocation operation with two participant-side forms: `Hire` and `Apply` | Two separate model operations; an implemented weighted `Q` update |
| **Isol** | One model-level allocation operation with two participant-side forms: `Fire` and `Quit` | Two separate model operations; an implemented weighted `Q` decrement or non-negativity guard |

### Implementation identifiers: keep as code names

When discussing implementation details, retain the exact code identifiers in backticks: `CompRef`, `CommRef`, `ChnlID`, `ChnlPH`, `ExpVK`, `LiabSide`, `AssetSide`, `LinearRec`, `StructRec`, `PubRec`, and `SubRec`. Explain their relationship to the preferred model terms instead of renaming the code in prose.

## 7. Open questions before normative convergence

1. **Pool and process lifecycle:** what exact implementation records and repository transitions create, update, terminate, and identify pool and process incarnations?
2. **Endpoint role mapping:** is `LiabSide` always the provider endpoint and `AssetSide` always the client endpoint, including initial binding and channel transfer?
3. **Channel identity lifecycle:** how do `ChnlID`, `CommRef`, and `CompRef` relate across public/private pool-channel switching, process-channel communication, forwarding, and incarnation creation?
4. **Allocation operations:** the vocabulary correspondence is agreed: `Hire`/`Apply` are the two sides of `Coop`, and `Fire`/`Quit` are the two sides of `Isol`. What changes to operation contracts, type representation, executor, and tests are required to implement the weighted `Q` updates and the non-negativity guard?
5. **Transaction grammar coverage:** where and how are the model-level `Coop`, `Isol`, and typed `spawn` constructs represented, type-checked, and executed?
6. **Call semantics:** what complete runtime path implements `ExternalCall` and `InternalCall`, including channel transfer, fresh incarnation identity, and servicing-pool selection?
7. **Pending interaction semantics:** what are the observable pending/matching boundaries, and how are concurrency, cancellation, failure, and atomicity handled?
8. **Residual protocol state:** how do `ExpVK` and `valkey.ADT` correspond to the model's residual transaction/session types, including dual endpoint checking?

## 8. Verification findings (first pass)

This pass inspected the executor switch cases and the end-to-end pool test at the pinned implementation snapshot.

### 8.1 Pool operations: declaration versus execution

The pool executor contains explicit cases for `AcceptSpec`, `AcquireSpec`, `ApplySpec`, `HireSpec`, `ReleaseSpec`, and `DetachSpec`. In each pair, one side can store a pending `SubRec`; when the counterpart arrives, the executor creates a fresh `ChnlID`, installs continuation bindings for both participants, and schedules a continuation where one is present.

The end-to-end test `test/e2e/pool_test.go` constructs a pool that performs:

- `Acquire` followed by `Hire` and `Release`;

- the matching `Accept` followed by `Apply` and `Detach`.

The test therefore provides evidence for a working paired path for access acquisition, competence negotiation, and access release in this snapshot. The vocabulary correspondence is agreed: `Hire` and `Apply` are the two participant-side forms of one model-level `Coop` operation. This does **not** establish the weighted allocation update required by `Coop`; the implementation currently has no weight parameter or demonstrated `Q` update.

By contrast, `FireSpec` and `QuitSpec` are declared in `pool/termexp`, and matching continuation record types also exist, but no corresponding executor cases were found in the inspected `pool/compexec/core/core.go`. Their presence is evidence of an AST/data representation, not an implemented runtime path.

### 8.2 Process calls: AST presence versus execution evidence

The process expression package declares `CallSpec`, `LinkSpec`, and `SpawnSpec`. However, no matching `CallSpec`, `LinkSpec`, or `SpawnSpec` execution cases were found in the inspected `proc/compexec/core/core.go` switch.

The end-to-end process-call test constructs a `CallSpec`, invokes the process executor, and then contains a TODO instead of asserting the resulting incarnation, channel bindings, or continuation behavior. This test is not evidence of successful call semantics.

Accordingly:

- `ExternalCall` ↔ `CallSpec` remains an **AST-level candidate only**;

- `InternalCall` ↔ `LinkSpec` remains **unresolved**;

- process-expression `SpawnSpec` remains an **AST-level candidate only** in this execution path.

### 8.3 Evidence boundary

A negative search for a type-switch case is bounded to the inspected executor file and commit. It does not prove that no adapter, alternate executor, or later implementation path exists elsewhere in the repository. The status above is therefore phrased as “no matching case found in the inspected executor”, not as a repository-wide claim that the feature does not exist.

Sources:

- [pool/compexec/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go)

- [pool/termexp/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/core/core.go)

- [proc/compexec/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go)

- [proc/termexp/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go)

- [test/e2e/pool_test.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/test/e2e/pool_test.go)

### 8.4 Endpoint roles and identity domains

The inspected pool execution creation path initializes its liability binding with `LiabSide` and its asset bindings with `AssetSide`. The process type checker then dispatches a `LiabSide` binding to `checkProvider` and the other side to `checkClient`; its context conversion likewise places liability bindings in the `Liabs` context and the remaining bindings in `Assets`.

This is sufficient evidence to align the implementation-side terminology as follows:

- `LiabSide` ↔ **provider side**;

- `AssetSide` ↔ **client side** (the checker treats every non-`LiabSide` value as client, while the declared side enum also has an unknown value; callers should therefore ensure only valid sides enter this path).

The three references are also constructed and used in separate roles:

- `CompRef` is created for a pool/process execution and identifies the participant execution;

- `CommRef` is created with a communication-exchange record and scopes the exchange;

- `ChnlID` is created as a channel identity and is used to query the exchange and bind participant-local channel variables.

The binding record carries all three, but that co-location does not make them interchangeable. A channel binding is the join point between participant execution, communication exchange, and channel identity. A more detailed lifecycle across public/private channel changes and process forwarding remains to be traced.

### 8.5 Allocation transitions and process-incarnation lifecycle

The canonical transaction model gives `Coop` and `Isol` precise state-changing semantics: for a named process `q` and positive weight `w`, `Coop` updates the current allocation function by adding `w`, while `Isol` subtracts `w`, subject to the non-negative-weight condition. `Spawn` is separately guarded by `Q(q) > 0` and does not itself modify `Q`.

The inspected implementation does not expose those semantics in its pool type representation:

- `pool/typeexp` contains `One`, `Link`, `Plus`, `With`, `Up`, and `Down`, but no `Coop` or `Isol`;

- its `ExpRec` variants carry a continuation and, for choices, process names, but no allocation function or weight;

- `HireSpec`/`ApplySpec` carry a process-term name and represent competence request/offer, not an explicit increment/decrement of `Q`;

- `FireSpec`/`QuitSpec` are declared, but no executor cases were found in the inspected pool executor;

- the pool type representation has no visible `Spawn` constructor either.

The vocabulary correspondence is agreed: `Hire` and `Apply` are the two participant-side forms of the single model operation `Coop`; `Fire` and `Quit` are the two participant-side forms of the single model operation `Isol`. They are not four separate model operations. This terminology alignment must not be mistaken for completed runtime semantics. In the inspected snapshot, the operation specifications have no weight parameter, the pool type representation has no allocation function or weight state, and no `Fire`/`Quit` executor cases were found. The weighted `Q` increment/decrement and the non-negativity guard therefore remain implementation work.

For process incarnations, `compsem.New()` creates a fresh `SemRef` using `identity.New()` plus a revision number. The pool executor's `Spawn` method persists a new `proc/compexec.ExecRec` with that reference and `LinearMode`. This is evidence for allocation of a fresh execution record and identifier. It is not evidence for a complete process-incarnation start:

- the inspected `Spawn` method does not bind channels, resolve a process declaration, or schedule a process body;

- `proc/compexec.RetrieveSnap` is currently a stub returning an empty snapshot;

- the inspected process PGX adapter's `selectChnls` SQL uses the literal `proc_id = 'proc1'` in its CTEs rather than the supplied execution reference, so this snapshot does not demonstrate correct per-incarnation channel retrieval through that adapter.

The model's identity rule says allocated incarnation identities are never reused. A fresh `xid`-based identifier generator is consistent with uniqueness in ordinary operation, but the inspected code alone does not prove the model-wide persistence and never-reuse guarantee across deletion, restoration, or all execution paths.

Sources:

- [about-transaction/README.md](https://github.com/orglang/rationale/blob/main/about-transaction/README.md)

- [about-incarnations-and-channels/README.md](https://github.com/orglang/rationale/blob/main/about-incarnations-and-channels/README.md)

- [pool/typeexp/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/typeexp/core/core.go)

- [pool/termexp/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/core/core.go)

- [adt/compsem/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/adt/compsem/core.go)

- [adt/identity/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/adt/identity/core.go)

- [pool/compexec/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go)

- [proc/compexec/core/core.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go)

- [proc/compexec/adapter/ds_pgx.go](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/adapter/ds_pgx.go)

## 9. Next verification pass

Before changing terminology in the canonical model documents, inspect and record evidence for the open questions above in this order:

1. Trace the pool operation path from AST/specification through adapters, type checking, executor, persistence, and tests.
2. Trace process calls and incarnation creation across process and pool APIs, including channel transfer.
3. Trace identity creation and lookup for `CompRef`, `CommRef`, and `ChnlID`.
4. Compare the resulting behavior with the language-level decisions in the canonical model documents.
5. Only then decide which mappings become **Confirmed**, which need a model distinction, and which represent implementation gaps.

No canonical terminology is changed by this inventory. In particular, do not replace model-level `Provider`/`Client`, `ExternalCall`/`InternalCall`, `Coop`/`Isol`, or `Channel` with implementation names solely on the basis of this table.
