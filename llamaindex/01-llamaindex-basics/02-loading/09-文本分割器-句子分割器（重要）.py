"""
专门用于将文本按自然语言句子边界拆分的工具，适用于需要保留完整语义单元的 NLP 任务
"""

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

# 初始化分割器
splitter = SentenceSplitter(
    chunk_size=512,  # 分割长度
    chunk_overlap=50,  # 重叠长度
    paragraph_separator="\r\n\r\n",  # 段落分割符 第一优先级
    secondary_chunking_regex="[^，。；！？]+[，。；！？]?" # 二级切分正则表达式 第二优先级
)
# 读取文件
documents = SimpleDirectoryReader(input_files=['data/小说.txt']).load_data()

# 分割文段
nodes = splitter.get_nodes_from_documents(documents)
for node in nodes:
    print(node.text, "---"*10)