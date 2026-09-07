# Codebase-Aware RAG --- Complete Pipeline Architecture

## 1. Project Goal

The project is a **codebase-aware Retrieval-Augmented Generation (RAG)
system**.

Its purpose is to take a local or remote Git repository, understand its
source code structurally, break it into meaningful code chunks, create
vector embeddings, store those chunks in PostgreSQL + pgvector, retrieve
the most relevant code for a user's question, and finally use an LLM to
generate an answer grounded in the retrieved code.

The high-level system is:

``` text
                         ┌─────────────────────────┐
                         │       USER QUERY        │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │       QUERY EMBEDDING   │
                         │        bge-m3            │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ PostgreSQL + pgvector   │
                         │   Semantic Retrieval    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     RetrievedChunks     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     ContextBuilder      │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    Gemini 2.5 Flash     │
                         │       Generation        │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      FINAL ANSWER       │
                         └─────────────────────────┘
```

There are therefore two major phases:

1.  **Indexing phase** --- understand and store the repository.
2.  **Query/RAG phase** --- retrieve relevant code and generate an
    answer.

------------------------------------------------------------------------

# 2. Complete Project Structure

The current/projected structure is:

``` text
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
```

Some test files are temporary/integration tests created during
development. They can later be consolidated into a cleaner test suite.

------------------------------------------------------------------------

# 3. Technologies Used

  Layer                 Technology
  --------------------- ----------------------------------------------
  Language              Python 3.11
  Environment           Conda
  Repository loading    Python `pathlib`, Git subprocess/clone logic
  Code parsing          Tree-sitter
  Python parser         `tree-sitter-python`
  Chunking              Custom AST-based chunker
  Metadata              Custom dataclasses + Tree-sitter
  Embeddings            `bge-m3`
  Embedding access      FreeLLMAPI
  Embedding provider    SeaLion
  Embedding dimension   1024
  Vector database       PostgreSQL
  Vector extension      pgvector
  Vector search         Cosine distance
  Vector index          HNSW
  LLM                   Gemini 2.5 Flash
  LLM access            FreeLLMAPI
  API client            OpenAI Python SDK
  Configuration         `.env` + `python-dotenv`
  Containerization      Docker / Docker Compose

------------------------------------------------------------------------

# 4. Environment and Configuration

The project uses a Conda environment:

``` text
codebase-rag
```

The Python environment is used for all project dependencies.

The `.env` file contains configuration/secrets such as:

``` env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/codebase_rag

FREELLMAPI_API_KEY=your_actual_key
FREELLMAPI_BASE_URL=http://127.0.0.1:31415/v1

EMBEDDING_MODEL=bge-m3
LLM_MODEL=gemini-2.5-flash
```

## Security rule

`.env` must be ignored by Git:

``` gitignore
.env
```

The FreeLLMAPI unified API key should never be committed to the
repository.

FreeLLMAPI itself is running locally and, in the current setup, exposes
its API through:

``` text
http://127.0.0.1:31415/v1
```

------------------------------------------------------------------------

# 5. PostgreSQL Setup

PostgreSQL runs through Docker.

Current `docker-compose.yml`:

``` yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: codebase-rag-postgres
    environment:
      POSTGRES_DB: codebase_rag
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

The database is:

``` text
Database: codebase_rag
User: postgres
Password: postgres
Host: localhost
Port: 5432
```

The PostgreSQL container is:

``` text
codebase-rag-postgres
```

------------------------------------------------------------------------

# 6. pgvector

The PostgreSQL `vector` extension is enabled:

``` sql
CREATE EXTENSION IF NOT EXISTS vector;
```

This allows PostgreSQL to store and search numerical embedding vectors.

The project currently uses:

``` text
VECTOR(1024)
```

because `bge-m3` returns 1024-dimensional dense embeddings in the
current configuration.

------------------------------------------------------------------------

# 7. Database Schema

Current `code_chunks` table:

``` sql
CREATE TABLE code_chunks (
    id BIGSERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    chunk_type TEXT NOT NULL,
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    language TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding VECTOR(1024)
);
```

## Column responsibilities

### `id`

Database-generated unique identifier.

``` text
BIGSERIAL PRIMARY KEY
```

### `file_path`

Repository-relative file path.

Example:

``` text
src/database/connection.py
```

### `chunk_type`

Identifies the kind of chunk.

Examples:

``` text
class
function
method
file
```

### `name`

Name of the chunk.

Examples:

``` text
get_connection
MetadataExtractor
extract
```

### `content`

Actual source-code text represented by the chunk.

### `start_line`

Starting source line.

### `end_line`

Ending source line.

### `language`

Programming language.

Example:

``` text
python
```

### `metadata`

Additional structural information stored as JSONB.

Current metadata fields:

``` json
{
    "parent_class": null,
    "parent_function": null,
    "decorators": [],
    "imports": [],
    "calls": []
}
```

### `embedding`

1024-dimensional dense vector generated by `bge-m3`.

------------------------------------------------------------------------

# 8. Vector Index

An HNSW index has been created:

``` sql
CREATE INDEX code_chunks_embedding_idx
ON code_chunks
USING hnsw (embedding vector_cosine_ops);
```

This supports efficient approximate nearest-neighbor searches using
cosine distance.

The query uses:

``` sql
embedding <=> query_embedding
```

The `<=>` operator is pgvector's cosine-distance operator.

Lower distance means greater similarity.

------------------------------------------------------------------------

# 9. Repository Loading

File:

``` text
src/ingestion/repo_loader.py
```

Main responsibility:

> Convert a repository source into `RepositoryFile` objects.

The loader accepts:

1.  A local repository path.
2.  A remote Git repository URL.

Example:

``` python
loader.load("./my-project")
```

or:

``` python
loader.load("https://github.com/user/project.git")
```

## High-level flow

``` text
source
  │
  ├── local path?
  │       │
  │       └── resolve path
  │
  └── Git URL?
          │
          └── clone repository
                  │
                  ▼
            repository path
                  │
                  ▼
          _walk_repository()
                  │
                  ▼
          RepositoryFile[]
```

------------------------------------------------------------------------

# 10. RepositoryFile

A repository file is represented conceptually as:

``` python
@dataclass
class RepositoryFile:
    path: str
    absolute_path: Path
    content: str
    language: str | None
    size_bytes: int
```

## Meaning

### `path`

Repository-relative path.

### `absolute_path`

Actual filesystem path.

### `content`

Full file contents.

### `language`

Detected programming language.

### `size_bytes`

File size.

------------------------------------------------------------------------

# 11. Repository Filtering

The repository loader walks the repository recursively.

For every path:

``` text
rglob("*")
```

it checks:

1.  Is it a file?
2.  Should it be ignored?
3.  Is its extension supported?
4.  Is its size below the maximum allowed?
5.  Can it be read?

Only valid files become `RepositoryFile` objects.

The important data flow is:

``` text
filesystem
    ↓
ignore filtering
    ↓
extension filtering
    ↓
size filtering
    ↓
UTF-8 read
    ↓
RepositoryFile
```

------------------------------------------------------------------------

# 12. AST Chunking

File:

``` text
src/ingestion/ast_chunker.py
```

Main responsibility:

> Convert one `RepositoryFile` into semantic `CodeChunk` objects.

Tree-sitter is used instead of splitting source code by arbitrary
character/line boundaries.

Current Python parser setup:

``` python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node

PYTHON_LANGUAGE = Language(tspython.language())
```

The parser map currently includes:

``` python
self._parsers = {
    "python": Parser(PYTHON_LANGUAGE)
}
```

------------------------------------------------------------------------

# 13. CodeChunk

The semantic chunk object is conceptually:

``` python
@dataclass
class CodeChunk:
    file_path: str
    chunk_type: str
    name: str
    content: str
    start_line: int
    end_line: int
    language: str
    metadata: ChunkMetadata
```

## Chunk types

### Class

``` text
chunk_type = "class"
```

### Top-level function

``` text
chunk_type = "function"
```

### Method

A function inside a class:

``` text
chunk_type = "method"
```

### Unsupported language

A complete-file fallback:

``` text
chunk_type = "file"
```

------------------------------------------------------------------------

# 14. Python AST Chunking Flow

For a Python file:

``` text
RepositoryFile
      ↓
source bytes
      ↓
Tree-sitter parser
      ↓
AST
      ↓
recursive traversal
      ↓
class/function/method nodes
      ↓
