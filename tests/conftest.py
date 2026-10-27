"""Shared test fixtures."""
import os
import sys
import pytest
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.personas import load_personas


@pytest.fixture
def all_personas():
    return load_personas()


@pytest.fixture
def persona_fresh_grad(all_personas):
    return next(p for p in all_personas if p["id"] == "fresh_grad")


@pytest.fixture
def persona_young_couple(all_personas):
    return next(p for p in all_personas if p["id"] == "young_couple")


@pytest.fixture
def persona_business_owner(all_personas):
    return next(p for p in all_personas if p["id"] == "business_owner")


@pytest.fixture
def persona_doctor(all_personas):
    return next(p for p in all_personas if p["id"] == "doctor")


@pytest.fixture
def persona_retiree(all_personas):
    return next(p for p in all_personas if p["id"] == "retiree")


@pytest.fixture
def persona_trader(all_personas):
    return next(p for p in all_personas if p["id"] == "trader")
