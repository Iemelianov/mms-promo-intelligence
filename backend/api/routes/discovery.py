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
from tools.sales_data_tool import SalesDataTool
from tools.context_data_tool import ContextDataTool
from tools.targets_config_tool import TargetsConfigTool

router = APIRouter()

sales_tool = SalesDataTool()
context_tool = ContextDataTool()
targets_tool = TargetsConfigTool()
baseline_engine = ForecastBaselineEngine(sales_data_tool=sales_tool, targets_tool=targets_tool)


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
    start_date, end_date = _month_to_range(month)
    try:
        baseline = baseline_engine.calculate_baseline((start_date, end_date))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    agg = sales_tool.get_aggregated_sales(
        date_range=(start_date, end_date),
        grain=["department"],
        filters={"channel": None},
    )
    opportunities: List[PromoOpportunity] = []
    for idx, row in agg.iterrows():
        estimated_potential = float(row["sales_value"] * 0.12)
        opportunities.append(
            PromoOpportunity(
                id=f"opp_{idx+1:02d}",
                department=row["department"],
                channel="mixed",
                date_range=DateRange(start_date=start_date, end_date=end_date),
                estimated_potential=estimated_potential,
                priority=len(agg) - idx,
                rationale=f"12% upside based on {row['department']} run-rate and recent demand",
            )
        )

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
    start_date, end_date = _month_to_range(month)
    try:
        baseline = baseline_engine.calculate_baseline((start_date, end_date))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    targets = targets or targets_tool.get_targets(month).model_dump()
    gaps = baseline_engine.calculate_gap_vs_targets(baseline, targets)
    target_sales = targets.get("sales_target", 1) or 1
    gap_percentage = {"sales": gaps["sales_gap"] / target_sales}

    return GapAnalysis(
        sales_gap=gaps["sales_gap"],
        margin_gap=gaps["margin_gap"],
        units_gap=gaps["units_gap"],
        gap_percentage=gap_percentage,
    )


@router.post("/analyze")
async def analyze(payload: DiscoveryAnalyzeRequest = Body(...)) -> dict:
    """Analyze situation and identify opportunities with baseline and gaps."""
    month = payload.month
    geo = payload.geo
    targets = payload.targets

    start_date, end_date = _month_to_range(month)
    baseline = baseline_engine.calculate_baseline((start_date, end_date))
    targets_data = targets or targets_tool.get_targets(month).model_dump()
    gaps = baseline_engine.calculate_gap_vs_targets(baseline, targets_data)
    opportunities = await get_opportunities(month=month, geo=geo, targets=targets)
    return {
        "baseline_forecast": {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
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
