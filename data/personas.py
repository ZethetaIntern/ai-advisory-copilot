"""
Persona definitions for the AI Advisory Co-pilot.
All 6 test personas as structured data.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import os


class Goal(BaseModel):
    """A financial goal."""
    name: str
    target_amount_today: float = Field(description="Target amount in today's rupees")
    years_to_goal: int
    priority: str = Field(description="HIGH / MEDIUM / LOW")
    inflation_type: str = Field(default="general", description="general / education / medical")
    is_recurring: bool = Field(default=False, description="True for retirement income goals")
    monthly_income_needed: Optional[float] = Field(default=None, description="For retirement income goals")
    income_years: Optional[int] = Field(default=None, description="Years of income needed in retirement")


class BehaviouralResponse(BaseModel):
    """Response to a behavioural risk question."""
    question_id: str
    question: str
    answer: str
    score: int = Field(ge=0, le=10)


class Persona(BaseModel):
    """Full client persona for the advisory co-pilot."""
    id: str
    name: str
    age: int
    city: str
    occupation: str
    monthly_income: float
    monthly_expenses: float
    existing_investments: float = 0
    existing_debt: float = 0
    monthly_emi: float = 0
    emergency_fund: float = 0
    dependants: int = 0
    income_stability: str = Field(description="STABLE / MODERATE / IRREGULAR")
    has_health_insurance: bool = True
    has_life_insurance: bool = False
    pension_income: float = 0
    
    # Behavioural flags
    trades_fno: bool = False
    past_panic_selling: bool = False
    previous_investment_experience: str = Field(default="NONE", description="NONE / BEGINNER / INTERMEDIATE / ADVANCED")
    
    # Goals
    goals: List[Goal]
    
    # Behavioural questionnaire responses
    behavioural_responses: List[BehaviouralResponse] = []
    
    # Additional notes
    notes: str = ""


# The 8-10 standard behavioural questions
BEHAVIOURAL_QUESTIONS = [
    {
        "id": "q1",
        "question": "If your portfolio dropped 25% in one month, what would you do?",
        "options": {
            "Sell everything immediately": 1,
            "Sell some holdings to reduce risk": 3,
            "Do nothing and wait": 6,
            "Buy more at lower prices": 9,
        }
    },
    {
        "id": "q2",
        "question": "What is your primary investment objective?",
        "options": {
            "Capital preservation": 2,
            "Regular income": 4,
            "Growth with some income": 6,
            "Aggressive growth": 9,
        }
    },
    {
        "id": "q3",
        "question": "How long can you leave your money invested without needing it?",
        "options": {
            "Less than 1 year": 1,
            "1-3 years": 3,
            "3-7 years": 6,
            "More than 7 years": 9,
        }
    },
    {
        "id": "q4",
        "question": "How would you describe your knowledge of financial markets?",
        "options": {
            "Very limited": 2,
            "Basic understanding": 4,
            "Good understanding": 7,
            "Expert level": 9,
        }
    },
    {
        "id": "q5",
        "question": "Which statement best describes your attitude to investment risk?",
        "options": {
            "I want to protect my capital even if returns are low": 2,
            "I want steady returns with minimal fluctuation": 4,
            "I accept moderate fluctuation for better long-term returns": 7,
            "I am comfortable with high volatility for potentially high returns": 9,
        }
    },
    {
        "id": "q6",
        "question": "If a friend recommended a hot stock tip, what would you do?",
        "options": {
            "Ignore it completely": 5,
            "Research it carefully before deciding": 7,
            "Invest a small amount to try": 4,
            "Invest a significant amount quickly": 2,
        }
    },
    {
        "id": "q7",
        "question": "What percentage of your monthly income are you willing to invest?",
        "options": {
            "Less than 10%": 3,
            "10-20%": 5,
            "20-35%": 7,
            "More than 35%": 9,
        }
    },
    {
        "id": "q8",
        "question": "How do you react when you see others making money in the market while your investments are flat?",
        "options": {
            "I feel anxious and want to switch": 2,
            "I feel tempted but stay the course": 5,
            "I stick to my plan without concern": 7,
            "I review and adjust only if fundamentally warranted": 8,
        }
    },
]


def _build_personas() -> List[Dict[str, Any]]:
    """Build all 6 test personas."""
    
    personas = [
        # 1. Fresh graduate
        {
            "id": "fresh_grad",
            "name": "Arjun Mehta",
            "age": 23,
            "city": "Bengaluru",
            "occupation": "Software Engineer",
            "monthly_income": 55000,
            "monthly_expenses": 30000,
            "existing_investments": 50000,
            "existing_debt": 0,
            "monthly_emi": 0,
            "emergency_fund": 80000,
            "dependants": 0,
            "income_stability": "STABLE",
            "has_health_insurance": True,
            "has_life_insurance": False,
            "pension_income": 0,
            "trades_fno": False,
            "past_panic_selling": False,
            "previous_investment_experience": "BEGINNER",
            "goals": [
                {
                    "name": "Emergency Fund (6 months)",
                    "target_amount_today": 180000,
                    "years_to_goal": 1,
                    "priority": "HIGH",
                    "inflation_type": "general",
                },
                {
                    "name": "Long-term Wealth Creation",
                    "target_amount_today": 10000000,
                    "years_to_goal": 25,
                    "priority": "MEDIUM",
                    "inflation_type": "general",
                },
            ],
            "behavioural_responses": [
                {"question_id": "q1", "question": "If your portfolio dropped 25% in one month, what would you do?", "answer": "Do nothing and wait", "score": 6},
                {"question_id": "q2", "question": "What is your primary investment objective?", "answer": "Aggressive growth", "score": 9},
                {"question_id": "q3", "question": "How long can you leave your money invested without needing it?", "answer": "More than 7 years", "score": 9},
                {"question_id": "q4", "question": "How would you describe your knowledge of financial markets?", "answer": "Basic understanding", "score": 4},
                {"question_id": "q5", "question": "Which statement best describes your attitude to investment risk?", "answer": "I accept moderate fluctuation for better long-term returns", "score": 7},
                {"question_id": "q6", "question": "If a friend recommended a hot stock tip, what would you do?", "answer": "Research it carefully before deciding", "score": 7},
                {"question_id": "q7", "question": "What percentage of your monthly income are you willing to invest?", "answer": "20-35%", "score": 7},
                {"question_id": "q8", "question": "How do you react when you see others making money in the market while your investments are flat?", "answer": "I feel tempted but stay the course", "score": 5},
            ],
            "notes": "Fresh out of college, first job. Wants to build emergency fund first, then start long-term investing. No financial dependants.",
        },
        
        # 2. Young couple
        {
            "id": "young_couple",
            "name": "Priya & Rahul Sharma",
            "age": 31,
            "city": "Pune",
            "occupation": "IT Professionals (dual income)",
            "monthly_income": 180000,
            "monthly_expenses": 95000,
            "existing_investments": 1500000,
            "existing_debt": 4500000,
            "monthly_emi": 38000,
            "emergency_fund": 400000,
            "dependants": 0,
            "income_stability": "STABLE",
            "has_health_insurance": True,
            "has_life_insurance": True,
            "pension_income": 0,
            "trades_fno": False,
            "past_panic_selling": False,
            "previous_investment_experience": "INTERMEDIATE",
            "goals": [
                {
                    "name": "Child's Higher Education",
                    "target_amount_today": 3000000,
                    "years_to_goal": 15,
                    "priority": "HIGH",
                    "inflation_type": "education",
                },
                {
                    "name": "Home Loan Prepayment",
                    "target_amount_today": 2000000,
                    "years_to_goal": 5,
                    "priority": "MEDIUM",
                    "inflation_type": "general",
                },
                {
                    "name": "Retirement Corpus",
                    "target_amount_today": 50000000,
                    "years_to_goal": 29,
                    "priority": "MEDIUM",
                    "inflation_type": "general",
                },
            ],
            "behavioural_responses": [
                {"question_id": "q1", "question": "If your portfolio dropped 25% in one month, what would you do?", "answer": "Do nothing and wait", "score": 6},
                {"question_id": "q2", "question": "What is your primary investment objective?", "answer": "Growth with some income", "score": 6},
                {"question_id": "q3", "question": "How long can you leave your money invested without needing it?", "answer": "3-7 years", "score": 6},
                {"question_id": "q4", "question": "How would you describe your knowledge of financial markets?", "answer": "Good understanding", "score": 7},
                {"question_id": "q5", "question": "Which statement best describes your attitude to investment risk?", "answer": "I accept moderate fluctuation for better long-term returns", "score": 7},
                {"question_id": "q6", "question": "If a friend recommended a hot stock tip, what would you do?", "answer": "Research it carefully before deciding", "score": 7},
                {"question_id": "q7", "question": "What percentage of your monthly income are you willing to invest?", "answer": "20-35%", "score": 7},
                {"question_id": "q8", "question": "How do you react when you see others making money in the market while your investments are flat?", "answer": "I review and adjust only if fundamentally warranted", "score": 8},
            ],
            "notes": "Dual income couple with home loan. Planning for child's education. Moderate risk appetite.",
        },
        
        # 3. Small business owner
        {
            "id": "business_owner",
            "name": "Ketan Patel",
            "age": 44,
            "city": "Surat",
            "occupation": "Textile Business Owner",
            "monthly_income": 250000,
            "monthly_expenses": 150000,
            "existing_investments": 3000000,
            "existing_debt": 1500000,
            "monthly_emi": 25000,
            "emergency_fund": 1500000,
            "dependants": 3,
            "income_stability": "IRREGULAR",
            "has_health_insurance": True,
            "has_life_insurance": True,
            "pension_income": 0,
            "trades_fno": False,
            "past_panic_selling": True,
            "previous_investment_experience": "BEGINNER",
            "goals": [
                {
                    "name": "Retirement at 58",
                    "target_amount_today": 30000000,
                    "years_to_goal": 14,
                    "priority": "HIGH",
                    "inflation_type": "general",
                },
                {
                    "name": "Daughter's Wedding",
                    "target_amount_today": 2500000,
                    "years_to_goal": 8,
                    "priority": "MEDIUM",
                    "inflation_type": "general",
                },
                {
                    "name": "Son's Education",
                    "target_amount_today": 2000000,
                    "years_to_goal": 6,
                    "priority": "HIGH",
                    "inflation_type": "education",
                },
            ],
            "behavioural_responses": [
                {"question_id": "q1", "question": "If your portfolio dropped 25% in one month, what would you do?", "answer": "Sell some holdings to reduce risk", "score": 3},
                {"question_id": "q2", "question": "What is your primary investment objective?", "answer": "Growth with some income", "score": 6},
                {"question_id": "q3", "question": "How long can you leave your money invested without needing it?", "answer": "3-7 years", "score": 6},
                {"question_id": "q4", "question": "How would you describe your knowledge of financial markets?", "answer": "Basic understanding", "score": 4},
                {"question_id": "q5", "question": "Which statement best describes your attitude to investment risk?", "answer": "I want steady returns with minimal fluctuation", "score": 4},
                {"question_id": "q6", "question": "If a friend recommended a hot stock tip, what would you do?", "answer": "Invest a small amount to try", "score": 4},
                {"question_id": "q7", "question": "What percentage of your monthly income are you willing to invest?", "answer": "10-20%", "score": 5},
                {"question_id": "q8", "question": "How do you react when you see others making money in the market while your investments are flat?", "answer": "I feel anxious and want to switch", "score": 2},
            ],
            "notes": "Irregular income from textile business. High cash holdings. Past panic selling during 2020 crash. Wants retirement security.",
        },
        
        # 4. Doctor
        {
            "id": "doctor",
            "name": "Dr. Sneha Kumar",
            "age": 38,
            "city": "Patna",
            "occupation": "Cardiologist",
            "monthly_income": 350000,
            "monthly_expenses": 120000,
            "existing_investments": 2000000,
            "existing_debt": 800000,
            "monthly_emi": 15000,
            "emergency_fund": 500000,
            "dependants": 2,
            "income_stability": "STABLE",
            "has_health_insurance": True,
            "has_life_insurance": True,
            "pension_income": 0,
            "trades_fno": False,
            "past_panic_selling": False,
            "previous_investment_experience": "NONE",
            "goals": [
                {
                    "name": "Retirement at 60",
                    "target_amount_today": 50000000,
                    "years_to_goal": 22,
                    "priority": "HIGH",
                    "inflation_type": "general",
                },
                {
                    "name": "Parents Medical Corpus",
                    "target_amount_today": 5000000,
                    "years_to_goal": 5,
                    "priority": "HIGH",
                    "inflation_type": "medical",
                },
                {
                    "name": "Children's Education",
                    "target_amount_today": 5000000,
                    "years_to_goal": 12,
                    "priority": "HIGH",
                    "inflation_type": "education",
                },
            ],
            "behavioural_responses": [
                {"question_id": "q1", "question": "If your portfolio dropped 25% in one month, what would you do?", "answer": "Sell everything immediately", "score": 1},
                {"question_id": "q2", "question": "What is your primary investment objective?", "answer": "Capital preservation", "score": 2},
                {"question_id": "q3", "question": "How long can you leave your money invested without needing it?", "answer": "3-7 years", "score": 6},
                {"question_id": "q4", "question": "How would you describe your knowledge of financial markets?", "answer": "Very limited", "score": 2},
                {"question_id": "q5", "question": "Which statement best describes your attitude to investment risk?", "answer": "I want to protect my capital even if returns are low", "score": 2},
                {"question_id": "q6", "question": "If a friend recommended a hot stock tip, what would you do?", "answer": "Ignore it completely", "score": 5},
                {"question_id": "q7", "question": "What percentage of your monthly income are you willing to invest?", "answer": "10-20%", "score": 5},
                {"question_id": "q8", "question": "How do you react when you see others making money in the market while your investments are flat?", "answer": "I feel anxious and want to switch", "score": 2},
            ],
            "notes": "High income but very risk-averse. Almost no investment experience. Under-invested relative to income. Needs medical corpus for aging parents.",
        },
        
        # 5. Retiree
        {
            "id": "retiree",
            "name": "V. Sundararajan",
            "age": 68,
            "city": "Chennai",
            "occupation": "Retired Bank Manager",
            "monthly_income": 35000,
            "monthly_expenses": 45000,
            "existing_investments": 8000000,
            "existing_debt": 0,
            "monthly_emi": 0,
            "emergency_fund": 300000,
            "dependants": 1,
            "income_stability": "STABLE",
            "has_health_insurance": True,
            "has_life_insurance": False,
            "pension_income": 35000,
            "trades_fno": False,
            "past_panic_selling": False,
            "previous_investment_experience": "INTERMEDIATE",
            "goals": [
                {
                    "name": "Monthly Retirement Income",
                    "target_amount_today": 10000,
                    "years_to_goal": 0,
                    "priority": "HIGH",
                    "inflation_type": "general",
                    "is_recurring": True,
                    "monthly_income_needed": 10000,
                    "income_years": 25,
                },
                {
                    "name": "Medical Emergency Corpus",
                    "target_amount_today": 2000000,
                    "years_to_goal": 2,
                    "priority": "HIGH",
                    "inflation_type": "medical",
                },
            ],
            "behavioural_responses": [
                {"question_id": "q1", "question": "If your portfolio dropped 25% in one month, what would you do?", "answer": "Sell some holdings to reduce risk", "score": 3},
                {"question_id": "q2", "question": "What is your primary investment objective?", "answer": "Regular income", "score": 4},
                {"question_id": "q3", "question": "How long can you leave your money invested without needing it?", "answer": "Less than 1 year", "score": 1},
                {"question_id": "q4", "question": "How would you describe your knowledge of financial markets?", "answer": "Good understanding", "score": 7},
                {"question_id": "q5", "question": "Which statement best describes your attitude to investment risk?", "answer": "I want to protect my capital even if returns are low", "score": 2},
                {"question_id": "q6", "question": "If a friend recommended a hot stock tip, what would you do?", "answer": "Ignore it completely", "score": 5},
                {"question_id": "q7", "question": "What percentage of your monthly income are you willing to invest?", "answer": "Less than 10%", "score": 3},
                {"question_id": "q8", "question": "How do you react when you see others making money in the market while your investments are flat?", "answer": "I stick to my plan without concern", "score": 7},
            ],
            "notes": "Retired bank manager with Rs 80 lakh corpus and Rs 35k pension. Needs supplemental monthly income. Expenses exceed pension by Rs 10k/month. Conservative approach needed for capital preservation.",
        },
        
        # 6. Aggressive trader
        {
            "id": "trader",
            "name": "Vikram Desai",
            "age": 29,
            "city": "Mumbai",
            "occupation": "Options Trader / Freelance",
            "monthly_income": 120000,
            "monthly_expenses": 80000,
            "existing_investments": 500000,
            "existing_debt": 200000,
            "monthly_emi": 10000,
            "emergency_fund": 50000,
            "dependants": 0,
            "income_stability": "IRREGULAR",
            "has_health_insurance": False,
            "has_life_insurance": False,
            "pension_income": 0,
            "trades_fno": True,
            "past_panic_selling": True,
            "previous_investment_experience": "ADVANCED",
            "goals": [
                {
                    "name": "Quick Wealth - 2x in 3 years",
                    "target_amount_today": 5000000,
                    "years_to_goal": 3,
                    "priority": "HIGH",
                    "inflation_type": "general",
                },
                {
                    "name": "Emergency Fund",
                    "target_amount_today": 500000,
                    "years_to_goal": 1,
                    "priority": "HIGH",
                    "inflation_type": "general",
                },
            ],
            "behavioural_responses": [
                {"question_id": "q1", "question": "If your portfolio dropped 25% in one month, what would you do?", "answer": "Buy more at lower prices", "score": 9},
                {"question_id": "q2", "question": "What is your primary investment objective?", "answer": "Aggressive growth", "score": 9},
                {"question_id": "q3", "question": "How long can you leave your money invested without needing it?", "answer": "1-3 years", "score": 3},
                {"question_id": "q4", "question": "How would you describe your knowledge of financial markets?", "answer": "Expert level", "score": 9},
                {"question_id": "q5", "question": "Which statement best describes your attitude to investment risk?", "answer": "I am comfortable with high volatility for potentially high returns", "score": 9},
                {"question_id": "q6", "question": "If a friend recommended a hot stock tip, what would you do?", "answer": "Invest a small amount to try", "score": 4},
                {"question_id": "q7", "question": "What percentage of your monthly income are you willing to invest?", "answer": "More than 35%", "score": 9},
                {"question_id": "q8", "question": "How do you react when you see others making money in the market while your investments are flat?", "answer": "I feel anxious and want to switch", "score": 2},
            ],
            "notes": "Active F&O trader with losses. Wants 'high returns fast'. Past panic selling. Low emergency fund. No insurance. The co-pilot must flag suitability issues and NOT simply comply with aggressive demands.",
        },
    ]
    
    return personas


def load_personas() -> List[Dict[str, Any]]:
    """Load all personas. Returns list of dicts."""
    return _build_personas()


def get_persona_by_id(persona_id: str) -> Dict[str, Any]:
    """Get a single persona by ID."""
    personas = load_personas()
    for p in personas:
        if p["id"] == persona_id:
            return p
    raise ValueError(f"Persona not found: {persona_id}")


def validate_persona(persona: Dict[str, Any]) -> Persona:
    """Validate a persona dict against the Pydantic schema."""
    return Persona(**persona)


if __name__ == "__main__":
    """Print all personas for verification."""
    personas = load_personas()
    for p in personas:
        validated = validate_persona(p)
        print(f"\n{validated.name} ({validated.id})")
        print(f"  Age: {validated.age}, City: {validated.city}")
        print(f"  Income: Rs {validated.monthly_income:,.0f}/month")
        print(f"  Goals: {len(validated.goals)}")
        for g in validated.goals:
            print(f"    - {g.name}: Rs {g.target_amount_today:,.0f} in {g.years_to_goal}y")