CodeChunk[]
```

The traversal keeps track of:

``` text
parent_class
parent_function
```

This allows methods and nested functions to retain their structural
context.

------------------------------------------------------------------------

# 15. Fallback Chunking

If a language has no configured parser, the entire file becomes one
chunk.

Conceptually:

``` python
CodeChunk(
    file_path=repository_file.path,
    chunk_type="file",
    name=repository_file.path,
    content=repository_file.content,
    start_line=1,
    end_line=line_count,
    language=repository_file.language or "unknown",
    metadata=ChunkMetadata(),
)
```

This means unsupported languages are not silently discarded.

------------------------------------------------------------------------

# 16. Metadata Extraction

File:

``` text
src/ingestion/metadata.py
```

The metadata model is:

``` python
@dataclass
class ChunkMetadata:
    parent_class: str | None = None
    parent_function: str | None = None
    decorators: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
```

## Metadata fields

### `parent_class`

The class containing the current chunk.

Example:

``` text
parent_class = "UserService"
```

### `parent_function`

Parent function for nested function contexts.

### `decorators`

Examples:

``` text
staticmethod
classmethod
property
```

### `imports`

Imports syntactically present in the relevant AST context.

### `calls`

Direct syntactic function/method calls discovered in the AST.

Important limitation:

> These calls are currently syntactic call names, not a complete
> resolved call graph.

Symbol resolution can be added later.

------------------------------------------------------------------------

# 17. Decorator AST Detail

Tree-sitter Python represents decorated functions approximately as:

``` text
decorated_definition
├── decorator
└── function_definition
```

Therefore decorators cannot always be found by simply inspecting
children of `function_definition`.

The metadata extractor accounts for this structure by checking the
current node and/or its parent when the parent is a
`decorated_definition`.

This was specifically required to correctly extract decorators such as:

``` python
@staticmethod
def foo():
    ...
```

------------------------------------------------------------------------

# 18. Embedding Architecture

Directory:

``` text
src/embedding/
```

Main components:

``` text
embedder.py
pipeline.py
```

The project uses:

``` text
bge-m3
```

through:

``` text
FreeLLMAPI
```

with the configured provider:

``` text
SeaLion
```

The embedding dimension is:

``` text
1024
```

------------------------------------------------------------------------

# 19. CodeEmbedder

File:

``` text
src/embedding/embedder.py
```

Responsibility:

> Convert text/code into embeddings.

It does NOT:

-   access PostgreSQL
-   insert database records
-   perform vector searches
-   build RAG prompts

Its API is:

``` python
embed_documents(texts)
embed_query(query)
```

------------------------------------------------------------------------

# 20. Document Embeddings

For indexing:

``` text
CodeChunk.content
      ↓
CodeEmbedder.embed_documents()
      ↓
FreeLLMAPI
      ↓
bge-m3
      ↓
1024-dimensional embedding
```

Multiple texts can be sent in one request.

This is important for batching.

------------------------------------------------------------------------

# 21. Query Embeddings

For retrieval:

``` text
User query
      ↓
CodeEmbedder.embed_query()
      ↓
FreeLLMAPI
      ↓
bge-m3
      ↓
1024-dimensional query vector
```

`embed_query()` currently delegates to the same underlying embedding
request but gives the application a semantically correct API boundary
between:

``` text
document/code embedding
```

and:

``` text
query embedding
```

------------------------------------------------------------------------

# 22. EmbeddingPipeline

File:

``` text
src/embedding/pipeline.py
```

Responsibility:

> Orchestrate embedding generation and database storage.

It connects:

``` text
CodeChunk[]
    ↓
CodeEmbedder
    ↓
embeddings
    ↓
ChunkStore
```

It does not load repositories or parse ASTs.

------------------------------------------------------------------------

# 23. Batch Processing

The pipeline supports a configurable batch size.

Example:

``` python
batch_size=32
```

For 100 chunks:

``` text
100 chunks
    ↓
