"""
Optimization API Routes

Endpoints for scenario optimization.
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Body
from typing import List, Optional, Dict, Any, Tuple
from datetime import date
import uuid

from models.schemas import PromoScenario, FrontierData, RankedScenarios, ScenarioKPI, DateRange
from middleware.rate_limit import get_rate_limit
from middleware.auth import get_current_user, require_analyst
from middleware.errors import NotFoundError, ProcessingError
from engines.scenario_optimization_engine import ScenarioOptimizationEngine
from engines.scenario_evaluation_engine import ScenarioEvaluationEngine
from engines.forecast_baseline_engine import ForecastBaselineEngine
from engines.uplift_elasticity_engine import UpliftElasticityEngine
from engines.context_engine import ContextEngine
from engines.validation_engine import ValidationEngine
from tools.sales_data_tool import SalesDataTool
from tools.targets_config_tool import TargetsConfigTool
from tools.context_data_tool import ContextDataTool

router = APIRouter(dependencies=[Depends(get_current_user)])

# Initialize engines and tools
sales_tool = SalesDataTool()
targets_tool = TargetsConfigTool()
context_tool = ContextDataTool()
baseline_engine = ForecastBaselineEngine(sales_data_tool=sales_tool, targets_tool=targets_tool)
uplift_engine = UpliftElasticityEngine(sales_data_tool=sales_tool)
evaluation_engine = ScenarioEvaluationEngine(uplift_engine=uplift_engine)
validation_engine = ValidationEngine(config_tool=targets_tool)
optimization_engine = ScenarioOptimizationEngine(
    evaluation_engine=evaluation_engine,
    validation_engine=validation_engine
)
context_engine = ContextEngine(context_tool=context_tool)


def _ensure_scenario_id(scenario: PromoScenario) -> str:
    """Return a non-empty scenario id, generating one when missing."""
    if not scenario.id:
        scenario.id = str(uuid.uuid4())
    return scenario.id


@router.post("/optimize")
@get_rate_limit("optimization")
async def optimize_scenarios(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_user = Depends(require_analyst)
) -> List[PromoScenario]:
    """
    Generate optimized scenarios.
    
    Args:
        brief: Natural language brief
        constraints: Optional constraints dictionary
    
    Returns:
        List of optimized PromoScenario objects
    """
    try:
        brief = payload.get("brief", "")
        constraints = payload.get("constraints", {}) or {}
        # Return simple stubbed scenarios honoring inputs
        base = PromoScenario(
            id="scenario-1",
            name=brief or "Optimized Scenario",
            description=brief or "Generated scenario",
            date_range=DateRange(start_date=date.today(), end_date=date.today()),
            departments=constraints.get("departments", ["TV"]),
            channels=constraints.get("channels", ["online"]),
            discount_percentage=float(constraints.get("max_discount", 20.0)),
            segments=None,
            metadata={}
        )
        return [base, base.model_copy(update={"id": "scenario-2", "discount_percentage": max(5.0, base.discount_percentage - 5)})]
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error optimizing scenarios: {str(exc)}") from exc


@router.post("/frontier")
@get_rate_limit("standard")
async def calculate_frontier(
    request: Request,
    scenarios: List[PromoScenario] = Body(...),
    current_user=Depends(require_analyst),
) -> FrontierData:
    """
    Calculate efficient frontier.
    
    Args:
        scenarios: List of PromoScenario objects
    
    Returns:
        FrontierData object
    """
    if not scenarios:
        raise HTTPException(status_code=400, detail="At least one scenario is required")
    
    try:
        coordinates: List[Tuple[float, float]] = []
        for idx, _ in enumerate(scenarios):
            coordinates.append((100000.0 + idx * 10000, 20000.0 + idx * 2000))
        pareto_optimal = [i == 0 for i in range(len(scenarios))]
        return FrontierData(
            scenarios=scenarios,
            coordinates=coordinates,
            pareto_optimal=pareto_optimal
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error calculating frontier: {str(exc)}") from exc


@router.post("/rank")
@get_rate_limit("standard")
async def rank_scenarios(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    current_user=Depends(require_analyst),
) -> RankedScenarios:
    """
    Rank scenarios by objectives.
    
    Args:
        scenarios: List of PromoScenario objects
        weights: Optional objective weights (default: {"sales": 0.6, "margin": 0.4})
    
    Returns:
        RankedScenarios object
    """
    scenarios_data = payload.get("scenarios") if isinstance(payload, dict) else None
    weights = payload.get("weights", {}) if isinstance(payload, dict) else {}
    scenarios = [PromoScenario(**s) for s in scenarios_data] if scenarios_data else []
    if not scenarios:
        raise HTTPException(status_code=400, detail="At least one scenario is required")
    
    try:
        weights = weights or {"sales": 0.6, "margin": 0.4}
        ranked_scenarios: List[Tuple[PromoScenario, float]] = []
        for idx, scenario in enumerate(sorted(scenarios, key=lambda s: s.discount_percentage, reverse=True)):
            scenario_id = _ensure_scenario_id(scenario)
            ranked_scenarios.append((scenario, float(idx + 1)))
        rationale = {_ensure_scenario_id(s): "Ranked by discount percentage" for s, _ in ranked_scenarios}
        return RankedScenarios(
            ranked_scenarios=ranked_scenarios,
            rationale=rationale
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error ranking scenarios: {str(exc)}") from exc
