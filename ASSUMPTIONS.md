# Assumptions

This document records all assumptions made in the AI Advisory Co-pilot project.
Every assumption is explicit and reviewable by the adviser.

## General Assumptions

1. **Currency**: All amounts are in Indian Rupees (INR/Rs).
2. **Tax**: Tax implications are NOT modeled in this prototype. In a production system, LTCG/STCG, indexation, and new tax regime would be incorporated.
3. **Inflation is configurable**: Default assumptions are general ~6%, education ~10%, medical ~9%.
4. **No guarantee of returns**: All projections are based on historical averages and are explicitly marked as assumptions, not promises.
5. **Direct plans only**: We recommend only Direct Growth plans (no regular/commission plans) per SEBI RIA guidelines.

## Risk Profiling Assumptions

6. **Risk Capacity** is computed from objective financial data (income stability, horizon, liabilities, dependants, emergency fund).
7. **Risk Tolerance** is computed from 8 behavioural questions scored 0-10 each, plus behavioural flags (F&O trading, panic selling history).
8. **Conflict resolution**: Final band = min(capacity band, tolerance band). If they differ by >1 band, `needs_adviser_review=True`.
9. **Band mapping**: 0-20 Conservative, 21-40 Moderately Conservative, 41-60 Moderate, 61-80 Moderately Aggressive, 81-100 Aggressive.

## Financial Planning Assumptions

10. **SIP formula**: Future Value of Annuity: FV = PMT × [((1+r)^n - 1) / r] × (1+r) for beginning-of-period.
11. **Step-up SIP**: Assumed 10% annual increase in SIP amount (configurable).
12. **Expected returns by asset class** (nominal, NOT guaranteed):
    - Large Cap Equity: ~12% p.a.
    - Flexi/Multi Cap: ~13% p.a.
    - Mid Cap: ~14% p.a.
    - Small Cap: ~15% p.a.
    - Balanced/Hybrid: ~10% p.a.
    - Short Duration Debt: ~7% p.a.
    - Liquid/Money Market: ~6% p.a.
    - Nifty 50 Index: ~12% p.a.
13. **Retirement**: 4% safe withdrawal rate (adjusted for Indian context). Bucket strategy with 2-year cash, 3-year debt, rest in equity.
14. **Glide path**: Linear shift from equity to debt over the final 5 years before each goal.

## Data Assumptions

15. **NAV data source**: AMFI NAVAll.txt and mfapi.in (free, public APIs).
16. **If data download fails**, we fall back to cached data or documented sample data and label it clearly.
17. **Fund selection**: Based on publicly available data only (NAV history, scheme master). Expense ratios and AUM from factsheets.
18. **Backtest limitation**: Survivorship bias exists (we can only backtest funds that exist today). Clearly disclosed.
19. **Past performance caveat**: All historical returns are past performance and do not indicate future results.

## RAG / Research Assumptions

20. **Document sources**: Publicly available factsheets, SIDs, and portfolio disclosures from AMC websites.
21. **Chunking**: Per-page chunking with doc name + page number metadata for precise citations.
22. **Citation requirement**: Every factual claim must have a source citation. "Not found in sources" is preferred over guessing.
23. **Verifier**: Numbers and named entities in answers are verified against cited chunk text.

## Regulatory / Compliance Assumptions

24. **SEBI RIA Regulations (2013, amended 2020)**: Adviser must act in client's best interest, recommend direct plans, disclose conflicts.
25. **No execution**: This is an advisory tool only. No transactions are executed.
26. **Adviser approval required**: All client-facing output goes through DRAFT -> APPROVED state machine.
27. **Mandatory disclosures**: Auto-appended to all outputs (direct plan, no commission, risk statement, past performance caveat).

## Persona Assumptions

28. **Income figures**: Monthly take-home (post-tax) unless noted otherwise.
29. **Existing investments**: Total current investment portfolio value.
30. **Emergency fund**: Current liquid savings earmarked for emergencies.
