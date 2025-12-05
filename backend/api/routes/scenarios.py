"""
Scenario Lab API Routes

Endpoints for scenario creation, evaluation, and comparison.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
import uuid

from models.schemas import PromoScenario, ScenarioKPI, ComparisonReport, ValidationReport, BaselineForecast, DateRange
from engines.scenario_evaluation_engine import ScenarioEvaluationEngine
from engines.validation_engine import ValidationEngine
from engines.forecast_baseline_engine import ForecastBaselineEngine
from engines.uplift_elasticity_engine import UpliftElasticityEngine
from engines.context_engine import ContextEngine
from tools.sales_data_tool import SalesDataTool
from tools.targets_config_tool import TargetsConfigTool
from tools.context_data_tool import ContextDataTool

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

# In-memory scenario store (for demo; replace with DB in production)
SCENARIO_STORE: Dict[str, PromoScenario] = {}


@router.post("/create")
async def create_scenario(
    brief: str,
    parameters: Optional[Dict[str, Any]] = None
) -> PromoScenario:
    """
    Create a promotional scenario from brief.
    
    Args:
        brief: Natural language brief
        parameters: Optional scenario parameters
    
    Returns:
        PromoScenario object
    """
    # Parse parameters or use defaults
    params = parameters or {}
    
    # Extract scenario details from brief/parameters
    # For MVP: use parameters directly, in production this would use LLM to parse brief
    scenario = PromoScenario(
        id=str(uuid.uuid4()),
        name=params.get("name", f"Scenario from brief"),
        description=brief,
        date_range=params.get("date_range"),
        departments=params.get("departments", ["TV", "Gaming"]),
        channels=params.get("channels", ["online", "store"]),
        discount_percentage=params.get("discount_percentage", 15.0),
        segments=params.get("segments"),
        metadata=params.get("metadata"),
    )
    SCENARIO_STORE[scenario.id] = scenario
    return scenario


@router.get("/{scenario_id}")
async def get_scenario(scenario_id: str) -> PromoScenario:
    """Get scenario details."""
    scenario = SCENARIO_STORE.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.put("/{scenario_id}")
async def update_scenario(scenario_id: str, updated: PromoScenario) -> PromoScenario:
    """Update scenario."""
    if scenario_id not in SCENARIO_STORE:
        raise HTTPException(status_code=404, detail="Scenario not found")
    SCENARIO_STORE[scenario_id] = updated
    return updated


@router.delete("/{scenario_id}")
async def delete_scenario(scenario_id: str) -> dict:
    """Delete scenario."""
    if scenario_id not in SCENARIO_STORE:
        raise HTTPException(status_code=404, detail="Scenario not found")
    del SCENARIO_STORE[scenario_id]
    return {"deleted": True, "scenario_id": scenario_id}


@router.post("/evaluate")
async def evaluate_scenario(
    scenario: PromoScenario
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
        
        return kpi
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error evaluating scenario: {str(exc)}") from exc


@router.post("/compare")
async def compare_scenarios(
    scenarios: List[PromoScenario] = None,
    scenario_ids: Optional[List[str]] = None
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
            stored = SCENARIO_STORE.get(sid)
            if stored:
                scenarios.append(stored)
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
            recommendations=recommendations
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error comparing scenarios: {str(exc)}") from exc


@router.post("/validate")
async def validate_scenario(
    scenario: PromoScenario,
    kpi: Optional[ScenarioKPI] = None
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
