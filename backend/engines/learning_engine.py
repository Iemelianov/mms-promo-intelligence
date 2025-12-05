"""
Learning Engine

Updates uplift models from post-mortems.

Input: Post-mortem reports, current model
Output: Updated UpliftModel

Methodology:
- Compare forecasted vs actual uplift
- Adjust coefficients by category/channel
- Weight recent data more heavily
"""

from typing import List, Optional, Dict
from datetime import datetime

from models.schemas import PostMortemReport, UpliftModel


class LearningEngine:
    """Engine for learning from post-mortem reports and updating models."""
    
    def __init__(self):
        """Initialize Learning Engine."""
        pass
    
    def update_uplift_model(
        self,
        current_model: UpliftModel,
        post_mortems: List[PostMortemReport]
    ) -> UpliftModel:
        """
        Update uplift model based on post-mortem reports.
        
        Args:
            current_model: Current UpliftModel
            post_mortems: List of PostMortemReport objects
        
        Returns:
            Updated UpliftModel with adjusted coefficients
        """
        if not post_mortems:
            return current_model

        # Collect per-department/channel errors if provided in uplift_analysis.by_department
        per_key_errors: Dict[str, Dict[str, List[float]]] = {}
        global_errors: List[float] = []

        for pm in post_mortems:
            sales_err = pm.forecast_accuracy.get("sales_pct_error", 0)
            if sales_err is not None:
                global_errors.append(sales_err)

            by_dept = pm.uplift_analysis.get("by_department") if pm.uplift_analysis else None
            if by_dept and isinstance(by_dept, dict):
                for dept, chans in by_dept.items():
                    for ch, err in chans.items():
                        per_key_errors.setdefault(dept.upper(), {}).setdefault(ch.lower(), []).append(err)

        def _mean_error(errors: List[float]) -> float:
            return sum(errors) / len(errors) if errors else 0.0

        def _adjust_factor(err: float) -> float:
            return max(0.8, min(1.2, 1 - err))

        new_coeffs: Dict[str, Dict[str, float]] = {}
        for dept, chans in current_model.coefficients.items():
            new_coeffs[dept] = {}
            for ch, val in chans.items():
                if dept in per_key_errors and ch in per_key_errors[dept]:
                    err = _mean_error(per_key_errors[dept][ch])
                    factor = _adjust_factor(err)
                else:
                    factor = _adjust_factor(_mean_error(global_errors))
                new_coeffs[dept][ch] = max(0.5, min(3.0, val * factor))

        return UpliftModel(
            coefficients=new_coeffs,
            version=f"{current_model.version}-adj",
            last_updated=datetime.now()
        )
    
    def calculate_model_adjustments(
        self,
        post_mortems: List[PostMortemReport],
        category: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate adjustment factors for model coefficients.
        
        Args:
            post_mortems: List of PostMortemReport objects
            category: Optional category filter
            channel: Optional channel filter
        
        Returns:
            Dictionary with adjustment factors
        """
        errors: List[float] = []
        per_key_errors: Dict[str, Dict[str, List[float]]] = {}

        for pm in post_mortems:
            sales_err = pm.forecast_accuracy.get("sales_pct_error", 0)
            if sales_err is not None:
                errors.append(sales_err)

            by_dept = pm.uplift_analysis.get("by_department") if pm.uplift_analysis else None
            if by_dept and isinstance(by_dept, dict):
                for dept, chans in by_dept.items():
                    for ch, err in chans.items():
                        per_key_errors.setdefault(dept.upper(), {}).setdefault(ch.lower(), []).append(err)

        def _mean_error(arr: List[float]) -> float:
            return sum(arr) / len(arr) if arr else 0.0

        def _adjust(err: float) -> float:
            return max(0.8, min(1.2, 1 - err))

        if category or channel:
            dept_key = category.upper() if category else None
            ch_key = channel.lower() if channel else None
            if dept_key and dept_key in per_key_errors:
                if ch_key and ch_key in per_key_errors[dept_key]:
                    return {"adjustment": _adjust(_mean_error(per_key_errors[dept_key][ch_key]))}
                if not ch_key:
                    merged = [e for arr in per_key_errors[dept_key].values() for e in arr]
                    return {"adjustment": _adjust(_mean_error(merged))}

        # Fallback to global adjustment
        return {"adjustment": _adjust(_mean_error(errors))}

