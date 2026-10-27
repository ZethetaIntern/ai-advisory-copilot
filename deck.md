# AI Advisory Co-pilot for SEBI-Registered Investment Advisers (RIA)
## Hackathon Pitch Deck (10 Slides)

---

### Slide 1: Title & Vision
* **Title:** AI Advisory Co-pilot for SEBI-Registered Investment Advisers (RIA)
* **Subtitle:** Fiduciary-Grade, Deterministic, Zero-Hallucination Decision Support System
* **Track:** Zeckathon PS04
* **Core Philosophy:** "The LLM explains; Python computes. The adviser governs; the client is protected."
* **Presenter / Team:** Senior ML/Fintech Engineering Team

---

### Slide 2: The Problem: The RIA Dilemma
* **Scale vs Fiduciary Duty:** India has over 1,300 registered RIAs serving 1.4B people. Personalizing goal-based financial plans for thousands of families is manually exhausting.
* **The Peril of Generic LLMs:**
  * Generic LLMs hallucinate numbers, NAVs, and expense ratios.
  * LLMs promise or imply guaranteed returns—a direct violation of SEBI regulations.
  * Direct execution without adviser supervision breaches SEBI Investment Advisers Regulations (2013).
* **Our Solution:** A co-pilot built with hard architectural constraints: zero mathematical hallucination, code-enforced approval state machine, and hybrid RAG with page-level verification.

---

### Slide 3: System Architecture & Workflow
```
[User / Adviser] <---> [Streamlit Dashboard / FastAPI]
                              │
    ┌─────────────────────────┼─────────────────────────┐
    ▼                         ▼                         ▼
[Risk Engine]         [Goal Planner]           [Portfolio Engine]
Capacity vs Tolerance  Compound Inflation       Direct Fund Screener
Deterministic Scores   FV of Annuity Due        10Y Backtest Engine
    │                         │                         │
    └─────────────────────────┼─────────────────────────┘
                              ▼
                [Guardrails & Suitability]
                • Input injection / guarantee filter
                • SEBI Reg 17 suitability checks
                • Output scan + mandatory disclosures
                              │
                              ▼
                [Research Assistant (RAG)]
                • SQLite Structured Fact Table Router
                • BM25 + Dense Semantic Hybrid Retrieval
                • Strict Verifier (verbatim page citations)
                              │
                              ▼
                [Adviser Approval State Machine]
                • DRAFT -> PENDING_REVIEW -> APPROVED
                • Immutable Audit Trail Log
                • Client PDF Gate (Blocks export unless approved)
```

---

### Slide 4: Deterministic Risk Profiling & Conflict Resolution
* **Dual-Axis Assessment:**
  1. **Risk Capacity (0-100):** Objective financial data—income stability, goal horizons, debt-to-income, dependants, emergency fund coverage, and human capital stage.
  2. **Risk Tolerance (0-100):** 8 behavioural psychometric questions + behavioural flag penalties (F&O derivatives trading, past panic selling).
* **Transparent Conflict Rule:**
  $$\text{Final Band} = \min(\text{Capacity Band}, \text{Tolerance Band})$$
* **Adviser Review Trigger:** If capacity and tolerance differ by >1 band, sets `needs_adviser_review=True` with automated natural language diagnostic.
* **Demonstrated Across 6 Diverse Personas:** From fresh grad Arjun Mehta to aggressive trader Vikram Desai.

---

### Slide 5: Goal-Based Financial Planner & Glide Path
* **Dynamic Compound Inflation:**
  $$FV = PV \times (1 + i)^n$$
  * Configurable by category: General (6%), Higher Education (10%), Healthcare (9%).
* **Mathematical Precision:**
  * Monthly Flat SIP via Future Value of Annuity Due formula.
  * Step-Up SIP (10% annual escalation) modeling real salary growth.
* **Linear Glide Path:** Linearly shifts equity to debt over the final 5 years before goal maturity to eliminate sequence-of-returns drawdown risk.
* **Retiree Decumulation Engine:**
  * 3-Bucket Strategy: Bucket 1 (2Y Cash/Liquid), Bucket 2 (4Y Short Duration Debt), Bucket 3 (Growth Equity/Hybrid).
  * Stress-tested across 25 years with sequence-of-returns resilience.

---

