# Архитектура: инструмент синхронизации Anki ⇄ Cambridge Dictionary

## Обзор

```
   внешне, пользователем             (независимый, отдельный инструмент — не вызывается отсюда)
 ┌─────────────────────┐               ┌───────────────────────────────┐
 │ массовый импорт      │               │  lexicon-scraper/             │
 │ новых записей в Anki  │               │  пишет таблицы cambridge_*    │
 │ (не этот инструмент)  │               │  напрямую в sync.sqlite       │
 └──────────┬───────────┘               └───────────────┬───────────────┘
            │                                            │ пишет
            ▼                                            ▼
 ┌─────────────────────────────────────┐   ┌───────────────────────────────────────┐
 │  Anki, через AnkiConnect             │   │           sync/sync.sqlite            │
 │  (addons/anki_connect)               │   │           (в .gitignore)              │
 │  записи выбираются через любую       │   │                                        │
 │  соседнюю колоду под                 │   │  cambridge_words ─▶ parts_of_speech ─▶ │
 │  1_english::without_group::          │   │    transcriptions                      │
 │  definition/typing/word/typing_sent. │   │  parts_of_speech ─▶ senses ─▶          │
 │  — ОДНИ И ТЕ ЖЕ записи, разные       │   │    definitions ─▶ examples             │
 │  шаблоны. Записи не привязаны к      │   │                                        │
 │  колоде; привязаны только карточки.  │   │  note_definition_links (candidate/    │
 └──────────┬───────────▲───────────────┘   │   confirmed/rejected)                 │
            │           │                    │                                       │
   ⓪ discover-new│      │③ enrich (ограниченные,│  anki_notes (system_note_uuid —     │
   (только чтение)│① stamp│ расширяемые поля)   │   устойчивый якорь; anki_note_id —   │
            │    (Anki→ │                    │   рабочий ключ для AnkiConnect)       │
            │     Anki, │                    │                                       │
            │     без БД)│                   │                                       │
            └───────────┘◀──────────────────────────────────┘
                          ② pull (постатейный upsert, устойчивый, с проверкой)
```

Порядок операций: **⓪ `discover-new`** (только чтение) находит записи, импортированные пользователем, у которых ещё нет `_system_note_uuid`. **① `stamp`** (Anki → Anki, без БД) затем генерирует `_system_note_uuid`/`_system_hash` для этих записей напрямую — именно это делает их непустыми в принципе, и именно на этом строится вся идентичность в этой архитектуре (см. "Идентичность" ниже). Только после этого **② `pull`** (Anki → БД) зазеркаливает записи. `lexicon-scraper` заполняет таблицы Cambridge независимо, в любое время, вне общего цикла. **③ `enrich`** (БД → Anki) намеренно ограничен и расширяем — сегодня пишет только `cefr`, беря его только из **подтверждённой** связи Cambridge, с защитой, и заново получает актуальные значения перед записью.

Этот инструмент никогда не создаёт записи в Anki, никогда не запускается по расписанию и не имеет MCP-сервера — это постоянные исключения, а не отложенные функции.

## Структура директорий

```
sync/
  pyproject.toml, Makefile, requirements.txt, .env, .gitignore
  main.py                        # точка входа CLI на typer
  docs/
    plan.md, architecture.md, plan.ru.md, architecture.ru.md
  src/
    config/load_env.py           # load_dotenv() + простой pydantic.BaseModel + get_config(), тот же шаблон,
                                  # что и в собственном autotest_api/src/config/load_env.py пользователя
                                  # (без pydantic-settings)
    utils/path.py                # ROOT_PATH: подъём вверх до pyproject.toml
    utils/hashing.py             # compute_content_hash(fields: dict) -> str
    utils/logging.py             # общий логгер: файл + stdout, помощник для прогресса
    anki_client.py                 # invoke(action, **params) — тот же контракт, что и mcp/src/anki_client.py
    anki/
      notes.py                    # get_notes(deck), get_notes_fields(ids), update_note_fields(id, fields),
                                   # get_notes_missing_uuid(deck) — поиск по пустому полю для discover-new
    db/
      database.py                 # Database: обёртка над sqlite3 (execute/query/create_tables)
      tables/
        _table.py                  # базовый класс Table
        anki_notes.py
        cambridge_words.py
        cambridge_parts_of_speech.py
        cambridge_transcriptions.py
        cambridge_senses.py
        cambridge_definitions.py
        cambridge_examples.py
        note_definition_links.py
      service/
        anki_note.py                 # поиск сначала по system_note_uuid, запасной вариант — anki_note_id
        cambridge_word.py
        cambridge_part_of_speech.py
        cambridge_transcription.py
        cambridge_sense.py
        cambridge_definition.py
        note_definition_link.py      # жизненный цикл candidate/confirmed/rejected
    sync/
      discover_new.py                # ⓪ поиск в Anki, только чтение
      stamp.py                       # ① Anki → Anki
      pull.py                        # ② Anki → БД
      match.py                       # предлагает кандидатов (word, transcription, transcription_type)
      confirm.py                     # переводит кандидата в подтверждённые
      enrich.py                      # ③ БД → Anki
      diff.py                        # общий помощник для показа разницы, используется pull + enrich
```

