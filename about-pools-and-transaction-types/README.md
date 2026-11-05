<!-- Canonical semantics: pool and transaction-type model; shared participant/channel and process/pool selection rules are in ../about-incarnations-and-channels/README.md -->

# Pools and transaction types

> **Status: preliminary semantic research.** This document owns the pool and transaction-type model, including the transaction-specific protocol, agreement state, and negotiation lifecycle. It distinguishes intended semantics from publication rules and implementation observations; its conclusions remain research findings pending a normative specification.

**Scope and document boundaries**

- This document owns the technical model of pools and transaction types, including the pool's public transaction channel and its protocol.
- [Processes and session types](../about-processes-and-session-types/README.md) owns process declarations, definitions, and process-channel protocols.
- [Calls and spawns](../about-calls-and-spawns/README.md) owns named-process invocation, process-incarnation creation, channel transfer, and the generic creation semantics at the boundary with pool-level spawning.
- The root [README](../README.md) provides an accessible introduction and motivating example.
- [Calls and spawns](../about-calls-and-spawns/README.md) owns the intended semantics of `ExternalCall` and `InternalCall`; this document retains the pool-selection and transaction-protocol rules those calls rely on.

**Shared terminology:** see the [OrgLang glossary](../GLOSSARY.md).

## Part I. Conceptual model

### 1. Scope, evidence, and status

This research draft keeps language-level intended semantics, claims made by the supplied publication, and implementation observations separate. A normative language specification remains future work.

