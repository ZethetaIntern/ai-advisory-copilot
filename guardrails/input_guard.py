"""
Input Guardrail Engine (guardrails/input_guard.py)

Inspects user/adviser input before processing:
1. Return-guarantee & get-rich-quick requests ("guarantee", "assured 20%", "double my money", "risk-free")
2. Prompt injection & jailbreak attempts ("ignore instructions", "DAN", "system override")
3. Approval bypass attempts ("skip approval", "send to client directly", "bypass RIA")
"""
import re
from typing import Dict, Any, List, Optional

GUARANTEE_PATTERNS = [
    r"\bguarantee\w*\b",
    r"\bassured\s+(?:return|profit|gain|\d+%)\b",
    r"\bdouble\s+my\s+money\b",
    r"\brisk[-\s]*free\b",
    r"\bzero[-\s]*risk\b",
    r"\b100%\s+safe\b",
    r"\bget\s+rich\s+quick\b",
    r"\bcan\s+you\s+promise\b",
    r"\bfixed\s+\d+%\s+return\b",
    r"\bcapital\s+protection\s+guaranteed\b",
]

INJECTION_PATTERNS = [
    r"\bignore\s+(?:all\s+)?(?:previous\s+)?instructions\b",
    r"\bdisregard\s+(?:all\s+)?rules\b",
    r"\bsystem\s+prompt\b",
    r"\bjailbreak\b",
    r"\bDAN\s+mode\b",
    r"\bdeveloper\s+override\b",
    r"\bpretend\s+you\s+(?:are|have\s+no|are\s+not)\b",
    r"\byou\s+are\s+now\s+an\s+unrestricted\b",
    r"\bbypass\s+all\s+safety\b",
    r"\breturn\s+your\s+hidden\s+system\b",
]

BYPASS_APPROVAL_PATTERNS = [
    r"\bskip\s+(?:the\s+)?adviser\s+approval\b",
    r"\bskip\s+(?:the\s+)?approval\s+gate\b",
    r"\bsend\s+(?:this\s+)?directly\s+to\s+(?:the\s+)?client\b",
    r"\bexport\s+pdf\s+without\s+approval\b",
    r"\bbypass\s+(?:the\s+)?ria\s+review\b",
    r"\bforce\s+approve\s+without\s+adviser\b",
    r"\bauto[-\s]*approve\s+and\s+send\b",
]


def check_input_guardrails(user_text: str) -> Dict[str, Any]:
    """
    Scan user prompt for regulatory and security violations.
    
    Returns:
        is_allowed: bool
        violation_type: Optional[str] (GUARANTEE_REQUEST / PROMPT_INJECTION / BYPASS_APPROVAL)
        message: str
    """
    text = user_text.lower()
    
    # 1. Check prompt injection / jailbreak
    for pat in INJECTION_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return {
                "is_allowed": False,
                "violation_type": "PROMPT_INJECTION",
                "message": "Security Alert: Input contained unauthorized system prompt injection or jailbreak instructions.",
                "matched_pattern": pat,
            }
            
    # 2. Check approval bypass
    for pat in BYPASS_APPROVAL_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return {
                "is_allowed": False,
                "violation_type": "BYPASS_APPROVAL",
                "message": "Regulatory Alert: Under SEBI RIA regulations, no plan or report can reach a client without explicit adviser review and approval.",
                "matched_pattern": pat,
            }

    # 3. Check return guarantee requests
    for pat in GUARANTEE_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return {
                "is_allowed": False,
                "violation_type": "GUARANTEE_REQUEST",
                "message": "Regulatory Alert: Under SEBI regulations, RIAs and mutual funds cannot promise, assure, or guarantee returns. Mutual funds are subject to market risks.",
                "matched_pattern": pat,
            }

    return {
        "is_allowed": True,
        "violation_type": None,
        "message": "Input passed security and regulatory compliance checks.",
        "matched_pattern": None,
    }
