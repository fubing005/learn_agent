from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.dashscope import DashScope
from dotenv import load_dotenv
import os

from llama_index.readers.file import PyMuPDFReader

load_dotenv()


# LlamaIndex默认使用的大模型被替换为百炼达DashScope
Settings.llm = DashScope(
    model_name=os.getenv("LLM_MODEL"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    api_base_url=os.getenv("DASHSCOPE_BASE_URL"),
    max_tokens=1000
)
# 加载本地的嵌入模型
Settings.embed_model = HuggingFaceEmbedding(
    model_name=os.getenv("EMBEDDING_MODEL_PATH","")
)

# 从文档目录加载文件，自动选择对应的文档加载器
file_extractor = {
    ".pdf": PyMuPDFReader(),   # PDF 用 PyMuPDF,txt 用默认解析器
}
documents = SimpleDirectoryReader(
    "data",
    file_extractor=file_extractor
).load_data()

# 从文档创建索引
index = VectorStoreIndex.from_documents(documents)
# 将索引转换为查询引擎
query_engine = index.as_query_engine()
response = query_engine.query("财务部门的设置？")
print(response)
