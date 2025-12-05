"""
Scenario Lab API Routes

Endpoints for scenario creation, evaluation, and comparison.
"""

from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Optional, Dict, Any
import uuid
import json
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.schemas import PromoScenario, ScenarioKPI, ValidationReport, BaselineForecast, DateRange
from engines.scenario_evaluation_engine import ScenarioEvaluationEngine
from engines.validation_engine import ValidationEngine
from engines.forecast_baseline_engine import ForecastBaselineEngine
from engines.uplift_elasticity_engine import UpliftElasticityEngine
from engines.context_engine import ContextEngine
from tools.sales_data_tool import SalesDataTool
from tools.targets_config_tool import TargetsConfigTool
from tools.context_data_tool import ContextDataTool
from db.session import get_session
from db.base import Scenario as ScenarioDB, ScenarioKPI as ScenarioKPIDB, ValidationReportDB

router = APIRouter()

# Initialize engines and tools
sales_tool = SalesDataTool()
targets_tool = TargetsConfigTool()
context_tool = ContextDataTool()
baseline_engine = ForecastBaselineEngine(sales_data_tool=sales_tool, targets_tool=targets_tool)
uplift_engine = UpliftElasticityEngine(sales_data_tool=sales_tool)
evaluation_engine = ScenarioEvaluationEngine(uplift_engine=uplift_engine)
validation_engine = ValidationEngine(config_tool=targets_tool)
context_engine = ContextEngine(context_tool=context_tool)

# In-memory scenario store (legacy fallback)
SCENARIO_STORE: Dict[str, PromoScenario] = {}


class PromoDateRange(BaseModel):
    start: str
    end: str


class PromoBrief(BaseModel):
    month: str
    promo_date_range: PromoDateRange
    focus_departments: List[str]
    objectives: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None


class CreateScenarioRequest(BaseModel):
    brief: PromoBrief
    scenario_type: str = "balanced"
    parameters: Optional[Dict[str, Any]] = None


class UpdateScenarioRequest(BaseModel):
    mechanics: Optional[List[Dict[str, Any]]] = None
    departments: Optional[List[str]] = None
    channels: Optional[List[str]] = None
    discount_pct: Optional[float] = None
    segments: Optional[List[str]] = None


class CompareRequest(BaseModel):
    scenarios: Optional[List[PromoScenario]] = None
    scenario_ids: Optional[List[str]] = None


def _build_default_scenario(
    brief: PromoBrief,
    parameters: Optional[Dict[str, Any]] = None,
    scenario_type: str = "balanced"
) -> PromoScenario:
    """Create a simple scenario object from a brief/parameters."""
    params = parameters or {}
    start_raw = params.get("start_date") or brief.promo_date_range.start
    end_raw = params.get("end_date") or brief.promo_date_range.end
    from datetime import date as date_type

    def _coerce(value):
        if isinstance(value, str):
            return date_type.fromisoformat(value)
        return value

    start_date = _coerce(start_raw)
    end_date = _coerce(end_raw)
    return PromoScenario(
        id=str(uuid.uuid4()),
        name=params.get("name", f"{brief.month} {params.get('label', 'Scenario')}"),
        description=params.get("description") or f"{scenario_type.title()} scenario for {brief.month}",
        date_range=DateRange(
            start_date=start_date,  # type: ignore[arg-type]
            end_date=end_date,      # type: ignore[arg-type]
        ),
        departments=params.get("departments", brief.focus_departments or ["TV", "Gaming"]),
        channels=params.get("channels", ["online", "store"]),
        discount_percentage=float(params.get("discount_pct", params.get("discount_percentage", 15.0))),
        segments=params.get("segments"),
        metadata={"objectives": brief.objectives or {}, "constraints": brief.constraints or {}},
    )


