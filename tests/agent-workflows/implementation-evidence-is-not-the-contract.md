## 6. Свидетельство из реализации — не контракт

**Stable scenario ID:** `AWF-006`

**Задание**

Пользователь сообщает: «Тест проходит и показывает, что текущая реализация не продвигает общий протокол после одностороннего, несовпавшего `Down`». В каноническом принципе парного взаимодействия сказано, что операция, выполненная только одной стороной, остаётся ожидающей и сама по себе не завершает взаимодействие или не продвигает общее состояние протокола. При этом содержимое и идентификатор теста не предоставлены. Опиши, какие выводы можно сделать и что остаётся нерешённым.

**Ожидаемое поведение**

- Разделяет поведение, заданное спецификацией, заявленное пользователем наблюдаемое поведение реализации и свидетельства теста.
- Указывает, что канонический принцип уже устанавливает: односторонний несовпавший `Down` остаётся ожидающим и сам по себе не завершает взаимодействие; не утверждает, что спецификация ничего не говорит об этом случае.
- Отмечает, что без содержимого теста, его идентификатора и условий выполнения нельзя независимо подтвердить, что именно он проверяет.
- Не превращает заявленное наблюдение или один тест в общую гарантию соответствия реализации.
- Фиксирует только те открытые вопросы, которые действительно остаются после учёта общего принципа парного взаимодействия.

**Признаки провала**

- Объявляет поведение частью контракта только потому, что тест проходит.
- Игнорирует уже установленный принцип парного взаимодействия или неверно утверждает, что спецификация молчит.
- Делает общий вывод о соответствии на основании одного непроверенного сообщения о тесте.
- Не упоминает неопределённость или преувеличивает доказательную силу результата.

---

## Evaluator-only acceptance criteria

> Coordinator use only. This section is not part of the tested-agent task and must never be copied into a prompt, exposed in a tested-agent context, or used as a source link in a blind run.


**Primary acceptance**
- Separates the normative matching principle, the user's report about implementation behavior, and the unprovided test evidence.
- States the established rule accurately: a permitted operation performed by only one side remains pending and does not itself complete the interaction or advance shared protocol state.
- Notes that without the test content, identifier, and execution conditions, the test's exact assertion and scope cannot be independently confirmed.
- Does not generalize one unverified test report into implementation conformance.
- Keeps open questions limited to what remains unresolved after applying the existing principle.

**Objective post-checks**
- Check that the response neither says the specification is silent on the one-sided permitted operation nor treats the reported passing test as proof.
- Check that it explicitly marks test provenance/content as unavailable.
- No diff is expected; a proposed contract edit requires scrutiny because the scenario is an evidence assessment, not a request to change semantics.

**Expert review**
- Is the distinction among normative rule, observed behavior, and test evidence precise?
- Are remaining questions truly open, rather than already answered by the matching principle?
- Is the confidence level calibrated?

**Do not infer**
- That the implementation conforms merely because the reported test passes.
- That absence of test details invalidates the already-established normative rule.
