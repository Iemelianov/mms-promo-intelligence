"""
Creative API Routes

Endpoints for creative brief and asset generation.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import date, timedelta
import json
from sqlalchemy.orm import Session

from models.schemas import PromoScenario, CampaignPlan, CreativeBrief, AssetSpec
from engines.creative_engine import CreativeEngine
from tools.targets_config_tool import TargetsConfigTool
from tools.cdp_tool import CDPTool
from .scenarios import SCENARIO_STORE
from db.session import get_session
from db.base import CreativeBriefDB

router = APIRouter()

# Initialize engines and tools
config_tool = TargetsConfigTool()
cdp_tool = CDPTool()
creative_engine = CreativeEngine(cdp_tool=cdp_tool, config_tool=config_tool)


@router.post("/finalize")
async def finalize_campaign(
    scenarios: List[PromoScenario]
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
async def generate_brief(
    scenario: PromoScenario,
    segments: Optional[List[str]] = None,
    db: Session = Depends(get_session)
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
        # Persist brief snapshot
        db.add(
            CreativeBriefDB(
                scenario_id=scenario.id,
                brief=json.dumps(brief.model_dump()),
                assets=None,
            )
        )
        db.commit()
        return brief
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error generating brief: {str(exc)}") from exc


@router.post("/assets")
async def generate_assets(
    brief: CreativeBrief,
    db: Session = Depends(get_session)
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
        db.add(
            CreativeBriefDB(
                scenario_id=brief.scenario_id,
                brief=json.dumps(brief.model_dump()),
                assets=json.dumps([a.model_dump() for a in assets]),
            )
        )
        db.commit()
        return assets
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error generating assets: {str(exc)}") from exc


@router.post("/generate")
async def generate_creative_package(
    payload: dict,
    db: Session = Depends(get_session)
) -> dict:
    """
    Docs-friendly endpoint: generate creative brief and assets for scenarios.
    """
    scenario_ids = payload.get("scenario_ids") or []
    asset_types = payload.get("asset_types") or ["homepage_hero", "category_banner"]
    target_segments = payload.get("target_segments") or ["LOYAL_HIGH_VALUE"]

    briefs = []
    for scenario_id in scenario_ids or ["demo_scenario"]:
        scenario = SCENARIO_STORE.get(scenario_id) if "SCENARIO_STORE" in globals() else None  # type: ignore[name-defined]
        if not scenario:
            from datetime import date, timedelta
            from models.schemas import DateRange

            today = date.today()
            scenario = PromoScenario(
                id=scenario_id,
                name="Demo Scenario",
                description="Demo creative scenario",
                date_range=DateRange(start_date=today, end_date=today + timedelta(days=7)),
                departments=["TV", "Gaming"],
                channels=["online", "store"],
                discount_percentage=15.0,
            )
        brief = creative_engine.generate_creative_brief(scenario=scenario, segments=target_segments)
        assets = creative_engine.generate_asset_specs(brief)
        filtered_assets = [a for a in assets if a.asset_type in asset_types] or assets
        briefs.append({"scenario_id": scenario_id, "creative_brief": brief, "assets": filtered_assets})

        db.add(
            CreativeBriefDB(
                scenario_id=scenario_id,
                brief=json.dumps(brief.model_dump()),
                assets=json.dumps([a.model_dump() for a in filtered_assets]),
            )
        )
    db.commit()

    return {"briefs": briefs}
