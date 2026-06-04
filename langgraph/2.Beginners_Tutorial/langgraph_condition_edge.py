import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

llm = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini"),temperature=0.7)
# 路由函数
def classify_intent(state: MessagesState) -> str:
    """根据用户意图路由到不同的 Agent"""
    last_message = state["messages"][-1]

    if isinstance(last_message.content, str):
        content = last_message.content.lower()
    elif isinstance(last_message.content, list):
        content = " ".join(
            item if isinstance(item, str) else str(item)
            for item in last_message.content
        ).lower()
    else:
        content = ""

    if "天气" in content or "温度" in content:
        return "weather_agent"
    elif "代码" in content or "编程" in content:
        return "code_agent"
    elif "再见" in content or "退出" in content:
        return "farewell"
    else:
        return "general_agent"

# 定义各个 Agent 节点
def router_node(state: MessagesState) -> dict:
    """路由节点：不做处理，只用于触发路由判断"""
    return {}

def weather_node(state: MessagesState) -> dict:
    """天气 Agent"""
    response = llm.invoke([
        SystemMessage(content="你是一个天气助手，友好地回答天气相关问题。如果没有实时数据，可以给出一般性建议。"),
        *state["messages"]
    ])
    return {"messages": [response]}

def code_node(state: MessagesState) -> dict:
    """代码 Agent"""
    response = llm.invoke([
        SystemMessage(content="你是一个编程助手，擅长解答代码问题并给出清晰的代码示例。"),
        *state["messages"]
    ])
    return {"messages": [response]}

def general_node(state: MessagesState) -> dict:
    """通用 Agent"""
    response = llm.invoke([
        SystemMessage(content="你是一个友善的 AI 助手，可以回答各种问题。"),
        *state["messages"]
    ])
    return {"messages": [response]}

def farewell_node(state: MessagesState) -> dict:
    """告别节点"""
    return {"messages": [{"role": "assistant", "content": "再见！期待下次与你交流。"}]}

try:
    # 构建图
    builder = StateGraph(MessagesState)

    # 添加节点
    builder.add_node("router", router_node)
    builder.add_node("weather_agent", weather_node)
    builder.add_node("code_agent", code_node)
    builder.add_node("general_agent", general_node)
    builder.add_node("farewell", farewell_node)    
    
    # 添加边
    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router",
        classify_intent,
        {
            "weather_agent": "weather_agent",
            "code_agent": "code_agent",
            "general_agent": "general_agent",
            "farewell": "farewell",
        }
    )

    # 所有 agent 节点处理完后结束
    for node in ["weather_agent", "code_agent", "general_agent", "farewell"]:
        builder.add_edge(node, END)

    # 编译图
    graph = builder.compile()

    # 测试不同意图
    test_inputs = [
        "北京今天天气怎么样？",
        "帮我写一个 Python 快速排序",
        "你好，介绍一下你自己",
        "再见啦！"
    ]   

    for user_input in test_inputs:
        print(f"\n用户: {user_input}")
        result = graph.invoke({"messages": [HumanMessage(content=user_input)]})
        print(f"助手: {result['messages'][-1].content[:100]}...")
        print("-" * 50)

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))