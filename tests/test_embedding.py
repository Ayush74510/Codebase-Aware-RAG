# from sentence_transformers import SentenceTransformer


# model = SentenceTransformer(
#     "jinaai/jina-code-embeddings-1.5b"
# )

# text = """
# def add(a, b):
#     return a + b
# """

# embedding = model.encode(text)

# print("Embedding type:", type(embedding))
# print("Embedding shape:", embedding.shape)

# import voyageai # type: ignore
# from dotenv import load_dotenv
# load_dotenv()

# client = voyageai.Client()

# text = """
# def add(a, b):
#     return a + b
# """

# result = client.embed(
#     [text],
#     model="voyage-code-4",
#     input_type="document",
# )

# embedding = result.embeddings[0]

# print("Embedding type:", type(embedding))
# print("Embedding dimensions:", len(embedding))
# print("First 5 values:", embedding[:5])


from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="http://127.0.0.1:31415/v1",
    api_key=os.getenv("FREELLMAPI_API_KEY"),
)

response = client.embeddings.create(
    model="bge-m3",
    input=["def add(a, b): return a + b"],
)

embedding = response.data[0].embedding

print("Embedding type:", type(embedding))
print("Embedding dimensions:", len(embedding))
print("First 5 values:", embedding[:5])