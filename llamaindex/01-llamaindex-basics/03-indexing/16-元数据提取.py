"""
在许多情况下，特别是对于长篇文档，一段文本可能缺乏必要的上下文来消除与其他类似文本的歧义。
为了解决这个问题，我们使用LLM（Large Language Models）来提取与文档相关的某些上下文信息，以更好地帮助检索和语言模型消除外观相似的段落。
"""
from llama_config import get_llm
llm, embed_model = get_llm()
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
    TitleExtractor,
    KeywordExtractor,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import SimpleDirectoryReader


# 定义数据连接器去读取数据
documents = SimpleDirectoryReader(input_files=["data/小说.txt"]).load_data()

# 创建管道中转换组件
transformations = [
    SentenceSplitter(),
    TitleExtractor(nodes=5),
    QuestionsAnsweredExtractor(questions=3),
    SummaryExtractor(summaries=["prev", "self"]),
    KeywordExtractor(keywords=10)
]
# 创建摄取管道
pipeline = IngestionPipeline(transformations=transformations)

nodes = pipeline.run(documents=documents)

print(nodes)