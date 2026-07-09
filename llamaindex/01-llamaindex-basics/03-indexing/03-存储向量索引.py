"""
LlamaIndex 支持数十种向量存储。可以通过传递 StorageContext 来指定要使用的向量存储，然后在其中指定 vector_store 参数
"""
from llama_config import get_llm
llm, embed_model = get_llm()
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
import chromadb


# 定义本地化的向量化
chroma_client = chromadb.PersistentClient()
chroma_collection = chroma_client.get_or_create_collection("quickstart")
# 创建Chroma向量数据库对象
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 构建向量存储并自定义存储上下文
storage_context = StorageContext.from_defaults(
    vector_store=vector_store
)
# 加载文档并构建索引
documents = SimpleDirectoryReader(
    input_files=["data/deepseek介绍.txt"]
).load_data()

# 使用转换创建管道
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=250, chunk_overlap=50),
        TitleExtractor(),
        embed_model
    ],
    vector_store=vector_store,
)

# 运行管道
nodes = pipeline.run(documents=documents)
# 使用向量索引去进行存储
# index = VectorStoreIndex.from_documents(documents, show_progress=True, storage_context=storage_context)
# 可以使用摄取管道的方式去将向量存储和加载
index = VectorStoreIndex.from_vector_store(vector_store)
print(index.as_retriever().retrieve("deepseek的公司收益？"))