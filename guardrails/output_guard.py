"""
Output Guardrail Engine (guardrails/output_guard.py)

1. Scans text for prohibited promises or return guarantees.
2. Auto-appends mandatory SEBI Investment Advisers disclosures:
   - Direct mutual fund plans only (no commission)
   - Conflict of interest / Fiduciary declaration
   - Statutory Mutual fund market risk disclaimer
   - Past performance warning
   - Non-guarantee disclaimer
"""
import re
from typing import Dict, Any, List, Tuple

PROHIBITED_RETURN_PROMISES = [
    r"\bwe\s+guarantee\b",
    r"\bguarantee\w*\b",
    r"\bassured\s+(?:return|gain|profit|\d+%)\b",
    r"\byou\s+will\s+(?:definitely\s+)?earn\b",
    r"\brisk[-\s]*free\s+investment\b",
    r"\byour\s+money\s+will\s+double\b",
    r"\bpromise\s+(?:a\s+)?return\b",
]

MANDATORY_DISCLOSURES = [
    "DIRECT PLANS ONLY: All mutual fund investments recommended in this document are Direct Plans. The adviser does not receive any commissions, trailer fees, or distribution remuneration from Asset Management Companies.",
    "FIDUCIARY DUTY & CONFLICT OF INTEREST: The adviser is registered under SEBI (Investment Advisers) Regulations, 2013, and acts in a fiduciary capacity exclusively in the best interests of the client. No conflict of interest exists.",
    "STATUTORY RISK WARNING: Mutual fund investments are subject to market risks. Please read all scheme-related documents carefully before investing.",
    "PAST PERFORMANCE CAVEAT: Past performance is purely historical and does not indicate or guarantee future results.",
    "NO RETURN GUARANTEE: All numerical figures, compounding illustrations, and projections are based on documented assumptions for planning purposes only and DO NOT constitute a guarantee, promise, or forecast of returns.",
]


def scan_for_guarantees(text: str) -> Tuple[bool, List[str]]:
    """
    Check if text contains prohibited promise/guarantee language.
    Returns (has_violations, list_of_matched_patterns).
    """
    violations = []
    for pat in PROHIBITED_RETURN_PROMISES:
        matches = re.findall(pat, text, re.IGNORECASE)
        if matches:
            violations.extend(matches)
    return len(violations) > 0, violations


def sanitize_and_append_disclosures(advisory_text: str) -> str:
    """
    Ensure no return promises exist in text, and append mandatory SEBI RIA disclosures.
    """
    has_guarantee, matches = scan_for_guarantees(advisory_text)
    sanitized = advisory_text
    
    if has_guarantee:
        # Neutralize prohibited phrases
        for m in matches:
            sanitized = re.sub(re.escape(m), "[Projected under documented historical assumptions]", sanitized, flags=re.IGNORECASE)

    # Append formatted disclosures
    disclosures_block = "\n\n" + "=" * 65 + "\n"
    disclosures_block += "MANDATORY REGULATORY DISCLOSURES (SEBI RIA REGULATIONS 2013)\n"
    disclosures_block += "=" * 65 + "\n"
    for idx, disc in enumerate(MANDATORY_DISCLOSURES, 1):
        disclosures_block += f"{idx}. {disc}\n\n"
        
    return sanitized.strip() + disclosures_block
