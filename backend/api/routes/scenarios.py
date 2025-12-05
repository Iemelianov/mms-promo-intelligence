"""
Scenario Lab API Routes

Endpoints for scenario creation, evaluation, and comparison.
"""

import json
import uuid
from datetime import date
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.schemas import PromoScenario, ScenarioKPI, ValidationReport, DateRange
from middleware.auth import get_current_user, require_analyst
from middleware.rate_limit import get_rate_limit
from engines.scenario_evaluation_engine import ScenarioEvaluationEngine
from engines.validation_engine import ValidationEngine
from engines.forecast_baseline_engine import ForecastBaselineEngine
from engines.uplift_elasticity_engine import UpliftElasticityEngine
from engines.context_engine import ContextEngine
from tools.sales_data_tool import SalesDataTool
from tools.targets_config_tool import TargetsConfigTool
from tools.context_data_tool import ContextDataTool
from db.base import Scenario as ScenarioModel, ScenarioKPI as ScenarioKPIModel
from db.session import get_session

router = APIRouter(dependencies=[Depends(get_current_user)])

# Initialize engines and tools
sales_tool = SalesDataTool()
targets_tool = TargetsConfigTool()
context_tool = ContextDataTool()
baseline_engine = ForecastBaselineEngine(sales_data_tool=sales_tool, targets_tool=targets_tool)
uplift_engine = UpliftElasticityEngine(sales_data_tool=sales_tool)
evaluation_engine = ScenarioEvaluationEngine(uplift_engine=uplift_engine)
validation_engine = ValidationEngine(config_tool=targets_tool)
context_engine = ContextEngine(context_tool=context_tool)

class ScenarioBrief(BaseModel):
    month: Optional[str] = None
    promo_date_range: Optional[Dict[str, str]] = None
    focus_departments: Optional[List[str]] = None
    objectives: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None


class ScenarioCreatePayload(BaseModel):
    brief: ScenarioBrief
    scenario_type: Optional[str] = "balanced"


def _model_to_promo_scenario(model: ScenarioModel) -> PromoScenario:
    return PromoScenario(
        id=model.id,
        name=model.name,
        description=model.description,
        date_range=DateRange(start_date=model.date_start, end_date=model.date_end),
        departments=json.loads(model.departments or "[]"),
        channels=json.loads(model.channels or "[]"),
        discount_percentage=model.discount_percentage,
        segments=json.loads(model.segments or "[]") if model.segments else None,
        # Always return a dict to avoid AttributeError on callers using .get()
        metadata=json.loads(model.metadata or "{}") if model.metadata else {},
    )


def _store_promo_scenario(db: Session, scenario: PromoScenario, created_by: str) -> ScenarioModel:
    record = ScenarioModel(
        id=scenario.id or str(uuid.uuid4()),
        name=scenario.name,
        description=scenario.description,
        date_start=scenario.date_range.start_date,
        date_end=scenario.date_range.end_date,
        departments=json.dumps(scenario.departments),
        channels=json.dumps(scenario.channels),
        discount_percentage=scenario.discount_percentage,
        segments=json.dumps(scenario.segments or []),
        metadata=json.dumps(scenario.metadata or {}),
        created_by=created_by,
    )
    db.merge(record)
    db.commit()
    return db.get(ScenarioModel, record.id)


