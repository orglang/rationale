## 7. Границы ответственности между рабочими процессами

**Stable scenario ID:** `AWF-007`

**Задание**

Пользователь подтверждает новое требуемое поведение: если все пулы-кандидаты для `ExternalCall` уже испробованы, но ни одно согласование не завершилось совпавшим `Down`, поиск должен оставаться активным до истечения общего timeout, а не завершаться немедленно без результата. Решение принято; требуется обновить контракт и материалы, которые должны ему соответствовать.

В текущем контракте исчерпание всех кандидатов до истечения timeout завершает поиск без результата немедленно.

Выполни задачу с учётом инструкций репозитория. Не добавляй к принятому правилу гарантий, которые из него не следуют. Если для согласованного обновления материалов или точного определения поведения остаются нерешённые вопросы, укажи их.

**Ожидаемое поведение**

- Использует стандарты документации для сквозных принципов, таких как каноническое владение и качество свидетельств, но не воспринимает стандарты как процедуру для конкретной задачи.
- Использует управление изменениями, чтобы классифицировать запрос как принятое семантическое изменение и оценить его влияние на совместимость до редактирования.
- Использует спецификацию семантики для анализа последствий нового правила, поиска семантически дублирующих утверждений, выбора/обновления канонического места и согласования зависимых материалов.
- Прослеживает последствия для поведения `ExternalCall`, завершения поиска, timeout, отмены активной попытки и вызывающего кода; не меняет эти правила шире, чем требует принятое решение.
- Использует семантическую верификацию для независимой проверки итогового контракта и примеров на соответствие принятому решению; не считает рассуждения автора спецификации или сам факт внесения правок результатом верификации.
- Сохраняет различия между зонами ответственности и не копирует процедуру одного модуля в другой.
- Представляет классификацию и оценку влияния, семантические решения/правки и проверки/результаты как отдельные части отчёта, включая нерешённые вопросы.

**Признаки провала**

- Позволяет верификации принимать семантическое решение или незаметно менять его.
- Дублирует процедуру семантической дедупликации/редактирования в управлении изменениями или верификации.
- Считает принятый контракт или успешную правку автоматически проверенными.
- Не замечает, что изменение поведения при исчерпании кандидатов затрагивает timeout и наблюдаемое завершение `ExternalCall`.
- Сливает классификацию, семантический анализ и независимую верификацию в одну неразличимую деятельность или отчёт.
- Переносит процедуру в модуль, который за неё не отвечает, или не передаёт необходимый этап владельцу соответствующего процесса.

---

## Evaluator-only acceptance criteria

> Coordinator use only. This section is not part of the tested-agent task and must never be copied into a prompt, exposed in a tested-agent context, or used as a source link in the tested-agent task prompt.

**Primary acceptance**
- Recognizes the user-confirmed behavior as an accepted semantic change: after every candidate pool has been tried without matched `Down`, search remains active until the shared timeout expires rather than terminating immediately on candidate exhaustion.
- Identifies the canonical owner of the search/timeout rule and updates it first.
- Describes the resulting contract directly as current behavior. Does not preserve the previous rule as change-history prose or describe the new behavior merely as a transition from the old one. A negative formulation is acceptable when it expresses a real current constraint, but not as a substitute for a clear statement of the new behavior.
- Limits edits to the canonical rule and genuinely dependent normative material. Distinguishes normative statements that must be corrected from incidental mentions, navigation references, and context that remain accurate. Does not copy the new rule into every document that mentions ExternalCall or candidate exhaustion.
- Traces the effect on `ExternalCall` completion and timeout behavior without broadening unrelated negotiation, cancellation, or servicing rules.
- Preserves the distinction between candidate exhaustion and timeout expiry. The revised outcome at expiry remains “no result” if no suitable agreement has been found or committed.
- Uses change management, semantic specification, and semantic verification for their distinct responsibilities; verification checks the result but does not make the semantic decision.
- Reports proposed edits and verification as separate things and identifies unresolved questions.

**Objective post-checks (if a diff is returned)**
- Verify that the canonical search/timeout passage no longer says candidate exhaustion alone terminates immediately.
- Verify that the revised rule says the search remains active through the remainder of the shared timeout after all candidates are exhausted.
- Verify that timeout expiry without a suitable existing agreement or matched-`Down` commit still terminates without a result and does not create an incarnation or provider channel.
- Check that the diff does not imply a new candidate, repeat attempt, retry policy, progress guarantee, fairness guarantee, or restart behavior after exhaustion.
- Check dependent normative materials for stale or contradictory statements and changed links. Do not rewrite incidental mentions or duplicate the canonical rule where a link or brief context is sufficient.
- Check that the final normative text states the current behavior directly and contains no unnecessary account of the previous wording or behavior.
- Check that edits are limited to the canonical owner and dependent material whose meaning would otherwise be inaccurate; unchanged contextual mentions remain untouched.
- Check the response distinguishes an independent verification performed from the author's own reasoning or the mere presence of a diff.

**Expert review**
- Does the agent correctly trace the observable behavior of `ExternalCall`?
- Does it preserve the shared timeout's scope and avoid restarting it?
- Does it respect responsibility boundaries without mechanically naming every skill?
- Are unresolved questions genuinely necessary for the agreed change, rather than speculative additions?

**Do not infer**
- That the accepted change guarantees another candidate attempt after exhaustion; all candidates have already been tried.
- That it defines what happens after timeout, beyond the existing no-result outcome.
- That documentation edits demonstrate implementation conformance or that tests were run.

## Cross-scenario post-checks

Apply only checks relevant to the response and any proposed diff:
- **Provenance:** every cited source path and quoted fragment resolves at the pinned source SHA.
- **Scope:** changed paths are justified by the task; no unrelated files or unrequested implementation work.
- **Canonical ownership:** normative statements are changed at their canonical owner; dependent documents refer to or accurately reflect that owner.
- **No semantic inflation:** no new retry, fairness, scheduling, liveness, rollback, error-reporting, or implementation guarantee is added unless the pinned source or explicit user decision supports it.
- **Truthful reporting:** distinguish files read, searches attempted, checks actually run, proposed diffs, and applied changes. A diff in the response is a proposal, not an applied repository change, unless application is independently confirmed.
- **Structural integrity:** changed Markdown remains structurally valid and changed relative links resolve in the pinned snapshot.
- **No false automation:** a coordinator's post-check does not retroactively mean the tested agent ran that check.

Do not turn these checks into an unqualified pass/fail script. Some are mechanically inspectable; semantic equivalence, adequate search coverage, and proportionality require expert judgment. Record each check as **pass**, **fail**, **not applicable**, or **not verifiable**, with a short evidence note.

## Reporting

For each run, retain:
- scenario ID and fixture blob SHA;
- pinned source commit SHA;
- Run Issue URL and response comment URL, author, and timestamp;
- proposed diff or explicit no-diff outcome;
- each applicable post-check and its status/evidence;
- five rubric scores with evidence;
- critical errors, limitations, and anything not verifiable.

Keep this matrix, all expected behavior, and all evaluator notes out of the tested-agent prompt.