def _serialize_scenario(scenario: PromoScenario, label: Optional[str] = None) -> Dict[str, Any]:
    """Return a docs-friendly scenario payload."""
    mechanics = [
        {
            "department": dept,
            "channel": ch,
            "discount_pct": scenario.discount_percentage,
            "segments": scenario.segments or ["ALL"],
        }
        for dept in scenario.departments
        for ch in scenario.channels
    ]
    return {
        "id": scenario.id,
        "label": label or scenario.name,
        "name": scenario.name,
        "description": scenario.description,
        "mechanics": mechanics,
        "date_range": {
            "start": scenario.date_range.start_date.isoformat(),
            "end": scenario.date_range.end_date.isoformat(),
        },
        "departments": scenario.departments,
        "channels": scenario.channels,
        "discount_percentage": scenario.discount_percentage,
        "segments": scenario.segments,
        "metadata": scenario.metadata or {},
    }


def _scenario_from_db(row: ScenarioDB) -> PromoScenario:
    """Convert DB row to domain schema."""
    import datetime

    def _loads(val, default):
        try:
            return json.loads(val) if val else default
        except Exception:
            return default

    return PromoScenario(
        id=row.id,
        name=row.name,
        description=row.description,
        date_range=DateRange(
            start_date=row.date_start if isinstance(row.date_start, datetime.date) else DateRange.model_validate({"start_date": row.date_start, "end_date": row.date_end}).start_date,
            end_date=row.date_end,
        ),
        departments=_loads(row.departments, []),
        channels=_loads(row.channels, []),
        discount_percentage=row.discount_percentage,
        segments=_loads(row.segments, None),
        metadata=_loads(row.metadata, None),
    )


def _persist_scenario(db: Session, scenario: PromoScenario, created_by: Optional[str] = None) -> None:
    """Upsert scenario to DB."""
    record = db.query(ScenarioDB).filter(ScenarioDB.id == scenario.id).one_or_none()
    payload = {
        "id": scenario.id,
        "name": scenario.name,
        "description": scenario.description,
        "date_start": scenario.date_range.start_date,
        "date_end": scenario.date_range.end_date,
        "departments": json.dumps(scenario.departments),
        "channels": json.dumps(scenario.channels),
        "discount_percentage": scenario.discount_percentage,
        "segments": json.dumps(scenario.segments) if scenario.segments else None,
        "metadata": json.dumps(scenario.metadata) if scenario.metadata else None,
        "created_by": created_by,
    }
    if record:
        for k, v in payload.items():
            setattr(record, k, v)
    else:
        record = ScenarioDB(**payload)
        db.add(record)
    db.flush()


def _persist_kpi(db: Session, scenario_id: str, kpi: ScenarioKPI) -> None:
    """Store KPI snapshot."""
    kpi_row = ScenarioKPIDB(
        scenario_id=scenario_id,
        total_sales=kpi.total_sales,
        total_margin=kpi.total_margin,
        total_ebit=kpi.total_ebit,
        total_units=kpi.total_units,
        breakdown_by_channel=json.dumps(kpi.breakdown_by_channel),
        breakdown_by_department=json.dumps(kpi.breakdown_by_department),
        comparison_vs_baseline=json.dumps(kpi.comparison_vs_baseline),
    )
    db.add(kpi_row)
    db.flush()


def _persist_validation(db: Session, scenario_id: str, validation: ValidationReport) -> None:
    """Store validation report snapshot."""
    val_row = ValidationReportDB(
        scenario_id=scenario_id,
        is_valid=validation.is_valid,
        issues=json.dumps(validation.issues),
        fixes=json.dumps(validation.fixes),
        checks_passed=json.dumps(validation.checks_passed),
    )
    db.add(val_row)
    db.flush()


def _get_scenario(db: Session, scenario_id: str) -> Optional[PromoScenario]:
    row = db.query(ScenarioDB).filter(ScenarioDB.id == scenario_id).one_or_none()
    if row:
        return _scenario_from_db(row)
    return SCENARIO_STORE.get(scenario_id)


