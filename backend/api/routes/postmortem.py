"""
Post-mortem API routes.
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any

from middleware.auth import require_analyst
from middleware.rate_limit import get_rate_limit
from agents.post_mortem_agent import PostMortemAgent
from engines.post_mortem_analytics_engine import PostMortemAnalyticsEngine
from engines.learning_engine import LearningEngine
from tools.sales_data_tool import SalesDataTool
from .scenarios import SCENARIO_STORE

router = APIRouter()

postmortem_agent = PostMortemAgent(
    analytics_engine=PostMortemAnalyticsEngine(sales_data_tool=SalesDataTool()),
    learning_engine=LearningEngine(),
    sales_data_tool=SalesDataTool(),
)


class PostMortemRequest(BaseModel):
    scenario_id: str
    actual_data: Dict[str, float]
    period: Dict[str, str]


@router.post("/analyze")
@get_rate_limit("standard")
async def analyze_postmortem(
    request: PostMortemRequest,
    http_request: Request,
    current_user=Depends(require_analyst),
) -> Dict[str, Any]:
    """Analyze completed campaign (stubbed to spec shape)."""
    scenario = SCENARIO_STORE.get(request.scenario_id) if "SCENARIO_STORE" in globals() else None  # type: ignore[name-defined]
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found for post-mortem")
    forecast = {
        "total_sales": request.actual_data.get("sales_value", 0.0),
        "total_margin": request.actual_data.get("margin_value", 0.0),
        "total_units": request.actual_data.get("units", 0.0),
    }
    report = postmortem_agent.analyze_performance(scenario, forecast=forecast, actual_data=request.actual_data)
    return {"report": report}


@router.get("/{scenario_id}")
async def get_postmortem_report(scenario_id: str) -> Dict[str, Any]:
    """
    Docs-friendly: return a stored or demo post-mortem report for a scenario.
    """
    scenario = SCENARIO_STORE.get(scenario_id) if "SCENARIO_STORE" in globals() else None  # type: ignore[name-defined]
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found for post-mortem")
    actual = {
        "sales_value": 3100000,
        "margin_value": 700000,
        "units": 17500,
    }
    forecast = {
        "total_sales": 3200000,
        "total_margin": 720000,
        "total_units": 18000,
    }
    report = postmortem_agent.analyze_performance(
        scenario,
        forecast=forecast,
        actual_data=actual,
    )
    return {"report": report}
