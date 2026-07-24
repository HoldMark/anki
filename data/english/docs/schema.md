# `sync.sqlite` — schema reference (source of truth)

This document describes the SQLite database shared by the `sync` and `lexicon-scraper` projects
(both live as sibling directories under this `anki/` superproject). It is the **source of truth**
for the schema — table/column definitions, foreign keys, views, and which project owns which
tables. Each project's own docs (`sync/docs/architecture.md`,
`lexicon-scraper/docs/architecture.md`) describe *how* that project uses the schema (its commands,
its business logic) and link back here instead of repeating the column definitions.

## Location

```
anki/data/english/sync.sqlite
```

Git-ignored in both `sync` and `lexicon-scraper` (and at the `anki/` superproject level) — never
committed. Backups taken before risky schema changes live in `backups/` next to it, as
`backups/sync.sqlite.bak-<timestamp>[-<label>]`.

Both projects resolve the path via a `DB_PATH` env var (`.env`, loadable per-project), defaulting to
this file resolved relative to each project's own root:

| project | default resolution | config file |
|---|---|---|
| `sync` | `<sync root>/../data/english/sync.sqlite` | `sync/src/config/load_env.py` |
| `lexicon-scraper` | `<lexicon-scraper root>/../data/english/sync.sqlite` | `lexicon-scraper/configs/db.py` |

This only resolves correctly when both projects are checked out as siblings under the same `anki/`
superproject (true in this repo layout). A standalone checkout of either project elsewhere must set
`DB_PATH` explicitly (e.g. `DB_PATH=/abs/path/to/sync.sqlite`).

## Ownership

`sync` and `lexicon-scraper` are two independent git repositories that each keep their **own copy**
of the `CREATE TABLE` statements for the tables they share (`cambridge_*`) — neither imports the
other's code, by design (see `lexicon-scraper/docs/architecture.md`'s "The decision" section). Both
copies must be kept byte-identical whenever the shared schema changes.

| table | owner (writes) | readers |
|---|---|---|
| `cambridge_words` | `lexicon-scraper` | `sync` (`match`) |
| `cambridge_parts_of_speech` | `lexicon-scraper` | `sync` (`match`) |
| `cambridge_senses` | `lexicon-scraper` | `sync` (`match`) |
| `cambridge_definitions` | `lexicon-scraper` | `sync` (`match`, `enrich`) |
| `cambridge_examples` | `lexicon-scraper` | `sync` (`enrich`) |
| `anki_notes` | `sync` only | `sync` |
| `note_definition_links` | `sync` only | `sync` |

`lexicon-scraper` never touches `anki_notes` / `note_definition_links` — those exist only in
`sync`. `sync` never writes to `cambridge_*` — it only reads what `lexicon-scraper` imported from
Cambridge Dictionary.

## Entity relationships

```
cambridge_words ──▶ cambridge_parts_of_speech ──▶ cambridge_senses ──▶ cambridge_definitions ──▶ cambridge_examples
    (1)                    (N)                         (N)                    (N)                     (N)

anki_notes ──▶ note_definition_links ──▶ cambridge_definitions
   (1)              (N, candidate/confirmed/rejected)
```

- One Cambridge word has many parts of speech (each with its own transcription).
- One part of speech has many senses.
- One sense has many definitions (each with an optional CEFR level).
- One definition has many examples.
- One Anki note can have many `note_definition_links` rows (candidate matches during `match`,
  narrowed down via `confirm`); a note may end up with more than one **confirmed** link (a single
  card can legitimately cover more than one Cambridge definition — see `sync/docs/architecture.md`'s
  "Групповое подтверждение").

## Tables

### `cambridge_words`
*Owned by `lexicon-scraper`. One row per distinct English word imported from Cambridge Dictionary.*

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | autoincrement |
| `word` | TEXT NOT NULL | natural key — `UNIQUE(word)` |
| `imported_at` | TIMESTAMP NOT NULL | set on insert |

### `cambridge_parts_of_speech`
*Owned by `lexicon-scraper`. One row per (word, part-of-speech) pair.*

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | autoincrement |
| `word_id` | INTEGER NOT NULL | FK → `cambridge_words(id)` |
| `name` | TEXT NOT NULL | e.g. `noun`, `verb`, `adjective` |
| `transcription` | TEXT | IPA transcription, nullable |
| `transcription_type` | TEXT | e.g. `us`/`uk`, nullable |

Natural key: `UNIQUE(word_id, name)`. `transcription`/`transcription_type` live directly on this
table rather than a separate table — a part of speech never has more than one transcription in
this pipeline (decided 2026-07-23; see `sync/docs/checklist.md`'s schema-review entry for that
date).

### `cambridge_senses`
*Owned by `lexicon-scraper`. One row per distinct sense text under a part of speech.*

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | autoincrement |
| `part_of_speech_id` | INTEGER NOT NULL | FK → `cambridge_parts_of_speech(id)` |
| `text` | TEXT NOT NULL | e.g. "someone who takes advantage of a situation" |

