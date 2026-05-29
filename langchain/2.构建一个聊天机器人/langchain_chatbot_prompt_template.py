
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableConfig
import os

# 1. 核心步骤：加载 .env 文件到系统环境变量
load_dotenv()

# 2. 验证所有变量是否成功加载（包含模型名称）
required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

try:
    # 3. 实例化模型（传入确定的字符串变量）
    model = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )
    
    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         (
    #             "system",
    #             "You are a helpful assistant. Answer all questions to the best of your ability.",
    #         ),
    #         MessagesPlaceholder(variable_name="messages"),
    #     ]
    # )

    # chain = prompt | model

    # # response = chain.invoke({"messages": [HumanMessage(content="hi! I'm bob")]})
    # # print(response.content)

    # with_message_history = RunnableWithMessageHistory(chain, get_session_history)
    # config: RunnableConfig = {"configurable": {"session_id": "abc2"}}
    # response = with_message_history.invoke(
    #     [HumanMessage(content="Hi! I'm Jim")],
    #     config=config,
    # )
    # print(response.content)

    # response = with_message_history.invoke(
    #     [HumanMessage(content="What's my name?")],
    #     config=config,
    # )
    # print(response.content)

    # 提示词模板
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    chain = prompt | model

    # response = chain.invoke(
    #     {"messages": [HumanMessage(content="hi! I'm bob")], "language": "chinese"}
    # )
    # print(response.content)

    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="messages",
    )

    config: RunnableConfig = {"configurable": {"session_id": "abc11"}}
    response = with_message_history.invoke(
        {"messages": [HumanMessage(content="hi! I'm todd")], "language": "chinese"},
        config=config,
    )
    print(response.content)

    response = with_message_history.invoke(
        {"messages": [HumanMessage(content="whats my name?")], "language": "chinese"},
        config=config,
    )
    print(response.content)
except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))

