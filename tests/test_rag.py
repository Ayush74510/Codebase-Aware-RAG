from src.embedding.embedder import CodeEmbedder
from src.generation.llm import CodeLLM
from src.rag import CodebaseRAG
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.retriever import Retriever


def test_rag_answers_codebase_question():
    embedder = CodeEmbedder()
    dense_retriever = Retriever(embedder)
    bm25_retriever = BM25Retriever()
    retriever = HybridRetriever(
        dense_retriever=dense_retriever,
        bm25_retriever=bm25_retriever,
    )
    llm = CodeLLM()

    rag = CodebaseRAG(
        retriever=retriever,
        llm=llm,
    )

    answer = rag.ask(
        "Where is the PostgreSQL database connection created?"
    )

    assert answer
    assert "connection" in answer.lower()