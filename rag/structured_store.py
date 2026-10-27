"""
Structured Fact Table (rag/structured_store.py)

Manages a structured SQLite table and CSV of key verified fund facts:
- Expense Ratio (TER)
- Exit Load
- Benchmark
- Minimum SIP
- Fund Manager & Tenure
- AUM
- Riskometer
- Launch Date

Uses precise regex word-boundary matching so words like 'term' do not match 'ter'.
"""
import os
import sqlite3
import re
from typing import Dict, Any, List, Optional, Tuple

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
DB_PATH = os.path.join(DATA_DIR, "fund_facts.db")

FACTS_SEED = [
    # Parag Parikh Flexi Cap Fund
    (135781, "Parag Parikh Flexi Cap Fund", "expense_ratio_direct", "0.68%", "0.68", "%", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 2, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "expense_ratio_regular", "1.34%", "1.34", "%", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 2, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "exit_load", "2.00% if redeemed on or before 365 days; 1.00% between 366-730 days; Nil after 730 days", "2% / 1% / Nil", "", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 2, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "benchmark", "NIFTY 500 TRI", "NIFTY 500 TRI", "", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "min_sip", "Rs 1,000", "1000", "INR", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 2, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "fund_manager", "Rajeev Thakkar", "Rajeev Thakkar", "", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "manager_tenure", "11.2 years", "11.2", "years", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "aum", "Rs 72,500 Crores", "72500", "INR Crores", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "riskometer", "Very High", "Very High", "", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "launch_date", "May 28, 2013", "2013-05-28", "", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "equity_mandate", "Minimum 65% in Indian equities", "65%", "%", "PPFAS_FlexiCap_SID.pdf", 14, "2026-10-01"),
    (135781, "Parag Parikh Flexi Cap Fund", "foreign_equity_allocation", "14.8%", "14.8", "%", "PPFAS_FlexiCap_Factsheet_Oct2026.pdf", 2, "2026-10-01"),

    # HDFC Top 100 Fund
    (119598, "HDFC Top 100 Fund", "expense_ratio_direct", "1.08%", "1.08", "%", "HDFC_Top100_Factsheet_Oct2026.pdf", 2, "2026-10-01"),
    (119598, "HDFC Top 100 Fund", "exit_load", "1.00% if redeemed within 1 year; Nil thereafter", "1%", "", "HDFC_Top100_Factsheet_Oct2026.pdf", 2, "2026-10-01"),
    (119598, "HDFC Top 100 Fund", "benchmark", "NIFTY 100 TRI", "NIFTY 100 TRI", "", "HDFC_Top100_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (119598, "HDFC Top 100 Fund", "min_sip", "Rs 100", "100", "INR", "HDFC_Top100_Factsheet_Oct2026.pdf", 2, "2026-10-01"),
    (119598, "HDFC Top 100 Fund", "fund_manager", "Rahul Baijal", "Rahul Baijal", "", "HDFC_Top100_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (119598, "HDFC Top 100 Fund", "aum", "Rs 33,450 Crores", "33450", "INR Crores", "HDFC_Top100_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (119598, "HDFC Top 100 Fund", "riskometer", "Very High", "Very High", "", "HDFC_Top100_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (119598, "HDFC Top 100 Fund", "launch_date", "01-Jan-2013", "2013-01-01", "", "HDFC_Top100_Factsheet_Oct2026.pdf", 1, "2026-10-01"),

    # SBI Small Cap Fund
    (122639, "SBI Small Cap Fund", "expense_ratio_direct", "0.69%", "0.69", "%", "SBI_SmallCap_Factsheet_Oct2026.pdf", 2, "2026-10-01"),
    (122639, "SBI Small Cap Fund", "exit_load", "1.00% if redeemed on or before 1 year; Nil after 1 year", "1%", "", "SBI_SmallCap_Factsheet_Oct2026.pdf", 2, "2026-10-01"),
    (122639, "SBI Small Cap Fund", "benchmark", "S&P BSE 250 SmallCap TRI", "S&P BSE 250 SmallCap TRI", "", "SBI_SmallCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (122639, "SBI Small Cap Fund", "min_sip", "Rs 500", "500", "INR", "SBI_SmallCap_Factsheet_Oct2026.pdf", 2, "2026-10-01"),
    (122639, "SBI Small Cap Fund", "fund_manager", "R. Srinivasan", "R. Srinivasan", "", "SBI_SmallCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (122639, "SBI Small Cap Fund", "manager_tenure", "11.5 years", "11.5", "years", "SBI_SmallCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (122639, "SBI Small Cap Fund", "aum", "Rs 28,000 Crores", "28000", "INR Crores", "SBI_SmallCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (122639, "SBI Small Cap Fund", "riskometer", "Very High", "Very High", "", "SBI_SmallCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),

    # HDFC Mid-Cap Opportunities Fund
    (120505, "HDFC Mid-Cap Opportunities Fund", "expense_ratio_direct", "0.76%", "0.76", "%", "HDFC_MidCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120505, "HDFC Mid-Cap Opportunities Fund", "exit_load", "1.00% within 1 year; Nil after 1 year", "1%", "", "HDFC_MidCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120505, "HDFC Mid-Cap Opportunities Fund", "benchmark", "NIFTY Midcap 150 TRI", "NIFTY Midcap 150 TRI", "", "HDFC_MidCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120505, "HDFC Mid-Cap Opportunities Fund", "min_sip", "Rs 100", "100", "INR", "HDFC_MidCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120505, "HDFC Mid-Cap Opportunities Fund", "fund_manager", "Chirag Setalvad (15.0 years)", "Chirag Setalvad", "", "HDFC_MidCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120505, "HDFC Mid-Cap Opportunities Fund", "manager_tenure", "15.0 years", "15.0", "years", "HDFC_MidCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120505, "HDFC Mid-Cap Opportunities Fund", "aum", "Rs 65,000 Crores", "65000", "INR Crores", "HDFC_MidCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120505, "HDFC Mid-Cap Opportunities Fund", "riskometer", "Very High", "Very High", "", "HDFC_MidCap_Factsheet_Oct2026.pdf", 1, "2026-10-01"),

    # HDFC Short Term Debt Fund
    (120716, "HDFC Short Term Debt Fund", "expense_ratio_direct", "0.38%", "0.38", "%", "HDFC_ShortTerm_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120716, "HDFC Short Term Debt Fund", "exit_load", "Nil", "Nil", "", "HDFC_ShortTerm_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120716, "HDFC Short Term Debt Fund", "benchmark", "CRISIL Short Duration Debt Index", "CRISIL Short Duration Debt Index", "", "HDFC_ShortTerm_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120716, "HDFC Short Term Debt Fund", "min_sip", "Rs 100", "100", "INR", "HDFC_ShortTerm_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120716, "HDFC Short Term Debt Fund", "fund_manager", "Anil Bamboli", "Anil Bamboli", "", "HDFC_ShortTerm_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120716, "HDFC Short Term Debt Fund", "manager_tenure", "14.0 years", "14.0", "years", "HDFC_ShortTerm_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120716, "HDFC Short Term Debt Fund", "aum", "Rs 16,500 Crores", "16500", "INR Crores", "HDFC_ShortTerm_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120716, "HDFC Short Term Debt Fund", "riskometer", "MODERATE", "MODERATE", "", "HDFC_ShortTerm_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120716, "HDFC Short Term Debt Fund", "credit_quality", "94.2% in AAA / Sovereign rated debt instruments", "94.2%", "%", "HDFC_ShortTerm_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120716, "HDFC Short Term Debt Fund", "ytm", "7.42% p.a.", "7.42", "%", "HDFC_ShortTerm_Factsheet_Oct2026.pdf", 1, "2026-10-01"),

    # Axis Bluechip Fund
    (120586, "Axis Bluechip Fund", "expense_ratio_direct", "0.95%", "0.95", "%", "Axis_Bluechip_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120586, "Axis Bluechip Fund", "exit_load", "1% for units in excess of 10% within 12 months; Nil after 12 months", "1%", "", "Axis_Bluechip_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120586, "Axis Bluechip Fund", "benchmark", "S&P BSE 100 TRI", "S&P BSE 100 TRI", "", "Axis_Bluechip_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120586, "Axis Bluechip Fund", "min_sip", "Rs 100", "100", "INR", "Axis_Bluechip_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120586, "Axis Bluechip Fund", "fund_manager", "Shreyash Devalkar", "Shreyash Devalkar", "", "Axis_Bluechip_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120586, "Axis Bluechip Fund", "aum", "Rs 32,100 Crores", "32100", "INR Crores", "Axis_Bluechip_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
    (120586, "Axis Bluechip Fund", "riskometer", "Very High", "Very High", "", "Axis_Bluechip_Factsheet_Oct2026.pdf", 1, "2026-10-01"),
]


def init_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fund_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scheme_code INTEGER,
            fund_name TEXT,
            metric_name TEXT,
            display_value TEXT,
            raw_value TEXT,
            unit TEXT,
            source_doc TEXT,
            page_num INTEGER,
            as_of_date TEXT,
            UNIQUE(scheme_code, metric_name)
        )
    """)
    cur.executemany("""
        INSERT OR REPLACE INTO fund_facts 
        (scheme_code, fund_name, metric_name, display_value, raw_value, unit, source_doc, page_num, as_of_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, FACTS_SEED)
    conn.commit()
    return conn


def detect_metric_type(query: str) -> Optional[str]:
    """Accurately identify which structured metric a user is inquiring about with regex word boundaries."""
    q = query.lower()
    
    # Do not match if asking about ungrounded questions
    if any(k in q for k in ["shares of", "bitcoin", "crypto", "forex", "gold loan", "rental yield", "guarantee"]):
        return None

    # Expense ratio: ensure \bter\b or 'expense ratio'
    if re.search(r"\bexpense ratio\b|\btotal expense\b|\bter\b", q):
        return "expense_ratio_direct"
    if re.search(r"\bexit load\b|\bredemption fee\b", q):
        return "exit_load"
    if re.search(r"\bbenchmark\b", q):
        return "benchmark"
    if re.search(r"\bmin(imum)?\s+(?:monthly\s+)?sip\b|\bmin(imum)?\s+investment\b", q):
        return "min_sip"
    if re.search(r"\byield to maturity\b|\bytm\b", q):
        return "ytm"
    if re.search(r"\bcredit quality\b|aaa|sovereign", q):
        return "credit_quality"
    if re.search(r"\bwho manages\b|\bfund manager\b|\bmanaged by\b", q):
        return "fund_manager"
    if re.search(r"\btenure\b|\bhow long\b", q):
        return "manager_tenure"
    if re.search(r"\baum\b|\bassets under management\b|\btotal aum\b", q):
        return "aum"
    if re.search(r"\briskometer\b|\brisk classification\b", q):
        return "riskometer"
    if re.search(r"\blaunch date\b|\binception\b", q):
        return "launch_date"
    if re.search(r"\bforeign\b|\boverseas\b|\bglobal equity\b", q):
        return "foreign_equity_allocation"
    if re.search(r"\bindian\s+equity\b|\bmandate\b", q):
        return "equity_mandate"
    return None


def detect_fund_in_query(query: str) -> Optional[str]:
    q = query.lower()
    if "parag parikh" in q or "ppfas" in q:
        return "Parag Parikh Flexi Cap Fund"
    if "hdfc top 100" in q:
        return "HDFC Top 100 Fund"
    if "sbi small cap" in q:
        return "SBI Small Cap Fund"
    if "hdfc mid-cap" in q or "hdfc mid cap" in q:
        return "HDFC Mid-Cap Opportunities Fund"
    if "hdfc short term" in q:
        return "HDFC Short Term Debt Fund"
    if "axis bluechip" in q:
        return "Axis Bluechip Fund"
    return None


def lookup_structured_fact(query: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    metric = detect_metric_type(query)
    fund_name = detect_fund_in_query(query)
    
    if not metric or not fund_name:
        return None
        
    conn = init_db(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT fund_name, metric_name, display_value, source_doc, page_num, as_of_date
        FROM fund_facts
        WHERE fund_name = ? AND metric_name = ?
    """, (fund_name, metric))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return None
        
    f_name, m_name, val, doc, page, as_of = row
    citation = f"[{doc}, p.{page}]"
    
    readable_metric = metric.replace("_", " ").title()
    answer = f"The {readable_metric} of {f_name} is {val} {citation}."
    
    return {
        "answered_from_table": True,
        "fund_name": f_name,
        "metric_name": m_name,
        "value": val,
        "source_doc": doc,
        "page_num": page,
        "citation": citation,
        "answer": answer,
    }
