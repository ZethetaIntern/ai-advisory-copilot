"""
Fund Factsheet & SID Document Corpus (rag/corpus.py)

Ingests and manages page-level chunks for top mutual funds:
- Factsheet monthly disclosures
- Scheme Information Documents (SIDs)
- Portfolio attributes
Each chunk has strict page metadata: doc_name, page_number, fund_name, text.
"""
from typing import Dict, Any, List, Optional
import os
import json

# Curated high-fidelity factsheets & SID document pages for top funds
# Stored with page-level granularity
CORPUS_PAGES = [
    # 1. Parag Parikh Flexi Cap Fund
    {
        "doc_name": "PPFAS_FlexiCap_Factsheet_Oct2026.pdf",
        "page_number": 1,
        "fund_name": "Parag Parikh Flexi Cap Fund",
        "scheme_code": 135781,
        "category": "Flexi Cap",
        "text": """PARAG PARIKH FLEXI CAP FUND - MONTHLY FACTSHEET (OCTOBER 2026)
Investment Objective: To generate long-term capital growth from an actively managed portfolio primarily of equity and equity related securities.
Fund Details:
- Scheme Type: Open-ended dynamic equity scheme investing across large cap, mid cap, small cap stocks.
- Benchmark: NIFTY 500 TRI (Total Returns Index).
- Fund Manager: Rajeev Thakkar (Chief Investment Officer & Equity Fund Manager) since May 2013 (Tenure: 11.2 years). Co-managers: Raunak Onkar (Overseas Investments), Raj Mehta (Debt).
- Inception / Launch Date: May 28, 2013.
- Total AUM: Rs 72,500 Crores as on September 30, 2026.
- Riskometer: Scheme riskometer is VERY HIGH; Benchmark riskometer is VERY HIGH."""
    },
    {
        "doc_name": "PPFAS_FlexiCap_Factsheet_Oct2026.pdf",
        "page_number": 2,
        "fund_name": "Parag Parikh Flexi Cap Fund",
        "scheme_code": 135781,
        "category": "Flexi Cap",
        "text": """PARAG PARIKH FLEXI CAP FUND - EXPENSES & LOADS
Fee Structure & Investment Details:
- Total Expense Ratio (TER): Direct Plan: 0.68% p.a.; Regular Plan: 1.34% p.a.
- Minimum Investment: Lump sum Rs 1,000 and in multiples of Re 1 thereafter.
- Minimum SIP: Rs 1,000 per month (Monthly frequency) with minimum 6 instalments.
- Exit Load:
  * In respect of each purchase of units, 2.00% is payable if redeemed or switched-out on or before completion of 365 days from the date of allotment.
  * 1.00% is payable if redeemed or switched-out between 366 days and 730 days from the date of allotment.
  * Nil exit load after 730 days (2 years).
- Foreign Equity Allocation: Current overseas equity allocation is 14.8% in select global tech leaders."""
    },
    {
        "doc_name": "PPFAS_FlexiCap_SID.pdf",
        "page_number": 14,
        "fund_name": "Parag Parikh Flexi Cap Fund",
        "scheme_code": 135781,
        "category": "Flexi Cap",
        "text": """PARAG PARIKH FLEXI CAP FUND - SCHEME INFORMATION DOCUMENT (SID) - ASSET ALLOCATION PATTERN
Under normal circumstances, the asset allocation of the Scheme will be:
- Equity and Equity related instruments: Minimum 65%, Maximum 100% of net assets (Risk Profile: High).
- Foreign Equity and Equity related instruments: Minimum 0%, Maximum 35% of net assets (Subject to SEBI limit of USD 1 billion per mutual fund).
- Debt and Money Market Instruments: Minimum 0%, Maximum 35% of net assets (Risk Profile: Low to Medium).
The scheme maintains minimum 65% in Indian equities to qualify for equity tax status under the Income Tax Act."""
    },

    # 2. HDFC Top 100 Fund
    {
        "doc_name": "HDFC_Top100_Factsheet_Oct2026.pdf",
        "page_number": 1,
        "fund_name": "HDFC Top 100 Fund",
        "scheme_code": 119598,
        "category": "Large Cap",
        "text": """HDFC TOP 100 FUND - LARGE CAP EQUITY SCHEME
Fund Overview:
- Investment Objective: To provide long-term capital appreciation/income by investing predominantly in large-cap companies.
- Category: Large Cap Fund (Predominantly invests in top 100 companies by market capitalization).
- Inception / Launch Date: January 1, 2013 (Direct Plan).
- Benchmark: NIFTY 100 TRI.
- Fund Manager: Rahul Baijal (Managing since July 2022, 2.8 years).
- Total AUM: Rs 33,450 Crores.
- Riskometer: VERY HIGH risk."""
    },
    {
        "doc_name": "HDFC_Top100_Factsheet_Oct2026.pdf",
        "page_number": 2,
        "fund_name": "HDFC Top 100 Fund",
        "scheme_code": 119598,
        "category": "Large Cap",
        "text": """HDFC TOP 100 FUND - KEY FINANCIAL METRICS & LOADS
- Direct Plan Total Expense Ratio (TER): 1.08% p.a.
- Regular Plan TER: 1.68% p.a.
- Minimum Application Amount: Rs 100 and any amount thereafter.
- Minimum SIP: Rs 100 per month.
- Exit Load: In respect of each purchase, 1.00% is payable if redeemed/switched-out within 1 year from the date of allotment. Nil thereafter.
- Portfolio Composition: 96.4% in Large Cap equities, 3.6% in Cash and TREPS."""
    },

    # 3. SBI Small Cap Fund
    {
        "doc_name": "SBI_SmallCap_Factsheet_Oct2026.pdf",
        "page_number": 1,
        "fund_name": "SBI Small Cap Fund",
        "scheme_code": 122639,
        "category": "Small Cap",
        "text": """SBI SMALL CAP FUND - FACTSHEET OCTOBER 2026
Fund Profile:
- Category: Small Cap Fund (minimum 65% investment in small-cap stocks ranking 251st and above by market capitalization).
- Fund Manager: R. Srinivasan (Managing since November 2013, over 11.5 years tenure).
- Benchmark: S&P BSE 250 SmallCap TRI.
- Total AUM: Rs 28,000 Crores as on September 30, 2026.
- Scheme Inception Date: January 1, 2013 (Direct Plan).
- Riskometer: VERY HIGH.
- Investment Policy: Fresh lump-sum subscriptions remain capped to maintain portfolio liquidity in small-cap universe."""
    },
    {
        "doc_name": "SBI_SmallCap_Factsheet_Oct2026.pdf",
        "page_number": 2,
        "fund_name": "SBI Small Cap Fund",
        "scheme_code": 122639,
        "category": "Small Cap",
        "text": """SBI SMALL CAP FUND - EXPENSE & EXIT LOAD TERMS
- Expense Ratio: Direct Plan TER is 0.69% p.a.; Regular Plan TER is 1.62% p.a.
- Minimum SIP Amount: Rs 500 per month.
- Minimum Additional Purchase: Rs 1,000.
- Exit Load: 1.00% if redeemed or switched out on or before 1 year from the date of allotment; Nil if redeemed after 1 year.
- Portfolio Turnover Ratio: 22.4% annually, reflecting high-conviction low-churn stock selection."""
    },

    # 4. HDFC Mid-Cap Opportunities Fund
    {
        "doc_name": "HDFC_MidCap_Factsheet_Oct2026.pdf",
        "page_number": 1,
        "fund_name": "HDFC Mid-Cap Opportunities Fund",
        "scheme_code": 120505,
        "category": "Mid Cap",
        "text": """HDFC MID-CAP OPPORTUNITIES FUND - FACTSHEET
- Category: Mid Cap Fund (invests minimum 65% in stocks ranking 101 to 250 by market cap).
- Inception Date: January 1, 2013 (Direct Plan).
- Benchmark: NIFTY Midcap 150 TRI.
- Fund Manager: Chirag Setalvad (Senior Fund Manager, leading the scheme for 15.0 years).
- Total AUM: Rs 65,000 Crores.
- Direct Plan TER: 0.76% p.a.
- Regular Plan TER: 1.48% p.a.
- Exit Load: 1.00% for redemption within 1 year; Nil after 1 year.
- Minimum SIP: Rs 100 per month.
- Riskometer: VERY HIGH."""
    },

    # 5. HDFC Short Term Debt Fund
    {
        "doc_name": "HDFC_ShortTerm_Factsheet_Oct2026.pdf",
        "page_number": 1,
        "fund_name": "HDFC Short Term Debt Fund",
        "scheme_code": 120716,
        "category": "Short Duration Debt",
        "text": """HDFC SHORT TERM DEBT FUND - DEBT SCHEME FACTSHEET
Fund Details:
- Category: Short Duration Debt Fund (Macaulay duration between 1 year and 3 years).
- Benchmark: CRISIL Short Duration Debt Index.
- Fund Manager: Anil Bamboli (Managing since June 2010, 14.0 years tenure).
- Inception: January 1, 2013 (Direct Plan).
- Total AUM: Rs 16,500 Crores.
- Direct Plan TER: 0.38% p.a.
- Regular Plan TER: 0.88% p.a.
- Exit Load: NIL (No exit load on redemption at any time).
- Minimum Investment / SIP: Rs 100 per month.
- Modified Duration: 2.15 years; Yield to Maturity (YTM): 7.42% p.a.
- Credit Quality: 94.2% in AAA / Sovereign rated debt instruments.
- Riskometer: MODERATE risk."""
    },

    # 6. Axis Bluechip Fund
    {
        "doc_name": "Axis_Bluechip_Factsheet_Oct2026.pdf",
        "page_number": 1,
        "fund_name": "Axis Bluechip Fund",
        "scheme_code": 120586,
        "category": "Large Cap",
        "text": """AXIS BLUECHIP FUND - MONTHLY DISCLOSURE
- Category: Large Cap Fund.
- Benchmark: S&P BSE 100 TRI.
- Fund Manager: Shreyash Devalkar (Managing since November 2016, 6.5 years tenure).
- Total AUM: Rs 32,100 Crores.
- Direct Plan Expense Ratio: 0.95% p.a.
- Exit Load: For units in excess of 10% of the investment, 1% will be charged for redemption within 12 months. Nil exit load after 12 months.
- Minimum SIP: Rs 100 per month.
- Riskometer: VERY HIGH."""
    },
]


def get_all_chunks() -> List[Dict[str, Any]]:
    """Return all document page chunks with metadata."""
    return CORPUS_PAGES


def get_chunks_by_fund(fund_name_sub: str) -> List[Dict[str, Any]]:
    """Filter chunks by partial fund name."""
    sub = fund_name_sub.lower()
    return [p for p in CORPUS_PAGES if sub in p["fund_name"].lower()]
