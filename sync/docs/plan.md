# Plan: Anki ⇄ Cambridge Dictionary Sync Tool

## Purpose

A standalone CLI tool, living in this directory (`sync/`), that:

1. Mirrors Anki note data into a local SQLite database (`sync.sqlite`, kept inside this project and git-ignored).
2. Reads Cambridge Dictionary reference data that `lexicon-scraper` — an independent, separately-run tool — writes into that same database, kept in its own tables, fully separate from the Anki mirror.
3. Proposes candidate links between Anki notes and Cambridge reference entries, and lets those candidates be confirmed (manually, or automatically when unambiguous).
4. Enriches existing Anki notes with a small, explicitly whitelisted, extensible set of DB-derived fields (starting with `cefr`, with more fields to be added later) — never touching the content fields a human already owns in Anki (`word`, `definition`, `part_of_speech`, `examples`, etc.).

Anki is authoritative for its own content. The DB mirrors it for reference and enriches only what it's explicitly allowed to. This tool never creates new Anki notes, never runs automatically/on a schedule, and does not expose an MCP server — it is a manually-invoked CLI, full stop. See `architecture.md` for the full schema and command reference.

## Why this shape

- Anki notes already have two hidden, empty fields — `_system_hash` and `_system_note_uuid` — provisioned on the note type but not yet used anywhere. **`_system_note_uuid` was deliberately added as a stable identity anchor, specifically so this tool would not have to depend on Anki's own internal note id** for long-term identity (that id is only guaranteed stable for addressing a note *right now* via AnkiConnect — it isn't a durable cross-time/cross-import key). This plan is built around filling `_system_note_uuid`/`_system_hash` in as a first, DB-independent step, and treating the uuid — not the Anki note id — as the true long-term anchor once it exists.
- **Notes are not deck-scoped in Anki — cards are.** The same underlying note appears in multiple sibling decks (`1_english::without_group::definition`, `::typing`, `::word`, `::typing_sentence`) simultaneously, each showing a different card template over the same note data (verified live: the three "thick" notes appear identically in `definition`, `typing`, and `word`). A deck is only used here as a convenient way to select a set of notes via AnkiConnect's search — it is not a stable attribute of the note itself.
- Cambridge data was only ever partially imported into Anki, and Anki notes have since been hand-edited independently — `word`, `definition`, `part_of_speech`, and `examples` can all legitimately change inside Anki over time. **Transcription (pronunciation) is much less likely to change than definition/sense text**, so it's used as the primary key for proposing Anki↔Cambridge candidate links, and those candidates don't need re-checking on every sync cycle the way a definition-text match would. Because even transcription-based matching isn't a guaranteed 1:1 (one transcription can cover multiple senses), matches are always proposed as *candidates* first, promoted to a confirmed link only explicitly (manually, or automatically only when a note has exactly one unambiguous candidate).
- `lexicon-scraper` populates the Cambridge reference tables directly and independently — it is not invoked by this tool's CLI. This project only defines and reads that schema.
- The user will keep adding new notes to Anki over time via their own import process (outside this tool). This plan includes an explicit discovery step for notes that show up without `_system_hash`/`_system_note_uuid` yet, so they can be found, stamped, and pulled in a controlled, separate pass rather than assumed away.
- The existing codebase (`addons/grammar_drill/src/db/`) has an established hand-rolled SQLite convention (`Database` / `Table` / `Service`, no ORM) for the DB layer, and an established AnkiConnect access pattern (`mcp/src/anki_client.py`) — this tool follows both. Configuration follows the plain-`pydantic.BaseModel` + `python-dotenv` pattern used in the user's own `autotest_api/src/config/load_env.py` (a manual `os.environ.get(...)` → `BaseModel` builder function, not `pydantic-settings`).

## Phases

### Phase 1 — Project scaffolding

