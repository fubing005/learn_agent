import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from typing import Annotated, Literal, cast
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

model = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini"),temperature=0)


# 1. 定义状态 (State) - 遵循最佳实践，保持精简并使用限制重试的字段
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    retry_count: int  # 记录重试次数，防止无限循环

# 2. 定义 Agent 会调用的工具 (Tool)
def multiply(a: int, b: int) -> int:
    """乘法计算器。当需要计算 a 乘以 b 时使用此工具。"""
    return a * b

# 4. 定义节点函数 (Nodes)
def call_model(state: AgentState) -> dict:
    """调用大模型节点（幂等，返回增量更新）"""
    messages = state["messages"]
    response = model.invoke(messages)
    
    # 正确做法：只返回需要更新的字段，不直接修改输入 state
    return {"messages": [response]}

# 5. 定义条件路由函数 (Conditional Edges)
def should_continue(state: AgentState) -> Literal["tools"] | str:
    """控制流：判断是继续调用工具，还是结束运行"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 确保是 AIMessage 且包含 tool_calls
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return END
        
    # 无限循环熔断机制
    current_retry = state.get("retry_count", 0)
    if current_retry >= 3:
        print("⚠️ 达到最大尝试次数，强制熔断！")
        return END
        
    return "tools"

def increment_retry(state: AgentState) -> dict:
    """辅助节点：更新重试计数器"""
    current_retry = state.get("retry_count", 0)
    # 核心安全防护：如果是字符串，强转为数字
    if isinstance(current_retry, str):
        current_retry = int(current_retry) if current_retry.isdigit() else 0
        
    return {"retry_count": current_retry + 1}

try:
    tools = [multiply]
    tool_node = ToolNode(tools)
    # 6. 构建图结构 (Graph)
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("counter", increment_retry)

    # 设置连线
    workflow.add_edge(START, "agent")

    # 从 agent 出发进行条件路由
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "counter", # 如果需要调工具，先去技术器+1
            END: END
        }
    )

    # 工具执行完毕后，必须重新回到 agent 节点进行判断
    workflow.add_edge("counter", "tools")
    workflow.add_edge("tools", "agent")

    # 7. 编译图（暴露给 Studio 调用的变量名必须与配置文件一致）
    graph = workflow.compile()

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))