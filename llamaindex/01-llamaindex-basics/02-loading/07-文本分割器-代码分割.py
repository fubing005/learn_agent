"""
是专门用于处理源代码文件的工具，旨在将代码按逻辑结构（如函数、类、代码块）智能分割，同时保留语法完整性和上下文关联。
"""

from llama_index.core.node_parser import CodeSplitter
from llama_index.core import SimpleDirectoryReader
from tree_sitter import Language, Parser
import tree_sitter_python

# 读取文件
documents = SimpleDirectoryReader(input_files=['data/demo.py']).load_data()
# 手动创建 parser
parser = Parser(Language(tree_sitter_python.language()))
# 初始化代码分割器
splitter = CodeSplitter(
    language="python",
    chunk_lines=50,  # 每块行数
    chunk_lines_overlap=10,  # 重叠的数量
    max_chars=300,  # 块最大的数量
    parser=parser   # 手动传入
)
# 将文档转换成节点
nodes = splitter.get_nodes_from_documents(documents)
for node in nodes:
    print(f"Type: {node.metadata}\nText: {node.text}\n{'='*50}")