В этом проекте нет модуля `cambridge_import/` — за заполнение таблиц `cambridge_*` отвечает напрямую `lexicon-scraper`; этот код только определяет схему и читает из неё.

Повторяет разделение `Database` / `Table` / `Service`, используемое в `addons/grammar_drill/src/db/`: без ORM, сырой SQL как константы класса, `Database.execute`/`.query` возвращают `None` при ошибке. `anki_client.py` — буквальная копия контракта `invoke()` из `mcp/src/anki_client.py`, самодостаточная, а не импортируемая из другого проекта.

## Идентичность: `system_note_uuid` — якорь, `anki_note_id` — рабочий ключ

`_system_note_uuid` был добавлен в тип заметки именно для того, чтобы этот инструмент не зависел от собственного внутреннего id записи в Anki как устойчивой идентичности. `anki_note_id` по-прежнему обязателен для работы — каждый вызов AnkiConnect (`findNotes`, `notesInfo`, `updateNoteFields`) адресует записи по нему, — но он не рассматривается как долгосрочный якорь: `pull` ищет существующую строку `anki_notes` в первую очередь по `system_note_uuid`, когда он у записи уже есть, с запасным вариантом по `anki_note_id` только для записей, которые ещё не были проштампованы. Это означает, что непрерывность записи сохраняется, даже если её `anki_note_id` когда-либо изменится (например, при повторном импорте коллекции), пока сохраняется её `system_note_uuid`.

Отдельно от этого, `word`, `definition`, `part_of_speech` и `examples` вполне могут меняться внутри Anki впоследствии (ручное редактирование — это ожидаемо и нормально). В отличие от `WordsTable` из `grammar_drill`, который делает get-or-create по совпадению `(word, definition, pos)` как естественного ключа, `anki_notes` **никогда** не должна заново выводить или искать строку по совпадению содержимого — идентичность определяется только `system_note_uuid`/`anki_note_id`, никогда значениями полей.

## Привязка к колоде — это механизм выбора, а не идентичность

Записи в Anki не привязаны к колоде — привязаны карточки. Проверено вживую: одни и те же три id записей одинаково находятся при поиске в `1_english::without_group::definition`, `::typing` и `::word` — это одни и те же записи, отображаемые через разные шаблоны карточек в разных соседних колодах. Флаг `--deck` в `discover-new`/`stamp`/`pull`/`match` — это лишь удобный способ выбрать набор записей через поиск `findNotes` AnkiConnect; `anki_notes.source_deck` фиксирует, через какую колоду запись была найдена в последний раз, для информации/отладки, но это не уникальный и не авторитетный атрибут.

## Схема

### Зеркало Anki — `anki_notes`

Одна строка на запись Anki, обновляется индивидуально через `pull` — никогда сплошным удалением с последующей массовой вставкой, поэтому проблема с одной записью не может обрушить весь запуск.

| колонка | тип | примечания |
|---|---|---|
| `id` | INTEGER PK | |
| `anki_note_id` | INTEGER, UNIQUE NOT NULL | собственный id записи в Anki — нужен для вызовов AnkiConnect, но не является устойчивым якорем |
| `system_note_uuid` | TEXT, UNIQUE, NULL | зеркалирует `_system_note_uuid`; генерируется в `stamp`; **это и есть устойчивый якорь идентичности**, а не `anki_note_id` |
| `system_hash` | TEXT, NULL | зеркалирует `_system_hash`, как последний раз прочитано из Anki |
| `source_deck` | TEXT NOT NULL | колода, через которую запись была выбрана при последнем pull — только для справки, см. выше |
| `word`, `trans`, `trans_type`, `part_of_speech`, `sense`, `definition`, `cefr` | TEXT | |
| `example_1` … `example_7` | TEXT | |
| `audio`, `picture`, `video`, `hints` | TEXT | |
| `sync_status` | TEXT | `ok` / `error` — устанавливается `pull` для каждой записи |
| `sync_issue` | TEXT, NULL | понятное человеку описание при `sync_status='error'` |
| `last_pulled_at` | TIMESTAMP NOT NULL | |

