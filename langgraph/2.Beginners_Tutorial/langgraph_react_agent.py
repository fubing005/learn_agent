import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
import ast
import operator

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

llm = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini"),temperature=0.7)

# @tool 装饰器的核心作用，是把一个普通的 Python 函数转换为大模型（LLM）能够识别并调用的“工具”（Tool）
@tool
def search_web(query: str) -> str:
    """搜索网络获取最新信息。
    
    Args:
        query: 搜索关键词
    
    Returns:
        搜索结果摘要
    """
    # 实际项目中替换为真实搜索 API
    return f"关于 '{query}' 的搜索结果：这是模拟的搜索结果..."

@tool
def calculate(expression: str) -> str:
    """计算数学表达式。
    
    Args:
        expression: 数学表达式，如 '2 + 2' 或 '100 * 0.8'
    
    Returns:
        计算结果
    """
    
    # 安全的运算符映射
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }
    
    def safe_eval(node):
        if isinstance(node, ast.Expression):
            return safe_eval(node.body)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = safe_eval(node.left)
            right = safe_eval(node.right)
            return ops[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = safe_eval(node.operand)
            return ops[type(node.op)](operand)
        else:
            raise ValueError(f"不支持的表达式类型: {type(node)}")
    
    try:
        tree = ast.parse(expression, mode='eval')
        result = safe_eval(tree)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。
    
    Args:
        city: 城市名称
    
    Returns:
        天气信息
    """
    # 实际项目中替换为真实天气 API
    return f"{city} 今日天气：晴，温度 22C，湿度 60%"

def agent_node(state: MessagesState) -> dict:
    """Agent 推理节点：调用 LLM 决定下一步行动"""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

try:
    tools = [search_web, calculate, get_weather]
    llm_with_tools = llm.bind_tools(tools)

    # 构建 ReAct 图
    builder = StateGraph(MessagesState)
    
    # 添加节点
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(tools))  # 内置 ToolNode 自动处理工具调用

    # 添加边
    builder.add_edge(START, "agent")
    # 条件路由：如果 LLM 请求工具则执行工具，否则结束
    builder.add_conditional_edges(
        "agent",
        tools_condition,  # 内置路由函数
        {
            "tools": "tools",
            END: END
        }
    )

    # 工具执行完后返回 agent 继续推理
    builder.add_edge("tools", "agent")

    graph = builder.compile()

    # 测试
    # result = graph.invoke({
    #     "messages": [HumanMessage(content="北京今天天气如何？另外帮我计算 12 * 5")]
    # })
    # for message in result["messages"]:
    #     print(f"[{message.type}]: {message.content[:200] if message.content else '(工具调用)'}")

    # 流式观察 Agent 的每一步
    for chunk in graph.stream(
        {"messages": [HumanMessage(content="搜索 LangGraph 的最新特性")]},
        stream_mode="updates"
    ):
        for node_name, updates in chunk.items():
            print(f"\n=== 节点: {node_name} ===")
            for msg in updates.get("messages", []):
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"  -> 调用工具: {tc['name']}({tc['args']})")
                else:
                    print(f"  -> 输出: {msg.content[:200] if msg.content else '(无内容)'}")

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))