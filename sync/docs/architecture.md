# Architecture: Anki ⇄ Cambridge Dictionary Sync Tool

## Overview

```
   external, by the user            (independent, separate tool — not invoked from here)
 ┌─────────────────────┐               ┌───────────────────────────────┐
 │ bulk import of new   │               │  lexicon-scraper/             │
 │ notes into Anki       │               │  writes cambridge_* tables    │
 │ (not this tool)       │               │  directly into sync.sqlite    │
 └──────────┬───────────┘               └───────────────┬───────────────┘
            │                                            │ writes
            ▼                                            ▼
 ┌─────────────────────────────────────┐   ┌───────────────────────────────────────┐
 │  Anki, via AnkiConnect               │   │           sync/sync.sqlite            │
 │  (addons/anki_connect)               │   │           (git-ignored)               │
 │  notes selected via any sibling deck │   │                                        │
 │  under 1_english::without_group::    │   │  cambridge_words ─▶ parts_of_speech ─▶ │
 │  definition/typing/word/typing_sent. │   │    transcriptions                      │
 │  — SAME notes, different templates.  │   │  parts_of_speech ─▶ senses ─▶          │
 │  Notes aren't deck-scoped; cards are.│   │    definitions ─▶ examples             │
 └──────────┬───────────▲───────────────┘   │                                        │
            │           │                    │  note_definition_links (candidate/    │
   ⓪ discover-new│      │③ enrich (whitelisted,│   confirmed/rejected)                 │
   (read-only)   │① stamp│  extensible fields)│                                       │
            │    (Anki→ │                    │  anki_notes (system_note_uuid = the   │
            │     Anki, │                    │   durable anchor; anki_note_id is     │
            │     no DB)│                    │   the operational AnkiConnect key)    │
            └───────────┘◀──────────────────────────────────┘
                          ② pull (per-note upsert, resilient, reviewable)
```

Order of operations: **⓪ `discover-new`** (read-only) finds notes imported by the user that have no `_system_note_uuid` yet. **① `stamp`** (Anki → Anki, no DB) then mints `_system_note_uuid`/`_system_hash` for those notes directly — this is what makes them non-empty in the first place, and it's what the whole design anchors identity on (see "Identity" below). Only then does **② `pull`** (Anki → DB) mirror notes in. `lexicon-scraper` fills the Cambridge tables independently, at any time, out of band. **③ `enrich`** (DB → Anki) is deliberately narrow and extensible — today it writes only `cefr`, sourced only from a **confirmed** Cambridge link, guarded, and re-fetches live values before writing.

This tool never creates Anki notes, never runs on a schedule, and has no MCP server — these are permanent exclusions, not deferred features.

## Directory layout

```
sync/
  pyproject.toml, Makefile, requirements.txt, .env, .gitignore
  main.py                        # typer CLI entry point
  docs/
    plan.md, architecture.md, plan.ru.md, architecture.ru.md
  src/
    config/load_env.py           # load_dotenv() + plain pydantic.BaseModel + get_config(), same pattern as
                                  # the user's autotest_api/src/config/load_env.py (no pydantic-settings)
    utils/path.py                # ROOT_PATH: walk up to pyproject.toml
    utils/hashing.py             # compute_content_hash(fields: dict) -> str
    utils/logging.py             # shared logger: file + stdout, batch-progress helper
    anki_client.py                 # invoke(action, **params) — same contract as mcp/src/anki_client.py
    anki/
      notes.py                    # get_notes(deck), get_notes_fields(ids), update_note_fields(id, fields),
                                   # get_notes_missing_uuid(deck) — empty-field search for discover-new
    db/
      database.py                 # Database: sqlite3 wrapper (execute/query/create_tables)
      tables/
        _table.py                  # base Table class
        anki_notes.py
        note_definition_links.py
        cambridge/                   # every cambridge_* table, split out from the rest for readability
          cambridge_words.py
          cambridge_parts_of_speech.py
          cambridge_transcriptions.py
          cambridge_senses.py
          cambridge_definitions.py
          cambridge_examples.py
      service/
        anki_note.py                 # lookup by system_note_uuid first, anki_note_id fallback — see "Identity"
        note_definition_link.py      # candidate/confirmed/rejected lifecycle
        cambridge/                    # mirrors tables/cambridge/ — one service per cambridge_* table
          cambridge_word.py
          cambridge_part_of_speech.py
          cambridge_transcription.py
          cambridge_sense.py
          cambridge_definition.py
    sync/
      discover_new.py                # ⓪ Anki search, read-only
      stamp.py                       # ① Anki → Anki
      pull.py                        # ② Anki → DB
      match.py                       # proposes candidates (word, transcription, transcription_type)
      confirm.py                     # promotes a candidate to confirmed
      enrich.py                      # ③ DB → Anki
      diff.py                        # shared before/after review helper, used by pull + enrich
```

