                    Query
                      │
             ┌────────┴────────┐
             ↓                 ↓
       Dense Retrieval     BM25 Retrieval
          bge-m3              keywords
             │                 │
             └────────┬────────┘
                      ↓
                 Result Fusion
                      ↓
                   Top-K
                      ↓
               ContextBuilder
                      ↓
                  CodeLLM