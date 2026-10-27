"""Tests for persona data integrity."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.personas import load_personas, validate_persona, get_persona_by_id


class TestPersonaData:
    """Test all persona fixtures."""
    
    def test_six_personas_exist(self, all_personas):
        assert len(all_personas) == 6
    
    def test_all_persona_ids(self, all_personas):
        ids = {p["id"] for p in all_personas}
        expected = {"fresh_grad", "young_couple", "business_owner", "doctor", "retiree", "trader"}
        assert ids == expected
    
    def test_all_personas_validate(self, all_personas):
        for p in all_personas:
            validated = validate_persona(p)
            assert validated.name
            assert validated.age > 0
            assert validated.monthly_income >= 0
    
    def test_fresh_grad(self, persona_fresh_grad):
        p = persona_fresh_grad
        assert p["age"] == 23
        assert p["city"] == "Bengaluru"
        assert p["monthly_income"] == 55000
        assert p["dependants"] == 0
        assert len(p["goals"]) >= 2
    
    def test_young_couple(self, persona_young_couple):
        p = persona_young_couple
        assert p["age"] == 31
        assert p["city"] == "Pune"
        assert p["monthly_emi"] > 0  # Has home loan
        assert any("Education" in g["name"] for g in p["goals"])
    
    def test_business_owner(self, persona_business_owner):
        p = persona_business_owner
        assert p["income_stability"] == "IRREGULAR"
        assert p["past_panic_selling"] == True
        assert p["dependants"] == 3
    
    def test_doctor(self, persona_doctor):
        p = persona_doctor
        assert p["monthly_income"] == 350000
        assert p["previous_investment_experience"] == "NONE"
        assert any("Medical" in g["name"] for g in p["goals"])
    
    def test_retiree(self, persona_retiree):
        p = persona_retiree
        assert p["age"] == 68
        assert p["pension_income"] == 35000
        assert p["existing_investments"] == 8000000
        assert any(g.get("is_recurring", False) for g in p["goals"])
    
    def test_trader(self, persona_trader):
        p = persona_trader
        assert p["trades_fno"] == True
        assert p["past_panic_selling"] == True
        assert p["income_stability"] == "IRREGULAR"
        assert not p["has_health_insurance"]
    
    def test_all_have_behavioural_responses(self, all_personas):
        for p in all_personas:
            assert len(p["behavioural_responses"]) == 8, f"{p['name']} has {len(p['behavioural_responses'])} responses, expected 8"
    
    def test_all_have_goals(self, all_personas):
        for p in all_personas:
            assert len(p["goals"]) >= 1, f"{p['name']} has no goals"
    
    def test_get_persona_by_id(self):
        p = get_persona_by_id("fresh_grad")
        assert p["name"] == "Arjun Mehta"
    
    def test_get_persona_invalid_id(self):
        with pytest.raises(ValueError):
            get_persona_by_id("nonexistent")
