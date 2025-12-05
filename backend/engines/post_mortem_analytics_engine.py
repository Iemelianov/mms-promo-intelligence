"""
Post-Mortem Analytics Engine

Analyzes actual vs forecasted performance.
"""

from typing import Optional, Dict, Any

from models.schemas import PromoScenario, PostMortemReport
from tools.sales_data_tool import SalesDataTool


class PostMortemAnalyticsEngine:
    """Engine for analyzing campaign performance after execution."""

    def __init__(self, sales_data_tool: Optional[SalesDataTool] = None):
        self.sales_data_tool = sales_data_tool

    def analyze_performance(
        self,
        scenario: PromoScenario,
        forecast: Dict[str, Any],
        actual_data: Dict[str, Any],
    ) -> PostMortemReport:
        """Analyze actual performance vs forecast and return a PostMortemReport."""
        forecast_sales = float(forecast.get("total_sales") or forecast.get("sales_value") or 0.0)
        forecast_margin = float(forecast.get("total_margin") or forecast.get("margin_value") or 0.0)
        forecast_units = float(forecast.get("total_units") or forecast.get("units") or 0.0)
        forecast_ebit = float(forecast.get("total_ebit") or forecast.get("ebit") or 0.0)

        actual_sales = float(actual_data.get("sales_value", 0) or 0.0)
        actual_margin = float(actual_data.get("margin_value", 0) or 0.0)
        actual_units = float(actual_data.get("units", 0) or 0.0)
        actual_ebit = float(actual_data.get("ebit", actual_margin - actual_sales * 0.1))

        def _pct_err(actual: float, expected: float) -> float:
            if expected == 0:
                return 0.0
            return (actual - expected) / expected

        forecast_accuracy = {
            "sales_abs_error": actual_sales - forecast_sales,
            "sales_pct_error": _pct_err(actual_sales, forecast_sales),
            "margin_abs_error": actual_margin - forecast_margin,
            "margin_pct_error": _pct_err(actual_margin, forecast_margin),
            "units_abs_error": actual_units - forecast_units,
            "units_pct_error": _pct_err(actual_units, forecast_units),
            "ebit_abs_error": actual_ebit - forecast_ebit,
            "ebit_pct_error": _pct_err(actual_ebit, forecast_ebit),
        }

        uplift_analysis = {
            "observed_uplift_sales": actual_sales - forecast_sales,
            "observed_uplift_margin": actual_margin - forecast_margin,
        }

        # Post-promo dip heuristic: requires post-period sales in payload
        post_promo_dip = None
        post_sales = actual_data.get("post_period_sales_value")
        post_days = actual_data.get("post_period_days", 0) or 0
        promo_days = max((scenario.date_range.end_date - scenario.date_range.start_date).days + 1, 1)
        if post_sales is not None and post_days:
            promo_avg = actual_sales / promo_days if promo_days else 0
            post_avg = float(post_sales) / float(post_days)
            if promo_avg > 0:
                post_promo_dip = (post_avg - promo_avg) / promo_avg
                uplift_analysis["post_promo_avg"] = post_avg
                uplift_analysis["promo_avg"] = promo_avg

        # Cannibalization heuristic: expects list of other_categories with before/during sales.
        cannibalization_signals = []
        other_categories = actual_data.get("other_categories") or []
        for cat in other_categories:
            before = float(cat.get("sales_before", 0) or 0)
            during = float(cat.get("sales_during", 0) or 0)
            if before > 0 and (during - before) / before < -0.05:
                cannibalization_signals.append(
                    f"Potential cannibalization in {cat.get('department','unknown')}: {((during-before)/before):.1%}"
                )

        insights = []
        if forecast_accuracy["sales_pct_error"] > 0.05:
            insights.append("Sales exceeded forecast; consider increasing baseline or lowering discount uplift assumptions.")
        if forecast_accuracy["sales_pct_error"] < -0.05:
            insights.append("Sales underperformed; revisit uplift coefficients and promo depth.")
        if forecast_accuracy["margin_pct_error"] < -0.05:
            insights.append("Margin erosion beyond forecast; check discount and mix effects.")
        if post_promo_dip is not None and post_promo_dip < -0.1:
            insights.append("Detected post-promo dip >10%; consider softer landing tactics.")
        if cannibalization_signals:
            insights.append("Cannibalization signals detected in non-promoted categories.")
        if not insights:
            insights.append("Performance within expected range.")

        return PostMortemReport(
            scenario_id=scenario.id or "unknown",
            forecast_accuracy=forecast_accuracy,
            uplift_analysis=uplift_analysis,
            post_promo_dip=post_promo_dip,
            cannibalization_signals=cannibalization_signals or None,
            insights=insights,
        )

    def calculate_forecast_accuracy(
        self,
        forecast: Dict[str, float],
        actual: Dict[str, float],
    ) -> Dict[str, float]:
        """Calculate forecast accuracy metrics."""

        def _pct_err(actual: float, expected: float) -> float:
            if expected == 0:
                return 0.0
            return (actual - expected) / expected

        return {
            "sales_abs_error": (actual.get("sales_value") or 0) - (forecast.get("sales_value") or 0),
            "sales_pct_error": _pct_err(actual.get("sales_value") or 0, forecast.get("sales_value") or 0),
            "margin_abs_error": (actual.get("margin_value") or 0) - (forecast.get("margin_value") or 0),
            "margin_pct_error": _pct_err(actual.get("margin_value") or 0, forecast.get("margin_value") or 0),
            "units_abs_error": (actual.get("units") or 0) - (forecast.get("units") or 0),
            "units_pct_error": _pct_err(actual.get("units") or 0, forecast.get("units") or 0),
        }

    def detect_cannibalization(
        self,
        scenario: PromoScenario,
        actual_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Detect cannibalization effects (placeholder)."""
        signals = []
        other_categories = actual_data.get("other_categories") or []
        for cat in other_categories:
            before = float(cat.get("sales_before", 0) or 0)
            during = float(cat.get("sales_during", 0) or 0)
            if before > 0 and (during - before) / before < -0.05:
                signals.append(
                    f"Potential cannibalization in {cat.get('department','unknown')}: {((during-before)/before):.1%}"
                )
        return {"signals": signals, "note": "Heuristic cannibalization check"}

