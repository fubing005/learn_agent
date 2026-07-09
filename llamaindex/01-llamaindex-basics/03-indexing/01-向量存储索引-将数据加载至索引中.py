
"""
基本用法：使用 Vector Store 的最简单方法是使用 from_documents 加载一组文档并从中构建索引。
"""

from llama_config import get_llm
llm, embed_model = get_llm()
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader


# 加载文档并构建索引
documents = SimpleDirectoryReader(
    input_files=["data/deepseek介绍.txt"]
).load_data()

# 当使用 from_documents 时，的文档将被分成块，并解析为Node 对象，这些对象是文本字符串的轻量级抽象，用于跟踪元数据和关系。
index = VectorStoreIndex.from_documents(documents, show_progress=True)
print(index.as_retriever().retrieve("deepseek的公司收益？"))


# 默认情况下，VectorStoreIndex 将以 2048 个节点一批生成并插入向量。
# 如果受到内存限制（或者内存有剩余），可以通过传递 insert_batch_size=2048 和期望的批量大小来修改此设置。
# 当插入到远程托管的向量数据库时，这一点尤其有帮助，因为它可以减少网络往返的次数。
# index = VectorStoreIndex.from_documents(
#     documents, show_progress=True, insert_batch_size=2048
# )