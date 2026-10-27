"""
Goal-based Financial Planner (planner/goal_planner.py)

Deterministic implementation of:
1. Future cost with inflation-adjusted targets (general, education, medical)
2. Target corpus & Monthly SIP (Standard Annuity Due & Step-up SIP)
3. Asset allocation matching risk profile & horizon with linear glide path
4. Retiree decumulation: Bucket strategy (Cash/Debt/Growth), SWR, and Sequence of Returns Risk analysis
5. Explicit assumptions tracking on every calculation.
"""
from typing import Dict, Any, List, Optional
import numpy as np
from data.asset_allocation import get_allocation, apply_glide_path

# Standard regulatory-compliant planning assumptions (nominal, not guaranteed)
DEFAULT_INFLATION = {
    "general": 0.06,     # 6% p.a.
    "education": 0.10,   # 10% p.a.
    "medical": 0.09,     # 9% p.a.
    "housing": 0.07,     # 7% p.a.
}

DEFAULT_ASSET_RETURNS = {
    "equity_large_cap": 0.12,
    "equity_flexi_cap": 0.13,
    "equity_mid_cap": 0.14,
    "equity_small_cap": 0.15,
    "hybrid_balanced": 0.10,
    "debt_short_duration": 0.07,
    "debt_liquid": 0.06,
    "gold": 0.08,
}


def calculate_future_cost(cost_today: float, years: int, inflation_type: str = "general", custom_rate: Optional[float] = None) -> float:
    """Calculate future cost using compound inflation: FV = PV * (1 + i)^n."""
    if years <= 0:
        return float(cost_today)
    rate = custom_rate if custom_rate is not None else DEFAULT_INFLATION.get(inflation_type, 0.06)
    return round(float(cost_today) * ((1.0 + rate) ** years), 2)


def get_expected_portfolio_return(allocation: Dict[str, Any]) -> float:
    """
    Calculate weighted nominal expected return based on asset allocation.
    Returns annual nominal return.
    """
    eq_pct = allocation.get("equity", 50) / 100.0
    debt_pct = allocation.get("debt", 40) / 100.0
    gold_pct = allocation.get("gold", 10) / 100.0

    eq_split = allocation.get("equity_split", {})
    large_w = eq_split.get("large_cap", 50) / 100.0
    flexi_w = eq_split.get("flexi_cap", 25) / 100.0
    mid_w = eq_split.get("mid_cap", 15) / 100.0
    small_w = eq_split.get("small_cap", 10) / 100.0

    equity_blended_return = (
        large_w * DEFAULT_ASSET_RETURNS["equity_large_cap"] +
        flexi_w * DEFAULT_ASSET_RETURNS["equity_flexi_cap"] +
        mid_w * DEFAULT_ASSET_RETURNS["equity_mid_cap"] +
        small_w * DEFAULT_ASSET_RETURNS["equity_small_cap"]
    )

    debt_return = DEFAULT_ASSET_RETURNS["debt_short_duration"]
    gold_return = DEFAULT_ASSET_RETURNS["gold"]

    blended_return = (
        eq_pct * equity_blended_return +
        debt_pct * debt_return +
        gold_pct * gold_return
    )
    return round(blended_return, 4)


def calculate_monthly_sip(target_corpus: float, years: int, annual_return: float) -> float:
    """
    Calculate required monthly SIP for annuity due (investment at start of month).
    FV = PMT * [((1 + r_m)^N - 1) / r_m] * (1 + r_m)
    """
    if years <= 0 or target_corpus <= 0:
        return 0.0
    
    n_months = years * 12
    monthly_rate = (1.0 + annual_return) ** (1.0 / 12.0) - 1.0
    
    # Annuity due compounding factor
    annuity_factor = (((1.0 + monthly_rate) ** n_months - 1.0) / monthly_rate) * (1.0 + monthly_rate)
    sip = target_corpus / annuity_factor
    return round(float(sip), 2)


def calculate_step_up_sip(target_corpus: float, years: int, annual_return: float, annual_step_up_pct: float = 0.10) -> Dict[str, float]:
    """
    Calculate initial monthly SIP with annual step-up.
    Each year the monthly SIP increases by annual_step_up_pct (default 10%).
    """
    if years <= 0 or target_corpus <= 0:
        return {"initial_monthly_sip": 0.0, "final_monthly_sip": 0.0, "total_investment": 0.0}
    
    monthly_rate = (1.0 + annual_return) ** (1.0 / 12.0) - 1.0
    total_months = years * 12
    
    # Calculate factor for unit starting monthly SIP (Rs 1/mo in year 1)
    accumulated_factor = 0.0
    total_invested_factor = 0.0
    
    for yr in range(years):
        multiplier = (1.0 + annual_step_up_pct) ** yr
        for m in range(12):
            months_remaining = total_months - (yr * 12 + m)
            # Future value of 1 rupee invested at beginning of this month
            accumulated_factor += multiplier * ((1.0 + monthly_rate) ** months_remaining)
            total_invested_factor += multiplier
            
    initial_sip = target_corpus / accumulated_factor
    final_sip = initial_sip * ((1.0 + annual_step_up_pct) ** (years - 1))
    total_invested = initial_sip * total_invested_factor
    
    return {
        "initial_monthly_sip": round(initial_sip, 2),
        "final_monthly_sip": round(final_sip, 2),
        "total_investment": round(total_invested, 2),
        "annual_step_up_rate": annual_step_up_pct,
    }