### Справочные данные Cambridge — нормализовано, префикс `cambridge_`, заполняются извне через `lexicon-scraper`

Повторяет форму pydantic-моделей `lexicon-scraper` (`Word → PartOfSpeech → Transcription` и `PartOfSpeech → Sense → Definition → Example`). Никогда не записывается `discover-new`, `stamp`, `pull` или `enrich` — этот проект только определяет схему и читает из неё.

| таблица | колонки | уникальность |
|---|---|---|
| `cambridge_words` | `id PK, word, imported_at` | `UNIQUE(word)` |
| `cambridge_parts_of_speech` | `id PK, word_id FK, name` | `UNIQUE(word_id, name)` |
| `cambridge_transcriptions` | `id PK, part_of_speech_id FK, transcription, transcription_type` | `UNIQUE(part_of_speech_id, transcription_type)` |
| `cambridge_senses` | `id PK, part_of_speech_id FK, text` | `UNIQUE(part_of_speech_id, text)` |
| `cambridge_definitions` | `id PK, sense_id FK, text NOT NULL, cefr` | `UNIQUE(sense_id, text)` |
| `cambridge_examples` | `id PK, definition_id FK, text` | — |

### Таблица-связка — `note_definition_links` (жизненный цикл candidate → confirmed)

У одной записи может быть **несколько кандидатных строк** (одна транскрипция может покрывать несколько значений/sense), поэтому `anki_note_id` здесь **не** уникален — уникальна только пара.

| колонка | тип | примечания |
|---|---|---|
| `id` | INTEGER PK | |
| `anki_note_id` | INTEGER NOT NULL | FK на `anki_notes.anki_note_id`; сам по себе не уникален |
| `cambridge_definition_id` | INTEGER NOT NULL | FK |
| `match_method` | TEXT | `word_transcription` / `manual` |
| `status` | TEXT | `candidate` / `confirmed` / `rejected` |
| `created_at` | TIMESTAMP | |
| `confirmed_at` | TIMESTAMP, NULL | |

`UNIQUE(anki_note_id, cambridge_definition_id)` предотвращает дублирующие кандидатные строки для одной и той же пары. Не более одной строки со статусом `confirmed` на запись гарантируется частичным уникальным индексом: `CREATE UNIQUE INDEX ... ON note_definition_links(anki_note_id) WHERE status='confirmed'`. Только строки `confirmed` читаются `enrich`.

## Стратегия сопоставления: сначала кандидаты, потом подтверждение

`match` предлагает кандидатов по ключу `(word, transcription, transcription_type)`, а не по тексту `definition`/`sense`, потому что транскрипция (произношение) редко меняется, даже когда записи Anki правятся вручную, в то время как текст `definition`/`sense`/`part_of_speech` вполне может измениться. Это влечёт два следствия:

1. Подтверждённая связь, once установленная, **не требует повторной проверки при каждой синхронизации** — она остаётся действительной, даже если текст `definition`/`sense` записи впоследствии разойдётся, поскольку сопоставление изначально не опиралось на этот текст.
2. Поскольку одна транскрипция всё ещё может законно покрывать несколько значений, `match` не может гарантировать единственный результат — он всегда создаёт ноль, одного или нескольких **кандидатов** на запись. Перевод в доверенную связь, пригодную для `enrich`, — отдельный, явный шаг (`confirm`), либо указанный вручную (`--note ID --definition ID`), либо автоматический только для однозначного случая (`--auto-single`, когда у записи сейчас ровно один неотклонённый кандидат).

`match` нужно (пере)запускать только когда обнаружены/проштампованы новые записи или импортированы новые слова Cambridge — не при каждом `pull`.

## Команды CLI

Реализовано на `typer`.

