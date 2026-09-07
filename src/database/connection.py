from __future__ import annotations
import os
import psycopg # type: ignore
from dotenv import load_dotenv
from pgvector.psycopg import register_vector # type: ignore

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set."
    )


def get_connection() -> psycopg.Connection:
    """Create and return a PostgreSQL connection."""

    connection = psycopg.connect(DATABASE_URL)
    register_vector(connection)
    return connection