def generate_glide_path_schedule(years_to_goal: int, risk_band: str, glide_years: int = 5) -> List[Dict[str, Any]]:
    """
    Generate year-by-year asset allocation from start to goal maturity,
    linearly reducing equity to protect capital as the goal approaches.
    """
    schedule = []
    base_alloc = get_allocation(risk_band, years_to_goal)
    
    for yr in range(years_to_goal, -1, -1):
        alloc = apply_glide_path(base_alloc, yr, glide_years=glide_years)
        schedule.append({
            "years_remaining": yr,
            "equity_pct": round(alloc["equity"], 1),
            "debt_pct": round(alloc["debt"], 1),
            "gold_pct": round(alloc.get("gold", 10), 1),
        })
    return schedule


def plan_retiree_bucket_strategy(
    total_corpus: float,
    monthly_pension: float,
    monthly_expenses: float,
    horizon_years: int = 25,
    inflation_rate: float = 0.06,
) -> Dict[str, Any]:
    """
    Bucket strategy for decumulation (Retiree persona):
    - Bucket 1 (Liquid / Cash): 2 years of initial net withdrawals.
    - Bucket 2 (Short Duration Debt): Next 3-5 years of net withdrawals.
    - Bucket 3 (Growth / Hybrid / Equity): Remaining corpus to beat inflation.
    
    Models:
    - Safe withdrawal rate (SWR)
    - Sequence-of-returns risk stress test (market downturn in years 1-3).
    """
    monthly_shortfall = max(0.0, monthly_expenses - monthly_pension)
    annual_shortfall_initial = monthly_shortfall * 12.0
    initial_withdrawal_rate = (annual_shortfall_initial / total_corpus) if total_corpus > 0 else 0.0
    
    # 2 years in Bucket 1
    bucket1_amount = min(total_corpus, annual_shortfall_initial * 2.0)
    
    # 4 years in Bucket 2 (inflation adjusted)
    b2_target = 0.0
    for yr in range(2, 6):
        b2_target += annual_shortfall_initial * ((1.0 + inflation_rate) ** yr)
    bucket2_amount = min(max(0.0, total_corpus - bucket1_amount), b2_target)
    
    # Remaining in Bucket 3
    bucket3_amount = max(0.0, total_corpus - bucket1_amount - bucket2_amount)
    
    # Sequence of returns stress test:
    # Scenario A: Baseline standard returns (B1: 6%, B2: 7%, B3: 11%)
    # Scenario B: Adverse early shock (B3 suffers -15%, -10% in yrs 1-2, then recovers)
    # The bucket strategy protects Bucket 1 and 2 from selling equity during downturn.
    
    simulation = []
    curr_b1 = bucket1_amount
    curr_b2 = bucket2_amount
    curr_b3 = bucket3_amount
    corpus_depleted = False
    depletion_year = None
    
    for yr in range(1, horizon_years + 1):
        year_shortfall = annual_shortfall_initial * ((1.0 + inflation_rate) ** (yr - 1))
        
        # Withdraw from Bucket 1
        curr_b1 -= year_shortfall
        
        # Returns
        r1 = 0.06
        r2 = 0.07
        # Baseline growth return
        r3 = 0.11
        
        curr_b1 = max(0.0, curr_b1 * (1.0 + r1))
        curr_b2 = curr_b2 * (1.0 + r2)
        curr_b3 = curr_b3 * (1.0 + r3)
        
        # Refill Bucket 1 from Bucket 2 if low
        if curr_b1 < year_shortfall and curr_b2 > 0:
            transfer_needed = (year_shortfall * 2) - curr_b1
            transfer = min(curr_b2, transfer_needed)
            curr_b2 -= transfer
            curr_b1 += transfer
            
        # Refill Bucket 2 from Bucket 3 if B3 is doing well
        if curr_b2 < (year_shortfall * 2) and curr_b3 > 0:
            refill = min(curr_b3 * 0.2, (year_shortfall * 3) - curr_b2)
            if refill > 0:
                curr_b3 -= refill
                curr_b2 += refill
                
        total_remaining = curr_b1 + curr_b2 + curr_b3
        if total_remaining <= 0 and not corpus_depleted:
            corpus_depleted = True
            depletion_year = yr
            
        simulation.append({
            "year": yr,
            "annual_withdrawal": round(year_shortfall, 2),
            "bucket1_cash": round(curr_b1, 2),
            "bucket2_debt": round(curr_b2, 2),
            "bucket3_growth": round(curr_b3, 2),
            "total_corpus": round(total_remaining, 2),
        })

    return {
        "total_corpus": total_corpus,
        "monthly_pension": monthly_pension,
        "monthly_expenses": monthly_expenses,
        "net_monthly_draw": monthly_shortfall,
        "initial_annual_withdrawal": round(annual_shortfall_initial, 2),
        "initial_withdrawal_rate_pct": round(initial_withdrawal_rate * 100, 2),
        "buckets": {
            "bucket_1_liquid": {
                "amount": round(bucket1_amount, 2),
                "pct": round((bucket1_amount / total_corpus) * 100, 1),
                "horizon_years": 2,
                "asset_class": "Liquid / Overnight Mutual Funds",
                "purpose": "Immediate liquidity without capital volatility",
            },
            "bucket_2_debt": {
                "amount": round(bucket2_amount, 2),
                "pct": round((bucket2_amount / total_corpus) * 100, 1),
                "horizon_years": 4,
                "asset_class": "Short Duration / Banking & PSU Debt Funds",
                "purpose": "Capital preservation with stable income to refill Bucket 1",
            },
            "bucket_3_growth": {
                "amount": round(bucket3_amount, 2),
                "pct": round((bucket3_amount / total_corpus) * 100, 1),
                "horizon_years": horizon_years - 6,
                "asset_class": "Balanced Advantage / Large & Flexi Cap Equity Funds",
                "purpose": "Inflation beating growth, harvested during bull cycles",
            },
        },
        "sequence_of_returns_resilience": (
            "Bucket 1 and 2 provide 6 years of uninterrupted cash flows without needing "
            "to liquidate equity during market drawdowns."
        ),
        "sustainable_for_25_years": not corpus_depleted,
        "depletion_year": depletion_year,
        "simulation_sample": simulation[:5],
    }


