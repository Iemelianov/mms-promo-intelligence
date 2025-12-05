"""
Post-mortem API routes.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from models.schemas import PostMortemReport, PromoScenario, DateRange
from engines.post_mortem_analytics_engine import PostMortemAnalyticsEngine
from engines.scenario_evaluation_engine import ScenarioEvaluationEngine
from engines.forecast_baseline_engine import ForecastBaselineEngine
from engines.uplift_elasticity_engine import UpliftElasticityEngine
from engines.context_engine import ContextEngine
from engines.learning_engine import LearningEngine
from tools.sales_data_tool import SalesDataTool
from tools.context_data_tool import ContextDataTool
from tools.targets_config_tool import TargetsConfigTool
from db.session import get_session
from db.base import Scenario as ScenarioDB
from api.routes.scenarios import _get_scenario  # reuse helper

router = APIRouter()

sales_tool = SalesDataTool()
context_tool = ContextDataTool()
targets_tool = TargetsConfigTool()
baseline_engine = ForecastBaselineEngine(sales_data_tool=sales_tool, targets_tool=targets_tool)
uplift_engine = UpliftElasticityEngine(sales_data_tool=sales_tool)
evaluation_engine = ScenarioEvaluationEngine(uplift_engine=uplift_engine)
context_engine = ContextEngine(context_tool=context_tool)
postmortem_engine = PostMortemAnalyticsEngine(sales_data_tool=sales_tool)
learning_engine = LearningEngine()


@router.post("/analyze")
async def analyze_postmortem(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Analyze completed campaign and return post-mortem report.
    """
    scenario_id = payload.get("scenario_id")
    actual_data = payload.get("actual_data") or {}
    period = payload.get("period") or {}

    if not scenario_id:
        raise HTTPException(status_code=400, detail="scenario_id is required")

    scenario = _get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Re-evaluate forecast KPIs for the scenario period
    baseline = baseline_engine.calculate_baseline(
        (scenario.date_range.start_date, scenario.date_range.end_date)
    )
    uplift_model = uplift_engine.build_uplift_model({})
    context = context_engine.build_context(
        geo="DE",
        date_range=DateRange(
            start_date=scenario.date_range.start_date,
            end_date=scenario.date_range.end_date
        )
    )
    forecast_kpi = evaluation_engine.evaluate_scenario(scenario, baseline, uplift_model, context)

    report = postmortem_engine.analyze_performance(
        scenario=scenario,
        forecast=forecast_kpi.model_dump(),
        actual_data=actual_data
    )

    return {
        "report": report,
        "forecast_kpi": forecast_kpi,
        "actual_kpi": {
            "sales_value": actual_data.get("sales_value"),
            "margin_value": actual_data.get("margin_value"),
            "units": actual_data.get("units"),
            "ebit": actual_data.get("ebit"),
        },
    }
"""
Post-mortem API routes.
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any

from middleware.auth import require_analyst
from middleware.rate_limit import get_rate_limit

router = APIRouter()


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
    return {
        "report": {
            "scenario_id": request.scenario_id,
            "forecast_kpi": {
                "sales_value": 3200000,
                "margin_value": 720000,
                "units": 18000,
            },
            "actual_kpi": request.actual_data,
            "vs_forecast": {
                "sales_value_error_pct": -3.1,
                "margin_value_error_pct": -2.8,
            },
            "insights": [
                "Uplift in Gaming was over-estimated",
                "TV sales exceeded forecast",
            ],
            "learning_points": ["Adjust Gaming uplift coefficient by -5%"],
        }
    }


@router.get("/{scenario_id}")
async def get_postmortem_report(scenario_id: str) -> Dict[str, Any]:
    """
    Docs-friendly: return a stored or demo post-mortem report for a scenario.
    """
    return {
        "report": {
            "scenario_id": scenario_id,
            "forecast_kpi": {
                "sales_value": 3200000,
                "margin_value": 720000,
                "units": 18000,
            },
            "actual_kpi": {
                "sales_value": 3100000,
                "margin_value": 700000,
                "units": 17500,
            },
            "vs_forecast": {
                "sales_value_error_pct": -3.1,
                "margin_value_error_pct": -2.8,
                "ebit_error_pct": -4.4,
            },
            "insights": [
                "Uplift in Gaming was over-estimated",
                "TV sales exceeded forecast",
            ],
        }
    }