- `pyproject.toml`, `Makefile`, `requirements.txt`, `.env`, `.gitignore` (must include `sync.sqlite`, `.env`, `venv/`, `__pycache__/`).
- `main.py` as a `typer` CLI entry point.
- `src/config/load_env.py`: `load_dotenv()` at import time, a plain `pydantic.BaseModel` config class, and a `get_config()` builder function reading `os.environ.get(...)` explicitly — mirroring the user's existing `autotest_api` config pattern, not `pydantic-settings`.
- A shared logger (file + stdout) used by every command for both discrete action logs and batch-progress reporting (see Phase 8).

### Phase 2 — DB layer

- `src/db/database.py`: `Database` class wrapping `sqlite3` (`execute`/`query`, idempotent `create_tables`) — same pattern as `grammar_drill`.
- `src/db/tables/_table.py`: base `Table` class.
- Table classes for the Anki mirror (`anki_notes`) and the Cambridge reference tables (`cambridge_words`, `cambridge_parts_of_speech`, `cambridge_transcriptions`, `cambridge_senses`, `cambridge_definitions`, `cambridge_examples`), plus `note_definition_links`. This tool creates and owns all of this schema, including the `cambridge_*` tables — `lexicon-scraper` writes into them but the schema itself is defined here.
- Corresponding `Service` classes. Note: unlike `grammar_drill`'s `WordService` (which does get-or-create by matching content fields), `anki_notes` is looked up primarily by `system_note_uuid` once one exists (the durable anchor), falling back to `anki_note_id` — never by matching on `word`/`definition`/`part_of_speech`/`examples`, since those fields can legitimately change inside Anki.

### Phase 3 — Anki access

