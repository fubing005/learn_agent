
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from dotenv import load_dotenv
import os

load_dotenv()

documents = SimpleDirectoryReader(input_files=['data/小说.txt']).load_data()

embed_model = HuggingFaceEmbedding(model_name=os.getenv("EMBEDDING_MODEL_PATH",""))


"""
buffer_size=考虑的上下文窗口大小,
breakpoint_percentile_threshold=决定"在哪里切分文本"的阈值，
举例说明：
如果文档中有 100 个可能的切分点，设置为 95 意味着只会在语义变化最剧烈的 5 个位置进行切分
值越高（如 99）→ 切分点越少，每块文本更长
值越低（如 80）→ 切分点越多，每块文本更短
"""
splitter = SemanticSplitterNodeParser(
    buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
)

nodes = splitter.get_nodes_from_documents(documents)
# 打印生成的节点
for node in nodes:
    print(node.text, node.metadata, "------")