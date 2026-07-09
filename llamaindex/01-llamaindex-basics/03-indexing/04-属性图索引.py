from llama_config import get_llm
llm, embed_model = get_llm()
from llama_index.core import PropertyGraphIndex
from llama_index.core import SimpleDirectoryReader

# 加载文档并构建索引
documents = SimpleDirectoryReader(
    input_files=["data/小说.txt"]
).load_data()

# 创建属性图
index = PropertyGraphIndex.from_documents(
    documents,
)

# 使用
retriever = index.as_retriever(
    include_text=True,  # 包括与匹配路径的源块
    similarity_top_k=2,  # 向量 kg 节点检索的前 k 个
)
nodes = retriever.retrieve("萧炎的斗之力是多少？")    # 只查向量 / 图，不调用 LLM
print(nodes)
query_engine = index.as_query_engine(
    include_text=False,  # 包括与匹配路径的源块
    similarity_top_k=3,  # 向量 kg 节点检索的前 k 个
)
response = query_engine.query("萧炎的斗之力是多少？") # 查向量 / 图 + 调用 LLM 生成回答
print("-" * 20)
print(response)