- `src/anki_client.py`: same `invoke(action, **params)` contract as `mcp/src/anki_client.py`, duplicated here so `sync/` stays self-contained.
- `src/anki/notes.py`: `get_notes(deck)`, `get_notes_fields(ids)`, `update_note_fields(id, fields)`, plus a helper to search for notes with an empty `_system_note_uuid` field (AnkiConnect's empty-field search syntax) for Phase 4.

### Phase 4 — `discover-new` (read-only, finds freshly-imported notes)

- The user will keep importing new notes into Anki over time, outside this tool. New notes won't have `_system_hash`/`_system_note_uuid` yet.
- `discover-new [--deck NAME]` searches the selection deck for notes with an empty `_system_note_uuid`, and reports them (count + note id + word) — no writes. This is purely a visibility step before running `stamp`.

### Phase 5 — `stamp` (Anki → Anki, no DB involved)

Runs **before** any DB population, and is naturally safe to re-run over an entire deck at any time (including after new notes are discovered):
- Compute the content hash from the note's freshly-fetched live fields (not from any DB mirror).
- Mint a `system_note_uuid` only if currently empty (unless `--force`) — this is the anchor value, generated once and never regenerated afterward except by explicit force.
- Write both `_system_hash` and `_system_note_uuid` back via `update_note_fields`, skipping a field that's already non-empty unless `--force`.
- Supports `--dry-run` to preview the write count first — expect this to touch the entire selected note set on the very first run, and just the newly-discovered subset on later runs.

### Phase 6 — `pull` (Anki → DB, resilient per-note upsert)

- Fetch all notes for the selection deck (now stamped).
- Process **one note at a time**, not a blanket delete-and-reinsert. Look up the existing mirror row primarily by `system_note_uuid` (so a note keeps its identity even if its `anki_note_id` were ever to change) falling back to `anki_note_id` for the rare case a uuid isn't present. A problem with one note (missing/unexpected data) must not abort the whole run — record that note's row with a `sync_status='error'` and a human-readable `sync_issue` message, log it, and continue.
- **Review step**: before committing each changed row, show a before/after diff (which fields changed, old → new) for confirmation. Skippable via `--skip-review` or the `REQUIRE_REVIEW=false` config flag, in which case changes apply without pausing.
- Logs and prints progress for batch runs: `[current/total] (percent%) — note <id>: created / updated / unchanged / error`, plus a final summary count.

### Phase 7 — Cambridge data (external, out of scope for this tool's code)

- `lexicon-scraper` runs independently and writes directly into this project's `cambridge_*` tables (schema defined in Phase 2). This project does not own an import command and does not call `lexicon-scraper` itself.

### Phase 8 — `match` / `confirm` / `review`

- `match`: proposes **candidate** links between `anki_notes` and `cambridge_definitions`, keyed on `(word, transcription, transcription_type)` — chosen because transcription rarely changes even when definition/sense text is hand-edited. A single transcription can still cover multiple senses, so this reliably produces zero, one, or several candidates per note, never a guaranteed single match. Safe and cheap to re-run; only needs to run again when new notes are discovered/stamped or new Cambridge words are imported — not on every `pull`.
- `confirm`: promotes a specific candidate to the actual link used by enrichment — either named explicitly (`--note ID --definition ID`) or automatically for any note that currently has exactly one non-rejected candidate (`--auto-single`). At most one confirmed link exists per note at a time.
- `review`: read-only report of notes with zero candidates, notes with multiple unresolved candidates awaiting `confirm`, and any `sync_status='error'` rows from the last `pull`.

### Phase 9 — `enrich` (DB → Anki, whitelisted and extensible)

- Writes a small, explicit set of fields from DB-derived data, sourced only from **confirmed** links. **Only `cefr` today**, written only if Anki's `cefr` is currently empty — built as an extensible registry of (field name → value resolver) so more fields can be added later without redesigning the command.
- Re-fetches live Anki values immediately before writing each field (guards against a concurrent hand-edit since the last `pull`).
- Same review/diff and skip-review behavior as `pull` (Phase 6), the same non-empty guard (`--force` to override), and the same progress logging.

## Out of scope (permanently, not just "for now")

- Creating new Anki notes from Cambridge data or anything else — this tool never calls `addNote`.
- Automatic or scheduled runs of any kind — this is a manually-invoked CLI only.
- An MCP server for this project — not planned at all, now or later.
- Any Cambridge-import code living in this project — that's `lexicon-scraper`'s responsibility, run independently.
- Deck-based partitioning of note identity — notes aren't deck-scoped, so `anki_notes` is anchored on `system_note_uuid`/`anki_note_id`; deck is only a selection mechanism.

## New-note workflow (recap)

External bulk import into Anki (by the user, outside this tool) → `discover-new` (see what's new) → `stamp` (write hash/uuid for the new notes; safe to run broadly) → `pull` (mirror them into the DB) → `match` (propose candidates for the new notes) → `confirm` → `enrich`.

## Verification

- `discover-new` immediately after a fresh Anki import lists exactly the newly-imported notes and nothing already stamped.
- `stamp --dry-run` on the `definition` selection deck reports one planned write per note on the very first run (both fields empty) and, on a later run after a fresh import, reports writes only for the newly-discovered notes.
- `stamp` followed by `pull` shows every mirrored note already carrying a non-empty `system_hash`/`system_note_uuid`.
- Running `pull` twice in a row with no Anki changes in between reports zero diffs and zero errors.
- Deliberately editing a note's `definition` in Anki, then running `pull`, surfaces a visible before/after diff for exactly that field — but a previously **confirmed** Cambridge link for that note remains valid (transcription didn't change), so `enrich` still works without needing `match`/`confirm` to be re-run.
- `match` on a word whose Cambridge entry has one transcription covering three senses produces three candidate rows for the corresponding note(s); `confirm --auto-single` only resolves the ones that map 1:1, leaving the rest for manual review.
- `enrich --dry-run` reports a planned `cefr` write only for notes with an empty `cefr` and a **confirmed** (not just candidate) Cambridge link.
- Deleting/corrupting one note's fields (simulated) during `pull` does not abort the batch — the run completes, that note is marked `sync_status='error'`, and the rest of the notes are processed normally.