32
32
32
4
```

Each batch is embedded together.

This avoids making one API request per code chunk.

Bad approach:

``` text
chunk 1 → API
chunk 2 → API
chunk 3 → API
...
```

Better approach:

``` text
batch of chunks → one embedding request
```

------------------------------------------------------------------------

# 24. Database Connection

File:

``` text
src/database/connection.py
```

Responsibility:

> Create configured PostgreSQL connections.

The database URL is loaded from:

``` text
DATABASE_URL
```

The connection is created with psycopg.

The pgvector adapter is registered on each connection:

``` python
register_vector(connection)
```

This is important because Python embedding vectors must be correctly
adapted to PostgreSQL's `vector` type.

------------------------------------------------------------------------

# 25. ChunkStore

File:

``` text
src/database/chunk_store.py
```

Responsibility:

> Persist `CodeChunk` objects and their embeddings.

API:

``` python
insert_chunk(
    chunk,
    embedding,
)
```

It maps:

``` text
CodeChunk
    +
embedding
    ↓
code_chunks table
```

------------------------------------------------------------------------

# 26. CodeChunk → Database Mapping

``` text
CodeChunk.file_path
        ↓
code_chunks.file_path

CodeChunk.chunk_type
        ↓
code_chunks.chunk_type

CodeChunk.name
        ↓
code_chunks.name

CodeChunk.content
        ↓
code_chunks.content

CodeChunk.start_line
        ↓
code_chunks.start_line

CodeChunk.end_line
        ↓
code_chunks.end_line

CodeChunk.language
        ↓
code_chunks.language

CodeChunk.metadata
        ↓
code_chunks.metadata

embedding
        ↓
code_chunks.embedding
```

The database generates the `id`.

------------------------------------------------------------------------

# 27. Metadata → JSONB

Python metadata:

``` python
ChunkMetadata(
    parent_class="UserService",
    parent_function=None,
    decorators=["staticmethod"],
    imports=["os"],
    calls=["get_connection"],
)
```

is serialized into JSON and stored in:

``` text
metadata JSONB
```

Example:

``` json
{
    "parent_class": "UserService",
    "parent_function": null,
    "decorators": ["staticmethod"],
    "imports": ["os"],
    "calls": ["get_connection"]
}
```

------------------------------------------------------------------------

# 28. Indexing Entry Point

File:

``` text
src/indexing/index_repository.py
```

Responsibility:

> Connect the repository loading, AST chunking, embedding, and storage
> components.

The orchestration is:

``` python
loader = RepositoryLoader()
repository_files = loader.load(source)

chunker = ASTChunker()

chunks = []

for repository_file in repository_files:
    chunks.extend(chunker.chunk(repository_file))

embedder = CodeEmbedder()
store = ChunkStore()

pipeline = EmbeddingPipeline(
    embedder=embedder,
    store=store,
)

pipeline.process(chunks)
```

Important detail:

`ASTChunker.chunk()` accepts **one `RepositoryFile`**, not a list.

Therefore the indexing layer must iterate:

``` python
for repository_file in repository_files:
    chunks.extend(chunker.chunk(repository_file))
```

rather than:

``` python
chunker.chunk(repository_files)
```

------------------------------------------------------------------------

# 29. Complete Indexing Pipeline

The complete indexing path is:

``` text
Repository source
      │
      ▼
RepositoryLoader
      │
      ▼
RepositoryFile[]
      │
      ▼
ASTChunker
      │
      ▼
CodeChunk[]
      │
      ▼
EmbeddingPipeline
      │
      ├───────────────┐
      ▼               ▼
CodeEmbedder      ChunkStore
      │               │
      ▼               │
FreeLLMAPI            │
      │               │
bge-m3                │
      │               │
1024-d vectors ───────┘
                      │
                      ▼
              PostgreSQL + pgvector
```

------------------------------------------------------------------------

# 30. Retrieval Architecture

Directory:

``` text
src/retrieval/
```

Components:

``` text
retriever.py
context_builder.py
```

The retrieval path is:

``` text
User question
      ↓
CodeEmbedder.embed_query()
      ↓
1024-dimensional vector
      ↓
PostgreSQL pgvector
      ↓
cosine similarity
      ↓
Top-K RetrievedChunk objects
```

------------------------------------------------------------------------

# 31. Retriever

File:

``` text
src/retrieval/retriever.py
```

Responsibility:

> Find the most semantically relevant stored code chunks.

It receives:

``` text
query
top_k
```

Example:

``` python
retriever.search(
    "Where is the PostgreSQL database connection created?",
    top_k=5,
)
```

------------------------------------------------------------------------

# 32. RetrievedChunk

Retrieval results are represented by:

``` python
@dataclass
class RetrievedChunk:
    id: int
    file_path: str
    chunk_type: str
    name: str
    content: str
    start_line: int
    end_line: int
    language: str | None
    metadata: dict
    distance: float
