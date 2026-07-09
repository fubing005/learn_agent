from llama_config import get_llm
llm, embed_model = get_llm()
from llama_index.core import SimpleDirectoryReader
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core import VectorStoreIndex

# 加载文档
documents = SimpleDirectoryReader(input_files=["data/小说.txt"]).load_data()
# 创建索引
index = VectorStoreIndex.from_documents(documents)
print(index.as_query_engine().query("古河是谁"))

# 将索引存储在本地
index.storage_context.persist("./vector_store_index")

# 从本地加载已存储的索引数据
new_storage_context = StorageContext.from_defaults(persist_dir="./vector_store_index")
new_index = load_index_from_storage(new_storage_context)
print(new_index.as_query_engine().query("古河是谁"))