# Tested-agent prompt template

Generate one complete task prompt for each planned run. The prompt is placed in the body of that run's GitHub Issue. The Run Issue is the tested agent's sole entry point.

Never include evaluator-only material: expected behavior, failure signals, rubric, scores, coordinator notes, evaluation ID, Run ID, or the A/B/C condition label. Do not expose the evaluation design or the run's condition.

## Run Issue body template

```text
Ты — агент, которому поручено выполнить задание ниже.

Выполни задание, полностью приведённое в этом тикете. Это единственный промпт для данного запуска.

Задание:

[ВСТАВЬТЕ ПОЛНЫЙ ТЕКСТ РАЗДЕЛА «ЗАДАНИЕ» ИЗ СЦЕНАРИЯ. НЕ ЗАМЕНЯЙТЕ ЕГО ССЫЛКОЙ.]

Доступные исходные материалы:

[ВСТАВЬТЕ ИЛИ ПРИЛОЖИТЕ ТОЛЬКО МАТЕРИАЛЫ, ФАКТИЧЕСКИ ДОСТУПНЫЕ АГЕНТУ, ИЗ ИЗОЛИРОВАННОГО SNAPSHOT. НЕ ДАВАЙТЕ ССЫЛКИ НА ИСХОДНЫЙ РЕПОЗИТОРИЙ, ЕСЛИ ТАМ ЕСТЬ СКРЫТЫЕ EVALUATOR-ONLY МАТЕРИАЛЫ.]

Используй только указанные зафиксированные версии. Не подменяй их материалами из других веток, более поздних коммитов или текущего состояния репозитория.

Ограничения:
- Если ссылка или файл недоступны, сообщи об этом; не подменяй версию и не утверждай, что изучил недоступное содержимое.
- Ссылки сами по себе не ограничивают доступ. Не обходи ограничения доступа и придерживайся указанного набора материалов.
- Не заявляй о командах, тестах или инструментах, которыми фактически не пользовался.
- Не изменяй исходные файлы или другие Issues. Не пытайся найти родительский Evaluation Issue, другие запуски или coordinator-only материалы. Не добавляй в свой комментарий ссылки или упоминания о них. Не выполняй слияние.
- Включай unified diff только если задание требует конкретного изменения или diff необходим для однозначного представления предложения. Включи его целиком в комментарий; отдельные файлы не нужны.
- Для задач на анализ/решение/рекомендацию не создавай diff формально. Дай вывод и обоснование; отделяй предложение от принятого решения и реально выполненного изменения.
- Если изменение не обосновано или не разрешено, объясни почему и что требуется для продолжения.
- Разделяй факты, предположения, наблюдения о реализации, результаты проверок, решения и открытые вопросы.
- Не раскрывай и не угадывай критерии оценки.

Формат ответа:
Дай структурированный ответ, достаточный для понимания результата и обоснования. Укажи фактически выполненные проверки; не заявляй о невыполненных действиях.

**Обязательно опубликуй полный финальный ответ verbatim отдельным новым комментарием к этому же Run Issue.** Не сокращай, не пересказывай и не разбивай ответ на несколько комментариев. Не публикуй ответ в другом тикете или репозитории. Если GitHub-интеграция недоступна, нет прав на комментирование или публикация завершилась ошибкой, прямо сообщи об этом в чате и не утверждай, что комментарий опубликован. Не считай ответ в чате заменой комментария.
```

## Coordinator procedure

For each planned run:

1. Copy the complete `Задание` section from the selected scenario into a new Run Issue body; exclude evaluator-only sections.
2. Add only the exact source materials available to the tested agent, preferably as an isolated sanitized snapshot. Do not include evaluation/Run IDs, run condition label, rubric, or coordinator-only metadata.
3. Validate the body and the complete Issue surface (title, body, labels, comments, attachments): no placeholders, missing materials, false access claims, evaluator leakage, parent references, or sibling-run references.
4. Create the Run Issue in the isolated run repository. Retain its exact URL and a private canonical copy of the prompt in the coordinator-only Evaluation record.
5. Give the tested agent only the Run Issue URL. Verify that its ChatGPT context has a GitHub integration capable of creating Issue comments and the required permission. Do not infer capability from the coordinator's own tools.
6. After the attempt, verify the complete answer comment exists on the correct Issue. Record the comment permalink, author, and timestamp in the private assessment record. If no comment was successfully published, mark response capture incomplete; do not create the response comment on the agent's behalf.

The coordinator-only Evaluation record may link to Run Issues. **The reverse must never occur:** no Run Issue may link to, mention, identify, or otherwise reveal its parent Evaluation or any sibling Run. Do not put the parent and child tickets in the same repository when a true blind boundary is required. A child ticket without a parent link is not itself proof of access isolation: repository permissions apply beyond an individual Issue.

Use a fresh independent session per run. Do not create repositories or change their access settings without the user's authorization.
