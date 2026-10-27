"""
Asset allocation models based on risk band and investment horizon.
All allocations are deterministic and documented.
"""

# Asset allocation by risk band and horizon
# Format: {"equity": %, "debt": %, "gold": %}
# Equity further split: large_cap, mid_cap, small_cap based on risk band

ALLOCATION_MODELS = {
    "Conservative": {
        "short": {"equity": 10, "debt": 80, "gold": 10},     # < 3 years
        "medium": {"equity": 25, "debt": 65, "gold": 10},     # 3-7 years
        "long": {"equity": 35, "debt": 55, "gold": 10},       # > 7 years
    },
    "Moderately Conservative": {
        "short": {"equity": 20, "debt": 70, "gold": 10},
        "medium": {"equity": 35, "debt": 55, "gold": 10},
        "long": {"equity": 50, "debt": 40, "gold": 10},
    },
    "Moderate": {
        "short": {"equity": 30, "debt": 60, "gold": 10},
        "medium": {"equity": 50, "debt": 40, "gold": 10},
        "long": {"equity": 65, "debt": 25, "gold": 10},
    },
    "Moderately Aggressive": {
        "short": {"equity": 40, "debt": 50, "gold": 10},
        "medium": {"equity": 60, "debt": 30, "gold": 10},
        "long": {"equity": 75, "debt": 15, "gold": 10},
    },
    "Aggressive": {
        "short": {"equity": 50, "debt": 40, "gold": 10},
        "medium": {"equity": 70, "debt": 20, "gold": 10},
        "long": {"equity": 85, "debt": 10, "gold": 5},
    },
}

# Equity sub-allocation by risk band
EQUITY_SUB_ALLOCATION = {
    "Conservative": {"large_cap": 80, "flexi_cap": 15, "mid_cap": 5, "small_cap": 0},
    "Moderately Conservative": {"large_cap": 65, "flexi_cap": 20, "mid_cap": 10, "small_cap": 5},
    "Moderate": {"large_cap": 50, "flexi_cap": 25, "mid_cap": 15, "small_cap": 10},
    "Moderately Aggressive": {"large_cap": 35, "flexi_cap": 25, "mid_cap": 25, "small_cap": 15},
    "Aggressive": {"large_cap": 25, "flexi_cap": 25, "mid_cap": 25, "small_cap": 25},
}


def get_horizon_bucket(years: int) -> str:
    """Classify investment horizon."""
    if years <= 3:
        return "short"
    elif years <= 7:
        return "medium"
    else:
        return "long"


def get_allocation(risk_band: str, years_to_goal: int) -> dict:
    """Get asset allocation for a given risk band and horizon.
    
    Returns:
        dict with keys: equity, debt, gold (percentages),
        plus equity_split with sub-allocations.
    """
    horizon = get_horizon_bucket(years_to_goal)
    base = ALLOCATION_MODELS[risk_band][horizon].copy()
    equity_split = EQUITY_SUB_ALLOCATION[risk_band].copy()
    
    base["equity_split"] = equity_split
    base["horizon_bucket"] = horizon
    base["risk_band"] = risk_band
    base["years_to_goal"] = years_to_goal
    
    return base


def apply_glide_path(allocation: dict, years_to_goal: int, glide_years: int = 5) -> dict:
    """Apply glide path: shift equity to debt linearly over final glide_years.
    
    Args:
        allocation: Base allocation dict
        years_to_goal: Years remaining
        glide_years: Over how many years to shift (default 5)
    
    Returns:
        Adjusted allocation dict
    """
    result = allocation.copy()
    
    if years_to_goal <= 0:
        # At goal: minimal equity
        result["equity"] = max(10, allocation["equity"] * 0.2)
        result["debt"] = 90 - result.get("gold", 10)
        return result
    
    if years_to_goal < glide_years:
        # Linear interpolation
        progress = 1.0 - (years_to_goal / glide_years)
        target_equity = max(10, allocation["equity"] * 0.2)
        current_equity = allocation["equity"]
        
        result["equity"] = current_equity - (current_equity - target_equity) * progress
        result["debt"] = 100 - result["equity"] - result.get("gold", 10)
    
    return result