def _persist_kpi(db: Session, scenario_id: str, kpi: ScenarioKPI) -> ScenarioKPIModel:
    record = ScenarioKPIModel(
        scenario_id=scenario_id,
        total_sales=kpi.total_sales,
        total_margin=kpi.total_margin,
        total_ebit=kpi.total_ebit,
        total_units=kpi.total_units,
        breakdown_by_channel=json.dumps(kpi.breakdown_by_channel),
        breakdown_by_department=json.dumps(kpi.breakdown_by_department),
        comparison_vs_baseline=json.dumps(kpi.comparison_vs_baseline),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("")
@router.post("/", include_in_schema=False)
@router.post("/create", include_in_schema=False)
@get_rate_limit("standard")
async def create_scenario(
    payload: Optional[ScenarioCreatePayload] = None,
    brief: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    current_user=Depends(require_analyst),
    db: Session = Depends(get_session),
) -> dict:
    """
    Create a promotional scenario from a structured brief (spec) or legacy params.
    """
    params = parameters or {}
    scenario_brief = payload.brief if payload else None

    date_range = None
    if scenario_brief and scenario_brief.promo_date_range:
        try:
            date_range = DateRange(
                start_date=date.fromisoformat(scenario_brief.promo_date_range.get("start")),
                end_date=date.fromisoformat(scenario_brief.promo_date_range.get("end")),
            )
        except Exception:
            pass
    elif params.get("date_range"):
        dr = params["date_range"]
        if dr:
            date_range = DateRange(
                start_date=dr.get("start_date"),
                end_date=dr.get("end_date"),
            )

    scenario = PromoScenario(
        id=str(uuid.uuid4()),
        name=params.get("name", "Scenario"),
        description=brief or (scenario_brief.month if scenario_brief else "Scenario"),
        date_range=date_range or DateRange(
            start_date=date.today(),
            end_date=date.today(),
        ),
        departments=(scenario_brief.focus_departments or params.get("departments", ["TV", "Gaming"]) if scenario_brief else params.get("departments", ["TV", "Gaming"])),
        channels=params.get("channels", ["online", "store"]),
        discount_percentage=params.get("discount_percentage", 15.0),
        segments=params.get("segments"),
        metadata={"objectives": scenario_brief.objectives if scenario_brief else {}},
    )

    stored = _store_promo_scenario(db, scenario, created_by=current_user.user_id)
    dept = scenario.departments[0] if scenario.departments else "unknown"
    channel = scenario.channels[0] if scenario.channels else "unknown"

    scenario_type = payload.scenario_type if payload is not None and payload.scenario_type else "balanced"

    response = {
        "scenario": {
            "id": stored.id,
            "label": scenario_type,
            "date_range": {
                "start": stored.date_start.isoformat(),
                "end": stored.date_end.isoformat(),
            },
            "mechanics": [
                {
                    "department": dept,
                    "channel": channel,
                    "discount_pct": scenario.discount_percentage,
                    "segments": scenario.segments or ["ALL"],
                }
            ],
        }
    }
    return response


@router.get("/{scenario_id}")
@get_rate_limit("standard")
async def get_scenario(
    scenario_id: str,
    current_user=Depends(require_analyst),
    db: Session = Depends(get_session),
):
    """Get scenario details."""
    stored = db.get(ScenarioModel, scenario_id)
    if not stored:
        raise HTTPException(status_code=404, detail="Scenario not found")
    scenario = _model_to_promo_scenario(stored)
    return {
        "scenario": {
            "id": scenario.id,
            "label": scenario.name,
            "date_range": {
                "start": scenario.date_range.start_date.isoformat(),
                "end": scenario.date_range.end_date.isoformat(),
            },
            "mechanics": scenario.metadata.get("mechanics", []),
        }
    }


@router.put("/{scenario_id}")
@get_rate_limit("standard")
async def update_scenario(
    scenario_id: str,
    updated: PromoScenario,
    current_user=Depends(require_analyst),
    db: Session = Depends(get_session),
) -> dict:
    """Update scenario."""
    existing = db.get(ScenarioModel, scenario_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Scenario not found")
    updated.id = scenario_id
    stored = _store_promo_scenario(db, updated, created_by=current_user.user_id)
    return {"scenario": _model_to_promo_scenario(stored)}


@router.delete("/{scenario_id}")
@get_rate_limit("standard")
async def delete_scenario(
    scenario_id: str,
    current_user=Depends(require_analyst),
    db: Session = Depends(get_session),
) -> dict:
    """Delete scenario."""
    existing = db.get(ScenarioModel, scenario_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(existing)
    db.commit()
    return {"deleted": True, "scenario_id": scenario_id}


@router.post("/evaluate")
@get_rate_limit("standard")
async def evaluate_scenario(
    scenario: PromoScenario,
    current_user=Depends(require_analyst),
    db: Session = Depends(get_session),
) -> ScenarioKPI:
    """
    Evaluate scenario and calculate KPIs.
    
    Args:
        scenario: PromoScenario to evaluate
    
    Returns:
        ScenarioKPI object
    """
    try:
        # Calculate baseline forecast
        baseline = baseline_engine.calculate_baseline(
            (scenario.date_range.start_date, scenario.date_range.end_date)
        )
        
        # Build uplift model
        uplift_model = uplift_engine.build_uplift_model({})
        
        # Get context
        context = context_engine.build_context(
            geo="DE",  # Default geo, could be parameterized
            date_range=DateRange(
                start_date=scenario.date_range.start_date,
                end_date=scenario.date_range.end_date
            )
        )
        
        # Evaluate scenario
        kpi = evaluation_engine.evaluate_scenario(
            scenario=scenario,
            baseline=baseline,
            uplift_model=uplift_model,
            context=context
        )
        _persist_kpi(db, scenario.id, kpi)
        return kpi
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error evaluating scenario: {str(exc)}") from exc


@router.post("/compare")
@get_rate_limit("standard")
async def compare_scenarios(
    scenarios: List[PromoScenario] = Body(default=None),
    scenario_ids: Optional[List[str]] = None,
    current_user=Depends(require_analyst),
    db: Session = Depends(get_session),
) -> ComparisonReport:
    """
    Compare multiple scenarios side-by-side.
    
    Args:
        scenarios: List of PromoScenario objects
    
    Returns:
        ComparisonReport object
    """
    if not scenarios and scenario_ids:
        scenarios = []
        for sid in scenario_ids:
            stored = db.get(ScenarioModel, sid)
            if stored:
                scenarios.append(_model_to_promo_scenario(stored))
    if not scenarios:
        raise HTTPException(status_code=400, detail="At least one scenario is required")
    
    try:
        # Evaluate all scenarios
        kpis: List[ScenarioKPI] = []
        for scenario in scenarios:
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
            kpi = evaluation_engine.evaluate_scenario(scenario, baseline, uplift_model, context)
            kpis.append(kpi)
        
        # Build comparison table
        comparison_table: Dict[str, List[float]] = {
            "sales": [kpi.total_sales for kpi in kpis],
            "margin": [kpi.total_margin for kpi in kpis],
            "ebit": [kpi.total_ebit for kpi in kpis],
            "units": [kpi.total_units for kpi in kpis],
        }
        
        # Generate recommendations (simplified)
        recommendations: List[str] = []
        if kpis:
            best_sales_idx = max(range(len(kpis)), key=lambda i: kpis[i].total_sales)
            best_margin_idx = max(range(len(kpis)), key=lambda i: kpis[i].total_margin)
            
            if best_sales_idx == best_margin_idx:
                recommendations.append(f"Scenario {best_sales_idx + 1} offers the best balance of sales and margin")
            else:
                recommendations.append(f"Scenario {best_sales_idx + 1} maximizes sales")
                recommendations.append(f"Scenario {best_margin_idx + 1} maximizes margin")
        
        return ComparisonReport(
            scenarios=scenarios,
            kpis=kpis,
            comparison_table=comparison_table,
            recommendations=recommendations,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error comparing scenarios: {str(exc)}") from exc


@router.post("/validate")
@get_rate_limit("standard")
async def validate_scenario(
    scenario: PromoScenario,
    kpi: Optional[ScenarioKPI] = None,
    current_user=Depends(require_analyst),
) -> ValidationReport:
    """
    Validate scenario against business rules.
    
    Args:
        scenario: PromoScenario to validate
        kpi: Optional ScenarioKPI for validation
    
    Returns:
        ValidationReport object
    """
    try:
        # If KPI not provided, evaluate scenario first
        if kpi is None:
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
            kpi = evaluation_engine.evaluate_scenario(scenario, baseline, uplift_model, context)
        
        # Validate scenario
        report = validation_engine.validate_scenario(scenario, kpi)
        
        return report
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error validating scenario: {str(exc)}") from exc
