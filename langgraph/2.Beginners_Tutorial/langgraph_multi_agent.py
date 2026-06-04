import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

llm = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0)

# 定义专家 Agent
def research_agent(state: MessagesState) -> dict:
    """研究 Agent：负责信息收集"""
    system = SystemMessage(content="你是一个专业的研究员，负责收集和整理信息。请简洁地总结关键信息。")
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}

def writing_agent(state: MessagesState) -> dict:
    """写作 Agent：负责内容创作"""
    system = SystemMessage(content="你是一个专业的写作者，负责根据已有信息撰写内容。请保持内容清晰流畅。")
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}

def review_agent(state: MessagesState) -> dict:
    """审校 Agent：负责质量控制"""
    system = SystemMessage(content="你是一个专业的编辑，负责审核和改进内容质量。请指出问题并给出改进建议。")
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}

# 主管 Agent 决定流程
def supervisor_node(state: MessagesState) -> dict:
    """主管：协调各专家 Agent 的工作"""
    system = SystemMessage(content="""你是一个工作流主管。
根据任务进度决定下一步应该由哪个 Agent 处理。
分析对话历史，只返回以下之一：RESEARCH、WRITING、REVIEW、FINISH
- RESEARCH：需要收集更多信息
- WRITING：信息充足，可以开始写作
- REVIEW：写作完成，需要审核
- FINISH：任务已完成
""")
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}

def route_by_supervisor(state: MessagesState) -> str:
    """根据主管决策路由"""
    raw_content = state["messages"][-1].content
    if isinstance(raw_content, list):
        last_msg = "".join(str(item) for item in raw_content).strip().upper()
    else:
        last_msg = raw_content.strip().upper()

    if "RESEARCH" in last_msg:
        return "research"
    elif "WRITING" in last_msg:
        return "writing"
    elif "REVIEW" in last_msg:
        return "review"
    else:
        return END

try:
    # 构建多 Agent 图
    builder = StateGraph(MessagesState)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("research", research_agent)
    builder.add_node("writing", writing_agent)
    builder.add_node("review", review_agent)

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges("supervisor", route_by_supervisor)

    # 每个专家完成后返回主管
    for agent in ["research", "writing", "review"]:
        builder.add_edge(agent, "supervisor")

    graph = builder.compile()

    # 测试多 Agent 协作
    result = graph.invoke({
        "messages": [HumanMessage(content="请帮我写一篇关于 Python 装饰器的简短介绍文章,回答要精简")]
    })

    print("=== 多 Agent 协作完成 ===")
    for i, msg in enumerate(result["messages"]):
        print(f"\n[{i+1}] {msg.type}: {msg.content[:150]}...")

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))