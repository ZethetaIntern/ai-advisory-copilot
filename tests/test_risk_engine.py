"""Tests for the risk profiling engine."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk.engine import (
    compute_risk_profile,
    compute_capacity_score,
    compute_tolerance_score,
    score_to_band,
    BAND_ORDER,
)


class TestScoreToBand:
    def test_conservative(self):
        assert score_to_band(10) == "Conservative"
        assert score_to_band(0) == "Conservative"
        assert score_to_band(20) == "Conservative"

    def test_moderately_conservative(self):
        assert score_to_band(30) == "Moderately Conservative"
    
    def test_moderate(self):
        assert score_to_band(50) == "Moderate"
    
    def test_moderately_aggressive(self):
        assert score_to_band(70) == "Moderately Aggressive"
    
    def test_aggressive(self):
        assert score_to_band(90) == "Aggressive"
    
    def test_clamp(self):
        assert score_to_band(-10) == "Conservative"
        assert score_to_band(110) == "Aggressive"


class TestCapacityScore:
    def test_fresh_grad_stable_income(self, persona_fresh_grad):
        score, breakdown = compute_capacity_score(persona_fresh_grad)
        assert 50 <= score <= 90  # Stable income, long horizon, no dependants
        assert breakdown["income_stability"] == 85
    
    def test_business_owner_irregular(self, persona_business_owner):
        score, breakdown = compute_capacity_score(persona_business_owner)
        assert breakdown["income_stability"] == 25  # Irregular
        assert breakdown["dependants"] == 35  # 3 dependants
    
    def test_retiree(self, persona_retiree):
        score, breakdown = compute_capacity_score(persona_retiree)
        # Retiree has short horizon, low capacity
        assert score < 60


class TestToleranceScore:
    def test_fresh_grad_moderate_tolerance(self, persona_fresh_grad):
        score, breakdown = compute_tolerance_score(persona_fresh_grad)
        assert 50 <= score <= 80
    
    def test_doctor_low_tolerance(self, persona_doctor):
        score, breakdown = compute_tolerance_score(persona_doctor)
        assert score < 40  # Very risk-averse responses
    
    def test_trader_flags(self, persona_trader):
        score, breakdown = compute_tolerance_score(persona_trader)
        assert "F&O_TRADER" in breakdown["flags"]
        assert "PAST_PANIC_SELLER" in breakdown["flags"]
        assert "NO_HEALTH_INSURANCE" in breakdown["flags"]


class TestFullProfile:
    def test_fresh_grad_profile(self, persona_fresh_grad):
        result = compute_risk_profile(persona_fresh_grad)
        assert result["capacity_band"] in BAND_ORDER
        assert result["tolerance_band"] in BAND_ORDER
        assert result["final_band"] in BAND_ORDER
        assert isinstance(result["needs_adviser_review"], bool)
    
    def test_final_band_is_min(self, persona_doctor):
        """Final band should be the more conservative of capacity and tolerance."""
        result = compute_risk_profile(persona_doctor)
        cap_idx = BAND_ORDER.index(result["capacity_band"])
        tol_idx = BAND_ORDER.index(result["tolerance_band"])
        final_idx = BAND_ORDER.index(result["final_band"])
        assert final_idx <= min(cap_idx, tol_idx)
    
    def test_trader_needs_review(self, persona_trader):
        """Trader persona should trigger adviser review."""
        result = compute_risk_profile(persona_trader)
        # Trader has high tolerance answers but irregular income, past panic selling
        # This should create a mismatch
        assert len(result["suitability_flags"]) > 0
    
    def test_retiree_conservative_override(self, persona_retiree):
        """Retiree should get conservative treatment regardless of tolerance answers."""
        result = compute_risk_profile(persona_retiree)
        final_idx = BAND_ORDER.index(result["final_band"])
        assert final_idx <= 1  # Conservative or Moderately Conservative
    
    def test_all_personas_produce_valid_profiles(self, all_personas):
        for p in all_personas:
            result = compute_risk_profile(p)
            assert 0 <= result["capacity_score"] <= 100
            assert 0 <= result["tolerance_score"] <= 100
            assert result["final_band"] in BAND_ORDER
            assert isinstance(result["needs_adviser_review"], bool)
    
    def test_doctor_high_capacity_low_tolerance(self, persona_doctor):
        """Doctor: high income (capacity) but very risk-averse (tolerance)."""
        result = compute_risk_profile(persona_doctor)
        cap_idx = BAND_ORDER.index(result["capacity_band"])
        tol_idx = BAND_ORDER.index(result["tolerance_band"])
        assert cap_idx > tol_idx  # Capacity exceeds tolerance
