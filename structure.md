codebase-rag/
├── README.md                      # Problem statement, architecture, eval results table — write this LAST but keep updating it
├── pyproject.toml                 # or requirements.txt — pin versions, this matters for reproducibility
├── docker-compose.yml             # pgvector + app service
├── Dockerfile
├── .env.example                   # never commit real .env
│
├── src/
│   └──-- 
│       ├── __init__.py
│       │
│       ├── ingestion/
│       │   ├── repo_loader.py     # clone/read target repo, walk files
│       │   ├── ast_chunker.py     # THE core differentiator — AST parsing into function/class chunks
│       │   ├── metadata.py        # attach file path, line range, call-graph edges to each chunk
│       │   └── embed_and_store.py # embed chunks, write to pgvector
│       │
│       ├── retrieval/
│       │   ├── dense_search.py    # vector similarity search
│       │   ├── lexical_search.py  # BM25 for exact symbol/identifier matches
│       │   ├── hybrid.py          # reciprocal rank fusion of dense + lexical
│       │   └── reranker.py        # cross-encoder reranking of top-k
│       │
│       ├── generation/
│       │   ├── prompt_templates.py
│       │   ├── llm_client.py      # Groq/other provider wrapper, keep swappable
│       │   └── citation_enforcer.py  # forces file:line citations, validates they exist
│       │
│       ├── eval/
│       │   ├── eval_set.json      # your 20-30 ground-truth Q&A pairs, hand-built
│       │   ├── run_eval.py        # scores hit-rate + faithfulness, run before/after every change
│       │   └── metrics.py
│       │
│       └── api/
│           ├── main.py            # FastAPI entrypoint
│           ├── routes.py
│           └── schemas.py         # pydantic request/response models
│
├── scripts/
│   ├── index_repo.py              # CLI: point at a repo, run full ingestion pipeline
│   └── benchmark_chunking.py      # CLI: compare naive vs AST chunking hit-rate — this generates your README table
│
├── tests/
│   ├── test_ast_chunker.py        # unit test the chunking logic on known code samples
│   ├── test_retrieval.py
│   └── test_citation_enforcer.py  # verify it actually refuses when it can't cite
│
└── frontend/                      # keep this minimal — Streamlit single file, or skip entirely for v1
    └── app.py