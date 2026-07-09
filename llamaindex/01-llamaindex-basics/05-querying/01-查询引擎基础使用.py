# import
from llama_config import get_llm
llm, embed_model = get_llm()

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# 加载文档
documents = SimpleDirectoryReader(input_files=["data/小说.txt"]).load_data()
# 创建索引对象
index = VectorStoreIndex.from_documents(documents)

# 查询引擎用来提问
# 检索对应的上下文->组合用户问题+检索的上下文交个LLM，去总结回复
res = index.as_query_engine().query("萧炎的爸爸叫什么名字？")
print(res)