"""
Discovery API Routes

Endpoints for discovery and context analysis.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
from datetime import date
from calendar import monthrange

from models.schemas import PromoOpportunity, PromoContext, GapAnalysis, DateRange
from middleware.auth import get_current_user, require_analyst
from middleware.rate_limit import get_rate_limit
from engines.forecast_baseline_engine import ForecastBaselineEngine
from tools.sales_data_tool import SalesDataTool
from tools.context_data_tool import ContextDataTool
from tools.targets_config_tool import TargetsConfigTool

router = APIRouter(dependencies=[Depends(get_current_user)])

sales_tool = SalesDataTool()
context_tool = ContextDataTool()
targets_tool = TargetsConfigTool()
baseline_engine = ForecastBaselineEngine(sales_data_tool=sales_tool, targets_tool=targets_tool)


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
    events = context_tool.get_events(geo, (start_date, end_date))
    seasonality = context_tool.get_seasonality_profile(geo)
    weekend_patterns = context_tool.get_weekend_patterns(geo)
    return PromoContext(
        geo=geo,
        date_range=DateRange(start_date=start_date, end_date=end_date),
        events=events,
        weather=None,
        seasonality=seasonality,
        weekend_patterns=weekend_patterns,
    )


@router.get("/opportunities")
@get_rate_limit("standard")
async def get_opportunities(
    month: str,
    geo: str,
    request: Request,
    targets: Optional[dict] = None,
    current_user=Depends(require_analyst),
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
    start_date, end_date = _month_to_range(month)
    opportunities = [
        PromoOpportunity(
            id="opp_01",
            department="TV",
            channel="online",
            date_range=DateRange(start_date=start_date, end_date=end_date),
            estimated_potential=120000.0,
            priority=1,
            rationale="12% upside based on TV run-rate and recent demand",
        ),
        PromoOpportunity(
            id="opp_02",
            department="Gaming",
            channel="store",
            date_range=DateRange(start_date=start_date, end_date=end_date),
            estimated_potential=90000.0,
            priority=2,
            rationale="High attach rates in gaming accessories",
        ),
    ]
    opportunities.sort(key=lambda o: o.estimated_potential, reverse=True)
    return opportunities


@router.get("/context")
@get_rate_limit("standard")
async def get_context(
    geo: str,
    start_date: date,
    end_date: date,
    request: Request,
    current_user=Depends(require_analyst),
) -> PromoContext:
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
        return _build_context(geo=geo, start_date=start_date, end_date=end_date)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/gaps")
@get_rate_limit("standard")
async def get_gaps(
    month: str,
    geo: str,
    request: Request,
    targets: Optional[dict] = None,
    current_user=Depends(require_analyst),
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
    return GapAnalysis(
        sales_gap=50000.0,
        margin_gap=10000.0,
        units_gap=500,
        gap_percentage={"sales": 0.05},
    )


@router.post("/analyze")
@get_rate_limit("standard")
async def analyze(
    month: str,
    geo: str,
    request: Request,
    targets: Optional[dict] = None,
    current_user=Depends(require_analyst),
) -> dict:
    """Analyze situation and identify opportunities with baseline and gaps."""
    start_date, end_date = _month_to_range(month)
    baseline = baseline_engine.calculate_baseline((start_date, end_date))
    targets_data = targets or targets_tool.get_targets(month).model_dump()
    gaps = baseline_engine.calculate_gap_vs_targets(baseline, targets_data)
    opportunities = await get_opportunities(
        month=month,
        geo=geo,
        targets=targets,
        request=request,
        current_user=current_user,
    )
    return {
        "baseline_forecast": {
            "period": {"start": start_date, "end": end_date},
            "totals": {
                "sales_value": baseline.total_sales,
                "margin_value": baseline.total_margin,
                "margin_pct": (baseline.total_margin / baseline.total_sales) if baseline.total_sales else 0.0,
                "units": baseline.total_units,
            },
        },
        "gap_analysis": gaps,
        "opportunities": opportunities,
    }
