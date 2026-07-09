from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core import SimpleDirectoryReader
# 读取文档
documents = SimpleDirectoryReader(input_files=['data/小说.txt']).load_data()

splitter = TokenTextSplitter(
    chunk_size=1024,
    chunk_overlap=20,
    separator=" ",
)
nodes = splitter.get_nodes_from_documents(documents)

print(f"len(nodes) = {len(nodes)}")
for node in nodes:
    print(node, "---"*10)