Natural key: `UNIQUE(part_of_speech_id, text)`.

### `cambridge_definitions`
*Owned by `lexicon-scraper`. One row per definition text under a sense.*

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | autoincrement |
| `sense_id` | INTEGER NOT NULL | FK → `cambridge_senses(id)` |
| `text` | TEXT NOT NULL | the definition itself |
| `cefr` | TEXT | CEFR level (`A1`–`C2`), nullable — not always present on Cambridge's page |

Natural key: `UNIQUE(sense_id, text)`.

### `cambridge_examples`
*Owned by `lexicon-scraper`. One row per example sentence under a definition.*

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | autoincrement |
| `definition_id` | INTEGER NOT NULL | FK → `cambridge_definitions(id)` |
| `text` | TEXT | nullable |

No uniqueness constraint (Cambridge can list near-duplicate examples) — `lexicon-scraper`'s
`SqliteWordRepository` dedups by hand at write time instead (reads existing texts for the
definition before inserting), since there's no natural key at the DB level to enforce it.

### `anki_notes`
*Owned exclusively by `sync`. One row per mirrored Anki note.*

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | autoincrement |
| `anki_note_id` | INTEGER NOT NULL | AnkiConnect's note id — operational, can change (e.g. collection re-import); `UNIQUE` |
| `word` | TEXT | |
| `trans` | TEXT | translation |
| `trans_type` | TEXT | |
| `part_of_speech` | TEXT | |
| `sense` | TEXT | |
| `definition` | TEXT | |
| `cefr` | TEXT | written by `enrich` |
| `example_1` … `example_7` | TEXT | up to 7 example slots |
| `audio` | TEXT | |
| `picture` | TEXT | |
| `video` | TEXT | |
| `hints` | TEXT | |
| `system_note_uuid` | TEXT | **durable identity anchor** — survives `anki_note_id` changes; `UNIQUE` |
| `system_hash` | TEXT | content fingerprint, written by `stamp` |
| `source_deck` | TEXT NOT NULL | which deck this row's last `pull` selected it from |
| `sync_status` | TEXT NOT NULL | e.g. `ok`, `error` |
| `sync_issue` | TEXT | populated when `sync_status = 'error'` |
| `last_pulled_at` | TIMESTAMP NOT NULL | |

Identity note: `system_note_uuid` is the durable key `sync` keys lookups on; `anki_note_id` is kept
only as the operational AnkiConnect key for making API calls. See `sync/docs/architecture.md`'s
"Identity" section for the full rationale.

### `note_definition_links`
*Owned exclusively by `sync`. Candidate → confirmed/rejected lifecycle linking `anki_notes` to
`cambridge_definitions`.*

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | autoincrement |
| `system_note_uuid` | TEXT NOT NULL | FK → `anki_notes(system_note_uuid)` |
| `cambridge_definition_id` | INTEGER NOT NULL | FK → `cambridge_definitions(id)` |
| `match_method` | TEXT NOT NULL | e.g. `_exact`, `_contains`, `_pos_sense` — how `match` proposed this pair |
| `status` | TEXT NOT NULL | `candidate` / `confirmed` / `rejected` |
| `created_at` | TIMESTAMP NOT NULL | |
| `confirmed_at` | TIMESTAMP | set when promoted to `confirmed` |

Natural key: `UNIQUE(system_note_uuid, cambridge_definition_id)` — prevents duplicating the same
pair, but a note may have several distinct **confirmed** pairs (a card can cover more than one
definition).

## Views

### `note_candidates`
Denormalized view joining `note_definition_links` (`status = 'candidate'`) across `anki_notes` and
the full `cambridge_*` chain, surfacing both sides of each unresolved candidate match side-by-side
(anki word/translation/definition alongside the Cambridge word/POS/transcription/sense/definition/
CEFR it might match). Defined in `sync/src/db/views.py`; recreated unconditionally (`DROP VIEW` +
`CREATE VIEW`) on every `ensure_schema()` call rather than `CREATE VIEW IF NOT EXISTS`, so its
definition can never silently go stale. Used both for ad hoc DB browsing and as the actual data
source for `sync`'s `confirm --interactive`.

## Changing the schema

Any change to a `cambridge_*` table (new column, rename, merge/split) must be made in **both**
repositories in the same pass:

- `sync/src/db/tables/cambridge/*.py`
- `lexicon-scraper/db/tables/cambridge_*.py` (+ `lexicon-scraper/db/service/cambridge_*.py` if a
  service constructor signature changes)

Verify both `_CREATION_QUERY` strings stay byte-identical afterward. `CREATE TABLE IF NOT EXISTS`
means whichever project runs first against a fresh DB "wins" the schema — if the two copies drift,
the loser writes/reads against a stale schema with no explicit error.

`anki_notes` / `note_definition_links` are exempt from this rule — they belong to `sync` alone.

Update this document alongside any such change — it is the shared reference both projects' own
docs point back to.