```

The `distance` is the cosine distance returned by pgvector.

Lower distance:

``` text
more similar
```

Higher distance:

``` text
less similar
```

------------------------------------------------------------------------

# 33. Vector Search Query

The core SQL is conceptually:

``` sql
SELECT
    id,
    file_path,
    chunk_type,
    name,
    content,
    start_line,
    end_line,
    language,
    metadata,
    embedding <=> %s AS distance
FROM code_chunks
ORDER BY embedding <=> %s
LIMIT %s;
```

The query embedding is explicitly converted to a pgvector `Vector`
object before being passed to PostgreSQL.

This prevents the type mismatch:

``` text
vector <=> double precision[]
```

and ensures:

``` text
vector <=> vector
```

------------------------------------------------------------------------

# 34. Cosine Similarity Retrieval

The retrieval process is:

``` text
Question
   ↓
query vector
   ↓
compare against stored vectors
   ↓
cosine distance
   ↓
sort ascending
   ↓
top K
```

Example:

``` text
Query:
"Where is the PostgreSQL database connection created?"

Result #1:
src/database/connection.py
get_connection
distance = 0.3516
```

The system successfully returned `get_connection` as the top result
during testing.

------------------------------------------------------------------------

# 35. ContextBuilder

File:

``` text
src/retrieval/context_builder.py
```

Responsibility:

> Convert `RetrievedChunk[]` into clean text suitable for an LLM prompt.

Instead of passing database objects directly to the LLM, it produces
structured context.

Example:

``` text
File: src/database/connection.py
Lines: 18-23
Type: function
Name: get_connection

```python
def get_connection():
    ...
```


    Multiple chunks are separated by:

    ```text
    ---

This creates clear boundaries between retrieved source-code sections.

------------------------------------------------------------------------

# 36. Generation Layer

Directory:

``` text
src/generation/
```

Main file:

``` text
llm.py
```

The project currently uses:

``` text
Gemini 2.5 Flash
```

through:

``` text
FreeLLMAPI
```

with model ID:

``` text
gemini-2.5-flash
```

------------------------------------------------------------------------

# 37. CodeLLM

File:

``` text
src/generation/llm.py
```

Responsibility:

> Generate a response from an LLM prompt.

It does NOT:

-   retrieve code
-   access PostgreSQL
-   generate embeddings
-   load repositories

Its API is:

``` python
generate(prompt)
```

Internally it uses the OpenAI-compatible API exposed by FreeLLMAPI.

------------------------------------------------------------------------

# 38. Current LLM Flow

``` text
Prompt
   ↓
OpenAI Python SDK
   ↓
FreeLLMAPI
   ↓
gemini-2.5-flash
   ↓
Google provider
   ↓
Text response
```

The LLM client is configured through:

``` env
FREELLMAPI_API_KEY=...
FREELLMAPI_BASE_URL=http://127.0.0.1:31415/v1
LLM_MODEL=gemini-2.5-flash
```

------------------------------------------------------------------------

# 39. Final RAG Pipeline

The eventual complete user-facing pipeline is:

``` text
                         USER
                          │
                          │
                    "Where is DB
                     connection?"
                          │
                          ▼
                 ┌─────────────────┐
                 │  CodeEmbedder   │
                 │  embed_query()  │
                 └────────┬────────┘
                          │
                     query vector
                          │
                          ▼
                 ┌─────────────────┐
                 │   PostgreSQL    │
                 │    pgvector     │
                 └────────┬────────┘
                          │
                    cosine search
                          │
                          ▼
                 ┌─────────────────┐
                 │   Top-K Chunks  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ ContextBuilder  │
                 └────────┬────────┘
                          │
                    formatted code
                          │
                          ▼
                 ┌─────────────────┐
                 │ Gemini 2.5 Flash│
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  FINAL ANSWER   │
                 └─────────────────┘
```

------------------------------------------------------------------------

# 40. Indexing vs Querying

It is important to keep these two flows conceptually separate.

## Indexing

Runs when a repository is added or re-indexed:

``` text
Repository
   ↓
