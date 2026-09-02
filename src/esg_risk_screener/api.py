"""HTTP API (FastAPI).

Thin layer over the same functions the CLI uses. Run locally with:

    uv run uvicorn esg_risk_screener.api:app --reload

Interactive docs at http://127.0.0.1:8000/docs

NOTE: scaffold - endpoints work, but auth, pagination and rate-limiting are
still to do (see WALKTHROUGH.md).
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from esg_risk_screener import db
from esg_risk_screener.llm import get_llm
from esg_risk_screener.pipeline import RunStats, run
from esg_risk_screener.report import build_report, summarise_counts

app = FastAPI(title="ESG Risk Screener", version="0.1.0")


class RunResponse(BaseModel):
    fetched: int
    stored: int
    assessed: int


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/run", response_model=RunResponse)
def run_pipeline(limit: int | None = None) -> RunStats:
    conn = db.get_connection()
    try:
        return run(conn, limit=limit)
    finally:
        conn.close()


@app.get("/assessments")
def list_assessments() -> list[dict]:
    conn = db.get_connection()
    try:
        db.init_db(conn)
        return [a.model_dump() for a in db.all_assessments(conn)]
    finally:
        conn.close()


@app.get("/stats")
def stats() -> dict:
    conn = db.get_connection()
    try:
        db.init_db(conn)
        return summarise_counts(db.all_assessments(conn))
    finally:
        conn.close()


@app.get("/report", response_class=None)
def report() -> dict:
    conn = db.get_connection()
    try:
        db.init_db(conn)
        return {"markdown": build_report(db.all_assessments(conn), get_llm())}
    finally:
        conn.close()
