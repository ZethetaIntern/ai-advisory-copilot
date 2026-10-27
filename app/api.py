"""
FastAPI Backend for RIA Advisory Co-pilot (app/api.py)
"""
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from data.personas import load_personas, get_persona_by_id
from risk.engine import compute_risk_profile
from planner.goal_planner import plan_goals
from portfolio.fund_screener import get_recommended_funds_for_allocation
from portfolio.backtest import run_portfolio_backtest
from guardrails.input_guard import check_input_guardrails
from guardrails.suitability import check_suitability
from rag.pipeline import RAGPipeline
from risk.approval import AdvisoryPlan, ApprovalStatus

app = FastAPI(
    title="Zeckathon PS04 - AI Advisory Co-pilot API",
    description="REST backend for SEBI-registered Investment Adviser (RIA) co-pilot",
    version="1.0.0",
)

rag_pipeline = RAGPipeline()
active_plans: Dict[str, AdvisoryPlan] = {}


class QueryRequest(BaseModel):
    query: str


class PlanApprovalRequest(BaseModel):
    adviser_id: str
    notes: Optional[str] = "Approved by RIA"


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "RIA Advisory Co-pilot"}


@app.get("/personas")
def list_personas():
    return load_personas()


@app.post("/plan/{persona_id}")
def create_plan(persona_id: str):
    try:
        persona = get_persona_by_id(persona_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Persona not found")

    risk = compute_risk_profile(persona)
    goals = plan_goals(persona, risk)
    primary_alloc = goals[0].get("allocation", {})
    recs = get_recommended_funds_for_allocation(primary_alloc)
    suitability = check_suitability(persona, primary_alloc)
    
    plan = AdvisoryPlan(
        plan_id=f"PLAN-{persona_id.upper()}",
        client_id=persona_id,
        client_name=persona["name"],
        status=ApprovalStatus.DRAFT,
        risk_profile=risk,
        goals=goals,
        fund_recommendations=recs,
    )
    plan.submit_for_review("API-USER", "Submitted plan via API")
    active_plans[plan.plan_id] = plan

    return {
        "plan_id": plan.plan_id,
        "status": plan.status.value,
        "risk_profile": risk,
        "goals": goals,
        "recommendations": recs,
        "suitability": suitability,
    }


@app.post("/research/query")
def research_query(req: QueryRequest):
    guard = check_input_guardrails(req.query)
    if not guard["is_allowed"]:
        return {
            "query": req.query,
            "answer": guard["message"],
            "citations": [],
            "guardrail_blocked": True,
        }
    return rag_pipeline.answer_query(req.query)


@app.post("/plan/{plan_id}/approve")
def approve_plan(plan_id: str, req: PlanApprovalRequest):
    if plan_id not in active_plans:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan = active_plans[plan_id]
    try:
        plan.approve(req.adviser_id, req.notes)
        return {"plan_id": plan_id, "status": plan.status.value, "audit_log": plan.audit_log}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/plan/{plan_id}/pdf")
def get_pdf(plan_id: str):
    if plan_id not in active_plans:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan = active_plans[plan_id]
    try:
        pdf_bytes = plan.export_pdf()
        return Response(content=pdf_bytes, media_type="application/pdf")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
