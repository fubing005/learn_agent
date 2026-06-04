
import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

def prompt_engineer_node(state: MessagesState):
    print("\n--- 节点 1: 提示词优化 ---")
    last_message = state["messages"][-1]
    
    # 构造一条系统提示或修改意见，追加到状态中
    optimized_msg = HumanMessage(
        content=f"请用幽默讽刺的语气回答这个问题：{last_message.content}"
    )
    # MessagesState 会自动将这个新消息追加到列表末尾
    return {"messages": [optimized_msg]}

def call_model_node(state: MessagesState):
    print("\n--- 节点 2: 调用大模型 ---")
    # 此时 state["messages"] 已经自动包含了【用户原消息 + 优化后的消息】
    print(f"当前状态中的消息总数: {len(state['messages'])}")
    
    response = model.invoke(state["messages"])
    return {"messages": [response]}

#-------------------------------------------------------

# 为了能精准修改某条消息，我们通常在生成时为它指定一个唯一的 id
SHARED_MESSAGE_ID = "ai_msg_unique_123"

# 节点 1：模拟用户发帖与 AI 生成一条带有固定 ID 的消息
def create_initial_messages(state: MessagesState):
    print("\n--- 节点 1: 生成初始消息 ---")
    
    # 模拟返回一条带有固定 ID 的 AI 消息
    return {
        "messages": [
            AIMessage(
                content="这是最初的 AI 回复内容，包含了一些错误的废话。", 
                id=SHARED_MESSAGE_ID
            )
        ]
    }

# 节点 2：执行【修改】操作（覆盖特定 ID 的消息）
def modify_message_node(state: MessagesState):
    print("\n--- 节点 2: 执行修改操作 ---")
    
    # 构造一条同名 id 的新消息
    updated_message = AIMessage(
        content="✨ [已修改] 这是经过人工审核或精简后的正确内容。", 
        id=SHARED_MESSAGE_ID # 关键：ID 必须完全一致
    )
    
    # 返回给 MessagesState
    return {"messages": [updated_message]}

# 节点 3：执行【删除】操作（抹除特定 ID 的消息）
def delete_message_node(state: MessagesState):
    print("\n--- 节点 3: 执行删除操作（清空该消息） ---")
    
    # 如果想删除这条消息，返回一个 RemoveMessage，并传入它的 id
    return {"messages": [RemoveMessage(id=SHARED_MESSAGE_ID)]}

# -------------------------------------------------------------

def trim_history_to_keep_last_4(state: MessagesState):
    print("\n--- [节点 A] 历史裁剪检查开始 ---")
    messages = state["messages"]
    print(f"当前检查点内存中的消息总数: {len(messages)}")
    
    # 我们设定阈值：如果消息总数超过 4 条，就开始裁剪
    if len(messages) > 4:
        number_to_delete = len(messages) - 4
        print(f"👉 警告：消息数已达 {len(messages)} 条，需要删除最老的 {number_to_delete} 条。")
        
        # 提取老消息的 ID 并封装为 RemoveMessage 信号
        delete_signals = []
        for m in messages[:number_to_delete]:
            if m.id:
                delete_signals.append(RemoveMessage(id=m.id))
            else:
                # 极端情况：如果消息没有定义 ID，框架无法精准删除
                print(f"无法删除没有 ID 的消息: {m.content[:10]}...")
                
        # 返回 RemoveMessage 列表，LangGraph 会立刻在状态机中彻底抹除这些 ID 的消息
        return {"messages": delete_signals}
        
    print("✅ 消息数未超标，无需裁剪。")
    return {"messages": []}

# 大模型调用节点
def call_model_node_02(state: MessagesState):
    print("\n--- [节点 B] 调用大模型服务 ---")
    # 此时进入该节点时，state["messages"] 已经是被前面裁剪过、只剩最后 4 条的精简列表了
    print(f"送入大模型(LLM)的上下文消息数: {len(state['messages'])}")
    for idx, msg in enumerate(state['messages']):
         print(f"  [{idx+1}] {msg.type}: {msg.content[:15]}...")
         
    response = model.invoke(state["messages"])
    return {"messages": [response]}

try:
    model = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini"))

    # 构建状态图并加入持久化内存（Memory）
    workflow = StateGraph(MessagesState)

