"""
Optimization API Routes

Endpoints for scenario optimization.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from typing import List, Optional, Dict, Any, Tuple

from models.schemas import PromoScenario, FrontierData, RankedScenarios, ScenarioKPI, DateRange
from middleware.rate_limit import get_rate_limit
from middleware.auth import get_current_user
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

router = APIRouter()

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


@router.post("/optimize")
@get_rate_limit("optimization")
async def optimize_scenarios(
    brief: str,
    constraints: Optional[Dict[str, Any]] = None,
    request: Request = None,
    current_user = Depends(get_current_user)
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
        # Generate candidate scenarios
        candidates = optimization_engine.generate_candidate_scenarios(brief, constraints)
        
        # Evaluate and rank them
        objectives = constraints.get("objectives", {"sales": 0.6, "margin": 0.4}) if constraints else {"sales": 0.6, "margin": 0.4}
        optimized = optimization_engine.optimize_scenarios(candidates, objectives, constraints)
        
        return optimized
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error optimizing scenarios: {str(exc)}") from exc


@router.post("/frontier")
async def calculate_frontier(
    scenarios: List[PromoScenario]
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
        
        # Build coordinates (sales, margin) for frontier
        coordinates: List[Tuple[float, float]] = [
            (kpi.total_sales, kpi.total_margin) for kpi in kpis
        ]
        
        # Identify Pareto-optimal scenarios (scenarios that are not dominated)
        pareto_optimal: List[bool] = []
        for i, kpi in enumerate(kpis):
            is_optimal = True
            for j, other_kpi in enumerate(kpis):
                if i != j:
                    # Check if other scenario dominates this one
                    if (other_kpi.total_sales >= kpi.total_sales and 
                        other_kpi.total_margin >= kpi.total_margin and
                        (other_kpi.total_sales > kpi.total_sales or other_kpi.total_margin > kpi.total_margin)):
                        is_optimal = False
                        break
            pareto_optimal.append(is_optimal)
        
        return FrontierData(
            scenarios=scenarios,
            coordinates=coordinates,
            pareto_optimal=pareto_optimal
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error calculating frontier: {str(exc)}") from exc


@router.post("/rank")
async def rank_scenarios(
    scenarios: List[PromoScenario],
    weights: Optional[Dict[str, float]] = None
) -> RankedScenarios:
    """
    Rank scenarios by objectives.
    
    Args:
        scenarios: List of PromoScenario objects
        weights: Optional objective weights (default: {"sales": 0.6, "margin": 0.4})
    
    Returns:
        RankedScenarios object
    """
    if not scenarios:
        raise HTTPException(status_code=400, detail="At least one scenario is required")
    
    try:
        # Default weights
        weights = weights or {"sales": 0.6, "margin": 0.4}
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        # Evaluate all scenarios
        scenario_scores: List[Tuple[PromoScenario, float]] = []
        
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
            
            # Calculate composite score
            # Normalize sales and margin to 0-1 scale (using max values as reference)
            # For MVP, use simple scoring
            sales_score = kpi.total_sales / 1000000.0  # Normalize to millions
            margin_score = (kpi.total_margin / kpi.total_sales) if kpi.total_sales > 0 else 0.0
            
            composite_score = (
                weights.get("sales", 0.5) * sales_score +
                weights.get("margin", 0.5) * margin_score
            )
            
            scenario_scores.append((scenario, composite_score))
        
        # Sort by score (descending)
        scenario_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Generate rationale
        rationale: Dict[str, str] = {}
        for i, (scenario, score) in enumerate(scenario_scores):
            rank = i + 1
            rationale[scenario.id or f"scenario_{i}"] = (
                f"Rank {rank}: Score {score:.3f} "
                f"(Sales weight: {weights.get('sales', 0.5):.2f}, "
                f"Margin weight: {weights.get('margin', 0.5):.2f})"
            )
        
        return RankedScenarios(
            ranked_scenarios=scenario_scores,
            rationale=rationale
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Error ranking scenarios: {str(exc)}") from exc