No `cambridge_import/` module exists in this project — `lexicon-scraper` is responsible for populating the `cambridge_*` tables directly; this codebase only defines and reads that schema.

Follows the `Database` / `Table` / `Service` split used in `addons/grammar_drill/src/db/`: no ORM, raw SQL as class-level string constants, `Database.execute`/`.query` returning `None` on error. `anki_client.py` is a literal copy of `mcp/src/anki_client.py`'s `invoke()` contract, kept standalone rather than cross-imported.

## Identity: `system_note_uuid` is the anchor, `anki_note_id` is operational

`_system_note_uuid` was added to the note type specifically so this tool would not have to depend on Anki's own internal note id as the durable identity. `anki_note_id` is still required operationally — every AnkiConnect call (`findNotes`, `notesInfo`, `updateNoteFields`) addresses notes by it — but it is not treated as the long-term anchor: `pull` looks up an existing `anki_notes` row primarily by `system_note_uuid` when the note already has one, falling back to `anki_note_id` only for notes that haven't been stamped yet. This means a note's continuity survives even if its `anki_note_id` were ever to change (e.g. collection re-import), as long as its `system_note_uuid` is preserved.

Separately, `word`, `definition`, `part_of_speech`, and `examples` can all legitimately change inside Anki after the fact (hand-editing is expected and normal). Unlike `grammar_drill`'s `WordsTable`, which does get-or-create by matching `(word, definition, pos)` as a natural key, `anki_notes` must **never** re-derive or look up a row by content equality — identity comes only from `system_note_uuid`/`anki_note_id`, never from field values.

## Deck scoping is a selection mechanism, not an identity

Notes are not deck-scoped in Anki — cards are. Verified live: the same three note ids appear identically when searching `1_english::without_group::definition`, `::typing`, and `::word` — they're the same underlying notes, rendered through different card templates in different sibling decks. A `--deck` flag on `discover-new`/`stamp`/`pull`/`match` is only a convenient way to select a set of notes via AnkiConnect's `findNotes` search; `anki_notes.source_deck` records which deck was last used to find a note, for provenance/debugging, but it is not a unique or authoritative attribute.

## Schema

### Anki mirror — `anki_notes`

One row per Anki note, upserted individually by `pull` — never a blanket delete-and-reinsert, so a problem with one note can't take down the whole run.

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | |
| `anki_note_id` | INTEGER, UNIQUE NOT NULL | Anki's own note id — required for AnkiConnect calls, not the durable anchor |
| `word`, `trans`, `trans_type`, `part_of_speech`, `sense`, `definition`, `cefr` | TEXT | |
| `example_1` … `example_7` | TEXT | |
| `audio`, `picture`, `video`, `hints` | TEXT | |
| `system_note_uuid` | TEXT, UNIQUE, NULL | mirrors `_system_note_uuid`; minted by `stamp`; **this is the durable identity anchor**, not `anki_note_id` |
| `system_hash` | TEXT, NULL | mirrors `_system_hash` as last read from Anki |
| `source_deck` | TEXT NOT NULL | deck used to select this note during the last pull — provenance only, see above |
| `sync_status` | TEXT | `ok` / `error` — set by `pull` per note |
| `sync_issue` | TEXT, NULL | human-readable description when `sync_status='error'` |
| `last_pulled_at` | TIMESTAMP NOT NULL | |

Column order groups human-owned content fields (`word` through `hints`) together, followed by the sync-machinery fields (`system_note_uuid` through `last_pulled_at`) — purely for readability when browsing the table directly; no code depends on column order (`Database.execute`/`.query` bind by name via `:param` placeholders, never positionally).

### Cambridge reference — normalized, prefix `cambridge_`, populated externally by `lexicon-scraper`

Mirrors `lexicon-scraper`'s pydantic shape (`Word → PartOfSpeech → Transcription` and `PartOfSpeech → Sense → Definition → Example`). Never written by `discover-new`, `stamp`, `pull`, or `enrich` — this project only defines the schema and reads from it.