Use the claim-status vocabulary from [Processes and session types, Section 1](../about-processes-and-session-types/README.md#1-scope-and-evidence): **Confirmed**, **Inferred**, and **Open**. Record the source and what it establishes for substantial or disputed claims. Implementation coverage is a separate dimension and should be recorded only when the relevant code path or test has been inspected.

### 2. Core model relationships

Use the [OrgLang glossary](../GLOSSARY.md) for shared term definitions. This section records the distinctions and project decisions that are specific to the pool/transaction model rather than maintaining a second glossary.

A transaction is the pool-to-pool interaction; its transaction type is the protocol governing that interaction; the agreement is the committed allocation state (the value of `Q`) associated with the logical transaction channel. A transaction identifier and a process channel identity refer to distinct resources. Their precise mapping remains **Open** pending evidence from the language contract or a verified execution path.

The public and private transaction channels are physically distinct representations of one logical transaction channel. They share its logical identity and transaction type, but have distinct physical identities. A matched `Up` creates a new private physical channel; matched `Down` commits its allocation state. The detailed matching, commit, and cancellation lifecycle is specified in [Incarnations and channels](../about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) and Section 2.1 below.

The provider/client endpoints are the two participant-relative sides of the shared transaction channel. Do not conflate the pool's public transaction channel with a process incarnation's provider channel; the latter is defined in [Calls and spawns](../about-calls-and-spawns/README.md#1-intended-semantics-of-named-process-calls).

The exact OrgLang syntax, checking rules, and runtime enforcement for transaction-type refinements remain **Open**. The current project direction is that the public channel type does not use refinements, while the private channel type may use refinement session types.

#### 2.1 Negotiation protocol and established agreement

The current model has three related concepts:

1. **Transaction type:** the protocol that governs how pools interact while establishing or modifying an agreement. It describes permitted messages, choices, constraints, and continuations.
2. **Negotiation interaction:** the pool-to-pool exchange governed by that protocol over the shared transaction channel. Its detailed operational representation remains unspecified.
3. **Agreement:** the committed allocation state (the value of the process allocation function `Q`) for the shared transaction channel `c`, accepted by the participating pools. Once established, this state can be found and reused by a later `ExternalCall`; finding it is distinct from negotiating or modifying it.

For the discovery and negotiation sequence, including the point at which incarnation creation may begin, see [Section 2.1](#21-negotiation-protocol-and-established-agreement).

##### What the formal transaction-type model establishes

The pool-specific grammar in [Section 4](#4-transaction-types) defines a **state-indexed protocol**:

- The type constructors describe interactions such as `grant`, `revoke`, `choice`, `coop`, `isol`, and `spawn`.
- The `Coop` and `Isol` constructors change the process-allocation-function value during the current private-channel access; `Q'` and `Q''` denote the values before and after an operation. They are not separate functions or stored fields. The current value becomes committed when the matching `Down` occurs.
- The spawn constructor requires positive allocation weight for the named process on that channel: `Q(q) > 0`; its continuation retains the stated `Q`.
- The type grammar also places a continuation `A` after these state constraints and transitions.

`Q` is the process allocation function associated with the logical transaction channel. Its current value is determined by that channel's latest committed private channel. The term **allocation state** denotes the value of this function for that logical channel at a particular point in the access lifecycle; it does not denote a separate function or stored object. `Q'` denotes the **uncommitted allocation state**: the current value of the same function during a private-channel access, before that value is committed. A **committed allocation state** is the value held by the latest committed private channel. Matched `Down` commits the current uncommitted allocation state. If the private-channel access is cancelled before that match, runtime discards the uncommitted allocation state. The function itself is not committed or replaced. Search uses the `Q` associated with the latest committed private channel only to check suitability conditions and select candidates; it does not modify `Q` or the committed channel. How search obtains `Q`—for example, by copying it, referring to it, or another mechanism—remains **Open**. An uncommitted private channel does not replace the current committed channel until its matching `Down`. The function's interpretation and transition rules are defined canonically in [Formal grammar and state-indexed rules](#formal-grammar-and-state-indexed-rules).

**Agreed working model:** the public channel type has no refinements; the private channel type may express refinements, with `Q` as the runtime value providing evidence for a relevant condition (for example, `Q(q) > 0`). `Q` exists in the context of private channels and changes with the corresponding channel's process-allocation-function value. `Q'` is only notation for that value during an uncommitted private-channel access, not a separate function or stored field. How `Q` is physically stored or associated with a private channel remains **Open**.

##### Agreement lifecycle: current contract and missing rules

| Stage | Current project contract | Still unspecified |
|---|---|---|
| Existing-agreement discovery | Search uses the `Q` associated with the latest committed private channel for each logical transaction channel, only to check conditions such as `Q(q) > 0` and select candidates. Search does not modify `Q` or the committed channel. | How search obtains `Q`; how committed private channels are made discoverable; visibility/ownership and selection among suitable channels belonging to different provider/client pairs. |
| Candidate selection | If discovery finds no suitable channel, manual intervention selects a candidate pool. Selection does not itself establish an agreement. | Authorization, candidate presentation, and whether candidates can be rejected before negotiation starts. |
| Private-channel access | Each matched `Up` that begins negotiation with a candidate pool creates a new private physical channel for the same logical transaction channel and initializes its allocation state from the initial function `Q⁰`, regardless of any allocation state committed by an earlier private channel for that logical channel. The domain of `Q⁰` is the competencies `C` of that candidate provider pool, and `Q⁰(q) = 0` for every `q ∈ C`. At most one uncommitted private channel may exist for a logical channel. | The physical mechanism for initializing a new private channel with `Q⁰` remains unspecified. The domain of `Q⁰` is determined by the candidate provider pool's competence set. Failure handling is addressed separately. |
| Negotiation | After matched `Up`, the candidate pool interacts with the calling pool over that pair's private channel according to the applicable transaction type. The attempt starts from the initial allocation state `Q⁰`, not from the allocation state of a previously committed private channel for that pair. Any number of `Coop` and `Isol` operations may change the channel's current allocation state; `Q'` denotes that uncommitted allocation state. The process being called is fixed throughout one `ExternalCall`. A negotiation is successful only when the provider's `detach` and the client's `release` match at `Down`; this matched `Down` is the commit point that commits the uncommitted allocation state. Protocol completion before the matched `Down` is not successful negotiation and does not make the new allocation state available to search or service. If the private-channel access is cancelled before matched `Down`, runtime terminates that private channel and discards its uncommitted allocation state. The previously committed private channel remains current and continues to supply the committed allocation state for subsequent search. Each candidate pool is tried at most once during a given `ExternalCall`; cancellation permits the search to proceed to another, not-yet-tried candidate pool while the overall search-and-negotiation timeout remains in force. Negotiation does not create a second concurrent private channel for the same logical transaction channel or a per-process agreement. | The exact protocol steps and proposal/acceptance rules, as well as candidate-pool eligibility and selection order. |
| Commit | When provider `detach` and client `release` match at `Down`, the current private channel's process-allocation-function value is committed, and that channel replaces the previous committed private channel as the current one for the logical transaction channel. `Down` itself does not modify `Q`. | Whether the superseded private channel is physically destroyed or retained. |
| Pre-commit cancellation | Cancellation terminates the active private-channel access before matched `Down`. Runtime discards the uncommitted state, including changes to `Q`, and restores both participants' active bindings to the public channel. The preceding committed private channel remains current and continues to supply the committed allocation state for search. Either participant or the external search controller may initiate cancellation; termination of the private channel is the signal by which the peer detects the end of the access. Runtime linearizes cancellation against matched `Down`: if the match commits first, commit wins and cannot be undone; if private-channel termination takes effect first, cancellation wins and no commit occurs. The search controller may then try another candidate pool that has not yet been tried in this `ExternalCall`, while the overall timeout remains in force. | The concrete runtime notification/termination mechanism and physical reclamation of the terminated private channel. |
| Service activation | Only after a suitable existing agreement is found or a new one is successfully established does the engine create the incarnation and deliver the provider channel. | Resource reservation/consumption semantics and failure handling between agreement establishment and channel delivery. |


##### Discovery, candidate selection, and timeout

For an `ExternalCall`, discovery examines discoverable logical transaction channels using, for each provider/client pair, the latest private channel committed through `Down`. It selects the first suitable logical channel encountered in the existing selection order; the rules defining that order remain **Open**. An uncommitted newer private channel does not replace the current search target.

If automatic discovery finds no suitable committed agreement, a participant of the calling pool selects candidate pools for negotiation. Candidate pools are tried in an unspecified order; selecting a candidate does not itself establish or modify an agreement. The process being called is fixed throughout one `ExternalCall`, and each candidate pool may be selected at most once during that call. Each matched `Up` creates a new private physical channel for the existing logical transaction channel and initializes its allocation state from `Q⁰`, irrespective of an earlier committed state. The previous committed private channel remains the search basis during negotiation. A negotiation succeeds only when provider `detach` and client `release` match at `Down`.

If either participant or the external search controller cancels an attempt before matched `Down`, runtime terminates the private channel, both participants detect termination, discard its uncommitted allocation state, and restore their active bindings to the public channel. The previous committed private channel remains current. The search controller may try another candidate not yet tried while the overall timeout remains in force. Candidate exhaustion terminates the search without a result immediately; it does not wait for timeout expiry.

One timeout supplied by the calling pool covers the complete discovery-and-negotiation procedure. It starts when automatic discovery begins and is not restarted for another candidate. Expiry before a suitable agreement is found or committed terminates the operation without a result. Once a suitable existing agreement has been found or a new agreement has been committed, the timeout no longer governs subsequent incarnation creation and channel delivery. Failure-reporting details remain unspecified; the proposed convention that `0` means infinity remains **Open**.

##### Questions required to complete the agreement model

- How is `Q` physically represented or associated with a private channel? The current model does not decide whether it is stored within the channel or represented separately.
- What exact formal syntax and typing judgment express the transaction type's protocol and its dependent state index `Q`?
- What operation or judgment distinguishes a negotiation that is still in progress from one whose agreement has been accepted by both parties?
- How do channel discovery and `ExternalCall` search interact with protocol-state transitions and channel linearity, and what determines which channels are visible to a searching pool?



### 3. Pool model

**Scope decision:** transaction channels exist only at the pool level. Process incarnations have process channels, which are distinct from pool transaction channels.

**Inferred working model:** a pool is represented by a pool term/state and exposes a public transaction channel through which other pools interact according to a transaction type. The provider/client endpoints and general matching principle are defined in [Incarnations and channels](../about-incarnations-and-channels/README.md#4-publication-subscription-and-matching); the channel-local process allocation function is defined in [Formal grammar and state-indexed rules](#formal-grammar-and-state-indexed-rules). The process's provider channel is a distinct resource. Pool lifecycle and behavior when a pool cannot service a request remain **Open**.

## Part II. Semantics and conformance

### 4. Transaction types

#### Formal grammar and state-indexed rules

The following grammar records the pool-specific values, continuations, and transaction-type constructors. The abstract term syntax, identifiers, placeholders, and publication/subscription mechanism are defined in [Incarnations and channels](../about-incarnations-and-channels/README.md).

| Значение *V*  | Семантика |
| :-----------  | :-------- |
| close          | Терминальный токен без какой-либо полезной информации. |
| grant(*c*) | Трансакция *c*, помеченная как grant. |
| revoke(*c*) | Трансакция *c*, помеченная как revoke. |
| choice(*c*) { *l* }   | Трансакция *c*, помеченная как choice, с классом *l*. |
| coop(*c*) { *w*·*q* } | Трансакция *c*, помеченная как coop, с весом распределения (*allocation weight*) *w* для именованного процесса *q*. |
| isol(*c*) { *w*·*q* } | Трансакция *c*, помеченная как isol, с весом распределения (*allocation weight*) *w* для именованного процесса *q*. |
| spawn(*c*)&nbsp;{&nbsp;*q*(&nbsp;*a*,&nbsp;*b*<sub>1</sub>,&nbsp;*b*<sub>2</sub>,...&nbsp;} | Трансакция *c*, помеченная как spawn, с вызовом именованного процесса *q* и аргументами *a*, *b*<sub>1</sub>, *b*<sub>2</sub>,... |
<p align="center"><sub>Таблица 1. Грамматика для значений</sub></p>

| Продолжение *K* | Семантика |
| :-------------- | :-------- |
| (close ⇒ *P*) | При получении терминального значения close продолжить как *P*. |
| (grant(*x*) ⇒ *P*) | При получении значения grant(*c*) продолжить как *P*[*c*/*x*]. Происходит связывание плейсхолдера *x* в рамках терма *P*. |
| (revoke(*x*) ⇒ *P*) | При получении значения revoke(*c*) продолжить как *P*[*c*/*x*]. Происходит связывание плейсхолдера *x* в рамках терма *P*. |
| (choice(*x*<sub>*𝚓*</sub>)&nbsp;{&nbsp;*𝚓*&nbsp;}&nbsp;⇒&nbsp;*P*<sub>*𝚓*</sub>)<sub>&nbsp;*𝚓*&nbsp;∈&nbsp;*𝙹*</sub> | При получении значения choice(*c*){*l*} для некоторого класса *l* ∈ *𝙹* продолжить как *P*<sub>*l*&nbsp;</sub>[*c*/*x*<sub>*𝚓*</sub>]. Происходит связывание плейсхолдера *x*<sub>*𝚓*</sub> в рамках терма *P*<sub>*𝚓*&nbsp;</sub> для каждого паттерна *𝚓* ∈ *𝙹*. |
| (coop(*x*) { *w*·*q* } ⇒ *P*) | При получении значения coop(*c*){*w*·*q*} продолжить как *P*[*c*/*x*]. Происходит связывание плейсхолдера *x* в рамках терма *P* и увеличение веса распределения для *q*. |
| (isol(*x*) { *w*·*q* } ⇒ *P*) | При получении значения isol(*c*){*w*·*q*} продолжить как *P*[*c*/*x*]. Происходит связывание плейсхолдера *x* в рамках терма *P* и уменьшение веса распределения для *q*. |
| (spawn(*x*) { q } ⇒ *P*) | При получении значения spawn(*c*){*q*(*a*, *b*<sub>1</sub>, *b*<sub>2</sub>,...} продолжить как *P*[*c*/*x*], если на канале *c* вес распределения процесса *q* положителен (*Q(q) > 0*). Происходит связывание плейсхолдера *x* в рамках терма *P* и порождение процесса *q*. |
<p align="center"><sub>Таблица 2. Грамматика для продолжений</sub></p>

#### Применение значений к продолжениям

Операция *V* ▷ *K* применяет полученное значение к соответствующему пуловому продолжению:

> close⠀▷⠀(close ⇒ *P*)⠀≜⠀P  
> grant(*c*)⠀▷⠀(grant(*x*) ⇒ *P*)⠀≜⠀*P*[*c*/*x*]  
> revoke(*c*)⠀▷⠀(revoke(*x*) ⇒ *P*)⠀≜⠀*P*[*c*/*x*]  
> choice(*c*) { *l* }⠀▷⠀(choice(*x*<sub>*𝚓*</sub>) { *𝚓* } ⇒ *P*<sub>*𝚓*</sub>)<sub>*𝚓* ∈ *𝙹*</sub>⠀≜⠀*P*<sub>*l*</sub>[*c*/*x*<sub>*l*</sub>]  
> coop(*c*) { *w*·*q* }⠀▷⠀(coop(*x*) { *w*·*q* } ⇒ *P*)⠀≜⠀*P*[*c*/*x*]  
> isol(*c*) { *w*·*q* }⠀▷⠀(isol(*x*) { *w*·*q* } ⇒ *P*)⠀≜⠀*P*[*c*/*x*]  
> spawn(*c*) { *q*(*a*, *b*₁, *b*₂,...) }⠀▷⠀(spawn(*x*) { *q* } ⇒ *P*)⠀≜⠀*P*[*c*/*x*], если *Q(q) > 0*

Для остальных комбинаций *V* и *K* операция *V* ▷ *K* не определена. Условие *Q(q) > 0* для `spawn` проверяется на том же логическом трансакционном канале; сама операция не изменяет *Q*.

#### Типы, ограничения, уточнения

Выражения типов соединяются при помощи *связующих*, которые могут быть унарными (например, up `￪`), бинарными (например, lolli `⊸`) или n-арными (например, external choice `&{...}`). Cлева от связующего в квадратных скобках может быть определено *ограничение*, а справа - *уточнение*.

Мы интерпретируем идентификаторы как приватные трансакции между пулами, в рамках которых осуществляется обмен сообщениями. Пул 1 может опубликовать значение и/или подписать продолжение в рамках трансакции, так что данные сообщения будут получены пулом 2 на другом конце трансакции. Значение *V* может быть опубликовано в трансакцию *a* при помощи конструкции *a*.*V*. Данное сообщение затем будет получено подпиской case *a* *K*, которая подаст полученное значение *V* в продолжение *K* для определения дальнейшего развития событий.

> *y*<sub>1</sub> : *B*<sub>1</sub>,...,*y*<sub>*n*</sub> : *B*<sub>*n*</sub> ⊢ *P* :: (*z* : *A*)

Пул *P* может *использовать* трансакции *y*<sub>1</sub>,...,*y*<sub>*n*</sub> для коммуникации с другими пулами согласно типам *B*<sub>1</sub>,...,*B*<sub>*n*</sub> соответственно и *предоставляет* трансакцию *z* типа *A*, в рамках которой с ним могут коммуницировать другие.

| Тип трансакции T | Семантика |
| :--------------- | :-------- |
| 𝟏  | Отправить токен close без продолжения. |
| ￪ *A* | Отправить токен grant. Продолжить как *A*. |
| ￬ *A* | Принять токен revoke. Продолжить как *A*. |
| [*l* ∈ *L*] ⨁{ *l* : *A*<sub>*l*</sub> } | Отправить токен choice с классом *l* ∈ *L*. Продолжить как *A*<sub>*l*</sub>. |
| [*l* ∈ *L*] &{ *l* : *A*<sub>*l*</sub> } | Принять токен choice с классом *l* ∈ *L*. Сопоставить класс с паттерном и продолжить как *A*<sub>*l*</sub>. |
| [*q* ∈ dom(*Q'*) ∧ *w* ∈ ℕ⁺] ⇱ [*Q''*] *A* | Отправить токен coop с именем процесса *q* и положительным целочисленным весом распределения *w*. Увеличить текущее значение веса: *Q''* = *Q'*[*q* ↦ *Q'*(*q*) + *w*]. Продолжить как [*Q''*] *A*. |
| [*q* ∈ dom(*Q'*) ∧ *w* ∈ ℕ⁺ ∧ *Q'*(*q*) ≥ *w*] ⇲ [*Q''*] *A* | Принять токен isol с именем процесса *q* и положительным целочисленным весом распределения *w*. Уменьшить текущее значение веса: *Q''* = *Q'*[*q* ↦ *Q'*(*q*) − *w*]. Продолжить как [*Q''*] *A*. |
| *q*(*a*, *b*₁, *b*₂,...) [*Q*(*q*) > 0] ⊸ [*Q*] *A* | Принять токен `spawn` с именем процесса *q* и каналами *a*, *b*₁, *b*₂,... Породить *q*, если его вес распределения на данном канале положителен. Продолжить как [*Q*] *A*. |
<p align="center"><sub>Таблица 4. Грамматика для типов</sub></p>

В текущей модели *Q* — **функция распределения процессов** (*process allocation function*) логического трансакционного канала: частичное отображение *Q* : 𝒫 ⇀ ℕ₀, где 𝒫 — множество имён процессов. Для данного логического трансакционного канала область определения *Q* совпадает с множеством компетенций *C* его provider pool; каждому имени процесса *q* функция сопоставляет относительный вес при распределении вызовов `ExternalCall` между фиксированной парой пулов. Значение *Q(q)* — вес процесса *q*, а не вероятность и не число уже выполненных вызовов. У каждого логического трансакционного канала своё текущее значение *Q*; оно определяется последним закоммиченным приватным каналом этого логического канала. Начальное значение определяется единым правилом: для каждого логического трансакционного канала область определения *Q⁰* равна множеству компетенций *C* его provider pool, а *Q⁰(q) = 0* для всех *q* ∈ *C*. Поэтому начальные функции разных каналов могут иметь разные области определения. Начальное значение *Q⁰* для negotiation с кандидатом определяется компетенциями соответствующего provider pool: его область определения равна *C*, а *Q⁰(q) = 0* для всех *q* ∈ *C*. Каждый совпавший `Up`, начинающий negotiation с кандидатом, создаёт новый приватный физический канал того же логического трансакционного канала и инициализирует allocation state этой попытки значением *Q⁰*, даже если у логического канала уже есть ранее закоммиченное allocation state. Одновременно у одного логического трансакционного канала может быть не более одного незакоммиченного приватного канала. Единственная точка commit этого доступа — совпавший `Down`, который коммитит текущее значение *Q*. Семантика отмены доступа до commit, включая восстановление публичных связываний, отбрасывание незакоммиченного *Q*, инициаторов отмены, обнаружение прекращения второй стороной и продолжение поиска только с ещё не испробованным пулом-кандидатом, определена в [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement) и [Section 2.1](#21-negotiation-protocol-and-established-agreement). Кратко: отмена — runtime-обработка, а не конструктор трансакционного типа; каждый пул-кандидат пробуется не более одного раза за `ExternalCall`, а исчерпание кандидатов завершает вызов без результата, не дожидаясь общего timeout. Общий timeout ограничивает весь поиск и переговоры; его истечение также завершает `ExternalCall` и не допускает следующего кандидата. Внутри приватного канала *Q* может изменяться произвольное число раз, в том числе ни разу, только операциями `Coop` и `Isol`: первая увеличивает вес, вторая уменьшает его. Обозначение *Q'* используется для значения *Q* в ходе текущего незакоммиченного приватного канала, а *Q''* — для значения после конкретной операции; это обозначения разных моментов изменения одной функции, а не утверждение о существовании отдельных функций или хранимых полей. Совпавший `Down` коммитит текущее значение *Q* и делает текущий приватный канал новым актуальным закоммиченным приватным каналом, замещая предыдущий. Сам `Down` не изменяет *Q* и не требует буквальной операции присваивания между *Q* и *Q'*. Физическое уничтожение или сохранение замещённого приватного канала остаётся открытой деталью. Область определения *Q* — компетенции *C* provider pool; нулевой вес означает, что компетенция объявлена, но не участвует в распределении. Вес *w* в `Coop` и `Isol` — строго положительное целое число (*w* ∈ ℕ⁺). Это описание жизненного цикла — проектное уточнение OrgLang, а не правило, автоматически приписываемое публикации.

Отношение положительных весов задаёт **пропорцию распределения** (*allocation ratio*) между процессами. Например, *Q(q₁) = 1*, *Q(q₂) = 3* и *Q(q₃) = 1* задают пропорцию 1:3:1 между количествами выполненных `ExternalCall` для этих процессов на канале *c* за достаточно длительный промежуток времени. Это долгосрочная пропорция, а не требование точного совпадения на каждом коротком интервале. В текущей модели функция *Q* полностью задаёт соглашение по каналу *c*: она определяет относительное распределение, но не абсолютную мощность или скорость обслуживания (rate). Если позднее понадобится выразить такие параметры, модель соглашений можно будет расширить.

#### Примеры

```
t0 = &{  
    new : q(a, b1, b2,...) [Q(q) > 0] ⊸ [Q] t0,  
    end : [∀q ∈ C. Q(q) = 0] ￬ 𝟏,  
    more : t1,  
    less : t2  
}  

t1 = ￪ ([q ∈ dom(Q') ∧ w ∈ ℕ⁺] ⇱ [Q'[q ↦ Q'(q) + w]] t0)

t2 = ￪ ([q ∈ dom(Q') ∧ w ∈ ℕ⁺ ∧ Q'(q) ≥ w] ⇲ [Q'[q ↦ Q'(q) − w]] t0)
```

Где *C* — компетенции из декларации provider pool, *dom(Q⁰) = C*, а исходно *Q⁰(q) = 0* для всех *q* ∈ *C*. Здесь *Q⁰* — начальная функция для конкретного provider pool; правило инициализации общее, но области определения функций разных каналов могут различаться.

В примерах *Coop* увеличивает текущее значение *Q(q)*, а *Isol* уменьшает его при условии, что результат неотрицателен; нулевой вес не удаляет *q* из области определения функции. Обе операции сохраняют множество компетенций и не затрагивают другие логические трансакционные каналы. Обозначение *Q'* показывает значение функции до операции, а *Q''* — после неё. Для `spawn` требуется только *Q(q) > 0* в действующей функции; само значение веса не передаётся как аргумент вызова. Полный жизненный цикл функции и точка коммита заданы выше.

| Question | Current status | Why it matters | Evidence needed |
|---|---|---|---|
| How should the adopted transaction-type constructor set be formalized in the surface grammar and typing rules? | **Open** | Determines how the already adopted constructors are expressed and checked. | A formal grammar and typing rules consistent with the constructor set recorded in the companion model; do not reopen the constructor inventory. |
| What are the remaining exact transition rules for `One`, `Up`, and `Down`, including type-state progression, ownership, and observable boundaries? | **Partly decided; partly Open** | Matching is the transition point; the remaining state progression and observability details govern conformance. | Preserve the adopted decisions in Section 6.2; specify remaining obligations, then test permitted and prohibited transitions. |
| How are pool-state constraints formalized in the type system? | **Agreed working model:** constraints expressed by transaction types are checked statically, using the current `Q` and accounting for preceding `Coop` and `Isol` transitions. | The exact typing judgment and formal rules remain to be specified. |


#### Per-channel allocation state

The transaction-type grammar is state-indexed: `Coop` and `Isol` transition the process allocation function associated with the shared transaction channel, while `spawn` requires a positive allocation weight for the requested process. The canonical definition of the function, its initialization, allocation weights, and transition side conditions are in [Formal grammar and state-indexed rules](#formal-grammar-and-state-indexed-rules).

The function `Q` is associated with each logical transaction channel, not with the client pool globally. Each logical transaction channel has its own allocation state: the committed value is determined by its latest committed private channel, and an active private-channel access may carry an uncommitted value. `Up` gives the new private channel the committed allocation state of that same logical channel; matched `Down` commits the value prepared there and makes that private channel current. A pool may participate in logical transaction channels with different counterpart pools. No cross-channel summation rule is currently imposed.

For a fixed provider/client pair, the working model permits only one established agreement, regardless of which process name is called. Consequently, that pair does not require a choice among several agreements or channels. Discovery may still select among suitable agreements offered by different provider/client pairs; the discovery and negotiation procedure is specified in [Section 2.1](#21-negotiation-protocol-and-established-agreement).

### 5. The pool's public transaction channel

**Inferred:** the pool's public transaction channel is part of the current explanatory pool model. Whether individual processes should have public channels remains **Open**.

The public transaction channel and private channels are physically distinct representations of one logical transaction channel. They have distinct physical identities, share one logical identity, and use the same transaction type. The provider and client pools each have their respective endpoint in these representations. Each matched `Up` creates a new private physical channel and makes it the active representation. Matched `Down` commits that private channel's current process-allocation-function value and restores the public channel as the active representation. If the active private-channel access is cancelled before matched `Down`, runtime terminates that access, discards its uncommitted state, and restores both participants' active bindings to the public channel. The latest committed private channel is the current committed channel for the logical transaction channel and supplies the `Q` used by search. Restoring the active binding to the public channel does not make the public channel the search target. The public channel type itself has no refinements. The exact matching points, participant continuations, and channel-identity rules are specified canonically in [Incarnations and channels](../about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) and [Section 6.2](#62-matched-transitions-continuations-and-channel-identity); this section does not restate those rules.

The lifecycle of `Q`, including initialization, updates during private-channel access, and commit at matched `Down`, is defined in [Section 2.1](#21-negotiation-protocol-and-established-agreement). The logical/physical identity switch and participant-continuation rules are defined in [Section 6.2](#62-matched-transitions-continuations-and-channel-identity).

This pool-level protocol is distinct from a process's provider channel and from channels mapped to a new incarnation's client-role parameters in `ExternalCall`. Process creation, pool selection, and the start of servicing are described in [Processes and session types](../about-processes-and-session-types/README.md).

### 6. Intended semantics and formal rules

This section records the agreed minimal language-level decisions for matching and continuation behavior, while leaving a complete operational semantics unfinished. The decisions below specify when the protocol transition counts as occurring; they do not establish implementation correctness, complete typing rules, failure semantics, or every state transition.

#### 6.1 Minimal transaction-type constructors

**Status: Project semantic decisions, with formalization still open.** The matching points, shared channel-identity rules, and participant-specific continuation obligations recorded below are adopted language-level requirements. Their complete typing judgments, operational rules, and implementation conformance are not yet established; this research document is not itself the normative language specification.

A transaction type describes the protocol exposed by a pool through its public transaction channel. A client's interactions must conform to this provider-side protocol, evaluated against the current protocol state. No separately declared client-side transaction type is required by this model.

| Constructor | Provider-side operation | Client-side operation | Minimal intended meaning | Further detail |
|---|---|---|---|---|
| `One` | `close` | `wait` | Terminal provider interaction and corresponding client wait. The client's enclosing expression may continue after `wait`; provider-side `close` has no executable continuation of its own. | Matching and shared-identity rule: Section 6.2. `One` does not itself imply process termination. |
| `Up A` | `accept` | `acquire` | Provider accepts access; client acquires access. | Matching, private identity, and participant continuation rules: Section 6.2. Formal typing remains open; `dual(A)` is provisional explanatory notation only. |
| `Down A` | `detach` | `release` | Provider detaches access; client releases access. | Matching, restoration of the original public identity, and mandatory participant-specific `ContExp` on both operations: Section 6.2. Formal typing and resource disposition remain open. |

The operation names above are implementation identifiers, not proposed surface syntax. The pool-side operation declarations are in [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core/core.go); the process-side declarations are in [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go). These declarations support the provider/client operation mapping, but by themselves do not establish the runtime transition order or full language semantics.

#### 6.2 Matched transitions, continuations, and channel identity

The general paired-interaction principle is defined in [Incarnations and channels](../about-incarnations-and-channels/README.md#4-publication-subscription-and-matching). This section specifies its pool-specific consequences:

- **`One`:** provider `close` matches client `wait`. Only the matched pair completes the transaction interaction and establishes one channel identity shared by both sides. Client-side `wait` may continue in its enclosing expression; provider-side `close` is terminal and has no executable continuation of its own.
- **`Up A`:** provider `accept` matches client `acquire`. Access becomes active and both participants' logical channel bindings resolve to a newly created private physical channel. This channel has its own identity, distinct from the public channel and from any earlier private channel, while representing the same logical transaction channel and carrying the same transaction type. Allocation-state initialization and negotiation are defined in [Section 2.1](#21-negotiation-protocol-and-established-agreement).
- **`Down A`:** provider `detach` matches client `release`. The current private channel's process-allocation-function value is committed, and both participants' logical channel bindings resolve back to the public physical channel. The current private channel replaces the previous committed private channel for that logical transaction channel and becomes the source of its current `Q` for subsequent search. `Down` itself does not modify `Q`. It does not imply physical destruction of the superseded private channel; its physical lifetime remains open. The logical identity and transaction type are unchanged. The process-allocation-function state commit is defined in [Section 2.1](#21-negotiation-protocol-and-established-agreement).
Each side of `Up A` and `Down A` carries its own participant-specific continuation; the expressions need not be textually identical and become eligible only after the corresponding pair matches. After `Up`, each uses the shared private identity; after `Down`, each uses the restored public identity. Pre-commit cancellation is a runtime lifecycle event, not a transaction-type operation and does not enable a transaction-type continuation. Provider continuations are checked against `A`, and client continuations against the corresponding client-side protocol type (provisionally `dual(A)`); the endpoint typing qualification is defined below.

The logical placeholder persists across the public/private transition: matched `Up` binds it to a newly created private physical channel, and matched `Down` restores the public physical binding after committing the private channel's allocation state. If the active access is cancelled before matched `Down`, runtime terminates the private-channel access and restores the public physical binding without committing its allocation state. The logical identity and shared transaction type remain unchanged; every private channel has its own physical identity. `One` has a separate shared-identity rule. Matching imposes no additional ordering between participant continuations. Search uses the `Q` associated with the latest committed private channel and does not modify it; how search obtains `Q` remains **Open**. A later `Down` replaces that channel as the current committed private channel. Whether terminated or superseded private-channel resources are physically reclaimed, and when, remains **Open**. The initialization and update rules for `Q` and `Q'` are defined in [Section 2.1](#21-negotiation-protocol-and-established-agreement).

##### Continuation correspondence: dual endpoint views

**Decision recorded from semantic review:** `A` describes the provider-side continuation protocol; the client-side continuation must be checked against the corresponding client-side protocol type. For brevity, this document uses `dual(A)` as a provisional notation for that client-side type. This notation is introduced here for explanatory purposes only: it is not an established OrgLang grammar constructor or operation, and no definition or derivation rule for it is assumed. The participant-specific continuation expressions need not be textually identical, but each must satisfy the typing obligation for its own endpoint. Matching the operation pair and binding the appropriate shared channel identity do not, by themselves, make arbitrary `ContExp` values valid.

This decision establishes the intended endpoint relationship, not the complete typing judgment. The formal representation of the client-side type, the typing rules, and how the continuation channel identity is substituted into each participant's continuation remain to be specified and tested.

##### Initial conformance examples

These examples translate the decisions in Section 6.2 into acceptance criteria for future tests; they are not claims that tests already exist or pass:

1. **`One`:** a client waiting for the provider's `close` may proceed to its own continuation only after the close/wait pair matches; matching establishes one channel identity shared by both sides. The close interaction does not itself terminate the enclosing client process.
2. **`Up`:** a client cannot treat access as acquired unless the provider-side protocol permits and matches the acquisition; both participants continue according to the continuation associated with `Up`.
3. **`Down`:** after a valid detach/release match, the current private channel's process-allocation-function value is committed, both sides regain the public channel identity, and the current private channel replaces the preceding committed private channel for that logical transaction channel. A subsequent matched `Up` must create a different private physical channel identity. Tests should verify that suitability checks use the `Q` associated with the preceding committed private channel until `Down`, then use the `Q` associated with the newly committed channel, without requiring `Down` itself to modify `Q` or destroy the superseded physical channel.
4. **Pre-commit cancellation:** when either participant or the external search controller cancels an active private-channel attempt before matched `Down`, verify that runtime termination of the private channel is detected by the peer, both active bindings return to the public channel, the uncommitted state (including changes to `Q`) is discarded, and the preceding committed private channel remains current. Verify that the search controller may try another candidate while the shared timeout remains in force.
5. **Protocol conformance:** an operation that contradicts the current provider-side protocol state is rejected or otherwise prevented according to a separately specified checking/enforcement rule; that enforcement mechanism is currently open.

For each rule adopted in this section, record:

1. **Preconditions:** the participant roles, channel/type state, and any agreement or resource prerequisites.
2. **Action:** which participant sends, receives, selects, or applies a continuation.
3. **Result:** the next protocol state, the identity and ownership of any channel/resource, and any change to pool state.
4. **Observable state at a transition boundary:** where relevant, state the pre-state/post-state and ordering constraints needed to preserve protocol and resource invariants. Detailed error reporting, recovery, retries, and abnormal-termination semantics are outside this specification pass.
5. **Evidence:** the source for the intended language rule, plus separate implementation-path/test evidence where conformance is claimed.

Until these points are settled, keep only the corresponding unresolved detail explicitly **Open** and link to the relevant question in Section 9. Do not downgrade the adopted matching, identity, or continuation requirements recorded in Section 6.2.

### 7. Publication correspondence

The pool-specific grammar in [Section 4](#4-transaction-types) assigns `grant`-send behavior to `↑ A` and `revoke`-receive behavior to `↓ A`, with continuation as `A`. This is part of the project's model, not a table reproduced from the publication. The publication supplies the general channel framework and continuation/application ideas: the abstract continuation grammar and the definition of `V ▷ K` are described in [Incarnations and channels](../about-incarnations-and-channels/README.md#6-substitution-and-continuation-application).

The project uses those ideas as the basis for its transaction-type interpretation. The correspondence between the publication's channel actions and OrgLang's transaction operations is therefore a model-level analogy, not a rule stated directly by the publication. The OrgLang language-level operation model additionally requires each side of `Down`—provider-side `detach` and client-side `release`—to carry its own participant-specific `ContExp`. These expressions need not be identical: the provider continuation is checked against `A`, and the client continuation against the corresponding client-side protocol type. This is a language-level requirement, not a claim that the current runtime operation structs already expose those fields. The publication table's send/accept wording also should not be equated mechanically with the current runtime operation names (`accept`/`acquire`, `detach`/`release`) without an explicit role and polarity mapping.

#### Initial constructor/role correspondence table

The table below separates the publication model's token polarity from OrgLang's current provider/client operation names. It is a working correspondence, not a claim that the runtime implementation already conforms.

| Type constructor | Publication-level action | Provider-side OrgLang operation | Client-side OrgLang operation | Established minimum | Still open |
|---|---|---|---|---|---|
| `One` (`𝟏`) | The provider-side type sends `close`; the client-side dual action receives/waits for it. | `close` | `wait` | The pair must match before the interaction counts as complete; matching establishes one shared channel identity. The client's enclosing expression may continue after `wait`; provider-side `close` is terminal for this interaction and has no executable continuation of its own. | The precise correspondence between the publication's terminal `close` case and OrgLang's enclosing-expression behavior, plus the formal typing of the shared identity for this terminal case. |
| `Up A` (`↑ A`) | The provider-side type sends `grant`, then continues as `A`; the client performs the complementary receive/acquire action. | `accept` | `acquire` | Access starts only when the pair matches; both participants use the shared new private channel identity. The provider continuation is checked against `A`, and the client continuation against its corresponding client-side protocol type (provisionally `dual(A)`). | The exact correspondence between the publication's actions and OrgLang's runtime operations, plus formal typing judgments and runtime conformance. |
| `Down A` (`↓ A`) | The provider-side type accepts/receives `revoke`, then continues as `A`; the client performs the complementary send/release action. | `detach` | `release` | Access ends only when the pair matches; both operations must carry their own participant-specific `ContExp`. After matching, each continuation may proceed with the restored original public channel identity. The provider continuation is checked against `A`, and the client continuation against its corresponding client-side protocol type (provisionally `dual(A)`). | The exact correspondence between the publication's actions and OrgLang's runtime operations, formal typing judgments, and runtime conformance. |

**Polarity rule for this comparison:** the transaction type is the protocol exposed by the provider. Accordingly, this project's analogy reads the action from the provider endpoint: `↑ A` sends `grant`, while `↓ A` receives `revoke`; the client endpoint performs the complementary action. This is the project's interpretation of the type table and provider role, not a direct statement about OrgLang in the publication or proof of the exact runtime implementation. The runtime names `accept`, `acquire`, `detach`, and `release` must still be checked against their code paths and tests, not matched by English verb similarity alone.

The initial comparison should cover:
- the grammar and reduction/application operation for values, continuations, and pool terms;
- the transaction-type constructors and their side conditions;
- the relationship between a type's constraints and the pool-state set used by the model;
- the spawn-form rule and its relationship, if any, to OrgLang's `SpawnSpec`.

**Open:** whether these publication constructs correspond one-to-one to OrgLang constructs. Similar names or matching notation are not sufficient evidence.

## Part III. Implementation evidence and open questions

### 8. Implementation mapping and evidence

Implementation conformance has not been established by this document. This section records **implementation mappings**: observed correspondences between pool/transaction model concepts and `go-engine` structures or execution paths. They are specific to the inspected source snapshot and do not make implementation details normative or establish complete semantic conformance.

| Path / symbol | Observed behavior | What this establishes | What remains unverified |
|---|---|---|---|
| [`pool/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go), `take` cases for `AcceptSpec` and `AcquireSpec` | If `commSnap.NextTurn()` is empty, the executor records a `SubRec` containing the operation and continuation, logs `taking half done`, and returns without binding either continuation. When the matching opposite operation is already registered, it creates one new channel ID, binds both participants' continuation channels to it, advances the exchange offset, and schedules non-nil continuations. | The inspected implementation permits a first-arriving operation to remain pending and performs continuation binding when the opposite operation is matched. | Whether the pending registration is externally observable, the intended atomicity/linearization point, cancellation/interleaving behavior, and whether this path is complete for all runtime cases. |
| [`pool/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go), `take` cases for `DetachSpec` and `ReleaseSpec` | The same pending-subscription pattern is used. On matching, the implementation creates a channel ID and binds both continuation channels; these cases do not schedule participant-specific `ContExp` expressions. The bound runtime continuation channels should not be confused with the language-level `ContExp` expressions required on both operations. The inspected code path alone does not establish how this ID relates to the original public channel identity at the language level. | The current implementation models `detach`/`release` as a paired interaction with a continuation channel after matching. | Resource disposition after the interaction and any broader lifecycle contract. |
| [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/core/core.go) and [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go), operation-spec declarations | In both packages, `DetachSpec` and `ReleaseSpec` contain only `CommChnlPH`; neither declares a `ContExp` field. By contrast, `AcceptSpec` and `AcquireSpec` declare `ContExp`. In the process package, `CloseSpec` has no `ContExp`, while `WaitSpec` does. | The inspected runtime operation-spec structures do **not** satisfy the language-level `Down` requirement recorded here: both `detach` and `release` must carry participant-specific `ContExp` values. `Up` already has continuation fields on both operations. | The runtime AST/specs, typing, adapters, executor, and tests must be brought into alignment with the `Down` contract. This is a documented conformance gap, not a reason to weaken the language-level requirement. |
| [`proc/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go), `takeWith` cases for `CloseSpec` and `WaitSpec` | If no opposite operation is registered, the executor records a pending subscription and returns. On matching `close`/`wait`, it creates a new channel ID and binds both sides to the `One` continuation type; the wait-side continuation is scheduled when non-nil. | The inspected process executor uses the same pending-then-match pattern for `One`. | Whether the language contract requires this exact scheduling/observability behavior, and abnormal termination/error behavior. |
| [`pool/termexp/adapter/tc.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/adapter/tc.go) | The adapter maps the core operation specifications to SDK operation variants with corresponding names. | The operation names are carried through the adapter. | An adapter mapping alone does not establish protocol correctness or type conformance. |
| [`test/e2e/pool_test.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/test/e2e/pool_test.go), `TestPool` / `waitClose` | The test builds an `Up`/`With`/`Down` pool type and exercises some pool acquisition/acceptance steps. The `close`/`wait` process interaction and final outcome assertion are commented out; the test contains a TODO for an assertion. | This file provides an example of intended test setup and partial execution coverage. | It does not currently establish an asserted end-to-end `One` outcome or full conformance for `Up`/`Down`. The test was inspected, not run in this task. |

These paths suggest that the implementation has a **pending registration** stage followed by a **matching/continuation-binding** stage. In the inspected `detach`/`release` path, the executor creates a channel ID and binds runtime continuation channels, but does not schedule participant-specific `ContExp` expressions (and the operation specs do not expose those fields). Runtime continuation-channel binding is distinct from the language-level continuation expressions required on both operations. This source-level observation does not tell us how that ID maps to the logical channel placeholder or to the original public identity described by the language-level model. The internal mechanism for preserving and restoring that identity is an implementation detail and is not specified here. Do not call the whole interaction atomic without defining the relevant observable boundary: the database mutation and broker scheduling path, and concurrent interleavings, would need to be traced to settle that question.

The [`TestPool` / `waitClose` example](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/test/e2e/pool_test.go) defines the type-level continuation as `Down { ContExp: Link{TypeQN: poolTypeQN} }`, but its runtime `ReleaseSpec` and `DetachSpec` literals supply only `CommChnlPH`. This is consistent with the operation-spec declarations above and exposes the same implementation gap: the example does not encode the two required participant-specific `ContExp` values. The test's final `close`/`wait` sequence and outcome assertion are commented out, so it is partial evidence only; it does not validate the complete lifecycle.

### 9. Open questions and next tests

| Open question | Behavior/decision affected | Evidence or test needed |
|---|---|---|
| How should the adopted transaction-type constructor set be formalized in the surface grammar and typing rules? | Exact syntax, typing judgments, and compatibility with parser and type-checker behavior. | Formalize the adopted constructor set; compare parser and type-checker support separately without reopening the constructor inventory. |
| What formal rules remain for `One`, `Up`, and `Down`? | Matching points, shared-identity rules, and the requirement for participant-specific `ContExp` on both `Down` operations are decided. Formal typing, type-state progression, ownership, and observable boundaries remain open. | Define the typing and state-transition judgments; add positive and negative tests without reopening the adopted decisions. |
| How is continuation typing formalized? | **Decision:** the provider-side continuation is checked against `A`, and the client-side continuation against the corresponding client-side protocol type, provisionally denoted `dual(A)`. This notation is not an established grammar construct. The formal judgments and channel-identity substitution remain open. | Define the typing judgments and client-side protocol type representation; test valid and invalid continuation pairs, including channel-identity substitution. |
| How do the publication's continuation notation and actions map to OrgLang's participant-specific continuations and runtime operations? | The OrgLang endpoint obligations are adopted; the correspondence between the publication's notation/actions and OrgLang's runtime operations remains open. | Verify provider/client polarity and action correspondence against language rules and runtime paths; do not infer runtime semantics from publication wording alone. |
| What is the physical lifetime of a private channel after `Down` commits it? | `Down` does not imply destruction; the latest committed private channel remains the search target until a later `Down` commits a newer one. Whether older private channels are retained, and for how long, remains **Open**. | Specify resource retention and reclamation separately from the agreed commit and search-target behavior. |
| How are the logical identity, public/private physical identities, and shared transaction type represented? | The logical identity is shared; the public and private physical channel identities are distinct; both physical representations use the same transaction type. The concrete identity mapping and physical representation of `Q`/`Q'` remain open. | Specify the identity/substitution representation and verify that `Up`/`Down` switch only the active physical binding while preserving logical identity and transaction type. |
| How do peer failure and runtime channel termination affect pending or matching `Up`/`Down` interactions? | Pre-commit cancellation by either participant or the external search controller, peer detection through private-channel termination, restoration of public bindings, and the winner of the cancellation-versus-`Down` race are decided. Crash/failure detection and the concrete runtime notification and reclamation mechanisms remain open. | Specify and test peer-absence/failure behavior and runtime termination/linearization; verify that a matched `Down` or cancellation wins as one indivisible outcome. |

| How are agreement parameters and timeout values represented? | Who supplies timeout, how it is checked, and whether it is static or dynamic. | Project decision; do not assume the proposed `0 = infinite` convention. |
| How are transaction identifiers allocated and related to process channel identities? | Identity uniqueness, resource ownership, and safe continuation substitution. | Identity contract and source/test evidence for allocation and substitution. |
| Which implementation paths establish conformance? | Confidence that intended protocol rules are executable. | Source-level trace and tests with observable assertions for each agreed rule. |

#### Minimum conformance test matrix

The following is an acceptance target for the adopted semantics, not a description of tests already present. Each pending case should be tested with both endpoint arrival orders, and each matched case should assert the observable post-state rather than only the absence of an API error.

- **Pending boundary:** after only `accept` or `acquire` (and separately only `detach` or `release`), assert that no protocol transition has occurred, no continuation has become eligible, and no participant can observe a partially changed channel state.
- **`Up` match:** after both `accept` and `acquire` match, assert one shared fresh private channel identity, the expected residual protocol state, and exactly one eligibility event for each non-null participant continuation. Use different provider/client continuation expressions to ensure they are not accidentally conflated.
- **`Down` match:** after both `detach` and `release` match, assert restoration of the original public channel identity (not a newly allocated public identity), the expected residual protocol state, and exactly one eligibility event for each participant-specific continuation. Include distinct continuation expressions and positive/negative typing cases for each endpoint.
- **`One` match:** assert that a lone `close` or `wait` remains pending; after the pair matches, assert completion with one shared channel identity, no provider-side executable continuation, and eligibility of the client's enclosing continuation when present.
- **Representation path:** round-trip every operation and continuation through AST, adapter, persistence, and executor representations. In particular, `Down` cannot pass the language-level continuation tests until both operation specs and their conversion paths can carry the required `ContExp` values.
- **Linearity and isolation:** reject duplicate/aliased channel identities and invalid endpoint continuation types; verify that a pending or matched operation does not mutate unrelated channels or another participant's bindings.

The current inspected `go-engine` paths provide useful pending/matching implementation observations, but the existing end-to-end scenarios include missing result assertions, and the `Down` operation representation does not yet expose the adopted language-level continuation expressions. These are implementation gaps to address, not reasons to weaken the acceptance criteria.