| команда | направление | эффект |
|---|---|---|
| `discover-new [--deck NAME]` | только чтение | Ищет в Anki записи с пустым `_system_note_uuid` (свежеимпортированные пользователем, вне этого инструмента) и выводит их. Без записи. |
| `stamp [--deck NAME] [--force] [--dry-run]` | Anki → Anki | Без чтения/записи БД. Вычисляет хеш контента из только что полученных живых полей и генерирует uuid, если он пуст; записывает оба поля, `_system_hash`/`_system_note_uuid`, обратно, пропуская непустые поля, если не указан `--force`. Безопасно перезапускать широко в любое время — затрагивает только непроштампованные записи. |
| `pull [--deck NAME] [--skip-review]` | Anki → БД | Постатейный upsert в `anki_notes`, поиск сначала по `system_note_uuid`, запасной вариант — `anki_note_id`. Показывает разницу "было/стало" по каждой изменившейся записи для подтверждения, если не указан `--skip-review` или `REQUIRE_REVIEW=false`. Проблема с одной записью фиксируется как `sync_status='error'` с сообщением в `sync_issue`, журналируется и не прерывает выполнение. Выводит прогресс `[i/всего] (%)` и итоговую сводку. |
| *(внешний)* `lexicon-scraper` | lexicon-scraper → БД | Не входит в этот CLI. Пишет напрямую в таблицы `cambridge_*`, запускается независимо. |
| `match [--deck NAME]` | внутри БД | Предлагает `candidate`-связи между `anki_notes` и `cambridge_definitions` через `(word, transcription, transcription_type)`. Безопасно и дёшево перезапускать; не нужно запускать при каждой синхронизации. |
| `confirm [--note ID --definition ID \| --auto-single]` | внутри БД | Переводит `candidate` в `confirmed` (конкретная указанная пара, либо автоматически, когда у записи ровно один однозначный кандидат). |
| `review` | только чтение | Выводит записи без кандидатов, записи с несколькими неразрешёнными кандидатами и записи с `sync_status='error'` из последнего `pull`. |
| `enrich [--force] [--dry-run] [--skip-review]` | БД → Anki | Пишет расширяемый, явно заданный набор полей — сейчас только `cefr` — беря их только из связей **`confirmed`**, только если поле пусто в Anki. Заново получает актуальные значения непосредственно перед записью. То же поведение сравнения/проверки и прогресса, что и в `pull`. |

Белый список для `enrich` реализован как небольшой реестр (имя поля → функция-резолвер), а не как встроенная логика, так что добавление нового поля из БД в будущем (помимо `cefr`) не потребует переделки команды — только регистрации нового резолвера.

## Хеш контента

```
def normalize(value: str | None) -> str:
    return value if value else "∅"

raw = "".join(normalize(v) for v in [
    word, trans, trans_type, part_of_speech, sense, definition, cefr,
    example_1, example_2, example_3, example_4, example_5, example_6, example_7,
    audio, picture, video, hints,
])
content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
```

Поля конкатенируются напрямую (без разделителя), но каждое пустое/`None` значение сначала заменяется фиксированным плейсхолдером (`"∅"`), чтобы два разных варианта границы между соседними полями не могли незаметно схлопнуться в одну и ту же строку. Исключены `_system_hash`/`_system_note_uuid` (были бы самоссылкой) и метаданные Anki (id записи, время изменения) — хешируется только контент, которым владеет человек.

- Впервые заполняется в `stamp`, вычисляется напрямую из только что полученных полей Anki (БД на этом этапе ещё не участвует).
- Пересчитывается только для чтения во время `pull` и сравнивается с текущим `_system_hash` записи, чтобы отметить расхождение — "эта запись была отредактирована вручную с момента последней простановки хеша" — ничего не записывая.

## Журналирование и прогресс

Общий логгер (файл + stdout) используется всеми командами. Для массовых операций (`discover-new`, `stamp`, `pull`, `match`, `enrich`):
- Каждая запись журналирует однострочный результат: `[i/всего] (%) запись <anki_note_id>: создана | обновлена | без изменений | пропущена | ошибка — <детали>`.
- Итоговая строка сводки: всего обработано, создано, обновлено, без изменений, пропущено, с ошибкой.
- Ошибки журналируются с достаточной детализацией для диагностики (id записи, поле, исключение), но никогда не прерывают пакетную обработку.

## Конфигурация