| table | columns | uniqueness |
|---|---|---|
| `cambridge_words` | `id PK, word, imported_at` | `UNIQUE(word)` |
| `cambridge_parts_of_speech` | `id PK, word_id FK, name` | `UNIQUE(word_id, name)` |
| `cambridge_transcriptions` | `id PK, part_of_speech_id FK, transcription, transcription_type` | `UNIQUE(part_of_speech_id, transcription_type)` |
| `cambridge_senses` | `id PK, part_of_speech_id FK, text` | `UNIQUE(part_of_speech_id, text)` |
| `cambridge_definitions` | `id PK, sense_id FK, text NOT NULL, cefr` | `UNIQUE(sense_id, text)` |
| `cambridge_examples` | `id PK, definition_id FK, text` | — |

### Link table — `note_definition_links` (candidate → confirmed lifecycle)

A note can have **multiple candidate rows** (one transcription can cover several senses/definitions), so `anki_note_id` is **not** unique here — only the pair is.

| column | type | notes |
|---|---|---|
| `id` | INTEGER PK | |
| `anki_note_id` | INTEGER NOT NULL | FK to `anki_notes.anki_note_id`; not unique alone |
| `cambridge_definition_id` | INTEGER NOT NULL | FK |
| `match_method` | TEXT | `word_transcription` / `manual` |
| `status` | TEXT | `candidate` / `confirmed` / `rejected` |
| `created_at` | TIMESTAMP | |
| `confirmed_at` | TIMESTAMP, NULL | |

`UNIQUE(anki_note_id, cambridge_definition_id)` prevents duplicate candidate rows for the same pair. At most one `confirmed` row per note is enforced with a partial unique index: `CREATE UNIQUE INDEX ... ON note_definition_links(anki_note_id) WHERE status='confirmed'`. Only `confirmed` rows are read by `enrich`.

## Matching strategy: candidates first, confirmation second

`match` proposes candidates keyed on `(word, transcription, transcription_type)` rather than `definition`/`sense` text, because transcription (pronunciation) rarely changes even when Anki notes are hand-edited, while `definition`/`sense`/`part_of_speech` text legitimately does. This has two consequences:

1. A confirmed link, once established, **does not need re-verification on every sync** — it stays valid even if the note's `definition`/`sense` text later drifts, since the match was never based on that text in the first place.
2. Because one transcription can still legitimately cover several senses, `match` cannot promise a single result — it always produces zero, one, or several **candidate** rows per note. Promotion to a trusted, `enrich`-usable link is a separate, explicit step (`confirm`), either named manually (`--note ID --definition ID`) or automatic only for the unambiguous case (`--auto-single`, when a note currently has exactly one non-rejected candidate).

`match` only needs to be (re-)run when new notes are discovered/stamped or new Cambridge words are imported — not on every `pull`.

## CLI commands

Built with `typer`.

| command | direction | effect |
|---|---|---|
| `discover-new [--deck NAME]` | read-only | Searches Anki for notes with an empty `_system_note_uuid` (freshly imported by the user, outside this tool) and reports them. No writes. |
| `stamp [--deck NAME] [--force] [--dry-run]` | Anki → Anki | No DB read/write. Computes the content hash from freshly-fetched live fields and mints a uuid if empty; writes both `_system_hash`/`_system_note_uuid` back, skipping non-empty fields unless `--force`. Safe to re-run broadly at any time — only touches unstamped notes. |
| `pull [--deck NAME] [--skip-review]` | Anki → DB | Per-note upsert into `anki_notes`, looked up by `system_note_uuid` first, `anki_note_id` fallback. Shows a before/after diff per changed note for confirmation unless `--skip-review` or `REQUIRE_REVIEW=false`. A problem with one note is recorded as `sync_status='error'` with a message in `sync_issue`, logged, and does not abort the run. Prints `[i/total] (pct%)` progress and a final summary. |
| *(external)* `lexicon-scraper` | lexicon-scraper → DB | Not part of this CLI. Writes directly into `cambridge_*` tables, run independently. |
| `match [--deck NAME]` | DB internal | Proposes `candidate` links between `anki_notes` and `cambridge_definitions` via `(word, transcription, transcription_type)`. Safe/cheap to re-run; no need to run on every sync. |
| `confirm [--note ID --definition ID \| --auto-single]` | DB internal | Promotes a `candidate` to `confirmed` (manual pair, or automatically when exactly one unambiguous candidate exists for a note). |
| `review` | read-only | Lists notes with zero candidates, notes with multiple unresolved candidates, and any `sync_status='error'` notes from the last `pull`. |
| `enrich [--force] [--dry-run] [--skip-review]` | DB → Anki | Writes an extensible, explicit whitelist of fields — currently just `cefr` — sourced only from **`confirmed`** links, only if empty in Anki. Re-fetches live values immediately before writing. Same diff/review and progress behavior as `pull`. |

