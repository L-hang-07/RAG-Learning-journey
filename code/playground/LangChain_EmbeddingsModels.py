from langchain_community.embeddings import DashScopeEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

model = DashScopeEmbeddings(
    model = "text-embedding-v3",
    dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
)

print(model.embed_query("你好"))
print(model.embed_documents(["你好", "世界"]))