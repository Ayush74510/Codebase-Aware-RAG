                   REPOSITORY
                       │
                       ▼
                ┌──────────────┐
                │ Repo Loader  │
                └──────┬───────┘
                       │
                 RepositoryFile
                       │
                       ▼
                ┌──────────────┐
                │ AST Chunker  │
                └──────┬───────┘
                       │
                    CodeChunk
                       │
                       ▼
                ┌──────────────┐
                │   Pipeline   │
                └──────┬───────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      ┌─────────────┐     ┌──────────────┐
      │  CodeEmbedder│     │  ChunkStore │
      └──────┬──────┘     └──────┬───────┘
             │                   │
             ▼                   │
        FreeLLMAPI               │
          bge-m3                 │
             │                   │
             │ 1024-d vector     │
             └─────────┬─────────┘
                       ▼
              PostgreSQL + pgvector