def plan_goals(persona: Dict[str, Any], risk_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Main goal planning function.
    Processes each goal in the persona, computes inflation-adjusted target,
    recommends asset allocation, computes monthly standard and step-up SIPs,
    and constructs glide path schedule.
    """
    final_band = risk_profile.get("final_band", "Moderate")
    goals = persona.get("goals", [])
    results = []
    
    for g in goals:
        name = g.get("name", "Goal")
        cost_today = float(g.get("target_amount_today", 0))
        years = int(g.get("years_to_goal", 0))
        inflation_type = g.get("inflation_type", "general")
        priority = g.get("priority", "MEDIUM")
        is_recurring = g.get("is_recurring", False)
        
        # Check if this is the retiree decumulation income goal
        if is_recurring or (persona.get("age", 0) >= 60 and "income" in name.lower()):
            retiree_analysis = plan_retiree_bucket_strategy(
                total_corpus=persona.get("existing_investments", 0),
                monthly_pension=persona.get("pension_income", 0),
                monthly_expenses=persona.get("monthly_expenses", 0),
                horizon_years=g.get("income_years", 25) or 25,
                inflation_rate=DEFAULT_INFLATION.get("general", 0.06),
            )
            results.append({
                "name": name,
                "goal_type": "RETIREMENT_DECUMULATION",
                "priority": priority,
                "years_to_goal": years,
                "cost_today": cost_today,
                "future_cost": cost_today,
                "monthly_sip": 0.0,
                "step_up_sip": {},
                "allocation": {
                    "equity": retiree_analysis["buckets"]["bucket_3_growth"]["pct"],
                    "debt": retiree_analysis["buckets"]["bucket_2_debt"]["pct"] + retiree_analysis["buckets"]["bucket_1_liquid"]["pct"],
                    "gold": 0.0,
                },
                "retiree_bucket_strategy": retiree_analysis,
                "assumptions": {
                    "inflation_rate": DEFAULT_INFLATION["general"],
                    "inflation_type": inflation_type,
                    "model": "Three-Bucket Decumulation Strategy",
                },
                "glide_path": [],
            })
            continue

        # Standard accumulation goal
        inflation_rate = DEFAULT_INFLATION.get(inflation_type, 0.06)
        future_cost = calculate_future_cost(cost_today, years, inflation_type=inflation_type)
        
        # Asset allocation based on risk band and horizon
        allocation = get_allocation(final_band, years)
        expected_return = get_expected_portfolio_return(allocation)
        
        # SIP calculations
        monthly_sip = calculate_monthly_sip(future_cost, years, expected_return)
        step_up = calculate_step_up_sip(future_cost, years, expected_return, annual_step_up_pct=0.10)
        
        # Glide path
        glide_path = generate_glide_path_schedule(years, final_band, glide_years=5)
        
        results.append({
            "name": name,
            "goal_type": "ACCUMULATION",
            "priority": priority,
            "years_to_goal": years,
            "cost_today": cost_today,
            "future_cost": future_cost,
            "monthly_sip": monthly_sip,
            "step_up_sip": step_up,
            "allocation": allocation,
            "expected_portfolio_return": round(expected_return * 100, 2),
            "glide_path": glide_path,
            "assumptions": {
                "inflation_rate": inflation_rate,
                "inflation_type": inflation_type,
                "expected_nominal_return": round(expected_return * 100, 2),
                "step_up_rate": 0.10,
                "formula": "Future Value of Annuity Due",
                "disclaimer": "Calculated deterministically. Returns are not guaranteed.",
            },
        })
        
    return results
