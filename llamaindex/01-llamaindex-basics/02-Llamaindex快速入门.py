import os

import fitz
from dotenv import load_dotenv
from llama_index.core import Document
from llama_index.core import VectorStoreIndex, get_response_synthesizer, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers.type import ResponseMode
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.dashscope import DashScope

load_dotenv()
# 开启简单的日志打印
# llama_index.core.set_global_handler("simple")

# 初始化千问模型(设置成默认)

# LlamaIndex默认使用的大模型被替换为百炼达DashScope
Settings.llm = DashScope(
    model_name=os.getenv("LLM_MODEL"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    api_base_url=os.getenv("DASHSCOPE_BASE_URL"),
    max_tokens=1000
)
# 加载本地的嵌入模型
Settings.embed_model = HuggingFaceEmbedding(
    model_name=os.getenv("EMBEDDING_MODEL_PATH","")
)


# 创建自定义提示词
text_qa_template = PromptTemplate(
    "你是一个严格的文档摘录助手。你的任务是从背景信息中**直接摘录**与问题相关的内容，不做任何扩展、总结或归类。\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "问题：{query_str}\n"
    "要求：\n"
    "1. 只回答背景中**明确出现**的内容，禁止引入其他段落的信息\n"
    "2. 如果某部分内容在背景中**只有标题没有内容**，直接说明'原文未提供具体内容'\n"
    "3. 禁止将其他章节的内容归类为'相关延伸'或'补充说明'\n"
    "4. 回答格式：直接引用原文条款，不要自己加框架（如'综上所述'、'此外'）\n"
    "5. 如果背景完全没有相关信息，只回复'文档中未提及'\n"
    "回答："
)


# 1.加载文档
doc = fitz.open("data/财务管理文档.pdf")
full_text = ""
for page in doc:
    full_text += page.get_text()
documents = [Document(text=full_text)]

# 2.切分文档->节点块
nodes = SentenceSplitter(chunk_size=1024, chunk_overlap=100, separator="\n\n").get_nodes_from_documents(documents)

# 摄取管道来去做切分文档+storage_context存储容器

# 3.创建索引
index = VectorStoreIndex(nodes)

# 4.创建检索器    混合检索 选择一个合适的检索器
retriever = index.as_retriever(similarity_top_k=5)

# 5.创建重排模型  # 对检索出来的文档进行处理（相似性过滤后处理器、重排模型）
reranker = SentenceTransformerRerank(model=os.getenv("RERANK_MODEL_PATH",""), top_n=2)

# 6.创建响应合成器  可以选择不同的响应模型来决定RAG的输出内容
response_synthesizer = get_response_synthesizer(
    response_mode=ResponseMode.COMPACT,
    text_qa_template=text_qa_template,  # 使用自定义的提示词
)

# 7.创建查询引擎
query_engine = RetrieverQueryEngine.from_args(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    node_postprocessors=[reranker]
)

# 开始执行流程
print(query_engine.query("财务管理权限划分？"))