"""
Creative API Routes

Endpoints for creative brief and asset generation.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import date, timedelta

from models.schemas import PromoScenario, CampaignPlan, CreativeBrief, AssetSpec
from middleware.auth import get_current_user, require_analyst
from middleware.rate_limit import get_rate_limit
from engines.creative_engine import CreativeEngine
from tools.targets_config_tool import TargetsConfigTool
from tools.cdp_tool import CDPTool

router = APIRouter(dependencies=[Depends(get_current_user)])

# Initialize engines and tools
config_tool = TargetsConfigTool()
cdp_tool = CDPTool()
creative_engine = CreativeEngine(cdp_tool=cdp_tool, config_tool=config_tool)


@router.post("/finalize")
@get_rate_limit("standard")
async def finalize_campaign(
    scenarios: List[PromoScenario],
    current_user=Depends(require_analyst),
) -> CampaignPlan:
    """
    Finalize selected scenarios into campaign plan.
    
    Args:
        scenarios: List of selected PromoScenario objects
    
    Returns:
        CampaignPlan object
    """
    if not scenarios:
        raise HTTPException(status_code=400, detail="At least one scenario is required")
    
    try:
        # Build timeline from scenario date ranges
        timeline: dict = {}
        
        # Collect all unique dates from scenarios
        all_dates = set()
        for scenario in scenarios:
            current_date = scenario.date_range.start_date
            while current_date <= scenario.date_range.end_date:
                all_dates.add(current_date)
                current_date = current_date + timedelta(days=1)
        
        # Build timeline (simplified: group by week)
        for scenario in scenarios:
            current_date = scenario.date_range.start_date
            while current_date <= scenario.date_range.end_date:
                week_start = current_date - timedelta(days=current_date.weekday())
                if week_start not in timeline:
                    timeline[week_start] = []
                timeline[week_start].append(f"{scenario.name}: {scenario.description}")
                current_date = current_date + timedelta(days=7)  # Weekly entries
        
        # Execution details
        execution_details = {
            "scenarios_count": len(scenarios),
            "total_departments": list(set(dept for s in scenarios for dept in s.departments)),
            "total_channels": list(set(ch for s in scenarios for ch in s.channels)),
            "date_range": {
                "start": min(s.date_range.start_date for s in scenarios),
                "end": max(s.date_range.end_date for s in scenarios)
            }
        }
        
        return CampaignPlan(
            scenarios=scenarios,
            timeline=timeline,
            execution_details=execution_details
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error finalizing campaign: {str(exc)}") from exc


@router.post("/brief")
@get_rate_limit("standard")
async def generate_brief(
    scenario: PromoScenario,
    segments: Optional[List[str]] = None,
    current_user=Depends(require_analyst),
) -> CreativeBrief:
    """
    Generate creative brief from scenario.
    
    Args:
        scenario: PromoScenario to generate brief for
        segments: Optional list of target segments
    
    Returns:
        CreativeBrief object
    """
    try:
        brief = creative_engine.generate_creative_brief(
            scenario=scenario,
            segments=segments
        )
        return brief
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error generating brief: {str(exc)}") from exc


@router.post("/assets")
@get_rate_limit("standard")
async def generate_assets(
    brief: CreativeBrief,
    current_user=Depends(require_analyst),
) -> List[AssetSpec]:
    """
    Generate asset specifications from creative brief.
    
    Args:
        brief: CreativeBrief to generate assets from
    
    Returns:
        List of AssetSpec objects
    """
    try:
        assets = creative_engine.generate_asset_specs(brief)
        return assets
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error generating assets: {str(exc)}") from exc