RepositoryLoader
   ↓
RepositoryFile[]
   ↓
ASTChunker
   ↓
CodeChunk[]
   ↓
CodeEmbedder.embed_documents()
   ↓
bge-m3
   ↓
1024-d embeddings
   ↓
ChunkStore
   ↓
PostgreSQL
```

## Querying

Runs for every user question:

``` text
Question
   ↓
CodeEmbedder.embed_query()
   ↓
bge-m3
   ↓
1024-d query vector
   ↓
pgvector
   ↓
Top-K CodeChunks
   ↓
ContextBuilder
   ↓
Gemini 2.5 Flash
   ↓
Answer
```

------------------------------------------------------------------------

# 41. Why AST-Based Chunking Matters

A naive RAG system might split source code every N characters or tokens:

``` text
file
 ↓
500 characters
 ↓
500 characters
 ↓
500 characters
```

That can split a function in the middle.

This project instead uses the AST:

``` text
Python file
    ↓
AST
    ├── class
    │    ├── method
    │    └── method
    │
    ├── function
    └── function
```

This creates semantically meaningful chunks.

For example:

``` python
def get_connection():
    ...
```

can remain a single retrievable unit.

------------------------------------------------------------------------

# 42. Why Metadata Matters

Vector similarity alone may retrieve semantically related but
structurally inappropriate chunks.

Metadata gives additional information:

``` text
parent_class
parent_function
decorators
imports
calls
```

For example:

``` json
{
    "parent_class": "DatabaseManager",
    "decorators": [],
    "imports": ["psycopg"],
    "calls": ["connect"]
}
```

This can later be used for:

-   filtering
-   reranking
-   context expansion
-   call-graph traversal
-   better explanations

------------------------------------------------------------------------

# 43. Why PostgreSQL + pgvector

The project does not need a separate vector database for the current
architecture.

PostgreSQL stores both:

``` text
structured code metadata
```

and:

``` text
vector embeddings
```

in one database.

That gives us:

``` text
SQL filtering
+
JSONB metadata
+
vector similarity
```

in the same storage system.

------------------------------------------------------------------------

# 44. Current Validation Status

The following components have already been successfully tested.

## Repository loading

``` text
RepositoryLoader
```

Status:

``` text
✅ Working
```

## AST chunking

Tests passed:

``` text
5 passed
```

Status:

``` text
✅ Working
```

Tested behavior includes:

-   Python functions
-   Python classes
-   methods vs functions
-   unsupported-language fallback
-   metadata extraction

## Embeddings

Tested:

``` text
bge-m3
```

Result:

``` text
Embedding dimensions: 1024
```

Status:

``` text
✅ Working
```

## PostgreSQL

Status:

``` text
✅ Working
```

## pgvector

Status:

``` text
✅ Working
```

## Chunk storage

A test chunk was successfully inserted:

``` text
Inserted chunk ID: 1
```

Status:

``` text
✅ Working
```

## Full indexing pipeline

The actual project was successfully indexed:

``` text
60 chunks
```

Status:

``` text
✅ Working
```

## Semantic retrieval

A real query successfully returned:

``` text
src/database/connection.py
get_connection
```

as the top result.

Status:

``` text
✅ Working
```

## Context building

Status:

``` text
✅ Working
```

## LLM

Gemini 2.5 Flash was successfully tested independently.

Status:

``` text
✅ Working
```

------------------------------------------------------------------------

# 45. Current End-to-End Status

The project has already reached this point:

``` text
                  ┌──────────────────┐
                  │    Repository    │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ RepositoryLoader │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │   ASTChunker     │
                  └────────┬─────────┘
                           │
                           ▼
                    CodeChunk[]
                           │
                           ▼
                  ┌──────────────────┐
                  │  CodeEmbedder    │
                  │     bge-m3       │
                  └────────┬─────────┘
                           │
                           ▼
                     1024 vectors
                           │
                           ▼
                  ┌──────────────────┐
                  │   PostgreSQL     │
                  │    pgvector      │
                  └────────┬─────────┘
                           │
                           │
              ───────── QUERY TIME ─────────
                           │
                           ▼
                       User Query
                           │
                           ▼
                  ┌──────────────────┐
                  │ embed_query()    │
                  └────────┬─────────┘
                           │
                           ▼
                    query vector
                           │
                           ▼
                  ┌──────────────────┐
                  │ pgvector search  │
                  └────────┬─────────┘
                           │
                           ▼
                    RetrievedChunk[]
                           │
                           ▼
                  ┌──────────────────┐
                  │ ContextBuilder   │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Gemini 2.5 Flash │
                  └────────┬─────────┘
                           │
                           ▼
                       Answer
