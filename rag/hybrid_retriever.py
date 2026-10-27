"""
Hybrid Retriever (rag/hybrid_retriever.py)

Combines:
1. BM25 Lexical Keyword Search (exact token matching, percentages, fund names)
2. Dense Semantic Vector Search (Pure NumPy TF-IDF with Cosine Similarity, zero DLL dependencies)
3. Reciprocal Rank Fusion (RRF) Reranking

Guarantees page-level chunks with metadata: doc_name, page_number.
"""
from typing import Dict, Any, List, Tuple, Optional
import math
import re
import numpy as np
from rank_bm25 import BM25Okapi
from rag.corpus import get_all_chunks


def tokenize(text: str) -> List[str]:
    """Simple alphanumeric tokenizer."""
    return re.findall(r"\b[A-Za-z0-9_.-]+\b", text.lower())


class PureNumpyTFIDF:
    """Pure Python/NumPy TF-IDF Vectorizer with Cosine Similarity."""
    def __init__(self, corpus: List[str]):
        self.docs_tokens = [tokenize(doc) for doc in corpus]
        self.num_docs = len(corpus)
        
        # Build vocab
        vocab_set = set()
        for dt in self.docs_tokens:
            vocab_set.update(dt)
        self.vocab = {term: idx for idx, term in enumerate(sorted(vocab_set))}
        self.vocab_size = len(self.vocab)
        
        # Compute IDF
        df = np.zeros(self.vocab_size, dtype=np.float32)
        for dt in self.docs_tokens:
            unique_terms = set(dt)
            for t in unique_terms:
                if t in self.vocab:
                    df[self.vocab[t]] += 1.0
        self.idf = np.log((self.num_docs + 1.0) / (df + 1.0)) + 1.0
        
        # Precompute normalized doc vectors
        self.doc_vectors = np.zeros((self.num_docs, self.vocab_size), dtype=np.float32)
        for i, dt in enumerate(self.docs_tokens):
            v = self._vectorize(dt)
            self.doc_vectors[i] = v

    def _vectorize(self, tokens: List[str]) -> np.ndarray:
        vec = np.zeros(self.vocab_size, dtype=np.float32)
        if not tokens:
            return vec
        for t in tokens:
            if t in self.vocab:
                vec[self.vocab[t]] += 1.0
        # Term frequency
        vec = vec / len(tokens)
        # Apply IDF
        vec = vec * self.idf
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def compute_similarity(self, query: str) -> np.ndarray:
        q_tokens = tokenize(query)
        q_vec = self._vectorize(q_tokens)
        # Dot product with normalized vectors gives cosine similarity
        return np.dot(self.doc_vectors, q_vec)


class HybridRetriever:
    def __init__(self, chunks: Optional[List[Dict[str, Any]]] = None):
        self.chunks = chunks if chunks is not None else get_all_chunks()
        self.corpus_texts = [c["text"] for c in self.chunks]
        
        # 1. Initialize BM25
        self.tokenized_corpus = [tokenize(doc) for doc in self.corpus_texts]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        
        # 2. Initialize Pure NumPy Dense Vectorizer
        self.vectorizer = PureNumpyTFIDF(self.corpus_texts)

    def retrieve_bm25(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Retrieve by BM25 score."""
        tokens = tokenize(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(int(idx), float(scores[idx])) for idx in top_indices if scores[idx] > 0]

    def retrieve_dense(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Retrieve by cosine similarity over semantic TF-IDF vectors."""
        sims = self.vectorizer.compute_similarity(query)
        top_indices = np.argsort(sims)[::-1][:top_k]
        return [(int(idx), float(sims[idx])) for idx in top_indices if sims[idx] > 0]

    def retrieve_hybrid(self, query: str, top_k: int = 3, rrf_k: int = 60) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion (RRF):
        score = sum(1.0 / (rrf_k + rank))
        Combines lexical and dense semantic signals.
        """
        bm25_res = self.retrieve_bm25(query, top_k=len(self.chunks))
        dense_res = self.retrieve_dense(query, top_k=len(self.chunks))
        
        rrf_scores: Dict[int, float] = {}
        
        for rank, (idx, _) in enumerate(bm25_res):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (rrf_k + rank + 1))
            
        for rank, (idx, _) in enumerate(dense_res):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (rrf_k + rank + 1))
            
        sorted_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)
        
        results = []
        for idx in sorted_indices[:top_k]:
            chunk = self.chunks[idx].copy()
            chunk["rrf_score"] = round(rrf_scores[idx], 4)
            chunk["citation"] = f"[{chunk['doc_name']}, p.{chunk['page_number']}]"
            results.append(chunk)
            
        return results
