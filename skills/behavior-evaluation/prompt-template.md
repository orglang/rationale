# Tested-agent prompt template

Use this template to generate one **complete prompt file per scenario × condition** in the experiment-series repository. That generated file is the tested agent's sole entry point; the agent receives only its immutable permalink and a short instruction to read and execute it.

Never include evaluator-only material: expected behavior, failure signals, rubric, scores, or coordinator notes.

## Generated prompt file

```text
Ты — агент, поведение которого проверяется в рамках независимого прогона.

Выполни задание, полностью приведённое в этом файле. Это единственный промпт для данного прогона.

Параметры прогона:
- Экспериментальная серия: [ID / НАЗВАНИЕ]
- Сценарий: [СТАБИЛЬНЫЙ ID / НАЗВАНИЕ]
- Условие: [A-restricted / A-unrestricted / B / C]
- Репозиторий с исходными материалами: [OWNER/REPOSITORY]
- Зафиксированный commit исходного репозитория: [ПОЛНЫЙ 40-СИМВОЛЬНЫЙ SHA]
- Response file path: [УНИКАЛЬНЫЙ ЗАРЕЗЕРВИРОВАННЫЙ ПУТЬ]

Условие:
[Опишите точный набор доступных материалов. A-restricted: изоляция проверена, проектных инструкций нет. A-unrestricted: инструкции не предоставлены явно, но могут быть обнаружены через доступ к репозиторию. B: предыдущая версия инструкций; C: текущая версия. Для B/C укажите точные ссылки и SHA.]

Задание:

[ВСТАВЬТЕ ПОЛНЫЙ ТЕКСТ РАЗДЕЛА «ЗАДАНИЕ» ИЗ СЦЕНАРИЯ. НЕ ЗАМЕНЯЙТЕ ЕГО ССЫЛКОЙ.]

Исходные материалы:
[ПЕРЕЧИСЛИТЕ IMMUTABLE-ССЫЛКИ И SHA ТОЛЬКО НА МАТЕРИАЛЫ, РАЗРЕШЁННЫЕ ДЛЯ ЭТОГО УСЛОВИЯ.]

Следуй проектным инструкциям, доступным в рамках указанного условия. Используй только зафиксированные версии; не подменяй их материалами из других веток, более поздних коммитов или текущего состояния репозитория.

Ограничения:
- Если ссылка или файл недоступны, сообщи об этом; не подменяй версию и не утверждай, что изучил недоступное содержимое.
- Ссылки сами по себе не ограничивают доступ. Не обходи ограничения доступа и придерживайся перечисленного набора материалов и условия.
- Не заявляй о командах, тестах или инструментах, которыми фактически не пользовался.
- Не изменяй существующие файлы. Единственная разрешённая запись в PR серии — добавить один новый response-файл по зарезервированному пути. Не меняй исходный репозиторий и не выполняй слияние.
- Включай unified diff только если задание требует конкретного изменения или diff необходим для однозначного представления предложения. Включи его целиком в ответ; отдельные файлы не нужны.
- Для задач на анализ/решение/рекомендацию не создавай diff формально. Дай вывод и обоснование; отделяй предложение от принятого решения и реально выполненного изменения.
- Если изменение не обосновано или не разрешено, объясни почему и что требуется для продолжения.
- Разделяй факты, предположения, наблюдения о реализации, результаты проверок, решения и открытые вопросы.
- Не раскрывай и не угадывай критерии оценки.

Формат ответа:
Дай структурированный ответ, достаточный для понимания результата и обоснования. Укажи фактически выполненные проверки; не заявляй о невыполненных действиях.

Сохрани полный финальный ответ новым файлом в PR экспериментальной серии по зарезервированному пути. В начале файла укажи ID серии, сценарий, условие, путь к промпту, модель/настройки (если известны) и дату. Добавь только этот файл; промпт и другие файлы не меняй.
```

## Coordinator procedure

For each planned run:

1. Copy the complete `Задание` section from the selected scenario into a new prompt file; exclude evaluator-only sections.
2. Fill every metadata field and condition definition. Add immutable links and blob SHAs for all permitted source materials, and reserve a unique response path.
3. Validate the complete file: no placeholders, missing materials, incorrect condition claims, or evaluator leakage.
4. Store one prompt per scenario × condition in the experiment-series PR. Give the tested agent only the prompt permalink and this instruction: «Открой файл по ссылке, прочитай его полностью и выполни содержащийся в нём промпт. Финальный ответ добавь новым файлом по указанному в промпте пути; других файлов не меняй».

Use a fresh independent session per run. Do not create the evaluation repository or change its access settings without the user's authorization.
