"""
Tests for Portfolio Module (tests/test_portfolio.py)
"""
import pytest
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portfolio.fund_metrics import (
    compute_cagr,
    compute_volatility,
    compute_max_drawdown,
    compute_sharpe_ratio,
    compute_rolling_returns,
)
from portfolio.fund_screener import (
    FACTSHEET_TABLE,
    score_fund,
    shortlist_funds_by_category,
    get_recommended_funds_for_allocation,
)
from portfolio.backtest import run_portfolio_backtest


class TestFundMetrics:
    def test_cagr_calculation(self):
        # 100 to 200 in 3 years: (2)^(1/3) - 1 = 0.2599 (26%)
        cagr = compute_cagr(100.0, 200.0, 3.0)
        assert round(cagr, 4) == 0.2599

    def test_max_drawdown(self):
        # Prices: 100 -> 120 -> 90 -> 110. Peak is 120, trough is 90 -> (90-120)/120 = -0.25 (-25%)
        series = pd.Series([100, 120, 90, 110])
        mdd = compute_max_drawdown(series)
        assert mdd == -0.25

    def test_sharpe_ratio(self):
        # 15% return, 10% vol, 6.5% Rf -> (15-6.5)/10 = 0.85
        sharpe = compute_sharpe_ratio(0.15, 0.10, risk_free_rate=0.065)
        assert sharpe == 0.85


class TestFundScreener:
    def test_factsheet_table_all_direct_growth(self):
        for code, fund in FACTSHEET_TABLE.items():
            assert "Direct" in fund["name"]
            assert "Growth" in fund["name"]
            assert fund["ter_direct"] > 0
            assert fund["aum_cr"] > 0

    def test_shortlist_covers_major_categories(self):
        shortlisted = shortlist_funds_by_category()
        assert "Large Cap" in shortlisted
        assert "Flexi Cap" in shortlisted
        assert "Mid Cap" in shortlisted
        assert "Small Cap" in shortlisted
        assert "Short Duration Debt" in shortlisted
        for cat, funds in shortlisted.items():
            assert 1 <= len(funds) <= 2
            for f in funds:
                assert "selection_rationale" in f
                assert f["overall_score"] > 0

    def test_recommended_funds_for_allocation(self):
        alloc = {
            "equity": 60,
            "debt": 30,
            "gold": 10,
            "equity_split": {"large_cap": 50, "flexi_cap": 25, "mid_cap": 15, "small_cap": 10},
        }
        recs = get_recommended_funds_for_allocation(alloc)
        assert len(recs) >= 4  # Large, Flexi, Mid, Small, Debt
        total_w = sum(r["bucket_weight_pct"] for r in recs)
        assert total_w == pytest.approx(90.0, abs=1.0)


class TestBacktest:
    def test_backtest_execution(self):
        alloc = {
            "equity": 65,
            "debt": 25,
            "gold": 10,
            "equity_split": {"large_cap": 50, "flexi_cap": 25, "mid_cap": 15, "small_cap": 10},
        }
        recs = get_recommended_funds_for_allocation(alloc)
        bt = run_portfolio_backtest(recs, backtest_years=5, initial_investment=100000.0)
        
        assert bt["final_portfolio_value"] > 0
        assert "metrics" in bt
        assert "portfolio" in bt["metrics"]
        assert "benchmark" in bt["metrics"]
        assert bt["metrics"]["portfolio"]["cagr_pct"] > 0
        assert len(bt["limitations"]) == 4
        assert len(bt["trajectory"]) > 0
