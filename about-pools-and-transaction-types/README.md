# Pools and transaction types

> **Status: preliminary research draft.** This document investigates the pool and transaction-type model described in the existing OrgLang research material and compares it with the current `orglang/go-engine` source. It is not a normative language specification. A constructor appearing in a grammar, AST, or Go type does not by itself establish its complete operational semantics.

**Audience:** readers investigating OrgLang pools, transactions, transaction types, and their relationship to processes and session types.

**Evidence policy:** semantic/evidential status and implementation status are separate axes. A claim may be described in a document while its implementation remains partial or unverified; an implementation detail does not, by itself, establish a language-level rule.

## Contents

- [Part I — Language model](#part-i--language-model)
  - [1. Scope, sources, and status labels](#1-scope-sources-and-status-labels)
  - [2. Core concepts and boundaries](#2-core-concepts-and-boundaries)
  - [3. Terminology correspondence](#3-terminology-correspondence)
  - [4. Formal notation and worked examples](#4-formal-notation-and-worked-examples)
  - [5. Candidate semantics and guarantees](#5-candidate-semantics-and-guarantees)
- [Part II — Publications](#part-ii--publications)
  - [6. What the cited session-types paper does and does not establish](#6-what-the-cited-session-types-paper-does-and-does-not-establish)
- [Part III — Implementation evidence](#part-iii--implementation-evidence)
  - [7. Implementation map](#7-implementation-map)
  - [8. Coverage and mismatches](#8-coverage-and-mismatches)
  - [9. Open questions](#9-open-questions)

## Part I — Language model

## 1. Scope, sources, and status labels

This document examines the distinction between a **pool** and a **process**, the transaction-like values and types proposed in OrgLang research material, the six constructors `grant`, `revoke`, `choice`, `coop`, `isol`, and `spawn`, and what can be verified in the Go implementation.

Sources inspected:

- [OrgLang rationale: processes and session types](../about-processes-and-session-types/README.md), used as the methodological and structural model.
- [OrgLang rationale: transaction](../about-transaction/README.md), used as research material for the pool/transaction grammar and examples. It is not treated as a normative specification.
- [`orglang/go-engine`](https://github.com/orglang/go-engine), particularly `pool/termdef`, `pool/termexp`, `pool/typeexp`, `pool/compexec`, and `test/e2e/pool_test.go`.
- Caires and Pfenning, [*Session Types as Intuitionistic Linear Propositions*](https://doi.org/10.1145/1863543.1863553) (2010), cited by the existing transaction document. Its relevance and limits are discussed in Section 6.

The transaction document contains a proposed formal grammar and reduction notation, but the sources inspected here do not establish that all of it is a complete, implemented OrgLang specification. The grammar below is therefore labelled as **reported research notation**, not silently promoted to a normative contract.

### Two independent status axes

**Semantic/evidential status**

- **Specified** — stated directly in a source that describes the relevant model. This label records what that source says; it does not make every research note a normative language specification.
- **Observed** — directly visible in inspected source code, tests, or comments.
- **Inferred** — a working interpretation derived from evidence, but not directly stated as a rule.
- **Open** — the available evidence does not settle the claim.

**Implementation status**

- **Implemented** — an executable path and relevant tests provide evidence for the described behavior.
- **Partial** — some representation or execution path exists, but the whole behavior is not established.
- **Not implemented** — the inspected implementation has no relevant path for the specific behavior.
- **Unverified** — the available inspection does not establish whether the behavior works end to end.

Statuses apply to individual claims, not to a term as a whole. For substantial claims, this document identifies the source and the limitations of the evidence. Go database transactions, for example, are implementation-level database operations and must not be conflated with atomicity of an OrgLang transaction.

## 2. Core concepts and boundaries

### Pool and process are not synonyms

The existing OrgLang transaction document proposes two related levels:

- **Process level:** the organization of work and interactions among participants.
- **Pool level:** the availability of capabilities and the conditions under which participants can cooperate.

This is a useful conceptual distinction in the research material (**Inferred** as a language-wide semantic boundary; source: [transaction research document](../about-transaction/README.md)). The inspected Go code also separates packages under `proc/` from packages under `pool/` (**Observed**; for example, [pool execution](https://github.com/orglang/go-engine/blob/main/pool/compexec/core.go) and the [pool end-to-end tests](https://github.com/orglang/go-engine/blob/main/test/e2e/pool_test.go)). Package separation is evidence of an implementation boundary, not a full definition of language semantics.

In the implementation, a pool declaration is represented by `pool/termdef/core.DefSpec`, containing a term name, a liability-side variable (`LiabVar`), and asset-side variables (`AssetVars`). A pool execution is represented separately by `pool/compexec/core.ExecSpec` and receives a fresh `compsem.SemRef`. A process has separate declaration and execution APIs under `proc/`. These shapes suggest a distinction between a reusable description and an execution instance, but do not alone define all semantic relationships.

**What is not established:** the inspected sources do not provide a single formal definition saying whether a pool is an organization, an execution context, a resource-bearing participant, or a combination of these at every semantic layer. Nor do they establish that a pool is simply a process with extra metadata.

### Transaction and transaction ID

The transaction research document interprets identifiers such as `a, b, c` as potentially representing private transactions between pools. It describes one pool publishing a value to a transaction and another pool receiving it through a continuation. This is a **candidate model** reported by that document, not independently confirmed by a normative specification.

The implementation has several distinct identity/reference types:

- `commsem.SemRef` identifies a communication exchange in the pool execution path.
- `identity.ADT` is used for channel identities.
- `compsem.SemRef` refers to a pool or process execution, depending on the API.
- `uniqsym.ADT` is used for qualified names.
- `symbol.ADT` is used for symbols such as channel placeholders.

These must not be collapsed into one generic “transaction ID.” In `pool/compexec/core.go`, creating a pool execution allocates a new communication reference and a channel identity, then records variables that refer to communication and execution state (**Observed**). This shows runtime identifiers in the implementation, but does not establish that a particular identifier is the language-level transaction `a` from the research grammar.

**Open:** whether each language-level transaction identifier denotes one communication exchange, a private relation between exactly two pools, a protocol endpoint, or another entity. The claim “a transaction is a private transaction between pools” remains **Inferred**, not **Specified**, on the evidence inspected.

### Pools, transactions, and transaction types

The research document proposes that a pool uses transaction identifiers to communicate and that a transaction type constrains which values/actions are permitted over that relation. It gives the typing shape

[
`y₁ : B₁, …, yₙ : Bₙ ⊢ P :: (z : A)`
]

and explains it as pool term `P` using transactions `yᵢ` with types `Bᵢ` and providing transaction (z) with type (A). This is **Specified in the research document** (as a statement made by that document), but its status as a normative OrgLang typing judgement is **Open**.

Do not equate the proposed transaction type with a process session type automatically. The implementation contains both `pool/typeexp` and `proc/typeexp`, and the pool type-expression package has constructors resembling familiar session-type connectives. That is a real structural resemblance, not proof that the two type languages have identical rules or runtime meanings.

## 3. Terminology correspondence

“Mapping status” below is separate from the two status axes in Section 1.

| OrgLang research term | Publication terminology | Implementation name | Mapping and limitation |
|---|---|---|---|
| Pool | No verified exact counterpart in the cited paper | `pool/termdef`, `pool/compexec` | **Provisional.** Package/API boundary is observed; full semantic correspondence is not established. |
| Process | Process | `proc/termdef`, `proc/compexec` | Broad correspondence is visible, but the exact semantics of a process incarnation depend on the process API. |
| Transaction / identifier `a, b, c` | Not established as a term in the cited session-types paper | `commsem.SemRef`, `identity.ADT`, `symbol.ADT` | **Unresolved.** These implementation types have different roles; none can be identified with the research identifier without more evidence. |
| Pool term `P` | No exact counterpart established | `pool/termexp.ExpSpec`, `pool/compstep.StepSpec` | **Provisional.** A pool expression is submitted as a step, but the reported formal grammar is not the same as the current Go data model. |
| Transaction type (T) | Session type / linear proposition is a related theoretical concept, not a proven synonym | `pool/typeexp.ExpSpec` and `ExpRec` | **Unresolved.** Similar constructors do not establish equivalence. |
| Placeholder `x, y, z` | Variables/names in formal notation, depending on the rule | `symbol.ADT`, `termvar.VarSpec`, `compvar.VarSpec` | **Provisional.** The implementation has separate symbol and variable records; substitution/identity rules need an explicit mapping. |
| `grant` | No exact correspondence established | Closest observed pool expression names: `Acquire`, `Accept` | **Unresolved.** Granting and requesting/accepting access may be related, but must not be treated as synonyms without a rule. |
| `revoke` | No exact correspondence established | Closest observed names: `Release`, `Detach` | **Unresolved.** The roles differ in comments and execution branches. |
| `choice` | Choice connectives occur in session-type theory | `PlusSpec`, `WithSpec` in `pool/typeexp` | **Provisional** only as a structural analogy; no direct mapping to the research value constructor is established. |
| `coop` / `isol` | No exact correspondence established | `HireSpec`, `ApplySpec`, `FireSpec`, `QuitSpec` exist in pool expression code | **Unresolved.** Hiring/application and firing/quitting are competency/role operations in comments, not demonstrated implementations of productivity-share operations. |
| `spawn` value | Process spawning is discussed in the research material | `SpawnSpec` in `pool/termexp/core.go`; `compexec.Spawn` API | **Partial / unresolved.** A spec type exists, but it is not part of the serialized expression kind set; the execution API's behavior does not prove the full value/continuation rule. |
| `Call` | Invocation/substitution in process calculus | Process-level `Call` in process research material | **Distinct until proven otherwise.** A pool-level `spawn` must not be equated with process-level `Call`. |

The current implementation's pool term-expression serialization uses `Acquire`, `Accept`, `Hire`, `Apply`, `Release`, and `Detach`; the Go source comments describe them as access request/offer, competency request/offer, access release, and access detachment. The same file declares `FireSpec`, `QuitSpec`, and `SpawnSpec`, but the displayed `ExpSpecDS` and `ExpKind` do not include corresponding serialized variants for these constructors. See [`pool/termexp/core.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core.go) and [`pool/termexp/core/ds.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core/ds.go). This mismatch is an implementation observation, not a claim that the language excludes the constructors.

## 4. Formal notation and worked examples

### 4.1 Reported value grammar

The existing transaction research document gives the following value forms. The grammar is reproduced here as **reported notation**; exact lexical syntax and complete typing rules are not established by the implementation inspected.

| Value | Intended reading in the research document | Evidence status |
|---|---|---|
| `close` | Terminal token without additional payload | **Specified** in research document |
| `grant`c`` | A grant-marked value carrying identifier `c` | **Specified** in research document |
| `revoke`c`` | A revoke-marked value carrying identifier `c` | **Specified** in research document |
| `choice`c` { l }` | A choice-marked value carrying `c` and label (l) | **Specified** in research document |
| `coop(c) { w·q }` | A cooperation-marked value carrying `c` and a weighted named process `q` | **Specified** in research document |
| `isol(c) { w·q }` | An isolation-marked value carrying `c` and a weighted named process `q` | **Specified** in research document |
| `spawn(c) { q(a, b₁, b₂, …) }` | A spawn-marked value carrying `c`, a named process, and identifiers/arguments | **Specified** in research document |

The notation distinguishes **placeholders** such as `x, y, z` from **identifiers** such as `a, b, c`. The research document says placeholders acquire meaning through substitution and that identifiers are substituted in their place. This is a useful proposed distinction, but the sources inspected do not fully specify identifier allocation, freshness, scope, lifetime, aliasing, or the exact representation of a placeholder at runtime. These details remain **Open**.

### 4.2 Reported continuation grammar and application

The research document describes continuations as branches waiting for values. Its examples include forms like

`grant`x` ⇒ P`

and a labelled choice continuation with one branch `Pⱼ` per label `j`. It defines an application operation (V 	riangleright K), which matches a value against a continuation and substitutes an identifier for the corresponding placeholder. For example, the document proposes:

[
`grant(c) ▷ (grant(x) ⇒ P) ≜ P[c/x]`
;	riangleq; P[c/x]
]

and analogous rules for `revoke`, `choice`, `coop`, `isol`, and `spawn`. Other value/continuation combinations are said to be undefined.

These equations are **Specified in the research document**, not verified as executable behavior in `go-engine`. A complete account would need to state what happens on a tag mismatch, missing choice label, duplicate label, unbound placeholder, or malformed payload. “Undefined” in a research rule must not be silently interpreted as a runtime exception, deadlock, rejected program, or rollback; the document does not establish which outcome applies.

### 4.3 Reported pool-term grammar

The same document proposes three pool terms:

| Term | Reading in the research document | Evidence status |
|---|---|---|
| `c ← a` | Connect identifiers `a` and `c` | **Specified** in research document |
| `c.V` | Publish value `V` on `c` | **Specified** in research document |
| `case` `c` `K` | Receive a value on `c` and apply it to continuation `K` | **Specified** in research document |

This grammar should not be confused with the current Go API. The inspected pool runtime takes a `compstep.StepSpec` containing an execution reference and a `pool/termexp.ExpSpec`; that expression uses the names discussed in Section 3. A direct implementation of the three reported term forms, including an operational rule for (c ← a), was not established by the files inspected (**Unverified**).

### 4.4 Transaction-type constructors

The transaction document presents a type grammar using linear-logic/session-type-like connectives, including `1`, up/down shifts, internal/external choice, and forms annotated with a multiset `Q` of weighted process names. Its prose associates:

- `grant` with an up-shift and continuation;
- `revoke` with a down-shift and continuation;
- `choice` with a choice label and branch;
- `coop` with adding a weighted process `w·q` to `Q`;
- `isol` with restricting/intersecting `Q` around a weighted process;
- `spawn` with a named process and a continuation.

These associations are **Specified in the research document** only. The exact mathematical rules need caution: in the supplied table, the prose says `isol` requires `w·q ∈ Q`, but the displayed update `Q′ = Q ∩ {w·q}` yields only the singleton member when that element is present, not a general “remove this member from `Q`” operation. Whether that is intended is **Open** and should not be corrected silently.

The multiset interpretation also needs a precise definition. The research document describes `Q` as a multiset whose multiplicity (w) represents a share of productivity associated with process (q), but does not establish the domain of (w), whether shares must sum to a fixed total, how duplicate process names combine, or how equality and membership are defined. These are **Open** constraints, not assumptions to import from conventional multisets or resource logics.

### 4.5 A small illustrative example

The following is a schematic reading of the research notation, not a verified executable program:

```text
case a {
  grant`x` => P
}
```

Read it as: wait for a value on identifier `a`; if the received value has the `grant` tag and carries identifier `c`, continue as (P[c/x]). Here `a` is the channel/transaction name being observed, `x` is a placeholder in the continuation, and `c` is the identifier supplied by the received value. The example assumes the continuation matches the received value; it does not specify a mismatch policy or prove how identifiers are generated.

A choice-shaped example is similarly schematic:

```text
case a {
  choice(x_left) { left }  => P_left
  choice(x_right) { right } => P_right
}
```

The research rule says the received label selects the corresponding branch and the received identifier is substituted for that branch's placeholder. The document does not fully specify whether labels are globally unique, how the label set is declared, or whether a choice can carry any payload beyond the identifier and label.

## 5. Candidate semantics and guarantees

### What the research document claims

| Claim | Source and status | What is not established |
|---|---|---|
| Pools exchange values and continuations through transaction identifiers. | Transaction research document; **Specified** as its proposed model. | Whether these identifiers correspond exactly to runtime communication references. |
| Applying a matching value to a continuation substitutes the supplied identifier for a placeholder. | Transaction research document; **Specified** as a proposed reduction rule. | Freshness, capture avoidance, scope, and runtime behavior on mismatch. |
| `choice` selects a labelled continuation. | Transaction research document; **Specified** as a proposed rule. | Label validation and failure behavior. |
| `coop` and `isol` affect a multiset of weighted process names. | Transaction research document; **Specified** as its account. | Weight domain, conservation, multiset algebra, and the questionable `isol` update. |
| `spawn` names a process and arguments and continues with a substituted identifier. | Transaction research document; **Specified** as its account. | Whether it creates an independent process, how arguments bind, and how it relates to pool/process APIs. |

### What the implementation shows

The pool execution code maintains execution references, variable records, communication exchange records, and communication turns. In `Take`, the implementation computes a step modification and exchange modification, writes turns/exchange/variables in an explicit database transaction, then sends follow-up steps through a broker. The accept/acquire paths can wait for a complementary turn and, once paired, advance the type key and schedule continuations (**Observed** in [`pool/compexec/core.go`](https://github.com/orglang/go-engine/blob/main/pool/compexec/core.go)).

This supports a limited statement: the implementation has a protocol-like pool communication mechanism with persisted state and continuations. It does **not** establish that the full research grammar is implemented, or that the communication operation has the same semantics as `V ▷ K`.

This is evidence of a process-creation path, but not evidence that the `spawn(c) { q(...) }` value reduction is implemented end to end.

### Atomicity, rollback, isolation, and partial effects

Do not infer language-level atomicity from the Go use of `ExplicitTx`. That transaction groups selected database writes; after it commits, `Take` sends scheduled steps to a broker outside that database transaction. The observed sequence means the database write and broker delivery are not visibly enclosed in one shared transaction in this function. It does not by itself prove that failures produce a partial language-level effect, because the broker, persistence, retries, and recovery semantics would need to be examined together.

Consequently:

- **Language-level atomicity of a transaction:** **Open**.
- **Language-level rollback on failure:** **Open**.
- **Isolation between concurrent pool operations:** **Open**.
- **Possibility of externally visible partial effects after a broker error:** **Inferred as a risk from the observed ordering**, not established as a guaranteed outcome.
- **Atomicity of the explicit database write group in the implementation:** **Observed** as the intended role of the database transaction API; database adapter behavior and failure tests would be needed to characterize all cases.
- **Equivalence between `isol` and database isolation:** **Not established**. The former is a research type/value constructor about `Q`; the latter is a database/runtime property.

No conclusion about rollback or serializability should be drawn from the constructor names alone.

## Part II — Publications

## 6. What the cited session-types paper does and does not establish

The existing transaction research document cites Luis Caires and Frank Pfenning, [*Session Types as Intuitionistic Linear Propositions* (2010)](https://doi.org/10.1145/1863543.1863553). The paper is relevant background for the relationship between session types and linear propositions. The transaction document itself uses that connection as motivation for a formal account.

However, the evidence reviewed here does not establish that the paper defines OrgLang pools, the identifiers `a, b, c` as private pool transactions, or the OrgLang constructors `grant`, `revoke`, `coop`, `isol`, and `spawn` with the semantics shown in Section 4. These constructors and the `Q`-annotated transaction types must therefore be treated as OrgLang research notation unless a more direct primary source is located.

A sound comparison is limited to the broad structural relationship: the research notation resembles a session-type/linear-logic presentation in using protocol constructors and continuations. That resemblance does not establish equivalence of judgments, operational rules, or guarantees. In particular, no claim about atomic commit, rollback, or isolation follows from the cited session-types paper merely because the OrgLang material uses the word “transaction.”

**Source limitation:** the paper is cited here as a theoretical background source, not as a verified source for the detailed pool grammar. Locating an OrgLang-specific publication or formal specification that defines these constructors would materially strengthen this section.

## Part III — Implementation evidence

## 7. Implementation map

The following links point to the current `main` branch of [`orglang/go-engine`](https://github.com/orglang/go-engine). Findings are observations about that source tree, not normative language claims.

| File / symbol | Observed evidence | Relevance and limitation |
|---|---|---|
| [`pool/termdef/core/core.go`](https://github.com/orglang/go-engine/blob/main/pool/termdef/core/core.go), `DefSpec`, `Create` | A pool term definition stores a term name, a liability-side variable, and asset-side variables with type references. | Establishes a definition representation, not a complete semantic definition of pool. |
| [`pool/compexec/core.go`](https://github.com/orglang/go-engine/blob/main/pool/compexec/core.go), `ExecSpec`, `Run` | Pool execution allocates a component reference, communication reference, and channel identity; writes implementation binding, execution, variable records, and exchange records. | Evidence of a runtime representation and creation path. |
| [`pool/compexec/core.go`](https://github.com/orglang/go-engine/blob/main/pool/compexec/core.go), `Take`, `take` | Pool steps inspect `AcceptSpec`/`AcquireSpec`, consult communication turns, update type state, and schedule continuations. | Demonstrates parts of the acquire/accept protocol. It is not a proof of the research reduction rules. |
| [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core/core.go) | Declares `AcquireSpec`, `AcceptSpec`, `HireSpec`, `ApplySpec`, `ReleaseSpec`, `DetachSpec`, as well as `FireSpec`, `QuitSpec`, `SpawnSpec`, and `SpawnSpec2`. | Presence of Go types does not mean every type can be encoded, decoded, or executed. |
| [`pool/termexp/core/ds.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core/ds.go) | Serialized expression kinds include acquire, accept, hire, apply, release, detach; no corresponding serialized fields/kinds are present for fire, quit, or spawn. | Strong evidence of a representation gap in this data model. Other paths would need inspection before claiming global non-implementation. |
| [`pool/typeexp/core/core.go`](https://github.com/orglang/go-engine/blob/main/pool/typeexp/core/core.go) | Defines one, link, plus, with, up, down, and product/sum interfaces; plus/with are commented as internal/external choice. | Supports a type-expression representation with session-type-like structure, not the full `Q`-annotated grammar from the research document. |
| [`pool/typeexp/core/tc.go`](https://github.com/orglang/go-engine/blob/main/pool/typeexp/core/tc.go) | Converts type specifications to records; the `DownSpec` case returns an `UpRec`. | A concrete implementation discrepancy worth verifying. It may be a bug or an intentional representation choice; the inspected code alone cannot settle which. |
| [`test/e2e/pool_test.go`](https://github.com/orglang/go-engine/blob/main/test/e2e/pool_test.go) | `TestPool` runs `WaitClose`; `RecvSend`, `CaseLab`, `Call`, and `Fwd` are commented out in the test entry point. A spawn sequence is also commented out later in the test. | Evidence that those scenarios are not currently exercised by this test entry point, not proof that all such features are absent. The active test also depends on an external PostgreSQL setup. |
| [`proto/rast2/exec/exec_test.go`](https://github.com/orglang/go-engine/blob/main/proto/rast2/exec/exec_test.go) | Contains a prototype evaluator test for a process-level `Spawn` construct. | This is a separate prototype/process calculus layer, not proof that pool `spawn` and process `Call` or pool spawning are equivalent. |

### Implementation status summary

| Specific claim | Semantic/evidential status | Implementation status | Reason |
|---|---|---|---|
| Pool definition has liability/asset variables in the current Go model. | **Observed** | **Implemented** | Definition record and creation code are present. |
| Pool execution allocates persisted execution and communication state. | **Observed** | **Implemented** | The `Run` path writes the corresponding records. |
| Acquire/accept steps can rendezvous via communication turns. | **Observed** | **Partial** | Relevant paths exist; this is not a complete verification of all branches/failure modes. |
| Every research value constructor is supported by the current pool expression serialization. | **Observed**: the serialized kind set is narrower than the declared spec types. | **Partial** | Several spec types are not represented in `ExpSpecDS`/`ExpKind`. |
| The full `grant/revoke/choice/coop/isol/spawn` continuation semantics are implemented. | **Open** | **Unverified** | No complete end-to-end mapping from the research grammar was established. |
| `spawn` creates a process execution record through `compexec.Spawn`. | **Observed** | **Partial** | Record creation exists, but the supplied expression is not interpreted in the inspected method. |
| Pool type expressions implement the research `Q`-multiset rules. | **Open** | **Unverified** | The inspected pool type model has familiar connectives but no visible `Q`-multiset structure. |
| The pool transaction model guarantees atomicity/rollback/isolation. | **Open** | **Unverified** | Database transactions are present, but they do not establish language-level guarantees. |

## 8. Coverage and mismatches

Three vocabularies must remain distinct:

1. **OrgLang research vocabulary:** pools, transaction identifiers, values, continuations, terms, and `Q`-annotated transaction types.
2. **Publication vocabulary:** session types and linear propositions in the cited background paper.
3. **Implementation vocabulary:** pool term definitions/expressions, type expressions, component executions, communication exchanges/turns, symbols, and database transactions.

The current implementation has a meaningful pool runtime, but the mapping from the proposed transaction grammar to that runtime is incomplete. In particular, access/competency operations in `pool/termexp` cannot simply be renamed as grant/revoke/coop/isol: the comments describe different roles and the exact semantic equations are not shown. Likewise, `pool/typeexp`'s `PlusSpec`/`WithSpec` provide a structural analogy to choice, but no direct constructor-by-constructor translation has been established.

The existence of both process and pool APIs, and of a process-level spawn operation, is not enough to prove equivalence between `spawn` and `Call`. The relevant contracts, argument substitution, resource transfer, and continuation behavior must be compared directly before asserting such an equivalence.

## 9. Open questions

1. **Pool/process boundary:** What is the formal definition of a pool, and which entities can own, execute, or provide a pool term? Is a pool execution a participant in its own right, or an execution context for work?
2. **Transaction identity:** What entity does a language-level identifier denote? Is it always private to exactly two pools? How does it map to `commsem.SemRef`, channel identities, and placeholders?
3. **Placeholder substitution:** What are the binding scopes and freshness rules? Is substitution capture-avoiding? How are identifiers created and transferred? Can they alias?
4. **Value/continuation mismatch:** What is the specified result when a value tag or choice label does not match a continuation? Is the program ill-typed, blocked, rejected at runtime, or handled another way?
5. **Choice constraints:** How are labels declared and checked? Are duplicate labels or an empty label set permitted?
6. **`coop` and `isol`:** What is the domain of (w), and what exactly does a share of productivity mean? Does `Q` form a multiset, a map of weights, or another structure? Does `isol` remove an entry, intersect with a singleton, or do something else?
7. **`spawn` arguments:** Which identifiers are passed as arguments, which are new, and how are they bound in the spawned process? Does spawn create a process incarnation, a pool execution, or both?
8. **`spawn` versus `Call`:** What are the separate formal rules and observable effects? No equivalence is established by the current evidence.
9. **Transaction types versus session types:** Is there a formal translation or shared typing judgment, or are the systems only inspired by similar linear-logic constructs?
10. **Runtime coverage:** Where are `FireSpec`, `QuitSpec`, `SpawnSpec`, and `SpawnSpec2` converted to persistent records and executed? Why are these variants absent from the displayed serialized kind set?
11. **Type conversion discrepancy:** Is the `DownSpec` to `UpRec` result in `pool/typeexp/core/tc.go` intentional or a defect?
12. **Atomicity and recovery:** What guarantees apply across database writes, broker delivery, continuation scheduling, and retries? Can a failure leave persisted state without the corresponding scheduled step, and how is recovery handled?
13. **Tests:** What is the current status of the commented-out pool scenarios, especially spawn and the communication/call examples? Which integration tests can be run reliably against a supported test environment?
14. **Primary sources:** Is there an OrgLang-specific paper or formal specification that directly defines pools, the six value constructors, and the `Q`-annotated transaction types? The cited session-types paper alone does not establish those details.

These questions should remain open until resolved by a direct semantic source, executable test, or verified implementation path. The purpose of this document is to preserve the boundary between the proposed model and what the sources actually establish, rather than to fill the gaps with assumptions.