The enrich whitelist is implemented as a small registry (field name → resolver function) rather than inline logic, so adding a new DB-derived field later (beyond `cefr`) doesn't require redesigning the command — only registering a new resolver.

## Content-hash design

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

Fields are concatenated directly (no delimiter) but each empty/`None` value is first replaced with a fixed placeholder (`"∅"`) so that two different splits between adjacent fields can't silently collide into the same raw string. Excludes `_system_hash`/`_system_note_uuid` themselves (self-referential) and Anki metadata (note id, mod time) — only human-owned content is hashed.

- First populated by `stamp`, computed directly from live-fetched Anki fields (no DB involved yet at that point).
- Recomputed read-only during `pull` and compared against the note's current `_system_hash` to flag drift — "this note was hand-edited since it was last stamped" — without writing anything.

## Logging & progress

A shared logger (file + stdout) is used by every command. For batch operations (`discover-new`, `stamp`, `pull`, `match`, `enrich`):
- Each note logs a one-line outcome: `[i/total] (pct%) note <anki_note_id>: created | updated | unchanged | skipped | error — <detail>`.
- A final summary line: total processed, created, updated, unchanged, skipped, errored.
- Errors are logged with enough detail to diagnose (note id, field, exception) but never abort the batch.

## Configuration

Plain `pydantic.BaseModel` + `python-dotenv`, following the exact pattern of the user's own `autotest_api/src/config/load_env.py`: `load_dotenv()` called at import time, a `BaseModel` config class, and a `get_config()` function that explicitly maps `os.environ.get(...)` calls into it — **not** `pydantic-settings`.

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

| setting | default |
|---|---|
| `ANKI_CONNECT_URL` | `http://127.0.0.1:8765` |
| `DB_PATH` | `sync.sqlite` inside this project (`sync/`), git-ignored |
| `DECK_NAME` | `1_english::without_group::definition` (any sibling deck works equally — see "Deck scoping" above) |
| `REQUIRE_REVIEW` | `true` — set `false` (or pass `--skip-review`) to apply `pull`/`enrich` changes without an interactive diff |

`lexicon-scraper`'s own configuration (how it points at `DB_PATH`) is out of scope here — that's an integration detail for `lexicon-scraper` itself to define when it's extended to write these tables.

## New-note workflow

The user will keep adding new notes to Anki over time via their own import process (outside this tool). This is handled as an explicit, separate pass rather than assumed away:

```
external bulk import (by user) → discover-new (read-only) → stamp (writes hash/uuid
  for the new notes) → pull (mirrors them into the DB) → match (candidates for the
  new notes) → confirm → enrich
```

`stamp` is safe to run broadly at any time (it only touches notes still missing a uuid/hash), so in practice `discover-new` exists mainly for visibility before committing to a `stamp` run, not because `stamp` itself needs to be scoped narrowly.

## Risks / edge cases

- **First `stamp` run**: every existing note currently has empty uuid/hash, so it touches the entire selected note set at once. Run `--dry-run` first.
- **Ambiguous Cambridge candidates**: one transcription can legitimately cover several senses — never auto-confirmed beyond the unambiguous case; surfaced via `review` for manual `confirm`.
- **`anki_note_id` instability**: if it ever changes for a note that already has a `system_note_uuid` (e.g. after a collection re-import), `pull` must recognize the note by its uuid and update the existing row rather than create a duplicate.
- **Per-note failure isolation**: `pull` must never abort on one bad note — the whole point of `sync_status`/`sync_issue` is to let the rest of the batch complete and surface exactly which notes need attention, via `review`.
- **Concurrent edits during `enrich`**: guarded by re-fetching live Anki fields immediately before writing `cefr` (or any future enriched field), skipping if already non-empty unless `--force`.
- **Cross-deck duplication**: since the same note can be found via multiple sibling decks, `pull`/`stamp` runs against different `--deck` values must not create duplicate `anki_notes` rows — enforced by the `system_note_uuid`/`anki_note_id` uniqueness, not by deck.
- **`lexicon-scraper` integration boundary**: this project defines the `cambridge_*` schema; making `lexicon-scraper` actually write into `sync.sqlite` is separate, future work outside this codebase.
- **DB file location**: `sync.sqlite` lives inside `sync/` and must be listed in `.gitignore` alongside `.env`, `venv/`, and `__pycache__/`.
