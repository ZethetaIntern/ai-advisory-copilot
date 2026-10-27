"""
Tests for Goal-based Planner (tests/test_goal_planner.py)
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk.engine import compute_risk_profile
from planner.goal_planner import (
    calculate_future_cost,
    calculate_monthly_sip,
    calculate_step_up_sip,
    generate_glide_path_schedule,
    plan_retiree_bucket_strategy,
    plan_goals,
    DEFAULT_INFLATION,
)


class TestInflationAndCost:
    def test_future_cost_zero_years(self):
        assert calculate_future_cost(100000, 0) == 100000.0

    def test_future_cost_general(self):
        # 100,000 at 6% for 10 years: 100000 * 1.06^10 = 179084.77
        cost = calculate_future_cost(100000, 10, inflation_type="general")
        assert round(cost, 0) == 179085.0

    def test_future_cost_education(self):
        # Education inflation 10%
        cost = calculate_future_cost(1000000, 15, inflation_type="education")
        # 1M * 1.1^15 = 4,177,248.17
        assert round(cost, -2) == 4177200.0

    def test_future_cost_medical(self):
        # Medical inflation 9%
        cost = calculate_future_cost(500000, 5, inflation_type="medical")
        assert cost > 500000 * (1.08 ** 5)


class TestSIPCalculations:
    def test_monthly_sip_positive(self):
        # Target 10,00,000 in 10 years at 12% annual return
        sip = calculate_monthly_sip(1000000, 10, 0.12)
        assert 4000 < sip < 5000  # Should be approx ~4,300

    def test_step_up_sip_lower_initial_than_flat_sip(self):
        target = 5000000
        years = 15
        r = 0.12
        flat_sip = calculate_monthly_sip(target, years, r)
        step_up = calculate_step_up_sip(target, years, r, annual_step_up_pct=0.10)
        
        # Initial step-up SIP should be substantially lower than flat SIP
        assert step_up["initial_monthly_sip"] < flat_sip
        # Final step-up SIP in year 15 will be higher
        assert step_up["final_monthly_sip"] > flat_sip
        assert step_up["total_investment"] > 0


class TestGlidePath:
    def test_glide_path_reduces_equity(self):
        schedule = generate_glide_path_schedule(years_to_goal=10, risk_band="Aggressive", glide_years=5)
        assert len(schedule) == 11
        # In early years (10, 9, 8..), equity is high
        initial_equity = schedule[0]["equity_pct"]
        # In final year (0), equity is minimum
        final_equity = schedule[-1]["equity_pct"]
        assert initial_equity > final_equity
        assert schedule[-1]["debt_pct"] > schedule[0]["debt_pct"]


class TestRetireeBucketStrategy:
    def test_retiree_buckets(self, persona_retiree):
        strategy = plan_retiree_bucket_strategy(
            total_corpus=persona_retiree["existing_investments"],
            monthly_pension=persona_retiree["pension_income"],
            monthly_expenses=persona_retiree["monthly_expenses"],
            horizon_years=25,
        )
        assert strategy["total_corpus"] == 8000000
        assert strategy["net_monthly_draw"] == 10000  # 45k expenses - 35k pension
        assert strategy["initial_annual_withdrawal"] == 120000
        assert strategy["initial_withdrawal_rate_pct"] == 1.5  # 1.2L / 80L = 1.5% - very conservative!
        assert strategy["sustainable_for_25_years"] is True
        assert "bucket_1_liquid" in strategy["buckets"]
        assert "bucket_2_debt" in strategy["buckets"]
        assert "bucket_3_growth" in strategy["buckets"]


class TestAllPersonasPlanning:
    def test_all_six_personas_can_be_planned(self, all_personas):
        for persona in all_personas:
            risk = compute_risk_profile(persona)
            goals_plan = plan_goals(persona, risk)
            assert len(goals_plan) == len(persona["goals"])
            for g in goals_plan:
                assert "future_cost" in g
                assert "allocation" in g
                assert "assumptions" in g
                assert g["future_cost"] >= g["cost_today"]
