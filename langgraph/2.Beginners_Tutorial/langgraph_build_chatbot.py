import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import SystemMessage, HumanMessage
load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

llm = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini"),temperature=0.7)
SYSTEM_PROMPT = """你是一个友善、专业的 AI 助手。
你的回答应该：
- 简洁清晰
- 使用中文回复
- 在不确定时主动询问用户
"""

def chatbot_node(state: MessagesState) -> dict:
    """核心对话节点"""
    system = SystemMessage(content=SYSTEM_PROMPT)
    messages = [system] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# 多轮对话函数
def chat(conversation_history: list, user_input: str) -> tuple[str, list]:
    """处理单轮对话，返回 AI 响应和更新后的历史"""
    conversation_history.append(HumanMessage(content=user_input))
    result = graph.invoke({"messages": conversation_history})
    conversation_history = result["messages"]
    ai_response = conversation_history[-1].content
    return ai_response, conversation_history

try:

    # 构建图
    builder = StateGraph(MessagesState)
    builder.add_node("chatbot", chatbot_node)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    graph = builder.compile()

    # 多轮对话示例
    history = []
    while True:
        user_input = input("你: ")
        if user_input.lower() in ["退出", "exit", "quit"]:
            print("再见！")
            break
    
        response, history = chat(history, user_input)
        print(f"助手: {response}\n")

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))