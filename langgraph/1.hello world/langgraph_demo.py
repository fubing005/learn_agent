
import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage


load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

# 作用：这是一个自定义的**节点（Node）**函数，名字叫 mock_llm。
# 参数 state：接收当前的图状态，其类型为 MessagesState（内置类型，专门用来存储和自动追加对话消息列表）。
# 返回值：在 LangGraph 中，节点返回一个字典来更新状态。这里它向状态中的 messages 列表追加了一条来自 AI 的、内容为 "hello world" 的消息。
def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

try:
    # 作用：初始化一个状态图（StateGraph）。
    # 核心机制：它指定了 MessagesState 作为整个图的全局状态模型。所有节点都会读取这个状态，并且更新这个状态。
    graph = StateGraph(MessagesState)
    # 向图中添加一个节点，节点名称默认为函数名 "mock_llm"。
    graph.add_node(mock_llm)
    # START 是 LangGraph 的内置起点，表示当图被调用时，立刻进入 "mock_llm" 节点。
    graph.add_edge(START, "mock_llm")
    # 当 "mock_llm" 节点执行完毕后，流程直接走向 END（内置终点），结束运行。
    graph.add_edge("mock_llm", END)
    # 编译图。在将图的结构（节点和边）定义好后，必须调用 .compile() 将其编译为一个可执行的 LangChain Runnable 对象。
    graph = graph.compile()
    # 启动图的运行。输入初始状态，这里传入了一条用户的初始消息："hi!"
    response = graph.invoke({"messages": [HumanMessage(content="hi!")]})
    print(response)
    ai_message_text = response["messages"][-1].content
    print(ai_message_text)

    '''
    执行流程：输入的 {"messages": [HumanMessage(content="hi!")]} 成为图的初始状态。流程从 START 流向 mock_llm 节点。mock_llm 执行，返回 {"messages": [{"role": "ai", "content": "hello world"}]}。LangGraph 自动将新消息追加（而不是覆盖）到 MessagesState 的消息列表中。流程走向 END。
    '''
except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))