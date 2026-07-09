from llama_config import get_llm
llm, embed_model = get_llm()
from llama_index.core.indices.property_graph import ImplicitPathExtractor
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter


# 加载文档并构建索引
documents = SimpleDirectoryReader(
    input_files=["data/小说.txt"]
).load_data()

s = SentenceSplitter()
nodes = s.get_nodes_from_documents(documents)


kg_extractor = ImplicitPathExtractor()

extracted_nodes = kg_extractor(nodes)
for node in extracted_nodes:
    print("节点文本：", node.text)   
    print("提取的关系：", node.metadata.get("relations", []))