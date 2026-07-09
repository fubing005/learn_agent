import chromadb

from llama_config import get_llm
llm, embed_model = get_llm()

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core import StorageContext, load_index_from_storage


# 加载文档
documents = SimpleDirectoryReader(input_files=["data/小说.txt"]).load_data()

# print("---------------使用chroma进行存储向量--------------------")
# 创建客户端和新的集合
# chroma_client = chromadb.EphemeralClient()  # 创建一个内存对象
chroma_client = chromadb.PersistentClient("./chroma_db")  # 创建一个本地存储的对象
# chroma_collection = chroma_client.get_or_create_collection("quickstart")
#
# # 设置ChromaVectorStore并加载数据
# vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
# # 创建一个存储容器
# storage_context = StorageContext.from_defaults(vector_store=vector_store)
#
# # 创建向量索引
# index = VectorStoreIndex.from_documents(
#     documents, storage_context=storage_context, embed_model=embed_model
# )
# print(chroma_collection.count())
# # 查询数据
# query_engine = index.as_query_engine()
# response = query_engine.query("古河是谁？")
# print(response)
# print("---------------使用chroma获取存储向量--------------------")
# chroma_collection_new = chroma_client.get_collection("quickstart")
# vector_store_new = ChromaVectorStore(chroma_collection=chroma_collection_new)
# # 加载索引（只恢复索引结构，不重新写入）
# index_new = VectorStoreIndex.from_vector_store(
#     vector_store=vector_store_new,
#     embed_model=embed_model  # 必须与原来用的一致
# )
#
# # 可以开始查询
# query_engine_new = index_new.as_query_engine()
# response = query_engine_new.query("萧炎的妹妹是谁？")
# print(response)

print("-------------------使用最基础的内存向量进行本地存储----------------------")
# 创建一个最基础的内存向量
vector_store = SimpleVectorStore()
# 创建一个存储容器
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 创建向量索引
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, embed_model=embed_model
)
# 查询数据
query_engine = index.as_query_engine()
response = query_engine.query("古河是谁？")
print(response)

# 将数据存储到本地
storage_context.persist("./storage")

# 从本地加载已存储的向量数据
storage_context_new = StorageContext.from_defaults(persist_dir="./storage")
# 通过load_index_from_storage去加载本地保存的index
new_index = load_index_from_storage(storage_context_new)
new_query_engine = new_index.as_query_engine()
new_response = new_query_engine.query("谁要和萧炎退婚")
print(new_response)