#---------------------------------------------------------- 

    # # 添加节点
    # workflow.add_node("engineer", prompt_engineer_node)
    # workflow.add_node("llm", call_model_node)

    # # 构建边：START -> engineer -> llm -> END
    # workflow.add_edge(START, "engineer")
    # workflow.add_edge("engineer", "llm")
    # workflow.add_edge("llm", END)

    # # 【核心进阶】内存检查点：赋予图“多轮对话记忆”的能力
    # memory = MemorySaver()
    # app = workflow.compile(checkpointer=memory)

    # # 必须指定 thread_id，LangGraph 靠它来识别不同的用户/对话
    # config: RunnableConfig = {"configurable": {"thread_id": "user_session_001"}}

    # # ---- 第一轮对话 ----
    # print("==== 第一轮输入 ====")
    # state_1 = app.invoke(
    #     {"messages": [HumanMessage(content="今天天气怎么样？")]}, 
    #     config=config
    # )
    # print(f"AI 回复: {state_1['messages'][-1].content}")
    

    # # ---- 第二轮对话（测试记忆能力） ----
    # print("\n==== 第二轮输入 ====")
    # # 我们不传历史记录，只传新问题，LangGraph 会自动从内存中读取之前的 MessagesState
    # state_2 = app.invoke(
    #     {"messages": [HumanMessage(content="我刚才问了什么？")]}, 
    #     config=config
    # )
    # print(f"AI 回复: {state_2['messages'][-1].content}")

# -----------------------------------------------------------------

    # # 消息的删除与修改
    # workflow.add_node("create", create_initial_messages)
    # workflow.add_node("modify", modify_message_node)
    # workflow.add_node("delete", delete_message_node)

    # # 路由线 1：START -> create -> modify -> END (测试修改)
    # workflow.add_edge(START, "create")
    # workflow.add_edge("create", "modify")
    # workflow.add_edge("modify", END)
    # # workflow.add_edge("modify","delete")
    # # workflow.add_edge("delete", END)

    # app = workflow.compile(checkpointer=MemorySaver())
    # config: RunnableConfig = {"configurable": {"thread_id": "edit_test_session"}}

    # # 触发运行
    # print("==== 开始图运行（测试修改） ====")
    # final_state = app.invoke({"messages": [HumanMessage(content="你好")]}, config=config)

    # # 打印最终的状态列表
    # print("\n==== 运行结束后的最终状态消息列表 ====")
    # for msg in final_state["messages"]:
    #     print(f"[{msg.type}] (ID: {msg.id}): {msg.content}")

#-----------------------------------------------------------------

    # 按历史消息数量删除
    '''
        START ──> [接收新消息] ──> [trim_history 节点] ──> [llm 节点] ──> END
                                   │
                           (判断是否需要裁剪)
    '''
    # 挂载两个节点
    workflow.add_node("trim_node", trim_history_to_keep_last_4)
    workflow.add_node("llm_node", call_model_node_02)

    # 设置调用流程线
    workflow.add_edge(START, "trim_node")        # 1. 任何新输入先送去检查裁剪
    workflow.add_edge("trim_node", "llm_node")    # 2. 裁剪完紧接着调用大模型
    workflow.add_edge("llm_node", END)           # 3. 大模型回复后结束本轮

    app = workflow.compile(checkpointer=MemorySaver())
    
    # 模拟连续多轮对话，触发裁剪流程
    config: RunnableConfig = {"configurable": {"thread_id": "token_control_session"}}

    # 第 1 轮（2条消息：1 user + 1 ai）
    print("\n==== 🚀 第 1 轮对话 ====")
    state = app.invoke({"messages": [HumanMessage(content="你好，我是小明。")]}, config=config)

    # 第 2 轮（此时共 4 条消息：2 user + 2 ai，刚好达到阈值不裁剪）
    print("\n==== 🚀 第 2 轮对话 ====")
    state = app.invoke({"messages": [HumanMessage(content="我刚才说我叫什么名字来着？")]}, config=config)

    # 第 3 轮（致命的一轮：加入新问题后，总数变成 5 条，触发裁剪流程！）
    print("\n==== 🚀 第 3 轮对话（触发裁剪） ====")
    state = app.invoke({"messages": [HumanMessage(content="今天天气真好啊。")]}, config=config)

    # 查看最终保留在内存中的状态
    print("\n==== 🏁 最终保存在 thread_id 中的健康历史 ====")
    for msg in state["messages"]:
        print(f"[{msg.type}]: {msg.content}")


except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))