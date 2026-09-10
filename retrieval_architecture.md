Repository
   │
   ▼
RepositoryLoader
   │
   ├── default ignored dirs
   └── tests/ excluded during indexing
   │
   ▼
ASTChunker
   │
   ▼
EmbeddingPipeline
   │
   ▼
PostgreSQL + pgvector
   │
   ├── Dense retrieval
   └── BM25 retrieval
          │
          ▼
      RRF Hybrid
          │
          ▼
      Context Builder
          │
          ▼
          LLM