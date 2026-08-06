# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make lint       # ruff linter (auto-fix) + formatter
make linter     # ruff linter only (--fix)
make formater   # ruff formatter only
make commit     # run pre-commit hooks on all files
```

Linter config: `pyproject.toml` — line length 120, Python 3.13, ruff rules E/W/F/I/B/UP/N. `cards_view/`, `lexicon-scraper/`, `data/` excluded from linting.

## Architecture

The project is a collection of **Anki addons** (plugins for the Anki spaced-repetition app, v25.9.2). Addons are loaded by Anki at startup from the `addons21/` folder in the user's Anki profile — each addon is a Python package with `__init__.py` as entry point.

### Addon: `error_freeze`

Hooks into `reviewer_will_answer_card` to freeze the rating buttons for a configurable duration when the user types a wrong answer on a `{{type:FieldName}}` card. After the freeze the user picks the rating themselves. Configurable per-deck via Anki's addon config system (`config.json` → `"decks": [...]`; empty list = all decks). Also hooks `reviewer_did_show_question` to reset state between cards.

### Addon: `review_grammar`

AI-powered grammar task system. Two flows communicated over the Anki webview JS bridge (`webview_did_receive_js_message`):

1. **`task_for_card_with_eng_word`** — `create_task.py` generates a grammar task (tense, sentence type, pronouns) using a daily seed for deterministic-per-word randomness. Returns a task with an Obsidian link.
2. **`check grammar and other`** — `review_task.py` submits the user's sentence to the **Google Gemini API** (`src/llm/gemini.py`) and returns structured feedback (correctness, errors, suggestions).

Persistence: SQLite via a hand-rolled table layer in `src/db/`. Config via env vars loaded by `src/config/`.

### Other directories

- `lexicon-scraper/` — BeautifulSoup scraper for Cambridge Dictionary, used to populate card content.
- `cards_view/` — Jinja-style card templates for English and Georgian decks.
- `sandbox/` — throwaway scripts, not part of any addon.

## Working with cards_view

Keep code comments in `cards_view/` short (what, not why/history). Put longer rationale, gotchas, and other useful background in `cards_view/docs/notes.md` (gitignored, local-only) instead.

## Commits across submodules

This repo's `addons/*`, `pdf2text/`, `lexicon-scraper/`, `mcp/`, and `sync/` are git submodules,
each with their own history. When a requested commit touches files inside one or more of these
submodules: commit inside each affected submodule first, then commit the resulting submodule
pointer bump(s) in this parent repo — all as part of the same request, without stopping to ask
the user again before the parent-level commit. Only pause and ask first if a submodule's changes
are ambiguous or unrelated to what was asked.
