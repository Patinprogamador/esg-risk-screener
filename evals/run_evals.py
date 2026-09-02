"""Evaluate the classifier against a labelled set.

    uv run python evals/run_evals.py

Uses whatever LLM_PROVIDER is configured. With the offline `fake` provider you
get a baseline; set LLM_PROVIDER=gemini + GEMINI_API_KEY for real numbers.
Writes a Markdown table to evals/RESULTS.md.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from esg_risk_screener.classify import classify_article
from esg_risk_screener.config import settings
from esg_risk_screener.llm import get_llm
from esg_risk_screener.models import Article
from esg_risk_screener.prompts import CLASSIFY_PROMPT_VERSION

HERE = Path(__file__).parent
LABELS = ["negative", "neutral", "positive"]


def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def main() -> None:
    rows = [json.loads(line) for line in (HERE / "dataset.jsonl").read_text().splitlines() if line]
    llm = get_llm()

    cat_correct = 0
    tp: Counter[str] = Counter()
    fp: Counter[str] = Counter()
    fn: Counter[str] = Counter()

    for row in rows:
        pred = classify_article(
            Article(
                url="https://eval/x", title=row["title"], summary=row["summary"], source="eval"
            ),
            llm,
        )
        if pred.category == row["expected_category"]:
            cat_correct += 1

        exp_sig, got_sig = row["expected_signal"], pred.signal
        if got_sig == exp_sig:
            tp[exp_sig] += 1
        else:
            fp[got_sig] += 1
            fn[exp_sig] += 1

    n = len(rows)
    lines = [
        f"# Eval results - classify_{CLASSIFY_PROMPT_VERSION}",
        "",
        f"- provider: `{settings.effective_provider}`  model: `{settings.llm_model}`",
        f"- dataset: {n} labelled items",
        f"- **category accuracy: {cat_correct / n:.0%}**",
        "",
        "| signal | precision | recall | f1 |",
        "|--------|-----------|--------|----|",
    ]
    f1s = []
    for label in LABELS:
        p, r, f1 = _prf(tp[label], fp[label], fn[label])
        f1s.append(f1)
        lines.append(f"| {label} | {p:.2f} | {r:.2f} | {f1:.2f} |")
    lines.append(f"| **macro** | | | **{sum(f1s) / len(f1s):.2f}** |")
    lines.append("")

    (HERE / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
