# `data/english/`

Shared SQLite database for the English vocabulary pipeline, used by both the `sync` and
`lexicon-scraper` projects (siblings under this `anki/` superproject). Lives here — outside either
project — because both write to it directly, as two independent git repos.

- `sync.sqlite` — the live database. Git-ignored, never committed.
- `backups/sync.sqlite.bak-*` — timestamped backups taken before risky schema changes.
- `docs/schema.md` — **source of truth** for the schema: tables, columns, foreign keys, views, and
  which project owns which tables. Read this before writing any code that touches the DB from a new
  or existing mini-project.
