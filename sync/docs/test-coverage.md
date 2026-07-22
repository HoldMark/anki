# Test coverage — what's verified and how

This file exists because two very different kinds of "tested" are mixed together in this
project, and it matters which one applies to a given command:

1. **Verified live** — actually run against the real Anki collection and/or the real
   `data/sync.sqlite`, by a human approving each real run.
2. **Verified by the automated test suite only** (`tests/`, run with `venv/bin/pytest`) —
   correct against synthetic/hand-seeded data on a disposable scratch DB, with a fake
   in-memory AnkiConnect standing in for the real one. No real Anki call, no real DB write.

The second kind is real coverage of the logic, but it is **not** the same as "this has been
seen to work on real Cambridge data" — because no real Cambridge data exists in this project
yet (`lexicon-scraper` hasn't been run against `data/sync.sqlite`). Every `match`/`confirm`/
`review`/`enrich` test uses definitions, senses, and transcriptions typed in by hand in the
test file itself.

## Per command

| command | automated tests | verified live | notes |
|---|---|---|---|
| `discover-new` | yes (`test_anki_notes.py`, `test_cli.py`) | **yes** | Ran for real against `1_english::without_group::definition`; read-only, no writes ever. |
| `stamp` | yes (`test_stamp.py`) — creation, skip-if-stamped, `--force`, `--dry-run`, per-note error isolation | **yes** | User ran the real (non-dry-run) `stamp`; confirmed live afterward: 0 notes missing `_system_note_uuid`. |
| `pull` | yes (`test_pull.py`) — create/update/unchanged, hand-edit diff detection, hash-drift tolerance, `--skip-review`/`REQUIRE_REVIEW` bypass, per-note error isolation | **yes** | Ran for real with `--skip-review`: `created=1699, error=0`; re-run confirmed `unchanged=1699, error=0`. The interactive review *prompt* itself (`REQUIRE_REVIEW=true`, no `--skip-review`) is only exercised by the test suite (mocked `input()`), not in a live run yet — reviewing ~1699 individual prompts wasn't practical for the first pull. |
| `match` | yes (`test_match.py`) — one-transcription/three-senses candidate fan-out (the exact scenario from `plan.md`'s verification list), no-match cases, idempotent re-run | **no** | `cambridge_*` tables are empty in the real DB — nothing to match against yet. All coverage is against hand-seeded synthetic Cambridge rows. |
| `confirm` | yes (`test_confirm.py`) — manual pairing, `--auto-single` resolving only unambiguous notes, unknown-pair rejection | **no** | Same reason as `match` — no real candidates exist to confirm yet. |
| `review` | yes (`test_review.py`) — zero-candidates, multi-candidates, pull-errors reporting | **no** (partially) | The `pull_errors` part of the report *could* be checked against the real DB today (it's currently empty, 0 errors, nothing interesting to show) — but zero/multi-candidates depend on `match` having run against real data first. |
| `enrich` | yes (`test_enrich.py`) — writes when empty, non-empty guard, `--force`, `--dry-run`, no-confirmed-link skip, missing-cefr-value case, per-note error isolation | **no** | Depends on `match`/`confirm` producing real confirmed links first, which depends on real Cambridge data. **`enrich` writes to the real Anki collection — do not run it for real until `match`/`confirm` have been exercised against real Cambridge data and reviewed.** |

## What this means practically

- `discover-new`, `stamp`, `pull` are trustworthy in the "seen it work for real" sense — go
  ahead and use them.
- `match`, `confirm`, `review`, `enrich` are trustworthy in the "logic is correct against every
  case I could think to construct" sense, but **have never touched a real Cambridge definition
  or written a real `cefr` value to Anki**. Once `lexicon-scraper` populates `cambridge_*` in
  `data/sync.sqlite`, these should be run cautiously and reviewed (dry-run/review mode first,
  same as `stamp`/`pull` were) before being trusted the same way.

## Running the suite

```
venv/bin/pytest          # from sync/
venv/bin/pytest -q       # quieter output
```

No prerequisites — the suite never requires Anki to be running and never touches
`data/sync.sqlite`; every test gets its own throwaway DB file (see `tests/conftest.py`).
