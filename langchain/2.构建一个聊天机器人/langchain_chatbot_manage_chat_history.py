
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, trim_messages
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableConfig
load_dotenv()

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
    model = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )

    trimmer = trim_messages(
        max_tokens=65,
        strategy="last",
        token_counter=model,
        include_system=True,
        allow_partial=False,
        start_on="human",
    )

    messages = [
        SystemMessage(content="you're a good assistant"),
        HumanMessage(content="hi! I'm bob"),
        AIMessage(content="hi!"),
        HumanMessage(content="I like vanilla ice cream"),
        AIMessage(content="nice"),
        HumanMessage(content="whats 2 + 2"),
        AIMessage(content="4"),
        HumanMessage(content="thanks"),
        AIMessage(content="no problem!"),
        HumanMessage(content="having fun?"),
        AIMessage(content="yes!"),
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    chain = (
        RunnablePassthrough.assign(messages=itemgetter("messages") | trimmer)
        | prompt
        | model
    )

    # # 忘记之前的消息: [我不知道你的名字。请告诉我你的名字！]
    # response = chain.invoke(
    #     {
    #         "messages": messages + [HumanMessage(content="what's my name?")],
    #         "language": "Chinese",
    #     }
    # )
    # print(response.content)

    # # 记住最近的消息: [你问了“2 + 2等于多少]
    # response = chain.invoke(
    #     {
    #         "messages": messages + [HumanMessage(content="what math problem did i ask")],
    #         "language": "Chinese",
    #     }
    # )
    # print(response.content)

    # 包装在消息历史中
    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="messages",
    )
    config: RunnableConfig = {"configurable": {"session_id": "abc20"}}
    # response = with_message_history.invoke(
    #     {
    #         "messages": messages + [HumanMessage(content="whats my name?")],
    #         "language": "Chinese",
    #     },
    #     config=config,
    # )
    # print(response.content)
    response = with_message_history.invoke(
        {
            "messages": [HumanMessage(content="what math problem did i ask?")],
            "language": "Chinese",
        },
        config=config,
    )
    print(response.content)


except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))