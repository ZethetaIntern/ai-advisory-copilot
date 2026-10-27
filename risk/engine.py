"""
Risk Profiling Engine

Computes:
- Risk CAPACITY score (0-100) from objective financial data
- Risk TOLERANCE score (0-100) from behavioural questionnaire + flags
- Final risk band using min(capacity_band, tolerance_band)
- Conflict detection when bands differ by >1

All scores are deterministic (no LLM involved).
"""
import numpy as np
from typing import Dict, Any, Tuple


# Band definitions: (min_score, max_score, band_name)
BANDS = [
    (0, 20, "Conservative"),
    (21, 40, "Moderately Conservative"),
    (41, 60, "Moderate"),
    (61, 80, "Moderately Aggressive"),
    (81, 100, "Aggressive"),
]

BAND_ORDER = [
    "Conservative",
    "Moderately Conservative",
    "Moderate",
    "Moderately Aggressive",
    "Aggressive",
]


def score_to_band(score: float) -> str:
    """Map a 0-100 score to a risk band."""
    score = max(0, min(100, score))
    for low, high, name in BANDS:
        if low <= score <= high:
            return name
    return "Moderate"  # fallback


def band_to_index(band: str) -> int:
    """Get numeric index of a band for comparison."""
    return BAND_ORDER.index(band)


