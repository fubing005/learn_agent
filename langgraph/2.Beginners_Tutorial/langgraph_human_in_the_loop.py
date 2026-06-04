import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

llm = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini"),temperature=0.7)

def request_node(state: MessagesState) -> dict:
    """接收用户请求"""
    return {"messages": state["messages"]}

def approval_node(state: MessagesState) -> dict:
    """审批节点：暂停等待人工审批"""
    last_msg = state["messages"][-1].content
   
    # 暂停执行，等待人工决策
    human_decision = interrupt({
        "question": "是否批准执行以下操作？",
        "action": last_msg
    })
   
    if human_decision == "approve":
        return {"messages": [{"role": "assistant", "content": f"操作已批准：{last_msg}"}]}
    else:
        return {"messages": [{"role": "assistant", "content":  f"操作已被拒绝：{last_msg}"}]}

def execute_node(state: MessagesState) -> dict:
    """执行节点"""
    return {"messages": [{"role": "assistant", "content": "任务执行完成！"}]}

try:
    # 构建图
    builder = StateGraph(MessagesState)
    builder.add_node("request", request_node)
    builder.add_node("approval", approval_node)
    builder.add_node("execute", execute_node)

    builder.add_edge(START, "request")
    builder.add_edge("request", "approval")
    builder.add_edge("approval", "execute")
    builder.add_edge("execute", END)

    # 使用 checkpointer 编译图
    checkpointer = MemorySaver()
    # 必须使用 checkpointer 才能支持 interrupt
    graph = builder.compile(checkpointer=checkpointer)

    # 在边上设置断点
    # 另一种方式：在编译时指定断点
    # graph = builder.compile(
    #     checkpointer=checkpointer,
    #     interrupt_before=["sensitive_node"],   # 执行该节点前暂停
    #     # interrupt_after=["review_node"],     # 执行该节点后暂停
    # )

    # 每次对话使用唯一 thread_id
    config: RunnableConfig = {"configurable": {"thread_id": "approval_session_001"}}

    # Step 1: 启动图，会在 interrupt 处暂停
    print("=== Step 1: 提交请求 ===")
    result = graph.invoke(
        {"messages": [HumanMessage(content="请删除数据库中的所有测试数据")]},
        config=config
    )
    print("图已暂停，等待审批...")

    # Step 2: 人工审批后，用 Command 恢复执行
    print("\n=== Step 2: 人工审批 ===")
    user_input = input("你: ")
    if user_input.lower() in ["退出", "exit", "quit"]:
        print("再见！")
    else:
        if user_input.lower() in ["批准","approve"]:
            # 批准操作
            result = graph.invoke(
                Command(resume="approve"),
                config=config
            )
            print(f"审批结果: {result['messages'][-2].content}")
            print(f"最终结果: {result['messages'][-1].content}")
        elif user_input.lower() in ["拒绝","reject"]:
            #如果要拒绝，使用：
            result = graph.invoke(
                Command(resume="reject"), 
                config=config
            )
            print(f"审批结果: {result['messages'][-2].content}")
            print(f"最终结果: {result['messages'][-1].content}")
        else:
            print("无效输入，请输入 '批准|approve' 或 '拒绝|reject'")

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))