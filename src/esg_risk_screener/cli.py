"""Command-line interface.

esg-screener ingest       fetch feeds, store new articles
esg-screener assess       classify + score unprocessed articles
esg-screener run          ingest + assess in one go
esg-screener report       print a Markdown briefing
esg-screener stats        print aggregate counts as JSON
"""

from __future__ import annotations

import argparse
import json

from esg_risk_screener import db
from esg_risk_screener.config import settings
from esg_risk_screener.llm import get_llm
from esg_risk_screener.pipeline import assess_pending, ingest, run
from esg_risk_screener.report import build_report, summarise_counts


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="esg-screener", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("ingest", "assess", "run", "report", "stats"):
        child = sub.add_parser(name)
        if name in ("assess", "run"):
            child.add_argument("--limit", type=int, default=None, help="cap articles assessed")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    limit = getattr(args, "limit", None)
    conn = db.get_connection()
    db.init_db(conn)

    if args.command == "ingest":
        fetched, stored = ingest(conn)
        print(f"fetched {fetched}, stored {stored} new")

    elif args.command == "assess":
        n = assess_pending(conn, get_llm(), limit=limit)
        print(f"assessed {n} article(s) using {settings.effective_provider}")

    elif args.command == "run":
        stats = run(conn, limit=limit)
        print(json.dumps(stats.__dict__, indent=2))

    elif args.command == "report":
        print(build_report(db.all_assessments(conn), get_llm()))

    elif args.command == "stats":
        counts = summarise_counts(db.all_assessments(conn))
        print(json.dumps(counts, indent=2, default=str))

    conn.close()
    return 0
