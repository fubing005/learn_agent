import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")


llm = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0.7)
# ==================== 🤖 2. 定义节点 (Nodes) ====================
def chatbot_node(state: MessagesState) -> dict:
    """聊天节点：注入系统提示词并调用大模型"""

    # 设定系统提示词，要求模型必须根据对话历史回答
    system_prompt = SystemMessage(content="你是一个亲切的个人助手。请根据用户的对话历史，准确回答他们的问题。")
    
    # 组合系统提示词和当前会话的所有历史消息
    full_messages = [system_prompt] + state["messages"]
    
    # 调用大模型获取回复
    response = llm.invoke(full_messages)
    
    # 返回字典，将新消息增量追加到全局状态的 messages 中
    return {"messages": [response]}

try:
    builder = StateGraph(MessagesState)

#----------------------------内存存储（适合开发测试）----------------------------------

    # checkpointer = MemorySaver()
    
    # builder.add_node("chatbot", chatbot_node)
    # builder.add_edge(START, "chatbot")
    # builder.add_edge("chatbot", END)
    # graph = builder.compile(checkpointer=checkpointer)

    # # 使用 thread_id 区分不同会话
    # config_user_a: RunnableConfig = {"configurable": {"thread_id": "user-alice"}}
    # config_user_b: RunnableConfig = {"configurable": {"thread_id": "user-bob"}}

    # user_msg_a1 = "我叫 Alice"
    # print(f"用户提问: {user_msg_a1}")
    # res_a1 = graph.invoke({"messages": [HumanMessage(content=user_msg_a1)]}, config=config_user_a)
    # print(f"AI 回复: {res_a1['messages'][-1].content}")
    # print("-" * 30)

    # user_msg_a2 = "我叫什么名字？"
    # print(f"用户提问: {user_msg_a2}")
    # res_a2 = graph.invoke({"messages": [HumanMessage(content=user_msg_a2)]}, config=config_user_a)
    # print(f"AI 回复: {res_a2['messages'][-1].content}")
    # print("-" * 30)
    # # Agent 能记住：你叫 Alice

    # # Bob 的对话完全独立
    # user_msg_b1 = "我叫什么名字？"
    # print(f"用户提问: {user_msg_b1}")
    # res_b1 = graph.invoke({"messages": [HumanMessage(content=user_msg_b1)]}, config=config_user_b)
    # print(f"AI 回复: {res_b1['messages'][-1].content}")
    # print("-" * 30)
    # # Agent 不知道 Bob 的名字（不同 thread_id）

#-----------------------------SQLite 持久化存储（适合本地项目）---------------------------------

    builder.add_node("chatbot", chatbot_node)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    config: RunnableConfig = {"configurable": {"thread_id": "persistent-chat"}}
    # 数据持久化到文件，程序重启后对话历史仍存在
    # with 语句被称为上下文管理器（Context Manager）
    # 它的核心作用是：自动管理资源的获取与释放。确保无论代码运行成功还是发生报错，资源都能被正确关闭。
    with SqliteSaver.from_conn_string("./chat_memory.db") as checkpointer:
        graph = builder.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "persistent-chat"}}
        
        # # 第一次运行
        # # graph.invoke({"messages": [HumanMessage(content="我叫张三")]}, config=config)
        
        # # 程序重启后再次运行，记忆仍然存在
        # result = graph.invoke(
        #     {"messages": [HumanMessage(content="你还记得我叫什么吗？")]},
        #     config=config
        # )
        # print(result["messages"][-1].content)
        
# ----------------------------查看对话历史----------------------------------

        # 获取某个 thread 的完整状态历史
        history = list(graph.get_state_history(config))

        for snapshot in history:
            print(f"时间: {snapshot.created_at}")
            print(f"消息数: {len(snapshot.values['messages'])}")
            print("---")

        # 获取当前状态
        current_state = graph.get_state(config)
        print(f"当前消息数: {len(current_state.values['messages'])}")

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))