"""
Engines Module

Business logic and computation modules:
- Context Engine: Builds comprehensive context for promotional planning
- Forecast & Baseline Engine: Calculates baseline forecasts
- Uplift & Elasticity Engine: Estimates promotional uplift
- Scenario Evaluation Engine: Calculates KPIs for scenarios
- Scenario Optimization Engine: Generates and optimizes scenarios
- Validation Engine: Validates scenarios against business rules
- Creative Engine: Generates creative briefs and copy
- Post-Mortem Analytics Engine: Analyzes actual vs forecasted performance
- Learning Engine: Updates uplift models from post-mortems
"""

from .context_engine import ContextEngine
from .forecast_baseline_engine import ForecastBaselineEngine
from .uplift_elasticity_engine import UpliftElasticityEngine
from .scenario_evaluation_engine import ScenarioEvaluationEngine
from .scenario_optimization_engine import ScenarioOptimizationEngine
from .validation_engine import ValidationEngine
from .creative_engine import CreativeEngine
from .post_mortem_analytics_engine import PostMortemAnalyticsEngine
from .learning_engine import LearningEngine

__all__ = [
    'ContextEngine',
    'ForecastBaselineEngine',
    'UpliftElasticityEngine',
    'ScenarioEvaluationEngine',
    'ScenarioOptimizationEngine',
    'ValidationEngine',
    'CreativeEngine',
    'PostMortemAnalyticsEngine',
    'LearningEngine',
]
