"""
Supply Chain Multi-Agent System — 20-Agent Pipeline
"""

import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agents.disruption_monitor import run as run_disruption_monitor
from agents.impact_analyser import run as run_impact_analyser
from agents.cost_estimator import run as run_cost_estimator
from agents.geopolitical_risk_assessor import run as run_geopolitical_risk_assessor
from agents.supplier_risk_evaluator import run as run_supplier_risk_evaluator
from agents.compliance_checker import run as run_compliance_checker
from agents.contract_risk_analyzer import run as run_contract_risk_analyzer
from agents.insurance_claims_advisor import run as run_insurance_claims_advisor
from agents.demand_forecaster import run as run_demand_forecaster
from agents.shortage_predictor import run as run_shortage_predictor
from agents.inventory_rebalancer import run as run_inventory_rebalancer
from agents.production_schedule_adjuster import run as run_production_schedule_adjuster
from agents.logistics_route_optimizer import run as run_logistics_route_optimizer
from agents.financial_hedging_advisor import run as run_financial_hedging_advisor
from agents.sustainability_assessor import run as run_sustainability_assessor
from agents.mitigation_recommender import run as run_mitigation_recommender
from agents.alt_supplier_finder import run as run_alt_supplier_finder
from agents.customer_communication import run as run_customer_communication
from agents.stakeholder_notifier import run as run_stakeholder_notifier
from agents.recovery_timeline_planner import run as run_recovery_timeline_planner

app = FastAPI(title="Supply Chain Multi-Agent System")


@app.middleware("http")
async def add_api_keys_to_env(request, call_next):
    gemini_key = request.headers.get("x-gemini-key")
    groq_key = request.headers.get("x-groq-key")
    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
    response = await call_next(request)
    return response


class RunRequest(BaseModel):
    input_data: dict


PIPELINE = [
    ("disruption_monitor",          run_disruption_monitor),
    ("impact_analyser",             run_impact_analyser),
    ("cost_estimator",              run_cost_estimator),
    ("geopolitical_risk_assessor",  run_geopolitical_risk_assessor),
    ("supplier_risk_evaluator",     run_supplier_risk_evaluator),
    ("compliance_checker",          run_compliance_checker),
    ("contract_risk_analyzer",      run_contract_risk_analyzer),
    ("insurance_claims_advisor",    run_insurance_claims_advisor),
    ("demand_forecaster",           run_demand_forecaster),
    ("shortage_predictor",          run_shortage_predictor),
    ("inventory_rebalancer",        run_inventory_rebalancer),
    ("production_schedule_adjuster", run_production_schedule_adjuster),
    ("logistics_route_optimizer",   run_logistics_route_optimizer),
    ("financial_hedging_advisor",   run_financial_hedging_advisor),
    ("sustainability_assessor",     run_sustainability_assessor),
    ("mitigation_recommender",      run_mitigation_recommender),
    ("alt_supplier_finder",         run_alt_supplier_finder),
    ("customer_communication",      run_customer_communication),
    ("stakeholder_notifier",        run_stakeholder_notifier),
    ("recovery_timeline_planner",   run_recovery_timeline_planner),
]


@app.get("/", response_class=HTMLResponse)
def read_root():
    static_index = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_index):
        with open(static_index, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Supply Chain Multi-Agent Backend is Running</h1>"


@app.get("/agents")
def list_agents():
    return {"agents": [{"id": name, "position": i + 1} for i, (name, _) in enumerate(PIPELINE)]}


@app.post("/run")
def run_pipeline(request: RunRequest):
    result = request.input_data
    agent_outputs = {}

    for agent_id, agent_fn in PIPELINE:
        print(f"[AGENT_START] {agent_id} | Input: {json.dumps(result)}")
        result = agent_fn(result)
        agent_outputs[agent_id] = result
        print(f"[AGENT_END] {agent_id} | Output: {json.dumps(result)}")

    return {"final_output": result, "agent_outputs": agent_outputs}


class RunAgentRequest(BaseModel):
    agent_id: str
    input_data: dict


@app.post("/run_agent")
def run_single_agent(request: RunAgentRequest):
    agent_fn = next((fn for name, fn in PIPELINE if name == request.agent_id), None)
    if not agent_fn:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_id}' not found")
    print(f"[AGENT_START] {request.agent_id} | Input: {json.dumps(request.input_data)}")
    result = agent_fn(request.input_data)
    print(f"[AGENT_END] {request.agent_id} | Output: {json.dumps(result)}")
    return {"agent_id": request.agent_id, "result": result}
