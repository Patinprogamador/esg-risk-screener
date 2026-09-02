# Architecture

## Why it is shaped this way

**Stages are independent functions, not one big script.** `fetch`, `classify`,
`score`, `report` each take plain inputs and return plain outputs. `pipeline.py`
chains them; `cli.py` and `api.py` are thin callers. That means every stage is
unit-testable in isolation, and a failure in one feed or one article does not
abort the run.

**The LLM is behind an interface.** `llm.LLMProvider` is a `Protocol` with two
methods. `GeminiProvider` is the real one; `FakeProvider` is a deterministic
keyword stub. Config decides which is used, falling back to `fake` when no key is
present. Nothing else in the codebase imports a vendor SDK.

**Scoring is deterministic on purpose.** An LLM classifies (fuzzy judgement);
a pure function scores (`base(signal) + 25 * severity`, clamped 0-100). A credit
committee can read `score.py` and reproduce any number by hand. All the scoring
rules are pinned by a parametrised table in `tests/test_score.py`.

## Data model

```
Article ──1:1──> Assessment
                   ├── Classification  (category, signal, severity, rationale)  ← LLM
                   └── RiskScore        (score 0-100, band low/medium/high)       ← rules
```

SQLite, two tables (`articles`, `assessments`) joined on the article id, which is
`sha256(url)` so re-runs never duplicate.

## Module map

| Module        | Responsibility                                            | LLM? |
|---------------|----------------------------------------------------------|------|
| `models.py`   | Pydantic types crossing every boundary                    | –    |
| `config.py`   | env / `.env` → `settings` singleton                       | –    |
| `fetch.py`    | RSS/Atom → `Article`, de-dupe                             | –    |
| `db.py`       | SQLite schema + read/write helpers                        | –    |
| `llm.py`      | provider Protocol + Gemini + Fake + factory              | –    |
| `prompts.py`  | load versioned prompt files                               | –    |
| `classify.py` | `Article` → `Classification`                              | yes  |
| `score.py`    | `Classification` → `RiskScore`                            | –    |
| `report.py`   | `[Assessment]` → Markdown; plain-Python aggregates        | yes  |
| `pipeline.py` | chain the stages, persist                                 | –    |
| `cli.py`      | argparse front end                                        | –    |
| `api.py`      | FastAPI front end                                         | –    |

## Known gaps

- API has no auth, pagination, or rate limiting (scaffold).
- `report` sends all assessments in one prompt — needs chunking at scale.
- Eval set is tiny; metrics not yet published.
