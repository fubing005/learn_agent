"""
如果希望更多地控制文档的索引方式，建议使用摄入管道。这允许自定义节点的分块、元数据和嵌入。
"""
from llama_config import get_llm
llm, embed_model = get_llm()
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings


# 加载文档并构建索引
documents = SimpleDirectoryReader(
    input_files=["data/deepseek介绍.txt"]
).load_data()

# 使用转换创建管道
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=250, chunk_overlap=50),
        TitleExtractor(),
        embed_model,
    ]
)

# 运行管道
nodes = pipeline.run(documents=documents)

# 当使用 from_documents 时，的文档将被分成块，并解析为Node 对象，这些对象是文本字符串的轻量级抽象，用于跟踪元数据和关系。
index = VectorStoreIndex(nodes, show_progress=True)
print(index.as_retriever().retrieve("deepseek的公司收益？"))