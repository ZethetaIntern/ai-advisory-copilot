"""
Suitability Guardrails Engine (guardrails/suitability.py)

Enforces SEBI Investment Advisers Regulations (Regulation 17 - Suitability):
- RIA must have reasonable basis for recommendation
- Must assess risk capacity vs tolerance
- High-risk products for low-capacity clients are blocked or flagged
- Senior citizen capital preservation guardrails
- Speculative trader guardrails (F&O, fast return demands)
"""
from typing import Dict, Any, List


def check_suitability(persona: Dict[str, Any], proposed_allocation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate investment suitability of proposed plan against client persona.
    Returns:
        is_suitable: bool
        flags: List[Dict[str, Any]] (BLOCK / WARNING / INFO)
        recommendations: List[str]
    """
    flags = []
    age = persona.get("age", 35)
    capacity_score = persona.get("risk_capacity_score", 50)
    monthly_expenses = persona.get("monthly_expenses", 0)
    emergency_fund = persona.get("emergency_fund", 0)
    is_fno_trader = persona.get("trades_fno", False)
    has_panic_sold = persona.get("past_panic_selling", False)
    
    equity_pct = proposed_allocation.get("equity", 50)
    eq_split = proposed_allocation.get("equity_split", {})
    small_cap_pct = eq_split.get("small_cap", 0)
    
    # 1. Senior Citizen Suitability Rule
    if age >= 60:
        if equity_pct > 40:
            flags.append({
                "severity": "BLOCK",
                "code": "SENIOR_CITIZEN_EXCESSIVE_EQUITY",
                "message": f"Client is {age} years old. Equity allocation of {equity_pct}% exceeds the regulatory 40% prudence limit for retirees in decumulation phase.",
                "remediation": "Cap equity at 25-35% and deploy 3-bucket strategy.",
            })
        if small_cap_pct > 10:
            flags.append({
                "severity": "BLOCK",
                "code": "SENIOR_CITIZEN_SMALL_CAP_BLOCKED",
                "message": f"Small-cap allocation of {small_cap_pct}% is unsuitable for client age {age} due to extreme volatility and drawdown risk.",
                "remediation": "Restrict equity holdings to Large Cap and Balanced Advantage funds.",
            })

    # 2. Speculative Trader Suitability Rule
    if is_fno_trader:
        if has_panic_sold:
            flags.append({
                "severity": "WARNING",
                "code": "TRADER_SPECULATIVE_BEHAVIOUR",
                "message": "Client has active F&O derivatives history combined with past panic selling during market corrections. High risk of repeating panic selling during normal equity volatility.",
                "remediation": "Reject high-beta small cap strategies. Enforce disciplined goal-based SIP in diversified index/flexi-cap funds.",
            })

    # 3. Low Capacity with High Risk Asset
    if capacity_score < 40 and equity_pct > 60:
        flags.append({
            "severity": "BLOCK",
            "code": "LOW_CAPACITY_EXCESSIVE_RISK",
            "message": f"Client risk capacity score is only {capacity_score}/100, but proposed equity is {equity_pct}%. Client cannot financially absorb prolonged market drawdowns.",
            "remediation": "Reduce equity to Moderate or Moderately Conservative levels (<50%).",
        })

    # 4. Inadequate Emergency Fund
    months_covered = (emergency_fund / monthly_expenses) if monthly_expenses > 0 else 0
    if months_covered < 3:
        flags.append({
            "severity": "WARNING",
            "code": "INSUFFICIENT_EMERGENCY_RESERVE",
            "message": f"Client has only {months_covered:.1f} months of emergency expenses covered (Rs {emergency_fund:,.0f}). Minimum recommended reserve is 6 months.",
            "remediation": "Allocate first 6 months of surplus savings to Liquid Mutual Funds before equity SIP.",
        })

    # 5. Insurance Coverage
    if not persona.get("has_health_insurance", True):
        flags.append({
            "severity": "WARNING",
            "code": "LACK_OF_HEALTH_INSURANCE",
            "message": "Client lacks standalone health insurance. Medical emergencies pose severe risk of forced portfolio liquidation.",
            "remediation": "Advise client to obtain adequate family floater health insurance before investing in lock-in assets.",
        })

    is_suitable = not any(f["severity"] == "BLOCK" for f in flags)
    
    return {
        "is_suitable": is_suitable,
        "flags_count": len(flags),
        "flags": flags,
    }
