from llama_config import get_llm
llm, embed_model = get_llm()

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core import SummaryIndex


"""
默认情况下，对象SimpleDocumentStore存储Node在内存中。
可以通过分别调用docstore.persist() 和（SimpleDocumentStore.from_persist_path(...)磁盘加载将它们持久化到磁盘。
"""

# 加载文档
documents = SimpleDirectoryReader(input_files=["data/小说.txt"]).load_data()
# 解析成节点
nodes = SentenceSplitter().get_nodes_from_documents(documents)
# 创建简单文档存储，并把节点传入
doc_store = SimpleDocumentStore()
doc_store.add_documents(nodes)

# 创建一个存储容器
storage_context = StorageContext.from_defaults(docstore=doc_store)

# 将文件进行本地存储
storage_context.persist("./documents")

# 从本地加载已存储的向量数据
new_storage_context = StorageContext.from_defaults(persist_dir="./documents")
print(new_storage_context.docstore.docs)