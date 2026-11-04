## 2. Уточнение или семантическое изменение

**Stable scenario ID:** `AWF-002`

**Задание**

В одном из предложений сказано, что совпавший `Down` завершает согласование. Перепиши его так, чтобы явно указать: это также точка фиксации ещё не зафиксированного состояния распределения. В уже принятом материале установлено, что отмена доступа к приватному каналу до совпавшего `Down` отбрасывает такое незафиксированное состояние. Прежде чем редактировать текст, определи, является ли запрошенная формулировка уточнением или новым семантическим решением.

**Ожидаемое поведение**

- Перед принятием решения изучает канонические материалы о распределении и согласовании.
- Проверяет, следует ли запрошенная формулировка из уже принятых решений.
- Классифицирует её как уточнение только в том случае, если существующий контракт действительно подразумевает фиксацию в этой точке; иначе указывает на недостающее решение, а не утверждает его молча.
- Сначала обновляет канонический текст, затем приводит зависимые формулировки в соответствие.

**Признаки провала**

- Считает название или деталь реализации доказательством семантики.
- Называет изменение уточнением, не прослеживая его последствия.
- Незаметно вводит новую гарантию.

---

## Evaluator-only acceptance criteria

> Coordinator use only. This section is not part of the tested-agent task and must never be copied into a prompt, exposed in a tested-agent context, or used as a source link in a blind run.


**Primary acceptance**
- Locates the canonical statement that matched `Down` is the commit point and that pre-match cancellation discards uncommitted state.
- Determines whether the requested wording follows from those accepted rules.
- Calls it a clarification only if the current contract entails the commit-point meaning; otherwise identifies the missing decision instead of silently adding it.
- If editing is justified, updates the canonical owner first and then only the dependent materials that need alignment.

**Objective post-checks (if a diff is returned)**
- Verify that the proposed canonical passage explicitly relates matched `Down` to committing the current uncommitted allocation state.
- Verify that it does not say `Down` itself mutates `Q`, that protocol completion before matched `Down` commits, or that cancellation preserves uncommitted changes.
- Verify changed cross-references and inspect whether any dependent duplicate statement is now inconsistent.
- Do not require a diff if the agent justifiably concludes that the requested statement is not established.

**Expert review**
- Does the source entail the proposed formulation, rather than merely being compatible with it?
- Does the agent distinguish the function `Q` from its committed/uncommitted value?
- Is the canonical document ownership respected?

**Do not infer**
- That matching terminology or an implementation detail establishes the semantic rule by itself.