Простой `pydantic.BaseModel` + `python-dotenv`, по точному образцу собственного файла пользователя `autotest_api/src/config/load_env.py`: `load_dotenv()` вызывается при импорте, класс конфигурации на `BaseModel`, и функция `get_config()`, явно отображающая вызовы `os.environ.get(...)` в неё — **не** `pydantic-settings`.

```python
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Config(BaseModel):
    anki_connect_url: str
    db_path: str
    deck_name: str
    require_review: bool

def get_config() -> Config:
    return Config(
        anki_connect_url=os.environ.get("ANKI_CONNECT_URL", "http://127.0.0.1:8765"),
        db_path=os.environ.get("DB_PATH", str(ROOT_PATH / "sync.sqlite")),
        deck_name=os.environ.get("DECK_NAME", "1_english::without_group::definition"),
        require_review=os.environ.get("REQUIRE_REVIEW", "true").lower() == "true",
    )
```

| настройка | значение по умолчанию |
|---|---|
| `ANKI_CONNECT_URL` | `http://127.0.0.1:8765` |
| `DB_PATH` | `sync.sqlite` внутри этого проекта (`sync/`), в `.gitignore` |
| `DECK_NAME` | `1_english::without_group::definition` (любая соседняя колода подойдёт одинаково — см. "Привязка к колоде" выше) |
| `REQUIRE_REVIEW` | `true` — установить `false` (или передать `--skip-review`), чтобы применять изменения `pull`/`enrich` без интерактивной проверки разницы |

Собственная конфигурация `lexicon-scraper` (как он указывает на `DB_PATH`) вне рамок этого документа — это деталь интеграции, которую предстоит определить самому `lexicon-scraper`, когда он будет расширен для записи в эти таблицы.

## Процесс работы с новыми записями

Пользователь будет продолжать добавлять новые записи в Anki со временем через собственный процесс импорта (вне этого инструмента). Это обрабатывается как явный, отдельный проход, а не просто предполагается, что таких случаев не будет:

```
внешний массовый импорт (пользователем) → discover-new (только чтение) → stamp (записывает
  hash/uuid для новых записей) → pull (зазеркаливает их в БД) → match (кандидаты для
  новых записей) → confirm → enrich
```

`stamp` безопасно запускать широко в любое время (он затрагивает только записи, у которых ещё нет uuid/hash), поэтому на практике `discover-new` существует в основном для наглядности перед запуском `stamp`, а не потому, что сам `stamp` нуждается в узком ограничении области действия.

## Риски и краевые случаи

- **Первый запуск `stamp`**: у всех существующих записей сейчас пустые uuid/hash, поэтому он затронет сразу весь выбранный набор записей. Сначала стоит запустить `--dry-run`.
- **Неоднозначные кандидаты Cambridge**: одна транскрипция может законно покрывать несколько значений — никогда не подтверждаются автоматически, кроме однозначного случая; выводятся через `review` для ручного `confirm`.
- **Нестабильность `anki_note_id`**: если он когда-либо изменится для записи, у которой уже есть `system_note_uuid` (например, после повторного импорта коллекции), `pull` должен распознать запись по её uuid и обновить существующую строку, а не создавать дубликат.
- **Изоляция ошибок по записям**: `pull` никогда не должен прерываться из-за одной плохой записи — весь смысл `sync_status`/`sync_issue` в том, чтобы дать остальной части пакета завершиться и точно показать, какие записи требуют внимания, через `review`.
- **Параллельные правки во время `enrich`**: защита обеспечивается повторным получением актуальных полей Anki непосредственно перед записью `cefr` (или любого будущего дополняемого поля), с пропуском, если поле уже не пусто, если не указан `--force`.
- **Дублирование между колодами**: поскольку одна и та же запись может быть найдена через несколько соседних колод, запуски `pull`/`stamp` с разными значениями `--deck` не должны создавать дублирующие строки `anki_notes` — это гарантируется уникальностью `system_note_uuid`/`anki_note_id`, а не колодой.
- **Граница интеграции с `lexicon-scraper`**: этот проект определяет схему `cambridge_*`; фактическая запись `lexicon-scraper` в `sync.sqlite` — отдельная будущая работа вне этого кода.
- **Расположение файла БД**: `sync.sqlite` находится внутри `sync/` и должен быть указан в `.gitignore` вместе с `.env`, `venv/` и `__pycache__/`.
