"""
Unit Tests for Vector Store & Semantic Retrieval Module
Validates dense embedding indexing, BM25 sparse keyword ranking, RRF hybrid search,
Knowledge Graph prerequisite discovery, and grounded RAG question answering.
"""

import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from vector_store import (
    PersistentVectorStore,
    VectorSearchResult,
    HybridSearchResult,
    RAGAnswerResponse
)


@pytest.fixture(scope="module")
def vector_store():
    return PersistentVectorStore()


class TestPersistentVectorStore:

    def test_01_index_initialization(self, vector_store):
        assert len(vector_store.doc_ids) > 0
        assert vector_store.embeddings is not None
        assert vector_store.embeddings.shape[1] == 384  # all-MiniLM-L6-v2 dimensions
        assert vector_store.bm25.doc_count > 0

    def test_02_semantic_search_skills(self, vector_store):
        results = vector_store.search("data processing and table manipulation in python", top_k=3, doc_type="skill")
        assert len(results) > 0
        top_skill = results[0]
        assert isinstance(top_skill, VectorSearchResult)
        assert top_skill.similarity_score > 0.35
        assert any(k in top_skill.metadata.get("skill_name", "") for k in ["Pandas", "Python", "Data", "SQL", "Feature"])

    def test_03_semantic_search_projects(self, vector_store):
        results = vector_store.search("computer vision convolutional networks", top_k=3, doc_type="project")
        assert len(results) > 0
        assert all(r.metadata.get("type") == "project" for r in results)

    def test_04_add_custom_document(self, vector_store):
        initial_count = len(vector_store.doc_ids)
        vector_store.add_document(
            doc_id="custom_k8s_01",
            text="Kubernetes cluster orchestration for distributed deep learning models",
            metadata={"type": "skill", "category": "DevOps"}
        )
        assert len(vector_store.doc_ids) == initial_count + 1
        results = vector_store.search("Kubernetes container orchestration", top_k=1)
        assert len(results) > 0
        assert results[0].doc_id == "custom_k8s_01"

    def test_05_hybrid_search_rrf(self, vector_store):
        """Hybrid search should combine dense similarity and sparse BM25 ranking."""
        results = vector_store.hybrid_search("SQL window functions dense rank", top_k=3, mode="hybrid")
        assert len(results) > 0
        top = results[0]
        assert isinstance(top, HybridSearchResult)
        assert top.combined_score > 0.0
        assert top.dense_score >= 0.0
        assert top.sparse_score >= 0.0
        assert len(top.matched_keywords) > 0

    def test_06_bm25_sparse_keyword_precision(self, vector_store):
        """BM25 search should excel at exact keyword acronym matching."""
        results = vector_store.hybrid_search("Docker multi-stage builder", top_k=3, mode="bm25")
        assert len(results) > 0
        assert results[0].sparse_score > 0.0

    def test_07_knowledge_graph_model_and_centrality(self, vector_store):
        """Knowledge graph model should return nodes, directed prerequisite edges, and centrality."""
        kg = vector_store.get_knowledge_graph_model()
        assert "nodes" in kg and len(kg["nodes"]) >= 20
        assert "edges" in kg and len(kg["edges"]) >= 15
        assert "top_gateway_skills" in kg
        assert len(kg["top_gateway_skills"]) > 0
        # Python or SQL or Math should be high centrality gateway
        gateway_names = [g["label"] for g in kg["top_gateway_skills"]]
        assert any(k in gateway_names for k in ["Python", "SQL", "Linear Algebra", "Mathematics", "Machine Learning"])

    def test_08_knowledge_graph_prerequisite_chain(self, vector_store):
        """Traversing prerequisite chain for Deep Learning should trace back to foundations."""
        chain = vector_store.get_prerequisite_chain("Deep Learning")
        assert len(chain) > 0
        assert "Deep Learning" in chain
        # Foundation skills should precede downstream
        assert any(k in chain for k in ["Python", "Machine Learning", "Linear Algebra", "NumPy"])

    def test_09_rag_technical_question_answering(self, vector_store):
        """RAG assistant should synthesize a grounded answer with citations and code."""
        resp = vector_store.ask_rag_assistant("How do I optimize SQL window queries with partition by?")
        assert isinstance(resp, RAGAnswerResponse)
        assert len(resp.answer) > 40
        assert len(resp.key_takeaways) >= 2
        assert len(resp.citations) > 0
        assert resp.code_snippet is not None
        assert "DENSE_RANK" in resp.code_snippet or "SELECT" in resp.code_snippet
