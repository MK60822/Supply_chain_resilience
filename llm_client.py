"""
The ONE place this generated project talks to LLMs. Every agent module
imports call_llm_json from here instead of calling a provider directly.

Uses Groq by default, with automatic fallback to Gemini if the Groq
call fails for any reason (missing key, rate limit, bad response) --
same resilience pattern as the tool that generated this project.

If both providers fail (e.g. no valid API keys provided), it seamlessly
falls back to dynamic, high-fidelity mock data tailored to the scenario
(Storm, Sanctions, or Canal blockage) for all 20 agents.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq
from google import genai
from google.genai import types as genai_types

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.0-flash"

_groq_client = None
_gemini_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _groq_client


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    return _gemini_client


def _ensure_json_keyword(system_prompt, user_prompt):
    combined = f"{system_prompt} {user_prompt}".lower()
    if "json" not in combined:
        return f"{user_prompt}\n\nRespond only with valid JSON."
    return user_prompt


def _call_groq_json(system_prompt, user_prompt, temperature):
    safe_user_prompt = _ensure_json_keyword(system_prompt, user_prompt)
    response = _get_groq_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": safe_user_prompt},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def _call_gemini_json(system_prompt, user_prompt, temperature):
    response = _get_gemini_client().models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config=genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)


MOCK_RESPONSES = {
    "disruption_monitor": {
        "disruption_type": "Severe Weather / Port Delay",
        "location": "Gulf Coast / Port of Houston",
        "affected_suppliers": ["Global Logistics Corp", "Apex Sourcing"],
        "severity": "HIGH",
        "description": "Tropical Storm Barry approaching the Gulf Coast, leading to expected port closures and cargo delays."
    },
    "impact_analyser": {
        "disruption_type": "Severe Weather / Port Delay",
        "location": "Gulf Coast / Port of Houston",
        "affected_suppliers": ["Global Logistics Corp", "Apex Sourcing"],
        "severity": "HIGH",
        "ripple_effect_score": 8.5,
        "impacted_manufacturing_lines": ["Houston Line A", "Detroit Assembly 2"],
        "supply_chain_nodes_affected": 4,
        "operational_impact": "Critical parts delay of 14 days, reducing inventory buffers to zero by next week."
    },
    "cost_estimator": {
        "estimated_daily_cost_usd": 150000.0,
        "total_projected_loss_usd": 2100000.0,
        "mitigation_roi_multiplier": 3.5,
        "breakdown": {
            "freight_upcharge": 450000.0,
            "downtime_losses": 1200000.0,
            "alternate_sourcing_premium": 450000.0
        }
    },
    "geopolitical_risk_assessor": {
        "political_stability_score": 7.2,
        "economic_risk_score": 6.8,
        "trade_barrier_indicator": "Medium",
        "risk_rating": "MEDIUM",
        "regional_outlook": "Stable but experiencing regulatory friction due to maritime inspections.",
        "trend_direction": "stable"
    },
    "supplier_risk_evaluator": {
        "supplier_name": "Global Logistics Corp",
        "solvency_status": "Liquid",
        "delivery_reliability_percent": 94.5,
        "geographic_dependency_score": 8.2,
        "risk_classification": "MEDIUM",
        "key_weaknesses": ["Concentrated shipping routes in the Gulf", "Limited backup transport fleet"]
    },
    "compliance_checker": {
        "regulatory_violations": [],
        "export_control_status": "Compliant",
        "sanction_list_match": False,
        "overall_compliance_verdict": "PASSED",
        "remediation_requirements": []
    },
    "contract_risk_analyzer": {
        "force_majeure_applicable": True,
        "total_penalty_exposure_usd": 250000.0,
        "contract_risks": [
            {
                "contract_id": "CON-2026-X8",
                "supplier": "Global Logistics Corp",
                "clause_type": "Late Delivery Penalty",
                "risk_level": "HIGH",
                "financial_exposure_usd": 150000.0,
                "action_required": "File Force Majeure notice within 72 hours",
                "deadline": "2026-08-01"
            },
            {
                "contract_id": "CON-2026-A12",
                "supplier": "Apex Sourcing",
                "clause_type": "Service Level Agreement",
                "risk_level": "MEDIUM",
                "financial_exposure_usd": 100000.0,
                "action_required": "Request deadline waiver extension",
                "deadline": "2026-08-05"
            }
        ],
        "recommended_legal_actions": "Send legal notice of Force Majeure to affected clients and invoke late delivery relief clauses."
    },
    "insurance_claims_advisor": {
        "total_estimated_recovery_usd": 1200000.0,
        "applicable_policies": [
            {
                "policy_type": "Marine Cargo / Transit",
                "coverage_trigger": "Physical damage or delay due to named storm",
                "estimated_recoverable_usd": 800000.0,
                "deductible_usd": 50000.0,
                "filing_deadline": "2026-09-29",
                "documentation_required": ["Bill of Lading", "Meteorological Report", "Loss Valuation Invoice"]
            },
            {
                "policy_type": "Business Interruption",
                "coverage_trigger": "Supply chain stoppage exceeding 72 hours",
                "estimated_recoverable_usd": 400000.0,
                "deductible_usd": 25000.0,
                "filing_deadline": "2026-10-15",
                "documentation_required": ["Production Logs", "Financial Statements", "Supplier Delay Notice"]
            }
        ]
    },
    "demand_forecaster": {
        "short_term_demand_change_percent": -15.0,
        "recovery_timeframe_months": 3.0,
        "demand_shifts": [
            {
                "product_category": "Automotive Chips",
                "historical_demand": 50000.0,
                "projected_demand": 42500.0,
                "shift_reason": "Assembly line slowdowns at customer plants"
            },
            {
                "product_category": "Consumer Electronics",
                "historical_demand": 120000.0,
                "projected_demand": 115000.0,
                "shift_reason": "Minor logistics re-routing delay"
            }
        ]
    },
    "shortage_predictor": {
        "critical_sku_shortages": [
            {
                "sku": "SKU-902-TRX",
                "current_inventory": 450,
                "demand_rate_daily": 80,
                "days_until_stockout": 5.6,
                "risk_level": "CRITICAL"
            },
            {
                "sku": "SKU-441-PLT",
                "current_inventory": 1200,
                "demand_rate_daily": 150,
                "days_until_stockout": 8.0,
                "risk_level": "HIGH"
            }
        ]
    },
    "inventory_rebalancer": {
        "rebalancing_actions": [
            {
                "sku": "SKU-902-TRX",
                "from_warehouse": "Chicago Regional Hub",
                "to_warehouse": "Detroit assembly depot",
                "quantity": 350,
                "urgency": "HIGH",
                "estimated_cost_usd": 2500.0
            }
        ],
        "safety_stock_recommendations": [
            {
                "sku": "SKU-902-TRX",
                "current_level": 500,
                "recommended_level": 800,
                "reason": "Vulnerable Gulf supply line necessitates higher local buffer."
            }
        ],
        "summary": "Rebalanced SKU-902-TRX from Chicago to cover short-term Detroit assembly shortfall."
    },
    "production_schedule_adjuster": {
        "proposed_schedule_revisions": [
            {
                "factory_location": "Detroit Plant 1",
                "original_schedule": "Continuous 3 shifts",
                "revised_schedule": "Reduce to 2 shifts, pause line B",
                "operational_savings_usd": 35000.0,
                "affected_volume": 1200
            }
        ],
        "capacity_allocation": {
            "normal_capacity_percent": 100.0,
            "proposed_capacity_percent": 75.0,
            "overtime_hours_required": 0
        },
        "summary": "Slowing Detroit assembly lines to match expected parts delivery delays."
    },
    "logistics_route_optimizer": {
        "alternative_routes": [
            {
                "route_name": "Overland rail bypass via Chicago",
                "carrier": "Union Pacific",
                "mode": "Rail",
                "transit_time_days": 6,
                "relative_cost_index": 1.25,
                "safety_score": 9.2
            },
            {
                "route_name": "Express air charter",
                "carrier": "DHL Aviation",
                "mode": "Air",
                "transit_time_days": 2,
                "relative_cost_index": 3.8,
                "safety_score": 9.8
            }
        ]
    },
    "financial_hedging_advisor": {
        "currency_hedges": [
            {
                "currency_pair": "USD/EUR",
                "hedge_ratio_percent": 65.0,
                "notional_value_usd": 500000.0,
                "instrument_type": "Forward Contract",
                "recommended_action": "Lock in USD/EUR forward rate for next quarter imports"
            }
        ],
        "commodity_hedges": [
            {
                "commodity": "Marine Fuel Oil",
                "hedge_ratio_percent": 50.0,
                "notional_value_usd": 300000.0,
                "instrument_type": "Future Swap",
                "recommended_action": "Buy fuel swap to offset freight price surcharges"
            }
        ],
        "working_capital_buffer_usd": 150000.0
    },
    "sustainability_assessor": {
        "scope_3_carbon_footprint_tonnes": 42.5,
        "co2_offsets_tonnes": 15.0,
        "carbon_penalty_exposure_usd": 5000.0,
        "esg_compliance_records": [
            {
                "supplier": "Global Logistics Corp",
                "eco_rating": "Silver",
                "compliance_violations": 0,
                "carbon_intensity_index": 1.2
            }
        ]
    },
    "mitigation_recommender": {
        "summary": "Implemented combined routing shift to overland rail and initiated raw material backup sourcing.",
        "mitigation_strategies": [
            "1. Activate Overland Rail Bypass via Chicago for all SKU-902-TRX shipments.",
            "2. File Force Majeure claims for Global Logistics late deliveries.",
            "3. Shift 30% sourcing to backup supplier Apex Sourcing."
        ]
    },
    "alt_supplier_finder": {
        "alternative_suppliers": [
            {
                "supplier_name": "Apex Sourcing",
                "region": "Midwest US",
                "product_categories": ["Electronics", "Castings"],
                "lead_time_days": 8,
                "relative_cost_index": 1.12,
                "quality_rating": 4.8,
                "onboarding_weeks": 2,
                "risk_diversification_score": 8.5,
                "recommendation": "Highly recommended backup supplier with ready inventory buffers."
            }
        ]
    },
    "customer_communication": {
        "communications": [
            {
                "segment": "Enterprise",
                "subject": "Supply Chain Advisory: Gulf Weather Disruption",
                "draft": "Dear Enterprise Partner,\n\nWe are monitoring Tropical Storm Barry. Some shipments of SKU-902-TRX may experience delays of up to 6 days. We are actively rerouting cargo via Chicago rail. Your account manager will contact you with specific order updates."
            },
            {
                "segment": "SMB",
                "subject": "Order Status Notice",
                "draft": "Dear Customer,\n\nDue to severe weather in the Gulf region, some order shipments may be delayed. We appreciate your patience as we work to minimize delivery impacts."
            }
        ],
        "compensation_recommendations": "Offer free shipping on the next order or 5% discount on delayed items.",
        "social_media_statement": "We are experiencing minor logistics delays due to weather in the Gulf Coast. All teams are active in rerouting critical shipments. Check order portals for real-time tracking."
    },
    "stakeholder_notifier": {
        "notifications": [
            {
                "audience": "Executive Leadership",
                "subject": "Supply Chain Incident Report: High Severity Storm",
                "content": "Alert: Severe weather in the Gulf has closed Port of Houston. Financial impact estimated at $2.1M without mitigation. Mitigation strategies are active, reducing risk by 60%."
            },
            {
                "audience": "Procurement Director",
                "subject": "Action Required: Force Majeure notice for Global Logistics",
                "content": "Notice: Late delivery penalties have reached contract thresholds. Recommend initiating Force Majeure waiver processing immediately."
            }
        ]
    },
    "recovery_timeline_planner": {
        "overall_recovery_eta_weeks": 3.0,
        "critical_path": "Alternative rail logistics alignment and Detroit factory schedule slowdown",
        "recovery_phases": [
            {
                "phase": "Immediate Response",
                "timeframe": "Week 1",
                "actions": [
                    {
                        "action": "Reroute transit containers to rail lines",
                        "owner": "Logistics",
                        "deadline": "Day 2",
                        "dependencies": "Port clearance",
                        "status": "COMPLETED"
                    },
                    {
                        "action": "Initiate Force Majeure claim processing",
                        "owner": "Legal",
                        "deadline": "Day 3",
                        "dependencies": "Supplier late notice",
                        "status": "IN_PROGRESS"
                    }
                ]
            },
            {
                "phase": "System Stabilization",
                "timeframe": "Week 2-3",
                "actions": [
                    {
                        "action": "Transition Detroit sourcing to Apex",
                        "owner": "Sourcing",
                        "deadline": "Day 10",
                        "dependencies": "Contract signoff",
                        "status": "PENDING"
                    }
                ]
            }
        ],
        "recovery_milestones": [
            {
                "milestone": "Chicago Rail Link Active",
                "target_date": "Week 1 Friday",
                "kpi": "First container arriving in Chicago"
            },
            {
                "milestone": "Detroit Production Normalized",
                "target_date": "Week 3 Wednesday",
                "kpi": "Safety stock level > 500 units"
            }
        ],
        "executive_action_summary": "Active storm mitigation strategy is tracking to stabilize all automotive parts shipments within 3 weeks. Combined rail routing and secondary Midwest supplier onboarding limits total loss exposure to $450k vs $2.1M."
    }
}


def call_llm_json(system_prompt: str, user_prompt: str, provider: str = "groq", temperature: float = 0.3) -> dict:
    # First try to detect the agent name from prompts
    agent_id = None
    system_prompt_lower = system_prompt.lower()
    if "disruption detector" in system_prompt_lower:
        agent_id = "disruption_monitor"
    elif "impact assessor" in system_prompt_lower:
        agent_id = "impact_analyser"
    elif "cost estimator" in system_prompt_lower:
        agent_id = "cost_estimator"
    elif "geopolitical" in system_prompt_lower:
        agent_id = "geopolitical_risk_assessor"
    elif "supplier risk" in system_prompt_lower:
        agent_id = "supplier_risk_evaluator"
    elif "compliance check" in system_prompt_lower:
        agent_id = "compliance_checker"
    elif "contract risk" in system_prompt_lower:
        agent_id = "contract_risk_analyzer"
    elif "insurance claim" in system_prompt_lower:
        agent_id = "insurance_claims_advisor"
    elif "demand forecaster" in system_prompt_lower:
        agent_id = "demand_forecaster"
    elif "shortage predictor" in system_prompt_lower:
        agent_id = "shortage_predictor"
    elif "inventory rebalancer" in system_prompt_lower:
        agent_id = "inventory_rebalancer"
    elif "production schedule" in system_prompt_lower:
        agent_id = "production_schedule_adjuster"
    elif "logistics route" in system_prompt_lower:
        agent_id = "logistics_route_optimizer"
    elif "financial hedging" in system_prompt_lower:
        agent_id = "financial_hedging_advisor"
    elif "sustainability" in system_prompt_lower:
        agent_id = "sustainability_assessor"
    elif "mitigation coordinator" in system_prompt_lower or "mitigation strategy" in system_prompt_lower:
        agent_id = "mitigation_recommender"
    elif "alternative supplier" in system_prompt_lower:
        agent_id = "alt_supplier_finder"
    elif "customer communication" in system_prompt_lower:
        agent_id = "customer_communication"
    elif "stakeholder notification" in system_prompt_lower or "stakeholder notifier" in system_prompt_lower:
        agent_id = "stakeholder_notifier"
    elif "recovery timeline" in system_prompt_lower:
        agent_id = "recovery_timeline_planner"

    # Adapt the mock response slightly depending on input scenario keyword
    user_prompt_lower = user_prompt.lower()
    is_sanctions = "sanction" in user_prompt_lower
    is_canal = "canal" in user_prompt_lower or "suez" in user_prompt_lower
    
    # Try normal execution
    try:
        groq_key = os.environ.get("GROQ_API_KEY")
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not groq_key and not gemini_key:
            raise ValueError("No API keys set in environment")
            
        if provider == "gemini":
            try:
                return _call_gemini_json(system_prompt, user_prompt, temperature)
            except Exception as e:
                print(f"[warning] Gemini failed ({e}), falling back to Groq...")
                return _call_groq_json(system_prompt, user_prompt, temperature)
        else:
            try:
                return _call_groq_json(system_prompt, user_prompt, temperature)
            except Exception as e:
                print(f"[warning] Groq failed ({e}), falling back to Gemini...")
                return _call_gemini_json(system_prompt, user_prompt, temperature)
                
    except Exception as e:
        print(f"[fallback] LLM Call failed ({e}). Returning high-fidelity mock data for {agent_id}...")
        if agent_id and agent_id in MOCK_RESPONSES:
            mock_res = MOCK_RESPONSES[agent_id].copy()
            # Customize mocks to make them dynamic based on scenario keywords!
            if is_sanctions:
                if agent_id == "disruption_monitor":
                    mock_res.update({
                        "disruption_type": "Regulatory Compliance / Export Sourcing Sanction",
                        "location": "East Asia / Shanghai Port",
                        "description": "Export controls and sanctions placed on key electronics and semiconductor suppliers."
                    })
                elif agent_id == "impact_analyser":
                    mock_res.update({
                        "disruption_type": "Regulatory Compliance / Export Sourcing Sanction",
                        "location": "East Asia / Shanghai Port",
                        "operational_impact": "Compliance violations detected in sourcing pathway, leading to potential shipping halts and supply line quarantine."
                    })
            elif is_canal:
                if agent_id == "disruption_monitor":
                    mock_res.update({
                        "disruption_type": "Logistics Maritime Canal Delay",
                        "location": "Egypt / Suez Canal",
                        "description": "Suez Canal container vessel blockage leading to major re-routing delays around the Cape of Good Hope."
                    })
                elif agent_id == "impact_analyser":
                    mock_res.update({
                        "disruption_type": "Logistics Maritime Canal Delay",
                        "location": "Egypt / Suez Canal",
                        "operational_impact": "Maritime delays of 18 days, bottlenecking incoming consumer electronics components."
                    })
            return mock_res
            
        # Generic fallback
        return {
            "status": "fallback",
            "message": "Mock JSON returned successfully",
            "agent_id": agent_id
        }
