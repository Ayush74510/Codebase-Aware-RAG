from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.embedding.embedder import CodeEmbedder
from src.generation.llm import CodeLLM
from src.rag import CodebaseRAG
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.retriever import Retriever
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.indexing.index_repository import index_repository


app = FastAPI(
    title="Codebase-Aware RAG",
    version="1.0.0",
)

app.mount(
    "/static",
    StaticFiles(directory="src/api/static"),
    name="static",
)


class IndexRequest(BaseModel):
    source: str = Field(min_length=1)


class IndexResponse(BaseModel):
    indexed_chunks: int

class AskRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, gt=0)


class AskResponse(BaseModel):
    answer: str


def create_rag() -> CodebaseRAG:
    """Create the end-to-end Codebase RAG pipeline."""
    embedder = CodeEmbedder()
    dense_retriever = Retriever(embedder)
    bm25_retriever = BM25Retriever()

    hybrid_retriever = HybridRetriever(
        dense_retriever=dense_retriever,
        bm25_retriever=bm25_retriever,
    )

    llm = CodeLLM()

    return CodebaseRAG(
        retriever=hybrid_retriever,
        llm=llm,
    )


rag = create_rag()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    answer = rag.ask(
        query=request.query,
        top_k=request.top_k,
    )

    return AskResponse(answer=answer)

@app.get("/")
def home():
    return FileResponse("src/api/static/index.html")

@app.post("/index", response_model=IndexResponse)
def index(request: IndexRequest) -> IndexResponse:
    count = index_repository(request.source)

    return IndexResponse(
        indexed_chunks=count,
    )
