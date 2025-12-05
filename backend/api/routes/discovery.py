"""
Discovery API Routes

Endpoints for discovery and context analysis.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Dict, Any
from datetime import date
from calendar import monthrange
from pydantic import BaseModel

from models.schemas import PromoOpportunity, PromoContext, GapAnalysis, DateRange
from engines.forecast_baseline_engine import ForecastBaselineEngine
from engines.context_engine import ContextEngine
from tools.sales_data_tool import SalesDataTool
from tools.context_data_tool import ContextDataTool
from tools.targets_config_tool import TargetsConfigTool
from tools.weather_tool import WeatherTool
from agents.discovery_agent import DiscoveryAgent

router = APIRouter()

sales_tool = SalesDataTool()
context_tool = ContextDataTool()
targets_tool = TargetsConfigTool()
baseline_engine = ForecastBaselineEngine(sales_data_tool=sales_tool, targets_tool=targets_tool)
context_engine = ContextEngine(context_tool=context_tool)
discovery_agent = DiscoveryAgent(
    context_engine=context_engine,
    forecast_engine=baseline_engine,
    context_tool=context_tool,
    weather_tool=WeatherTool(),
    targets_tool=targets_tool,
    sales_tool=sales_tool,
)


class DiscoveryAnalyzeRequest(BaseModel):
    month: str
    geo: str
    targets: Optional[Dict[str, Any]] = None


def _month_to_range(month: str) -> tuple:
    """Convert YYYY-MM to (start_date, end_date)."""
    try:
        year, month_num = map(int, month.split("-"))
        last_day = monthrange(year, month_num)[1]
        return date(year, month_num, 1), date(year, month_num, last_day)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid month format, expected YYYY-MM") from exc


def _build_context(geo: str, start_date: date, end_date: date) -> PromoContext:
    """Assemble a lightweight context object from static fixtures."""
    return discovery_agent.get_context(
        date_range=(start_date, end_date),
        geo=geo,
    )


@router.get("/opportunities")
async def get_opportunities(
    month: str,
    geo: str,
    targets: Optional[dict] = None
) -> List[PromoOpportunity]:
    """
    Analyze situation and identify promotional opportunities.
    
    Args:
        month: Target month (e.g., "2024-10")
        geo: Geographic region
        targets: Optional targets dictionary
    
    Returns:
        List of promotional opportunities
    """
    try:
        result = discovery_agent.analyze_situation(month=month, geo=geo, targets=targets)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    opportunities: List[PromoOpportunity] = result.get("opportunities", [])
    opportunities.sort(key=lambda o: o.estimated_potential, reverse=True)
    return opportunities


@router.get("/context")
async def get_context(
    geo: str,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """
    Get comprehensive context for promotional planning.
    
    Args:
        geo: Geographic region
        start_date: Start date
        end_date: End date
    
    Returns:
        PromoContext object
    """
    try:
        ctx = _build_context(geo=geo, start_date=start_date, end_date=end_date)
        ctx_dict = ctx.model_dump()
        ctx_dict["date_range"] = {
            "start": ctx.date_range.start_date.isoformat(),
            "end": ctx.date_range.end_date.isoformat(),
        }
        return {"context": ctx_dict}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/gaps")
async def get_gaps(
    month: str,
    geo: str,
    targets: Optional[dict] = None
) -> GapAnalysis:
    """
    Identify gaps between baseline and targets.
    
    Args:
        month: Target month
        geo: Geographic region
        targets: Optional targets dictionary to override defaults
    
    Returns:
        GapAnalysis object
    """
    try:
        result = discovery_agent.analyze_situation(month=month, geo=geo, targets=targets)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return result["gap_analysis"]


@router.post("/analyze")
async def analyze(payload: DiscoveryAnalyzeRequest = Body(...)) -> dict:
    """Analyze situation and identify opportunities with baseline and gaps."""
    month = payload.month
    geo = payload.geo
    targets = payload.targets

    result = discovery_agent.analyze_situation(month=month, geo=geo, targets=targets)
    return {
        "baseline_forecast": {
            "period": {
                "start": result["baseline"].date_range.start_date.isoformat(),
                "end": result["baseline"].date_range.end_date.isoformat(),
            },
            "totals": {
                "sales_value": result["baseline"].total_sales,
                "margin_value": result["baseline"].total_margin,
                "margin_pct": (
                    (result["baseline"].total_margin / result["baseline"].total_sales)
                    if result["baseline"].total_sales
                    else 0.0
                ),
                "units": result["baseline"].total_units,
            },
        },
        "gap_analysis": result["gap_analysis"],
        "opportunities": result["opportunities"],
    }