def compute_capacity_score(persona: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """
    Compute Risk Capacity Score (0-100) from objective financial data.
    
    Factors and weights:
    - Income stability (20%): STABLE=high, MODERATE=mid, IRREGULAR=low
    - Investment horizon (25%): Longest goal horizon
    - Liabilities-to-income ratio (20%): Lower is better
    - Dependants (15%): Fewer dependants = higher capacity
    - Emergency fund coverage (20%): Months of expenses covered
    
    Returns:
        (score, breakdown_dict)
    """
    breakdown = {}
    
    # 1. Income stability (0-100, weight 20%)
    stability_map = {"STABLE": 85, "MODERATE": 55, "IRREGULAR": 25}
    stability_score = stability_map.get(persona.get("income_stability", "MODERATE"), 55)
    breakdown["income_stability"] = stability_score
    
    # 2. Investment horizon (0-100, weight 25%)
    goals = persona.get("goals", [])
    if goals:
        max_horizon = max(g.get("years_to_goal", 0) for g in goals)
    else:
        max_horizon = 0
    
    if max_horizon >= 20:
        horizon_score = 95
    elif max_horizon >= 10:
        horizon_score = 75
    elif max_horizon >= 5:
        horizon_score = 55
    elif max_horizon >= 3:
        horizon_score = 35
    else:
        horizon_score = 15
    breakdown["investment_horizon"] = horizon_score
    
    # 3. Liabilities-to-income ratio (0-100, weight 20%)
    monthly_income = persona.get("monthly_income", 0)
    monthly_emi = persona.get("monthly_emi", 0)
    
    if monthly_income > 0:
        lia_ratio = monthly_emi / monthly_income
    else:
        lia_ratio = 1.0
    
    if lia_ratio <= 0.1:
        lia_score = 90
    elif lia_ratio <= 0.2:
        lia_score = 75
    elif lia_ratio <= 0.35:
        lia_score = 55
    elif lia_ratio <= 0.5:
        lia_score = 35
    else:
        lia_score = 15
    breakdown["liabilities_to_income"] = lia_score
    
    # 4. Dependants (0-100, weight 15%)
    dependants = persona.get("dependants", 0)
    if dependants == 0:
        dep_score = 90
    elif dependants == 1:
        dep_score = 70
    elif dependants == 2:
        dep_score = 50
    elif dependants == 3:
        dep_score = 35
    else:
        dep_score = 20
    breakdown["dependants"] = dep_score
    
    # 5. Emergency fund coverage (0-100, weight 20%)
    monthly_expenses = persona.get("monthly_expenses", 0)
    emergency_fund = persona.get("emergency_fund", 0)
    
    if monthly_expenses > 0:
        months_covered = emergency_fund / monthly_expenses
    else:
        months_covered = 0
    
    if months_covered >= 6:
        ef_score = 90
    elif months_covered >= 3:
        ef_score = 65
    elif months_covered >= 1:
        ef_score = 40
    else:
        ef_score = 15
    breakdown["emergency_fund_coverage"] = ef_score
    
    # Weighted score
    weights = {
        "income_stability": 0.20,
        "investment_horizon": 0.25,
        "liabilities_to_income": 0.20,
        "dependants": 0.15,
        "emergency_fund_coverage": 0.20,
    }
    
    total = sum(breakdown[k] * weights[k] for k in weights)
    
    # Life-stage / Age adjustment (Human capital decreases with age)
    age = persona.get("age", 35)
    age_adj = 0
    if age >= 65:
        age_adj = -15
    elif age >= 60:
        age_adj = -10
    
    total = max(0, min(100, total + age_adj))
    breakdown["age_adjustment"] = age_adj
    breakdown["weights"] = weights
    
    return round(total, 1), breakdown


def compute_tolerance_score(persona: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    Compute Risk Tolerance Score (0-100) from behavioural responses + flags.
    
    Base: Average of behavioural question scores (each 0-10, scaled to 0-100)
    Adjustments:
    - F&O trading: Indicates higher risk appetite BUT also recklessness -> flag
    - Past panic selling: Reduces tolerance (actions > words)
    - Age adjustment: Slight conservative tilt for older clients
    
    Returns:
        (score, breakdown_dict)
    """
    breakdown = {}
    
    # Base score from behavioural responses
    responses = persona.get("behavioural_responses", [])
    if responses:
        scores = [r.get("score", 5) for r in responses]
        avg_score = np.mean(scores)
        base_score = avg_score * 10  # Scale 0-10 to 0-100
    else:
        base_score = 50  # Default moderate
    
    breakdown["base_behavioural_score"] = round(base_score, 1)
    breakdown["num_responses"] = len(responses)
    
    # Adjustments
    adjustments = 0
    flags = []
    
    # F&O trading flag
    if persona.get("trades_fno", False):
        flags.append("F&O_TRADER")
        # F&O trading suggests high risk appetite, but combined with losses 
        # and panic selling indicates recklessness, not informed risk-taking
        if persona.get("past_panic_selling", False):
            adjustments -= 15  # Significant reduction
            flags.append("FNO_WITH_PANIC_SELLING")
    
    # Past panic selling
    if persona.get("past_panic_selling", False):
        adjustments -= 10
        flags.append("PAST_PANIC_SELLER")
    
    # Age-based adjustment (slight)
    age = persona.get("age", 35)
    if age >= 60:
        adjustments -= 10
        flags.append("SENIOR_CITIZEN")
    elif age >= 50:
        adjustments -= 5
    elif age <= 25:
        adjustments += 5  # Younger clients have time
    
    # No insurance flags
    if not persona.get("has_health_insurance", True):
        adjustments -= 5
        flags.append("NO_HEALTH_INSURANCE")
    
    if not persona.get("has_life_insurance", True) and persona.get("dependants", 0) > 0:
        adjustments -= 5
        flags.append("NO_LIFE_INSURANCE_WITH_DEPENDANTS")
    
    breakdown["adjustments"] = adjustments
    breakdown["flags"] = flags
    
    final_score = max(0, min(100, base_score + adjustments))
    breakdown["final_tolerance_score"] = round(final_score, 1)
    
    return round(final_score, 1), breakdown


def compute_risk_profile(persona: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute complete risk profile for a persona.
    
    Returns dict with:
    - capacity_score, capacity_band, capacity_breakdown
    - tolerance_score, tolerance_band, tolerance_breakdown
    - final_band (min of both)
    - needs_adviser_review (True if bands differ by >1)
    - review_reason (explanation if review needed)
    """
    capacity_score, capacity_breakdown = compute_capacity_score(persona)
    tolerance_score, tolerance_breakdown = compute_tolerance_score(persona)
    
    capacity_band = score_to_band(capacity_score)
    tolerance_band = score_to_band(tolerance_score)
    
    # Final band = min(capacity, tolerance) - more conservative
    cap_idx = band_to_index(capacity_band)
    tol_idx = band_to_index(tolerance_band)
    final_idx = min(cap_idx, tol_idx)
    final_band = BAND_ORDER[final_idx]
    
    # Check for conflict
    band_diff = abs(cap_idx - tol_idx)
    needs_review = band_diff > 1
    
    review_reason = ""
    if needs_review:
        if cap_idx > tol_idx:
            review_reason = (
                f"Client's financial capacity ({capacity_band}, score {capacity_score}) "
                f"significantly exceeds their behavioural risk tolerance ({tolerance_band}, "
                f"score {tolerance_score}). The client has the financial means to take more "
                f"risk but is psychologically uncomfortable with volatility. Recommend "
                f"discussion to understand if tolerance can grow with education, or if "
                f"conservative allocation is preferred."
            )
        else:
            review_reason = (
                f"Client's behavioural risk tolerance ({tolerance_band}, score {tolerance_score}) "
                f"significantly exceeds their financial capacity ({capacity_band}, "
                f"score {capacity_score}). The client wants aggressive returns but their "
                f"financial situation (income stability, liabilities, emergency fund) "
                f"does not support high-risk exposure. Recommend a conservative plan "
                f"with a clear explanation of why."
            )
    
    # Add suitability flags
    suitability_flags = []
    flags = tolerance_breakdown.get("flags", [])
    
    if "FNO_WITH_PANIC_SELLING" in flags:
        suitability_flags.append({
            "type": "WARNING",
            "message": "Client trades F&O but has history of panic selling. This indicates speculative behaviour, not informed risk-taking. Recommend structured investment approach.",
        })
    
    if "NO_HEALTH_INSURANCE" in flags:
        suitability_flags.append({
            "type": "ACTION_REQUIRED",
            "message": "Client lacks health insurance. Recommend securing health cover before aggressive investing.",
        })
    
    if persona.get("age", 0) >= 60 and final_band in ["Aggressive", "Moderately Aggressive"]:
        suitability_flags.append({
            "type": "WARNING",
            "message": "Senior citizen with aggressive risk profile. Capital preservation should be prioritized.",
        })
        # Override for safety
        final_band = "Moderately Conservative"
        needs_review = True
        review_reason = (
            f"Senior citizen (age {persona.get('age')}) risk band overridden from "
            f"{BAND_ORDER[final_idx]} to Moderately Conservative for capital preservation. "
            f"Adviser review required."
        )
    
    return {
        "capacity_score": capacity_score,
        "capacity_band": capacity_band,
        "capacity_breakdown": capacity_breakdown,
        "tolerance_score": tolerance_score,
        "tolerance_band": tolerance_band,
        "tolerance_breakdown": tolerance_breakdown,
        "final_band": final_band,
        "needs_adviser_review": needs_review,
        "review_reason": review_reason,
        "suitability_flags": suitability_flags,
    }
