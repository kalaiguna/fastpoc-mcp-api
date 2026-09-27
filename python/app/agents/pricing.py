from app.agents.models import PricingResult


def analyze_pricing(price: float, stock: int) -> PricingResult:
    """
    Rule-based pricing analysis.
    In a real A2A setup this would be a separate service with its own model/logic.
    """
    if stock <= 20:
        return PricingResult(
            suggested_min=round(price * 1.05, 2),
            suggested_max=round(price * 1.15, 2),
            discount_eligible=False,
            reasoning="Low stock signals high demand — premium pricing recommended.",
        )
    elif stock >= 80:
        return PricingResult(
            suggested_min=round(price * 0.85, 2),
            suggested_max=round(price * 0.95, 2),
            discount_eligible=True,
            reasoning="High stock suggests room for a discount to drive movement.",
        )
    else:
        return PricingResult(
            suggested_min=round(price * 0.95, 2),
            suggested_max=round(price * 1.05, 2),
            discount_eligible=False,
            reasoning="Stock levels are healthy — hold current price.",
        )
