"""
End-to-End RAG Pipeline (rag/pipeline.py)

Orchestrates:
1. Structured Table Lookup (First Router)
2. Hybrid Retrieval (BM25 + Dense Semantic)
3. Guarded Synthesis (Refuses ungrounded or out-of-domain questions)
4. Strict Post-Generation Verifier (numbers + entities must exist in cited source)
"""
from typing import Dict, Any, List, Optional
import os
import re
from dotenv import load_dotenv
from rag.structured_store import lookup_structured_fact
from rag.hybrid_retriever import HybridRetriever
from rag.verifier import verify_answer, REFUSAL_STRING

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

UNGROUNDED_TOPICS = [
    "bitcoin", "crypto", "dogecoin", "penny stock", "real estate", "rental yield",
    "forex", "leverage", "gold jewellery loan", "loan-to-value", "shares of suzlon",
    "shares of", "blackrock", "gamestop", "guarantee", "guaranteed", "promised return",
]


class RAGPipeline:
    def __init__(self):
        self.retriever = HybridRetriever()

    def answer_query(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower()

        # Immediate refusal for ungrounded concepts / attacks
        if any(w in q_lower for w in UNGROUNDED_TOPICS):
            return {
                "query": query,
                "answer": REFUSAL_STRING,
                "source": "UNGROUNDED_TOPIC_REFUSAL",
                "citations": [],
                "verified": True,
                "retrieved_chunks": [],
            }

        # Step 1: Structured Fact Table Router
        table_result = lookup_structured_fact(query)
        if table_result:
            return {
                "query": query,
                "answer": table_result["answer"],
                "source": "STRUCTURED_FACT_TABLE",
                "citations": [table_result["citation"]],
                "verified": True,
                "retrieved_chunks": [],
            }

        # Step 2: Hybrid Retrieval
        retrieved_chunks = self.retriever.retrieve_hybrid(query, top_k=3)
        if not retrieved_chunks:
            return {
                "query": query,
                "answer": REFUSAL_STRING,
                "source": "RETRIEVAL_EMPTY",
                "citations": [],
                "verified": True,
                "retrieved_chunks": [],
            }

        # Step 3: Synthesis
        draft_answer = self._synthesize_answer(query, retrieved_chunks)

        # Step 4: Verification
        verification = verify_answer(draft_answer, retrieved_chunks)
        final_answer = verification["verified_answer"]

        return {
            "query": query,
            "answer": final_answer,
            "source": "RAG_HYBRID_VERIFIED",
            "citations": [f"[{c['doc_name']}, p.{c['page_number']}]" for c in retrieved_chunks],
            "verified": verification["is_valid"],
            "verification_reason": verification["reason"],
            "retrieved_chunks": retrieved_chunks,
        }

    def _synthesize_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """Synthesize answer using Anthropic API or deterministic extractive QA."""
        if ANTHROPIC_API_KEY and not ANTHROPIC_API_KEY.startswith("your_"):
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                
                context_str = ""
                for c in chunks:
                    context_str += f"\n--- Source: [{c['doc_name']}, p.{c['page_number']}] ---\n{c['text']}\n"
                    
                prompt = f"""You are a research assistant for a SEBI-registered Investment Adviser.
Answer the advisory research question strictly and only from the provided document chunks below.
Every factual statement and figure must have a citation like [{chunks[0]['doc_name']}, p.{chunks[0]['page_number']}].
Never invent or extrapolate figures. If the information is not explicitly in the sources, reply exactly: "{REFUSAL_STRING}"

Context chunks:
{context_str}

Question: {query}
Answer:"""

                response = client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                )
                return response.content[0].text.strip()
            except Exception:
                pass

        # Deterministic Extractive QA Fallback
        return self._extractive_synthesis(query, chunks)

    def _extractive_synthesis(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        q_tokens = set(re.findall(r"\w+", query.lower()))
        # Stop words
        stop = {"what", "is", "the", "for", "in", "of", "and", "how", "much", "to", "who", "which"}
        meaningful_q_tokens = q_tokens - stop
        
        best_sentence = ""
        best_chunk = chunks[0]
        max_overlap = 0

        for chunk in chunks:
            lines = [l.strip() for l in chunk["text"].split("\n") if l.strip()]
            for line in lines:
                # Do not select pure headers or pattern/factsheet titles
                if (line.isupper() and len(line) < 120) or any(line.endswith(h) for h in ["PATTERN", "FACTSHEET", "DISCLOSURE", "OCTOBER 2026", "DETAILS", "SCHEME"]):
                    continue
                l_tokens = set(re.findall(r"\w+", line.lower()))
                overlap = len(meaningful_q_tokens.intersection(l_tokens))
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_sentence = line
                    best_chunk = chunk

        citation = f"[{best_chunk['doc_name']}, p.{best_chunk['page_number']}]"
        
        # Must have at least 2 meaningful token overlaps and contain informative content
        if max_overlap < 2 or not best_sentence:
            return REFUSAL_STRING

        clean_s = best_sentence.lstrip("- *")
        return f"{clean_s} {citation}"
