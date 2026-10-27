"""
Tests for FastAPI Backend (tests/test_api.py)
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_list_personas():
    res = client.get("/personas")
    assert res.status_code == 200
    personas = res.json()
    assert len(personas) == 6


def test_create_and_approve_plan_flow():
    # 1. Create plan for fresh graduate
    res = client.post("/plan/fresh_grad")
    assert res.status_code == 200
    data = res.json()
    plan_id = data["plan_id"]
    assert data["status"] == "PENDING_REVIEW"
    assert "risk_profile" in data
    assert "goals" in data
    assert "recommendations" in data

    # 2. Try to get PDF before approval -> Must return 403 Forbidden!
    pdf_res = client.get(f"/plan/{plan_id}/pdf")
    assert pdf_res.status_code == 403

    # 3. Approve plan
    app_res = client.post(f"/plan/{plan_id}/approve", json={"adviser_id": "RIA-01", "notes": "Approved"})
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "APPROVED"

    # 4. Get PDF after approval -> Must succeed with application/pdf!
    pdf_res_after = client.get(f"/plan/{plan_id}/pdf")
    assert pdf_res_after.status_code == 200
    assert pdf_res_after.headers["content-type"] == "application/pdf"
    assert len(pdf_res_after.content) > 1000  # Non-empty valid PDF


def test_research_query_via_api():
    # Valid query
    res = client.post("/research/query", json={"query": "What is the Direct Plan Expense Ratio (TER) of Parag Parikh Flexi Cap Fund?"})
    assert res.status_code == 200
    assert "0.68%" in res.json()["answer"]

    # Blocked query (guarantee request)
    res_block = client.post("/research/query", json={"query": "Can you guarantee a 25% return?"})
    assert res_block.status_code == 200
    assert res_block.json()["guardrail_blocked"] is True
