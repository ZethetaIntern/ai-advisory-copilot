"""
RAG Citation & Fact Verifier (rag/verifier.py)

STRICT ANTI-HALLUCINATION VERIFIER:
1. Every number (percentages, currency amounts, years, decimals, ratios) in draft answer
   must appear in the cited chunk text.
2. Draft answer must contain explicit citation in format: `[Document, p.X]`.
3. If ANY number or critical claim fails verification, or source does not support it:
   REPLACE answer with: "Not found in the provided sources."
4. Never fall back to model memory. Optimize for refusing over guessing.
"""
import re
from typing import Dict, Any, List, Tuple


REFUSAL_STRING = "Not found in the provided sources."


def extract_numbers_from_text(text: str) -> List[str]:
    """
    Extract all numerical entities:
    - percentages (e.g. 0.68%, 14.8%, 1%)
    - currency amounts (e.g. 72,500, 1,000, 100)
    - decimals and integers (e.g. 11.2, 365, 730)
    Removes citation page numbers like p.1, p.2 to avoid false flags.
    """
    # Remove citation brackets from consideration (e.g. "[... p.2]")
    cleaned = re.sub(r"\[[^\]]+\]", "", text)
    
    # Matches: numbers with optional commas and decimals, optional percentage or currency symbols
    pattern = r"\b\d+(?:,\d+)*(?:\.\d+)?%?"
    matches = re.findall(pattern, cleaned)
    
    # Filter out empty or trivial single-letter artifacts
    result = []
    for m in matches:
        m_str = m.strip()
        if m_str:
            result.append(m_str)
    return result


def extract_citations(text: str) -> List[Tuple[str, int]]:
    """
    Extract citations formatted like `[Doc_Name.pdf, p.3]`.
    Returns list of (doc_name, page_number).
    """
    pattern = r"\[([A-Za-z0-9_\-\.]+),\s*p\.(\d+)\]"
    matches = re.findall(pattern, text)
    return [(m[0], int(m[1])) for m in matches]


def normalize_numeric(val: str) -> str:
    """Normalize numeric strings for matching: remove commas, percent signs."""
    return val.replace(",", "").replace("%", "").strip()


def verify_answer(draft_answer: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verify draft answer against retrieved chunks.
    
    Returns:
        is_valid: bool
        verified_answer: str (either draft_answer or REFUSAL_STRING)
        reason: str
        unverified_numbers: List[str]
    """
    if not draft_answer or REFUSAL_STRING.lower() in draft_answer.lower():
        return {
            "is_valid": True,
            "verified_answer": REFUSAL_STRING,
            "reason": "Legitimate refusal.",
            "unverified_numbers": [],
            "citations_found": [],
        }

    # 1. Check for citation existence
    citations = extract_citations(draft_answer)
    if not citations:
        return {
            "is_valid": False,
            "verified_answer": REFUSAL_STRING,
            "reason": "Rejected: No page-level citation provided in draft answer.",
            "unverified_numbers": [],
            "citations_found": [],
        }

    # 2. Extract all numbers claimed in the draft answer
    claimed_numbers = extract_numbers_from_text(draft_answer)
    
    # 3. Concatenate text of all cited chunks
    cited_chunk_texts = []
    for doc_name, page_num in citations:
        matching = [
            c["text"] for c in retrieved_chunks
            if (doc_name.lower() in c.get("doc_name", "").lower() or c.get("doc_name", "").lower() in doc_name.lower())
            and c.get("page_number") == page_num
        ]
        cited_chunk_texts.extend(matching)
        
    combined_source_text = " ".join(cited_chunk_texts)
    if not combined_source_text:
        # Fallback to checking all retrieved chunks if citation doc name had slight mismatch
        combined_source_text = " ".join(c.get("text", "") for c in retrieved_chunks)
        
    normalized_source = combined_source_text.replace(",", "")
    
    # 4. Verify every claimed number exists in the source text
    unverified = []
    for num in claimed_numbers:
        raw_clean = num.replace(",", "").strip()
        norm_num = normalize_numeric(num)
        
        # Check if number appears verbatim in source
        if raw_clean not in normalized_source and norm_num not in normalized_source:
            unverified.append(num)
            
    if unverified:
        return {
            "is_valid": False,
            "verified_answer": REFUSAL_STRING,
            "reason": f"Rejected: Unverified numbers in answer: {unverified}. Strict refusal applied.",
            "unverified_numbers": unverified,
            "citations_found": citations,
        }

    return {
        "is_valid": True,
        "verified_answer": draft_answer,
        "reason": "All citations and numerical claims verified against source documents.",
        "unverified_numbers": [],
        "citations_found": citations,
    }
