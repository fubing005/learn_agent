from llama_config import init_settings,get_llm
init_settings()
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.core.extractors import (
    TitleExtractor,
)

# llm, embed_model = get_llm()

# 定义数据连接器去读取数据
documents = SimpleDirectoryReader(input_files=["data/小说.txt"]).load_data()
# 定义文本分割器
text_splitter = SentenceSplitter(chunk_size=256, chunk_overlap=30)

# 进行标题的提取
title_extractor = TitleExtractor(nodes=5, node_template="请为以下文档生成一个简洁的标题: {context_str}", num_workers=5)

# 创建数据摄入管道
pipeline = IngestionPipeline(
    transformations=[text_splitter, Settings.embed_model, title_extractor]
)

# 执行管道
nodes = pipeline.run(documents=documents)

# 打印处理后的节点
for node in nodes:
    print(node, "-------", "\n\n")
    print(node.metadata, "-------", "\n\n")