# from src.database.connection import get_connection


# with get_connection() as connection:
#     with connection.cursor() as cursor:
#         cursor.execute(
#             """
#             SELECT extversion
#             FROM pg_extension
#             WHERE extname = 'vector';
#             """
#         )

#         result = cursor.fetchone()

#         print(f"pgvector version: {result[0]}")

from src.database.connection import get_connection


with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1;")

        result = cursor.fetchone()

        print(result)