# llama_config.py
from dotenv import load_dotenv
import os
from llama_index.core import Settings
from llama_index.llms.dashscope import DashScope
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# 模块加载时自动执行
load_dotenv()


def get_llm():
    """
    获取配置好的 LLM 和嵌入模型
    用法: llm, embed_model = get_llm()
    """
    Settings.llm = DashScope(
        model_name=os.getenv("LLM_MODEL"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        api_base_url=os.getenv("DASHSCOPE_BASE_URL"),
        max_tokens=1000,
        is_chat_model=True
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name=os.getenv("EMBEDDING_MODEL_PATH", "")
    )

    return Settings.llm, Settings.embed_model


def init_settings():
    """
    直接设置到 LlamaIndex 全局 Settings（更常用）
    用法: init_settings()
    """
    Settings.llm = DashScope(
        model_name=os.getenv("LLM_MODEL"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        api_base_url=os.getenv("DASHSCOPE_BASE_URL"),
        max_tokens=1000,
        is_chat_model=True
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name=os.getenv("EMBEDDING_MODEL_PATH", "")
    )
