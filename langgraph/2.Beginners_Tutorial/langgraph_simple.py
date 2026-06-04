
import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Optional,Union, List, Dict, Any
from typing_extensions import TypedDict, NotRequired
# # 在 Jupyter Notebook 中可视化
# from IPython.core.display import Image
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
from langchain_core.messages.system import SystemMessage
from langchain_core.messages.human import HumanMessage
import asyncio


load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

class SimpleState(TypedDict):
    messages: str
    processed: bool

def greet_node(state: SimpleState) -> dict:
    """欢迎节点：生成问候语"""
    # print(f"[greet_node] 收到消息: {state['messages']}")
    return {"messages": f"你好！{state['messages']}"}

def process_node(state: SimpleState) -> dict:
    """处理节点：标记为已处理"""
    print(f"[process_node] 处理消息: {state['messages']}")
    return {"processed": True}

# 使用 TypedDict 定义状态
class AgentState(TypedDict):
    # 消息历史（add_messages reducer 自动追加而非覆盖）
    messages: Annotated[list, add_messages]
    
    # 普通字段（直接覆盖）
    user_id: NotRequired[str] #str
    session_id: NotRequired[str] #str
    
    # 可选字段
    error: NotRequired[Optional[str]]
    
    # 计数器（使用 operator.add 作为 reducer）
    retry_count: NotRequired[Annotated[int, lambda x, y: x + y]]

def simple_node(state: AgentState) -> dict:
    # 读取状态
    last_message = state["messages"][-1]
    
    # 执行操作
    response = f"收到: {last_message.content}"
    
    # 返回部分状态更新
    return {
        "messages": [{"role": "assistant", "content": response}]
    }

# 使用 Pydantic 定义状态（推荐用于生产）
class ProductionState(BaseModel):
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    user_id: str = ""
    confidence_score: float = 0.0
    
    class Config:
        arbitrary_types_allowed = True

# LangGraph 提供了内置的 MessagesState，专为对话场景设计
# 直接使用，无需自定义
# builder = StateGraph(MessagesState)

def llm_node(state: dict, llm: ChatOpenAI) -> Union[dict, str, List[Any], Dict[Any, Any]]:   #Dict
    """调用 LLM 的节点"""
    system_prompt = SystemMessage(content="你是一个有帮助的助手。")
   
    # 将系统提示与对话历史合并
    messages = [system_prompt] + state["messages"]
   
    # 调用 LLM
    response = llm.invoke(messages)
    return response.content
    # return {"messages": [response]}

# 3. 模拟一个外部的异步 I/O API 调用
async def some_async_api_call(user_input: str) -> str:
    # 模拟网络延迟 0.5 秒
    await asyncio.sleep(0.5)
    return f"【已处理】您刚才说的是：'{user_input}'"

# 异步节点
async def async_node(state: AgentState) -> dict:
    """异步节点，适合 I/O 密集型操作"""
    # 模拟一些内部节点的异步预处理
    await asyncio.sleep(0.1)
    
    # 获取最后一条消息的内容
    last_message_content = state["messages"][-1].content
    
    # 调用异步 API
    result = await some_async_api_call(last_message_content)
    
    # 返回符合 MessagesState/AgentState 结构的增量字典
    return {"messages": [{"role": "assistant", "content": result}]}

async def run_async_node(builder_agent):
    print("--- 正在异步调用图 (ainvoke) ---")

    # # 添加节点
    builder_agent.add_node("greet", greet_node)
    builder_agent.add_node("process", process_node)

    # 添加边
    builder_agent.add_edge(START, "greet")
    builder_agent.add_edge("greet", "process")
    builder_agent.add_edge("process", END)

    # Step 4: 编译图
    graph_agent = builder_agent.compile()

    # 构造初始输入状态
    initial_input: AgentState = {
        "messages": [{"role": "user", "content": "今天天气怎么样？"}]
    }
    
    # 🌟 使用 ainvoke 执行异步图，并使用 await 挂起等待结果
    result = await graph_agent.ainvoke(initial_input)
    
    print("\n--- 执行完毕，最终图状态返回 ---")
    print(result)
    
    print("\n--- 提取最新的一条 AI 回复 ---")
    print(result["messages"][-1].content)

# 使用类作为节点
'''
如果在真实的工业级项目里，你有 3 个不同的 Agent 节点（例如：A 分流器、B 业务专家、C 夸夸助手），它们都要调用大模型，只是提示词不同。传统函数写法：你需要复制粘贴写 3 个长得几乎一模一样的 def node_a、def node_b、def node_c 函数，代码极其冗余。类节点写法（面向对象）：你只需要写这一个 RouterNode 类，然后直接复用它创建 3 个不同的节点实例：
'''
class RouterNode:
    def __init__(self, llm, system_prompt: str):
        self.llm = llm
        self.system_prompt = system_prompt
    
    def __call__(self, state: AgentState) -> dict:
        """类实例可以作为节点使用"""
        messages = [
            SystemMessage(content=self.system_prompt),
            *state["messages"]
        ]
        response = self.llm.invoke(messages)
        return {"messages": [response]}

# 条件边是 LangGraph 的核心功能，根据当前 State 动态决定下一步。
def route_after_llm(state: AgentState) -> str:
    """
    路由函数：根据 LLM 的最新输出决定走哪条路径
    返回值必须是已注册节点名称或 END
    """
    last_message = state["messages"][-1]
    
    # 如果 LLM 请求使用工具
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # 否则结束
    return END

try:
    model = ChatOpenAI(model=os.getenv("LLM_MODEL","gpt-4o-mini"),temperature=0)

    builder_simple = StateGraph(SimpleState)
    builder_agent = StateGraph(AgentState)

    # # 添加节点
    # builder_simple.add_node("greet", greet_node)
    # builder_simple.add_node("process", process_node)

    # # 添加边
    # builder_simple.add_edge(START, "greet")
    # builder_simple.add_edge("greet", "process")
    # builder_simple.add_edge("process", END)

    # # Step 4: 编译图
    # graph_simple = builder_simple.compile()

    # # Step 5: 运行
    # result = graph_simple.invoke({"messages": "世界","processed": False})
    # print(f"\n最终结果: {result}")

    # # 在 Jupyter Notebook 中可视化
    # Image(graph_simple.get_graph().draw_mermaid_png())
    # # 或者打印 Mermaid 格式
    # print(graph_simple.get_graph().draw_mermaid())

# -----------------------LLM 调用节点------------------------------

    # state = {
    #     "messages": [
    #         HumanMessage(content="你好，请问人工智能是什么？")
    #     ]
    # }
    # response = llm_node(state, model)
    # print(response)

# ----------------------------异步节点--------------------------------

    # # 使用异步图
    # asyncio.run(run_async_node(builder_agent))

# ----------------------------使用类作为节点--------------------------

    # # 添加类节点
    # router = RouterNode(model, "你是一个专业的路由助手。")
    # builder_agent.add_node("router", router)

#-------------------------------Edges 边与条件路由----------------------

    # print(route_after_llm.__doc__)

    builder_agent.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "tools": "tool_executor",   # 返回 "tools" 时 -> tool_executor 节点
            END: END                    # 返回 END 时 -> 结束
        }
    )
   

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))