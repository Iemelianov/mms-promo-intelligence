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

        # Simple global adjustment: average absolute sales_pct_error to scale coefficients.
        errors: List[float] = []
        for pm in post_mortems:
            sales_err = pm.forecast_accuracy.get("sales_pct_error", 0)
            if sales_err is not None:
                errors.append(sales_err)

        if not errors:
            return current_model

        mean_err = sum(errors) / len(errors)
        # Clamp adjustment factor between 0.8 and 1.2 to avoid big swings.
        adjust = max(0.8, min(1.2, 1 - mean_err))

        new_coeffs: Dict[str, Dict[str, float]] = {}
        for dept, chans in current_model.coefficients.items():
            new_coeffs[dept] = {}
            for ch, val in chans.items():
                new_coeffs[dept][ch] = max(0.5, min(3.0, val * adjust))

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
        for pm in post_mortems:
            sales_err = pm.forecast_accuracy.get("sales_pct_error", 0)
            if sales_err is not None:
                errors.append(sales_err)

        if not errors:
            return {"adjustment": 1.0}

        mean_err = sum(errors) / len(errors)
        adjust = max(0.8, min(1.2, 1 - mean_err))
        return {"adjustment": adjust}

