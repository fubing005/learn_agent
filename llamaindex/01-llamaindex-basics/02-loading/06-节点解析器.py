import json

# 1.简单的文件节点解析器：根据文件的后缀名选择对应的解析器，解析成节点
# import json
#
# from llama_index.core.node_parser import SimpleFileNodeParser
# from llama_index.readers.file import FlatReader
# from pathlib import Path
#
# # 读取文件 FlatReader：从文件中提取原始文本
# md_docs = FlatReader().load_data(Path("data/小说.txt"))
#
# # 创建节点解析器，根据后缀名选择对应的解析器
# parser = SimpleFileNodeParser()
# # 将文档解析成节点
# nodes = parser.get_nodes_from_documents(md_docs)
# print(f"共解析出 {len(nodes)} 个节点")
# for node in nodes:
#     print(json.dumps(node.to_dict(), ensure_ascii=False, indent=2))


# 2.HTML节点解析器：根据指定的HTML标签提取内容，解析成节点
# from llama_index.core.node_parser import HTMLNodeParser
# from llama_index.readers.file import FlatReader
# from pathlib import Path
#
# # 读取文件 FlatReader：从文件中提取原始文本
# html_docs= FlatReader().load_data(Path("data/index.html"))
# # 使用 HTMLNodeParser，指定根据哪些标签创建节点
# # 需要安装 pip install beautifulsoup4
# parser = HTMLNodeParser(tags=["p", "h1", "li"])  # 只提取 p, h1, li 标签的内容作为节点
# nodes = parser.get_nodes_from_documents(html_docs)
# print(f"共解析出 {len(nodes)} 个节点")
# for node in nodes:
#     print(json.dumps(node.to_dict(), ensure_ascii=False, indent=2))


# 3.JSON节点解析器：根据指定的JSON路径提取内容，解析成节点
# from llama_index.core.node_parser import JSONNodeParser
# from llama_index.readers.file import FlatReader
# from pathlib import Path
#
# # 读取文件 FlatReader：从文件中提取原始文本
# json_docs = FlatReader().load_data(Path("data/request.json"))
#
# # 构建JSON节点解析器
# parser = JSONNodeParser()
# # 生成节点
# nodes = parser.get_nodes_from_documents(json_docs)
# print(f"共解析出 {len(nodes)} 个节点")
# for node in nodes:
#     print(json.dumps(node.to_dict(), ensure_ascii=False, indent=2))


# 4.Markdown节点解析器：解析原始的markdown文档
# from llama_index.core.node_parser import MarkdownNodeParser
# from llama_index.readers.file import FlatReader
# from pathlib import Path
#
# # 读取文件
# md_docs = FlatReader().load_data(Path("data/test.md"))
# parser = MarkdownNodeParser()
# nodes = parser.get_nodes_from_documents(md_docs)
# print(f"共解析出 {len(nodes)} 个节点")
# for node in nodes:
#     print(json.dumps(node.to_dict(), ensure_ascii=False, indent=2))


# 5.MarkdownElementNodeParser：能够更好的解析md中的表格，在MarkdownNodeParser的基础上，增加了元素关系（如前后关系）和自定义摘要提示词的功能
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.readers.file import FlatReader
from llama_index.llms.dashscope import DashScope
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import get_response_synthesizer
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
# LlamaIndex默认使用的大模型被替换为百炼
Settings.llm = DashScope(
    model_name=os.getenv("LLM_MODEL"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    api_base_url=os.getenv("DASHSCOPE_BASE_URL"),
    max_tokens=1000,
    is_chat_model=True
)
# 加载本地的嵌入模型
Settings.embed_model = HuggingFaceEmbedding(
    model_name=os.getenv("EMBEDDING_MODEL_PATH","")
)

# 自定义你的提示词
# 建议：明确告诉 AI 保持简洁，并提取关键的关键词（如命令、字段名）
MY_CUSTOM_SUMMARY_QUERY = (
    "你是一个技术文档解析助手。请提取以下 Markdown 表格或内容的极简摘要。"
    "要求：1. 严禁啰嗦；2. 必须包含表格中的关键实体词（如 API 路径、参数名、状态码）；"
    "3. 如果是代码相关内容，请保留具体的命令名称。请用中文摘要"
)

# 读取文件+解析文档
md_docs = FlatReader().load_data(Path("data/test.md"))
parser1 = MarkdownElementNodeParser(include_prev_next_rel=True, summary_query_str=MY_CUSTOM_SUMMARY_QUERY)
nodes = parser1.get_nodes_from_documents(md_docs)
print(f"共解析出 {len(nodes)} 个节点")
for node in nodes:
    print(json.dumps(node.to_dict(), ensure_ascii=False, indent=2))


# 构建向量索引
index = VectorStoreIndex(nodes)


retriever = index.as_retriever(similarity_top_k=5)
# 5. 创建查询引擎
response_synthesizer = get_response_synthesizer(
    response_mode="tree_summarize",
)

# 3. 组合成查询引擎
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
)

# 6. 测试查询
print("\n--- 测试查询 1：针对表格数据 ---")
response = query_engine.query("核心特性中，多轮对话主要是什么？")
print(response)
#
print("\n--- 测试查询 2：针对文本/代码内容 ---")
response = query_engine.query("快速开始的环境要求是什么？")
print(response)