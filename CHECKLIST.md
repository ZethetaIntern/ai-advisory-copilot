# Project Verification & Compliance Checklist
## Zeckathon PS04: AI Advisory Co-pilot for SEBI RIA

---

### 1. Hard Constraints Verification

| # | Hard Constraint | Status | Implementation & Code Location |
|---|-----------------|:------:|--------------------------------|
| 1 | **Deterministic Numbers** (Every number from Python, never LLM) | ✅ PASS | Implemented in `planner/goal_planner.py`, `risk/engine.py`, `portfolio/fund_metrics.py`. LLM is restricted to explanation/drafting only. |
| 2 | **Never Guarantee/Promise Returns** | ✅ PASS | Guardrails in `guardrails/input_guard.py` & `guardrails/output_guard.py` scan and block promise patterns. Mandatory disclaimers appended. |
| 3 | **One-Command Reproducibility** (`make reproduce` / `./reproduce.sh`) | ✅ PASS | Executable via `python scripts/reproduce.py`. Random seed pinned to 42. Caching in `data/nav_cache/`. |
| 4 | **Cite or Refuse** (Uncited figures score negative; refuse over guess) | ✅ PASS | Verifier in `rag/verifier.py` enforces verbatim chunk verification. Refuses with `"Not found in the provided sources."` |
| 5 | **Code-Enforced Approval Gate** (DRAFT -> APPROVED; PDF blocked) | ✅ PASS | Enforced in `risk/approval.py` state machine. `export_pdf()` raises `PermissionError` if `status != APPROVED`. |
| 6 | **Free / Open Data Only** (AMFI NAVAll.txt, mfapi.in, SIDs) | ✅ PASS | Download script in `scripts/download_data.py`. Fetches AMFI NAVAll.txt and mfapi.in historical data. |

---

### 2. Deliverables Checklist

#### A. Risk Profiling (`risk/`)
- [x] Risk Capacity score (0-100) computed from objective data (income stability, horizon, liabilities, dependants, emergency fund).
- [x] Risk Tolerance score (0-100) computed from 8 behavioural questions + behavioural flag penalties (F&O, panic selling).
- [x] 5 Risk Bands: Conservative, Moderately Conservative, Moderate, Moderately Aggressive, Aggressive.
- [x] Conflict rule: $\text{Final} = \min(\text{Capacity}, \text{Tolerance})$. Sets `needs_adviser_review=True` if difference > 1 band.
- [x] Unit tests in `tests/test_risk_engine.py` (all passing).

#### B. Goal-Based Planner (`planner/`)
- [x] Compound inflation: $FV = PV \times (1+i)^n$ with separate configurable rates (general 6%, education 10%, medical 9%).
- [x] Required corpus and monthly SIP via Future Value of Annuity Due formula.
- [x] Step-up SIP supporting annual percentage increase (10% p.a.).
- [x] Linear glide path shifting equity to debt over the final 5-7 years before goal maturity.
- [x] Retiree persona: 3-Bucket Strategy (Cash, Debt, Growth) for 25 years with sequence-of-returns resilience.
- [x] All assumptions explicitly output and tracked.
- [x] Unit tests in `tests/test_goal_planner.py` (all passing).

#### C. Portfolio Construction (`portfolio/`)
- [x] Strict filter: Direct + Growth plans only.
- [x] NAV history metrics: Rolling 3Y/5Y CAGR, volatility, max drawdown, Sharpe ratio.
- [x] Transparent multi-factor scoring (Returns 30%, Sharpe 25%, Drawdown 20%, TER 15%, AUM/Tenure 10%).
- [x] Shortlist top 1-2 funds per bucket with natural language selection rationale.
- [x] 10-year backtest with annual rebalancing against composite benchmark.
- [x] Explicit limitations disclosure (survivorship bias, Jan 2013 direct plan history, past performance caveat).
- [x] Unit tests in `tests/test_portfolio.py` (all passing).

#### D. Research Assistant with RAG (`rag/`)
- [x] Ingest factsheets, SIDs, and portfolio disclosures chunked per page with doc name + page number metadata.
- [x] Structured SQLite key facts table (`data/fund_facts.db`) routing factual queries first.
- [x] Pure NumPy dense vector + BM25 hybrid retrieval with Reciprocal Rank Fusion (RRF).
- [x] Strict anti-hallucination Verifier verifying numbers & entities against cited chunk text.
- [x] Evaluation benchmark `eval/fund_qa_25.json` with 25 test questions.
- [x] Evaluation script `eval/eval_rag.py` reporting accuracy, citation rate, refusal rate, and zero hallucinations (100% score).

#### E. Guardrails (`guardrails/`)
- [x] Input layer detecting return guarantees, prompt injection, and approval bypass attempts.
- [x] Suitability rules (senior citizen small cap block, trader flag, low capacity block, emergency fund warnings).
- [x] Output layer scanning for promises and auto-appending all 5 mandatory SEBI RIA disclosures.
- [x] Evaluation dataset `eval/adversarial_prompts.json` with 30 attack prompts (100% defense rate).
- [x] Unit tests in `tests/test_guardrails.py` (all passing).

#### F. Adviser Dashboard + Approval Workflow (`app/`)
- [x] Streamlit dashboard (`app/dashboard.py`) with persona picker, 5 tabs, interactive Plotly charts.
- [x] Approval state machine: DRAFT -> PENDING_REVIEW -> APPROVED / REJECTED with immutable audit log.
- [x] Client-ready PDF export (`app/pdf_export.py`) blocked until approved.
- [x] FastAPI REST API backend (`app/api.py`) with integration tests (`tests/test_api.py`).

---

### 3. Six Persona Fixtures Verification

| # | Persona | Key Attributes | Test Status |
|---|---------|----------------|:-----------:|
| 1 | Arjun Mehta | Fresh graduate, 23, Rs 55k/mo, Bengaluru | ✅ PASS |
| 2 | Priya & Rahul Sharma | Young couple, 31, home loan, child education | ✅ PASS |
| 3 | Ketan Patel | Business owner, 44, irregular income, Surat | ✅ PASS |
| 4 | Dr. Sneha Kumar | Doctor, 38, high income, risk-averse, Patna | ✅ PASS |
| 5 | V. Sundararajan | Retiree, 68, Rs 80L corpus, 3-bucket decumulation | ✅ PASS |
| 6 | Vikram Desai | Aggressive trader, 29, F&O losses, suitability flags | ✅ PASS |

---

### 4. Test Suite Summary
* Total Pytest Tests: **73** (Approval: 12, Personas: 13, Risk Engine: 18, Goal Planner: 9, Portfolio: 7, Guardrails: 10, API: 4)
* Pass Rate: **100%** (73/73 passing)
* Execution Time: **~1.5 seconds**
