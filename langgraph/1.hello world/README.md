为了深入理解 `MessagesState` 的核心机制，我们需要知道它最强大的地方在于：**它不只是一个普通的 Python 字典，而是一个内置了“通道合并器（Reducer）”的状态机**。这意味着当你向它返回新消息时，它不会覆盖旧消息，而是会自动**追加（Append）**。

下面我们通过扩展代码，展示 `MessagesState` 的 **3 个进阶核心用法**：

1. **自动追加（Reducer 机制）**：多节点连续修改状态。
2. **多轮对话记忆（State 保持）**：通过配置 `checkpointer` 实现多轮聊天。
3. **消息剪枝与清空（覆写机制）**：如何利用消息的 `id` 属性去更新、替换或删除历史消息。

``` python
import os
from uuid import uuid4
from langchain_core.messages import HumanMessage, AIMessage, RemoveMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# 1. 初始化大模型
model = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"))

# ==========================================
# 进阶用法演示 1：多节点连续操作 MessagesState
# ==========================================

# 节点 A：负责给用户的提示词“加点料”（前置处理）
def prompt_engineer_node(state: MessagesState):
    print("\n--- 节点 1: 提示词优化 ---")
    last_message = state["messages"][-1]
    
    # 构造一条系统提示或修改意见，追加到状态中
    optimized_msg = HumanMessage(
        content=f"请用幽默讽刺的语气回答这个问题：{last_message.content}"
    )
    # MessagesState 会自动将这个新消息追加到列表末尾
    return {"messages": [optimized_msg]}

# 节点 B：调用真实的大模型
def call_model_node(state: MessagesState):
    print("\n--- 节点 2: 调用大模型 ---")
    # 此时 state["messages"] 已经自动包含了【用户原消息 + 优化后的消息】
    print(f"当前状态中的消息总数: {len(state['messages'])}")
    
    response = model.invoke(state["messages"])
    return {"messages": [response]}


# ==========================================
# 2. 构建状态图并加入持久化内存（Memory）
# ==========================================
workflow = StateGraph(MessagesState)

# 添加节点
workflow.add_node("engineer", prompt_engineer_node)
workflow.add_node("llm", call_model_node)

# 构建边：START -> engineer -> llm -> END
workflow.add_edge(START, "engineer")
workflow.add_edge("engineer", "llm")
workflow.add_edge("llm", END)

# 【核心进阶】内存检查点：赋予图“多轮对话记忆”的能力
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


# ==========================================
# 3. 运行与验证
# ==========================================

# 必须指定 thread_id，LangGraph 靠它来识别不同的用户/对话【在langgraph中thread_id是固定写法】
config = {"configurable": {"thread_id": "user_session_999"}}

# ---- 第一轮对话 ----
print("==== 第一轮输入 ====")
state_1 = app.invoke(
    {"messages": [HumanMessage(content="今天天气怎么样？")]}, 
    config=config
)
print(f"AI 回复: {state_1['messages'][-1].content}")

# ---- 第二轮对话（测试记忆能力） ----
print("\n==== 第二轮输入 ====")
# 我们不传历史记录，只传新问题，LangGraph 会自动从内存中读取之前的 MessagesState
state_2 = app.invoke(
    {"messages": [HumanMessage(content="我刚才问了什么？")]}, 
    config=config
)
print(f"AI 回复: {state_2['messages'][-1].content}")


# ==========================================
# 进阶用法演示 3：如何修改或删除 MessagesState 中的消息
# ==========================================
print("\n==== 进阶：修改与删除操作 ====")

# 机制 A：修改消息（通过相同的 id）
# MessagesState 如果收到相同 id 的消息，会执行【替换】而不是【追加】
msg_id = str(uuid4())
state_test = {"messages": [AIMessage(content="原内容", id=msg_id)]}

# 模拟节点返回相同 id 的新消息
updated_message = AIMessage(content="修改后的新内容", id=msg_id)
# 结果：列表长度不变，“原内容”被覆盖为“修改后的新内容”

# 机制 B：删除消息（使用 RemoveMessage）
# 如果想清空或裁剪历史消息，避免 Token 爆炸，可以返回 RemoveMessage
def trim_history_node(state: MessagesState):
    # 假设我们想删除历史中的第一条消息
    first_msg_id = state["messages"][0].id
    if first_msg_id:
        return {"messages": [RemoveMessage(id=first_msg_id)]}
    return {"messages": []}
```

核心要点总结（高价值信息）

| 场景             | 你需要做的是                                                 | 背后原理                                                     |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **新增消息**     | `return {"messages": [NewMessage]}`                          | `MessagesState` 默认使用 `add_messages` 减速器，自动执行 `list.extend()` 追加操作。 |
| **修改某条历史** | `return {"messages": [AnyMessage(id="存在的ID", content="新内容")]}` | 如果 `id` 在当前状态列表中已存在，LangGraph 会直接**覆盖**该位置的消息。 |
| **删除某条历史** | `return {"messages": [RemoveMessage(id="要删的ID")]}`        | LangGraph 专用的删除标记，状态机看到它后会从列表中移除对应 ID 的消息。 |
| **实现多轮聊天** | 在 `.compile(checkpointer=MemorySaver())` 时传入内存锁，并在 `invoke` 时带上 `thread_id`。 | 图的状态会被序列化保存，下次带上同个 `thread_id` 访问时，状态会自动恢复。 |