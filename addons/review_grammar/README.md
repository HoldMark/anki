# review_grammar

Anki addon (v25.9.2) that generates English grammar tasks for vocabulary cards and checks them with Google Gemini AI.

## What it does

For each card with an English word, the addon:
1. **Generates a task** — picks a random tense, sentence type / usage, and pronoun. The combination is deterministic per word + date (same task all day, different tomorrow).
2. **Checks the answer** — sends the user's sentence to Gemini and returns structured feedback: grammar correctness, errors, style suggestions, and whether the word, part of speech, definition, tense, and pronoun are used correctly.

## Setup

### 1. API key

Create `.env` in the addon root:

```
goog-api-key=YOUR_GOOGLE_API_KEY
```

Get a key at [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. pyproject.toml

The addon expects `pyproject.toml` in the addon root (used for logger config):

```toml
[tool.logging.default]
format    = "{asctime} [{levelname}] {name}: {message}"
datefmt   = "%Y-%m-%d %H:%M:%S"
style     = "{"
stream    = "1"
request_headers  = "0"
response_headers = "0"
```

## Models & fallback

The addon tries models in order and automatically switches on a 429 rate-limit response:

| Priority | Model |
|---|---|
| 1 | `gemini-2.5-flash` |
| 2 | `gemini-2.5-flash-lite` |
| 3 | `gemini-2.0-flash` |

The switch is permanent for the session. If all models are exhausted, `{"result": "Rate limit exceeded"}` is returned to the JS side.

## JS integration

The addon communicates with Anki's webview via `pycmd` / `context.web.eval`:

| JS → Python (action) | Python → JS (callback) |
|---|---|
| `task_for_card_with_eng_word` | `receiveTask(result)` |
| `check grammar and other` | `receiveReviewResponse(result)` |

Error responses always contain a `result` key (`"Error"` or `"Rate limit exceeded"`). A successful review response has no `result` key and contains fields like `grammar_correctness`, `is_word`, `errors_with_grammar`, etc.

## Project structure

```
review_grammar/
├── __init__.py                        # entry point, hooks into webview_did_receive_js_message
├── .env                               # API key (not committed)
├── request-task-from-python.js        # JS: request task generation
├── request-task-review-to-python.js   # JS: send answer for review, render result
└── src/
    ├── core/
    │   ├── create_task.py             # task generation logic
    │   └── review_task.py             # review orchestration
    ├── llm/
    │   └── gemini.py                  # Gemini API client with model fallback
    ├── data/
    │   ├── models.py                  # ReviewResponseModel schema
    │   ├── prompts.py                 # system prompt for Gemini
    │   ├── english_data.py            # tenses, pronouns, sentence types with weights
    │   ├── parse_data.py              # DataToReview input parser
    │   └── base_request_data.py       # Gemini request builder
    ├── db/
    │   ├── database.py                # SQLite wrapper
    │   ├── db_writer.py               # write review results
    │   ├── tables/                    # table definitions (words, reviews, conditions)
    │   └── service/                   # query helpers per table
    ├── config/
    │   ├── read_env.py                # loads .env, exposes GOOGLE_API_KEY
    │   └── config_loader.py           # loads pyproject.toml logger config
    └── utils/
        ├── path.py                    # ROOT_PATH, LOGS_PATH
        └── logs/                      # logger, request/response logging decorators
```
