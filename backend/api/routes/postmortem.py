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
