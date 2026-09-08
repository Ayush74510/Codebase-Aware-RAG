from src.embedding.embedder import CodeEmbedder
from src.generation.llm import CodeLLM
from src.rag import CodebaseRAG
from src.retrieval.retriever import Retriever


def test_rag_answers_codebase_question():
    embedder = CodeEmbedder()
    retriever = Retriever(embedder)
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