Codebase_Aware_RAG/
│
├── src/
│   ├── __init__.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── repo_loader.py
│   │   ├── ast_chunker.py
│   │   └── metadata.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── chunk_store.py
│   │
│   ├── embedding/
│   │   ├── __init__.py
│   │   ├── embedder.py
│   │   └── pipeline.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── retriever.py
│   │   └── context_builder.py
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   └── llm.py
│   │
│   └── indexing/
│       ├── __init__.py
│       └── index_repository.py
│
├── tests/
│   ├── test_ast_chunker.py
│   ├── test_embedding.py
│   ├── test_embedder.py
│   ├── test_chunk_store.py
│   ├── test_pipeline.py
│   ├── test_retriever.py
│   ├── test_context_builder.py
│   └── test_llm_client.py
│
├── pyproject.toml
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md