```

------------------------------------------------------------------------

# 46. Remaining Major Work

The core indexing and retrieval infrastructure is working.

The next major step is to connect:

``` text
Retriever
    ↓
ContextBuilder
    ↓
CodeLLM
```

into a single RAG service.

The desired interface will eventually look conceptually like:

``` python
answer = rag.ask(
    "Where is the PostgreSQL database connection created?"
)
```

Internally:

``` text
ask(query)
   │
   ├── embed query
   │
   ├── retrieve top K
   │
   ├── build context
   │
   ├── construct grounded prompt
   │
   └── generate answer
```

------------------------------------------------------------------------

# 47. Important Future Improvements

The current system is a strong baseline, but several improvements can be
added later.

## Hybrid retrieval

Combine:

``` text
semantic/vector search
+
lexical/BM25 search
```

This is especially useful for exact identifiers such as:

``` text
get_connection
MetadataExtractor
DATABASE_URL
RepositoryFile
```

## Reranking

Retrieve a larger candidate set:

``` text
Top 20–50
```

then use a reranker to select the best:

``` text
Top 5
```

## Metadata filtering

Use metadata such as:

``` text
language
chunk_type
parent_class
```

to constrain retrieval.

## Context expansion

If a method is retrieved, retrieve related:

``` text
parent class
called functions
imported modules
```

when useful.

## Call-graph retrieval

The current `calls` metadata is syntactic.

A future symbol-resolution layer could construct:

``` text
function A
   ↓ calls
function B
   ↓ calls
function C
```

This would enable graph-aware code retrieval.

## Repository versioning

Store repository/commit information so multiple versions can coexist
safely.

## Incremental indexing

Instead of re-indexing every file, detect changed files and only
re-embed affected chunks.

## Better prompt grounding

The generation layer should explicitly instruct the LLM to:

-   use retrieved context,
-   distinguish evidence from inference,
-   avoid inventing repository details,
-   mention when the retrieved context is insufficient.

------------------------------------------------------------------------

# 48. Design Principles

The architecture follows these principles:

### Single responsibility

Each component should do one job.

``` text
RepositoryLoader → load files
ASTChunker       → create semantic chunks
MetadataExtractor→ extract metadata
CodeEmbedder     → create vectors
ChunkStore       → persist data
Retriever        → retrieve data
ContextBuilder   → format context
CodeLLM          → generate text
Pipeline         → orchestrate components
```

### Dependency separation

Embedding code should not know about PostgreSQL.

Database code should not know about LLMs.

Retrieval should not know how repositories are loaded.

Generation should not know how vectors are stored.

### Testability

Each layer can be tested independently:

``` text
Loader test
Chunker test
Embedder test
Store test
Retriever test
Context test
LLM test
```

### Configuration over hardcoding

Provider URLs, model IDs, and credentials are configuration.

``` env
FREELLMAPI_BASE_URL=...
EMBEDDING_MODEL=...
LLM_MODEL=...
DATABASE_URL=...
```

### Batch processing

Embedding operations should operate on batches rather than one API
request per chunk.

### Structured code understanding

AST boundaries are preferred over arbitrary text splitting whenever a
supported parser is available.

------------------------------------------------------------------------

# 49. Mental Model

The simplest way to remember the entire system is:

``` text
INDEX:

Repository
    ↓
Files
    ↓
AST
    ↓
Semantic chunks
    ↓
Metadata + embeddings
    ↓
PostgreSQL


QUERY:

Question
    ↓
Embedding
    ↓
Vector search
    ↓
Relevant code
    ↓
Context
    ↓
LLM
    ↓
Answer
```

Or even more compactly:

``` text
LOAD → PARSE → CHUNK → EMBED → STORE
                                  ↓
ASK → EMBED → RETRIEVE → CONTEXT → GENERATE
```

That is the complete architecture of the current Codebase-Aware RAG
system.
