# Walkthrough — read this when you're back

This is the guided tour of what got built while you were out. Nothing here is
published; everything is local and committed to git. Tests pass, lint passes.

---

## 1. The big picture

The program is a **pipeline** — data moves through stages, one direction:

```
RSS feeds  ->  fetch  ->  [SQLite: articles]  ->  classify (LLM)  ->  score (rules)  ->  [SQLite: assessments]  ->  report (LLM)
```

Each stage is a small function. `pipeline.py` calls them in order. `cli.py` and
`api.py` are just two doors into the same pipeline.

Two ideas worth locking in:

- **Only 2 stages use the LLM** (`classify`, `report`). The score is plain Python
  arithmetic so it's reproducible and you can defend the number.
- **The LLM is swappable.** Code talks to `LLMProvider` (an interface). Real =
  Gemini. Offline = `FakeProvider` (keyword guesser). Tests use the fake one, so
  the whole test suite runs with no API key.

---

## 2. File by file

| File | What it does | Concepts to notice |
|------|--------------|--------------------|
| `models.py` | Defines every data shape: `Article`, `Classification`, `RiskScore`, `Assessment`. Uses Pydantic — if a field is the wrong type it errors here, not later. | classes, type hints, `Enum`, `@property` (the `id` is computed from the URL) |
| `config.py` | Reads settings from `.env` / environment into one `settings` object. Nothing else reads env vars directly. | single source of truth, `@property` for the `gemini`→`fake` fallback |
| `fetch.py` | `fetch_feed(url, source)` → list of `Article`. Parses RSS with `feedparser`, drops entries with no title/link, collapses duplicate URLs with a dict. | `for` loop building a collection, `dict` for de-dupe, `getattr(x, "field", None)` for safety |
| `db.py` | SQLite: create tables, `insert_articles` (skips URLs already stored), `unprocessed_articles` (a `LEFT JOIN ... WHERE NULL`), `save_assessment`, `all_assessments`. | parameterised SQL (`?` placeholders — never string-format SQL), `total_changes` to count real inserts |
| `llm.py` | `LLMProvider` protocol + `GeminiProvider` + `FakeProvider` + `get_llm()` factory. | interface/implementation split, lazy `import` inside `__init__`, dependency injection |
| `prompts.py` + `prompts/*.md` | Prompts live as versioned text files, loaded by name. | separating prompt text from code so you can diff/evaluate it |
| `classify.py` | `classify_article(article, llm)` → builds the user message, calls `llm.complete_json`, validates the dict into a `Classification`. | trusting nothing from the model until Pydantic checks it |
| `score.py` | `score_classification(c)` → `RiskScore`. `base(signal) + 25*severity`, clamped 0–100, mapped to low/medium/high. Pure function. | a function with no side effects; easy to test exhaustively |
| `report.py` | Counts things in Python (`Counter`), then asks the LLM to write prose from the already-scored JSON. | keep math in code, only prose in the LLM |
| `pipeline.py` | `ingest`, `assess_pending`, `run` — chains the stages against an open DB connection. | orchestration layer, `@dataclass` for the return stats |
| `cli.py` | `argparse` sub-commands: `ingest`, `assess`, `run`, `report`, `stats`. | command-line parsing |
| `api.py` | FastAPI wrapper — same functions, over HTTP. **Scaffold**: works, but no auth/pagination yet. | web framework, `try/finally` to always close the DB |

---

## 3. How to drive it

```bash
uv sync                     # install everything from the lockfile
uv run pytest               # 28 tests, all offline
uv run python evals/run_evals.py   # classifier scored against evals/dataset.jsonl

# with a real key:
cp .env.example .env        # paste your Gemini key into .env
uv run esg-screener run     # fetch + classify + score real news
uv run esg-screener report  # print the briefing
uv run uvicorn esg_risk_screener.api:app --reload   # API at :8000/docs
```

The `.env` file is git-ignored. Your key never leaves your machine.

---

## 4. What's tested (so you can trust changes)

- `test_models` — the `Article.id` is stable; bad `Classification` values are rejected
- `test_fetch` — the sample feed parses, duplicate URL collapses (6 items → 5)
- `test_db` — insert counts only new rows; assessment round-trips
- `test_score` — a parametrised table pins every scoring rule
- `test_classify` — offline classifier flags a spill as negative/environmental
- `test_pipeline` — full run over the fixture feed; idempotent on a second run
- `test_api` — `/health`, `/stats`, `/assessments` respond

Run one file: `uv run pytest tests/test_score.py -q`

---

## 5. TODO together (needs your accounts — I did NOT do these)

- [ ] **GitHub**: rename `Patinprogamador` → `akin-martins`; create the repo; `git push`
- [ ] **Gemini key**: create at aistudio.google.com, put in `.env`, run `esg-screener run` for real
- [ ] **Real eval numbers**: `LLM_PROVIDER=gemini uv run python evals/run_evals.py`, commit `evals/RESULTS.md`
- [ ] **Deploy**: Render web service from the repo (uses the `Dockerfile`); put the live URL in the README
- [ ] **Finish the API**: API key header, pagination on `/assessments`, a proper `/report` content type
- [ ] **n8n**: import `n8n/esg-screener.workflow.json`, point it at the deployed URL, add a Slack/email step
- [ ] **README**: add a demo GIF, fill the live-demo link
- [ ] **dev.to post**: "Building an explainable ESG risk screener" — architecture + the fake-provider trick

---

## 6. Practice waiting for you

`pratica2.py` in the project root — next tier: dictionaries, lists of dicts,
filtering and aggregating (the same moves `fetch.py` and `report.py` use). Same
format as before: fill the functions, run the file, it prints `OK`.
