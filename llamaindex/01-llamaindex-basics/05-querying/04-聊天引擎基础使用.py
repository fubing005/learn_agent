from llama_config import get_llm
llm, embed_model = get_llm()

from llama_index.core.chat_engine import SimpleChatEngine



chat_engine = SimpleChatEngine.from_defaults(llm=llm)
# 创建聊天引擎
response = chat_engine.chat("我今天吃了火锅，心情很不错。")
print(response)

print("*" * 50)

res = chat_engine.chat("我今天吃了什么？")
print(res)