@router.post("/create")
async def create_scenario(
    payload: CreateScenarioRequest,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Create a promotional scenario from brief (docs-compliant response shape).
    """
    scenario = _build_default_scenario(payload.brief, payload.parameters, payload.scenario_type)
    SCENARIO_STORE[scenario.id] = scenario

    # Evaluate immediately for demo determinism
    baseline = baseline_engine.calculate_baseline(
        (scenario.date_range.start_date, scenario.date_range.end_date)
    )
    uplift_model = uplift_engine.build_uplift_model({})
    context = context_engine.build_context(
        geo=payload.brief.objectives.get("geo", "DE") if payload.brief.objectives else "DE",
        date_range=DateRange(
            start_date=scenario.date_range.start_date,
            end_date=scenario.date_range.end_date
        )
    )
    kpi = evaluation_engine.evaluate_scenario(scenario, baseline, uplift_model, context)
    validation = validation_engine.validate_scenario(scenario)

    _persist_scenario(db, scenario)
    _persist_kpi(db, scenario.id, kpi)
    _persist_validation(db, scenario.id, validation)
    db.commit()

    return {
        "scenario": _serialize_scenario(scenario, label=payload.scenario_type.title()),
        "kpi": kpi,
        "validation": validation,
    }


@router.get("/{scenario_id}")
async def get_scenario(
    scenario_id: str,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get scenario details with KPIs and validation."""
    scenario = _get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
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
    validation = validation_engine.validate_scenario(scenario, kpi)
    _persist_scenario(db, scenario)
    _persist_kpi(db, scenario.id, kpi)
    _persist_validation(db, scenario.id, validation)
    db.commit()
    return {"scenario": _serialize_scenario(scenario), "kpi": kpi, "validation": validation}


@router.put("/{scenario_id}")
async def update_scenario(
    scenario_id: str,
    updated: UpdateScenarioRequest,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Update scenario parameters then re-evaluate."""
    existing = _get_scenario(db, scenario_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Scenario not found")
    existing.departments = updated.departments or existing.departments
    existing.channels = updated.channels or existing.channels
    if updated.discount_pct is not None:
        existing.discount_percentage = updated.discount_pct
    if updated.segments is not None:
        existing.segments = updated.segments
    SCENARIO_STORE[scenario_id] = existing

    baseline = baseline_engine.calculate_baseline(
        (existing.date_range.start_date, existing.date_range.end_date)
    )
    uplift_model = uplift_engine.build_uplift_model({})
    context = context_engine.build_context(
        geo="DE",
        date_range=DateRange(
            start_date=existing.date_range.start_date,
            end_date=existing.date_range.end_date
        )
    )
    kpi = evaluation_engine.evaluate_scenario(existing, baseline, uplift_model, context)
    validation = validation_engine.validate_scenario(existing, kpi)
    _persist_scenario(db, existing)
    _persist_kpi(db, existing.id, kpi)
    _persist_validation(db, existing.id, validation)
    db.commit()
    return {"scenario": _serialize_scenario(existing), "kpi": kpi, "validation": validation}


@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: str,
    db: Session = Depends(get_session)
) -> dict:
    """Delete scenario."""
    # Delete DB first
    db.query(ScenarioKPIDB).filter(ScenarioKPIDB.scenario_id == scenario_id).delete()
    db.query(ValidationReportDB).filter(ValidationReportDB.scenario_id == scenario_id).delete()
    deleted = db.query(ScenarioDB).filter(ScenarioDB.id == scenario_id).delete()
    db.commit()
    if scenario_id in SCENARIO_STORE:
        del SCENARIO_STORE[scenario_id]
    if not deleted:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"deleted": True, "scenario_id": scenario_id}


@router.post("/evaluate")
async def evaluate_scenario(
    scenario: PromoScenario,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Evaluate scenario and calculate KPIs.
    
    Args:
        scenario: PromoScenario to evaluate
    
    Returns:
        ScenarioKPI object
    """
    try:
        # Ensure scenario has an ID for persistence
        if not scenario.id:
            scenario.id = str(uuid.uuid4())

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
        
        kpi = evaluation_engine.evaluate_scenario(
            scenario=scenario,
            baseline=baseline,
            uplift_model=uplift_model,
            context=context
        )
        validation = validation_engine.validate_scenario(scenario, kpi)
        _persist_scenario(db, scenario)
        _persist_kpi(db, scenario.id, kpi)
        _persist_validation(db, scenario.id, validation)
        db.commit()
        return {"kpi": kpi, "validation": validation}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error evaluating scenario: {str(exc)}") from exc


@router.post("/{scenario_id}/evaluate")
async def evaluate_scenario_by_id(
    scenario_id: str,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Docs-friendly: re-evaluate an existing scenario by id and return KPIs + validation.
    """
    scenario = _get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return await evaluate_scenario(scenario, db)


@router.post("/compare")
async def compare_scenarios(
    payload: Any = Body(...),
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Compare multiple scenarios side-by-side.
    
    Args:
        scenarios: List of PromoScenario objects
    
    Returns:
        ComparisonReport object
    """
    scenarios: List[PromoScenario] = []
    scenario_ids: Optional[List[str]] = None

    # Support both structured payload and raw list for backward compatibility
    if isinstance(payload, dict):
        scenario_ids = payload.get("scenario_ids")
        scenarios = payload.get("scenarios") or []
    elif isinstance(payload, list):
        scenarios = payload

    if not scenarios and scenario_ids:
        for sid in scenario_ids:
            stored = _get_scenario(db, sid)
            if stored:
                scenarios.append(stored)
    if not scenarios:
        raise HTTPException(status_code=400, detail="At least one scenario is required")

    scenarios = [
        s if isinstance(s, PromoScenario) else PromoScenario.model_validate(s)
        for s in scenarios
    ]
    
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
        
        comparison_table: Dict[str, List[float]] = {
            "sales": [kpi.total_sales for kpi in kpis],
            "margin": [kpi.total_margin for kpi in kpis],
            "ebit": [kpi.total_ebit for kpi in kpis],
            "units": [kpi.total_units for kpi in kpis],
        }

        recommendations: List[str] = []
        summary: Dict[str, Any] = {}
        if kpis:
            best_sales_idx = max(range(len(kpis)), key=lambda i: kpis[i].total_sales)
            best_margin_idx = max(range(len(kpis)), key=lambda i: kpis[i].total_margin)

            summary = {
                "best_sales": scenarios[best_sales_idx].id or f"scenario_{best_sales_idx+1}",
                "best_margin": scenarios[best_margin_idx].id or f"scenario_{best_margin_idx+1}",
            }

            if best_sales_idx == best_margin_idx:
                recommendations.append("Best balance of sales and margin")
            else:
                recommendations.append("One scenario maximizes sales; another maximizes margin")

        doc_scenarios = [
            {
                "id": s.id,
                "label": s.name,
                "kpi": kpis[idx],
            }
            for idx, s in enumerate(scenarios)
        ]

        return {
            "scenarios": scenarios,
            "kpis": kpis,
            "comparison_table": comparison_table,
            "recommendations": recommendations,
            "comparison": {
                "scenarios": doc_scenarios,
                "summary": summary,
            },
        }
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error comparing scenarios: {str(exc)}") from exc


@router.post("/validate")
async def validate_scenario(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_session)
) -> ValidationReport:
    """
    Validate scenario against business rules.
    """
    try:
        scenario_data = payload.get("scenario", payload)
        kpi_data = payload.get("kpi")
        scenario = scenario_data if isinstance(scenario_data, PromoScenario) else PromoScenario.model_validate(scenario_data)
        kpi_obj = None
        if kpi_data:
            kpi_obj = kpi_data if isinstance(kpi_data, ScenarioKPI) else ScenarioKPI.model_validate(kpi_data)

        if kpi_obj is None:
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
            kpi_obj = evaluation_engine.evaluate_scenario(scenario, baseline, uplift_model, context)
        
        report = validation_engine.validate_scenario(scenario, kpi_obj)
        _persist_validation(db, scenario.id, report)
        db.commit()
        return report
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error validating scenario: {str(exc)}") from exc