### Slide 6: Direct-Plan Mutual Fund Selection & 10Y Backtest
* **SEBI Compliance:** Direct Plans only (zero distribution commission or trailer fees).
* **Multi-Factor Scoring Model (100 pts):**
  * 30% Return consistency (3Y & 5Y rolling returns)
  * 25% Risk-adjusted performance (Sharpe Ratio with $R_f = 6.5\%$)
  * 20% Downside drawdown protection (Max Drawdown)
  * 15% Low Expense Ratio (Direct TER)
  * 10% AUM Liquidity & Fund Manager Tenure
* **10-Year Annual Rebalancing Backtest:**
  * Models real fund performance vs 65:35 Equity/Debt composite benchmark.
  * Explicitly reports CAGR, Volatility, Sharpe, and Drawdowns with statutory methodology limitations.

---

### Slide 7: RAG Research Assistant with Verifier (The Crown Jewel)
* **The Challenge:** Advisers need exact facts from 100+ page SIDs and monthly factsheets.
* **Two-Stage Routing Architecture:**
  1. **Structured Fact Table First:** Direct queries (TER, exit load, benchmark, min SIP, AUM, manager) resolve instantly from SQLite with verified document/page coordinates.
  2. **Hybrid BM25 + Dense Semantic Retrieval:** Multi-hop queries retrieve top page chunks via Reciprocal Rank Fusion (RRF).
* **Strict Anti-Hallucination Verifier:**
  * Verifies every number, percentage, and named entity against the cited source text.
  * Missing citations or unverified numbers trigger an automatic refusal: *"Not found in the provided sources."*
* **Benchmark Results (25 Test Questions):**
  * **Accuracy Rate:** 100.0% (25/25)
  * **Citation Rate on Factuals:** 100.0% (18/18)
  * **Refusal Rate on Unanswerable:** 100.0% (7/7)
  * **Hallucination Rate:** 0.0%

---

### Slide 8: Multi-Layer Guardrails & Suitability Engine
* **Input Layer:**
  * Blocks return guarantee demands (*"guarantee 20%"*, *"double my money"*).
  * Neutralizes prompt injections (*"ignore previous instructions"*, *"DAN mode"*).
  * Intercepts approval bypass attempts (*"send directly to client"*).
  * **Adversarial Benchmark:** 30/30 attacks blocked (100% defense rate).
* **Suitability Layer (SEBI Regulation 17):**
  * Senior citizens (>60) restricted from excessive equity (>40%) and small caps.
  * Speculative F&O traders redirected away from high-beta gambles to disciplined index SIPs.
  * Low capacity clients blocked from high-risk equity.
* **Output Layer:**
  * Scans draft text for prohibited return promises.
  * Auto-appends all 5 mandatory SEBI RIA disclosures.

---

### Slide 9: Approval Gate & Adviser Workflow
* **Code-Level State Machine:**
  $$\text{DRAFT} \longrightarrow \text{PENDING\_REVIEW} \longrightarrow \text{APPROVED} \text{ / } \text{REJECTED}$$
* **Hard Enforcement:**
  * Calling `export_pdf()` when status $\ne$ `APPROVED` raises a Python `PermissionError`.
  * No client-facing output can leave the system without explicit adviser authentication and sign-off.
* **Full Audit Trail:**
  * Every status transition logs adviser ID, digital timestamp, and review rationale.
* **Client-Ready PDF Generation:**
  * Generates clean, institutional-grade PDF with client profile, goal schedules, fund rationales, backtests, and mandatory regulatory disclaimers.

---

### Slide 10: Production Readiness, Limitations & Roadmap
* **What Works Today (100% Reproducible):**
  * Complete test suite passing: 69/69 unit & integration tests in ~1 second.
  * Reproduce script runs all 6 personas, RAG eval, and backtests with one command.
  * Live interactive Streamlit dashboard & FastAPI backend.
* **Documented Limitations (Honesty First):**
  * Direct plan historical data starts from Jan 2013 (13-year max live history).
  * Tax implications (LTCG 12.5%, STCG 20%) not modeled in this prototype.
  * Curated universe of top 30-50 direct mutual funds by category AUM.
* **Future Roadmap:**
  * Real-time CAMS/KFintech CAS statement parsing.
  * Multi-account household tax-loss harvesting engine.
  * Automated annual SEBI compliance audit packet generator.
