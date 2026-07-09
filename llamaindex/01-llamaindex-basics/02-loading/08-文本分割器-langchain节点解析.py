import json

from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core.node_parser import LangchainNodeParser
from llama_index.core import SimpleDirectoryReader

# 读取文件
documents = SimpleDirectoryReader(input_files=['data/小说.txt']).load_data()

# 包装LangChain中的递归切割文本
parser = LangchainNodeParser(RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50))
nodes = parser.get_nodes_from_documents(documents)
print(len(nodes))
for node in nodes:
    print(json.dumps(node.to_dict(), ensure_ascii=False, indent=2))
