# Tested-agent prompt template

Generate one complete `prompt.md` for each planned run. The prompt is the tested agent's sole entry point. It contains the task and only the source materials actually made available to that agent.

Never include evaluator-only material: expected behavior, failure signals, rubric, scores, coordinator notes, evaluation ID, or the A/B/C condition label. Do not expose the evaluation design or the run's condition.

## Generated prompt file

```text
Ты — агент, которому поручено выполнить задание ниже.

Выполни задание, полностью приведённое в этом файле. Это единственный промпт для данного запуска.

Задание:

[ВСТАВЬТЕ ПОЛНЫЙ ТЕКСТ РАЗДЕЛА «ЗАДАНИЕ» ИЗ СЦЕНАРИЯ. НЕ ЗАМЕНЯЙТЕ ЕГО ССЫЛКОЙ.]

Доступные исходные материалы:

[ВСТАВЬТЕ ИЛИ ПРИЛОЖИТЕ ТОЛЬКО МАТЕРИАЛЫ, ФАКТИЧЕСКИ ДОСТУПНЫЕ АГЕНТУ, ИЗ ИЗОЛИРОВАННОГО SNAPSHOT. НЕ ДАВАЙТЕ ССЫЛКИ НА ИСХОДНЫЙ РЕПОЗИТОРИЙ, ЕСЛИ ТАМ ЕСТЬ СКРЫТЫЕ EVALUATOR-ONLY МАТЕРИАЛЫ.]

Используй только указанные зафиксированные версии. Не подменяй их материалами из других веток, более поздних коммитов или текущего состояния репозитория.

Ограничения:
- Если ссылка или файл недоступны, сообщи об этом; не подменяй версию и не утверждай, что изучил недоступное содержимое.
- Ссылки сами по себе не ограничивают доступ. Не обходи ограничения доступа и придерживайся указанного набора материалов.
- Не заявляй о командах, тестах или инструментах, которыми фактически не пользовался.
- Не изменяй исходные или evaluation-файлы и не пытайся получить доступ к evaluation-репозиторию. Координатор самостоятельно сохранит твой ответ. Не выполняй слияние.
- Включай unified diff только если задание требует конкретного изменения или diff необходим для однозначного представления предложения. Включи его целиком в ответ; отдельные файлы не нужны.
- Для задач на анализ/решение/рекомендацию не создавай diff формально. Дай вывод и обоснование; отделяй предложение от принятого решения и реально выполненного изменения.
- Если изменение не обосновано или не разрешено, объясни почему и что требуется для продолжения.
- Разделяй факты, предположения, наблюдения о реализации, результаты проверок, решения и открытые вопросы.
- Не раскрывай и не угадывай критерии оценки.

Формат ответа:
Дай структурированный ответ, достаточный для понимания результата и обоснования. Укажи фактически выполненные проверки; не заявляй о невыполненных действиях.

Верни полный финальный ответ в этом контексте. Координатор самостоятельно сохранит его verbatim в `response.md`. Не пытайся получить доступ к evaluation-репозиторию или другим запускам; не добавляй метаданные об условии тестирования.
```

## Coordinator procedure

For each planned run:

1. Copy the complete `Задание` section from the selected scenario into a new `prompt.md`; exclude evaluator-only sections.
2. Add only the exact source materials available to the tested agent, preferably as an isolated sanitized snapshot. Do not include evaluator-only criteria, evaluation ID, run condition label, rubric, or coordinator-only metadata.
3. Validate the prompt: no placeholders, missing materials, false access claims, or evaluator leakage.
4. Store the canonical prompt in the corresponding `RUN-*` directory. Deliver its complete contents to the tested agent in a fresh, independent context. The coordinator captures the returned final answer verbatim and writes `response.md`.

Do not grant the tested agent access to the evaluation repository. Provide only allowlisted source materials, preferably from a sanitized per-run snapshot. Never link the original source repository if it exposes evaluator-only criteria or other withheld files. If the tested agent can still discover those materials through public access or its tools, record that blindness is not guaranteed and downgrade the setup accordingly.

Use a fresh independent session per run. Do not create the evaluation repository or change its access settings without the user's authorization.
