import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

def step1_node(state: MessagesState):
    print("------ [子图] 步骤 1: 调用 LLM 生成回复 (step1) ---")
    # 直接调用 LLM 处理当前所有的对话历史
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def step2_node(state: MessagesState):
    print("------ [子图] 步骤 2: 情感或格式分析 (step2) ---")
    # 获取上一步 LLM 的回复
    last_message = state["messages"][-1].content
    analysis = f"[分析结果: 此消息长度为 {len(last_message)} 个字符]"
    return {"messages": [AIMessage(content=analysis)]}

def preprocess_node(state: MessagesState):
    print("\n--- [主图] 步骤: 预处理 (preprocessing) ---")
    # 在消息流中加入一条系统提示
    return {"messages": [AIMessage(content="[预处理系统] 开始处理用户请求...")]}

def postprocess_node(state: MessagesState):
    print("--- [主图] 步骤: 后处理 (postprocessing) ---\n")
    # 最终的收尾工作
    return {"messages": [AIMessage(content="[后处理系统] 流程全部结束。")]}

def main():
    # 初始化输入状态，传入用户的提问
    initial_state: MessagesState = {
        "messages": [HumanMessage(content="你好，请用一句话介绍什么是量子计算。")]
    }
    
    # print("🚀 启动主图流式运行:")
    # # 使用 stream 方式运行，可以观察到每个节点的输出变化
    # for event in main_graph.stream(initial_state):
    #     for node_name, output in event.items():
    #         print(f"节点 [{node_name}] 执行完毕，产生了新消息。")
    #         print(f"输出 {output['messages'][-1].content}")
    '''
🚀 启动主图流式运行:

--- [主图] 步骤: 预处理 (preprocessing) ---
节点 [preprocessing] 执行完毕，产生了新消息。
输出 [预处理系统] 开始处理用户请求...
------ [子图] 步骤 1: 调用 LLM 生成回复 (step1) ---
------ [子图] 步骤 2: 情感或格式分析 (step2) ---
节点 [sub_workflow] 执行完毕，产生了新消息。
输出 [分析结果: 此消息长度为 54 个字符]
--- [主图] 步骤: 后处理 (postprocessing) ---

节点 [postprocessing] 执行完毕，产生了新消息。
输出 [后处理系统] 流程全部结束。    
    '''
#-----------------------------------------------------------------

    # 最后打印出完整的消息流结果
    print("\n================ 最终对话流历史 ================")
    config: RunnableConfig = {"configurable": {"thread_id": "test-session-1"}}

    print("🚀 开始流式运行工作流:")
    # 运行时必须传入 config
    for event in main_graph.stream(initial_state, config=config):
        for node_name, output in event.items():
            print(f"✅ 节点 [{node_name}] 执行完毕")

    # 传入相同的 config 获取状态
    final_state = main_graph.get_state(config=config)
     # 从状态中提取出合并后的所有消息
    all_messages = final_state.values.get("messages", [])
    # 循环遍历并打印每条消息的角色和具体内容
    for idx, msg in enumerate(all_messages, start=1):
        # 根据消息类型判断角色名称
        role = "User" if isinstance(msg, HumanMessage) else "AI"
        print(f"[{idx}] {role}: {msg.content}")
    
    print("==================================================")
'''
================ 最终对话流历史 ================
🚀 开始流式运行工作流:

--- [主图] 步骤: 预处理 (preprocessing) ---
✅ 节点 [preprocessing] 执行完毕
------ [子图] 步骤 1: 调用 LLM 生成回复 (step1) ---
------ [子图] 步骤 2: 情感或格式分析 (step2) ---
✅ 节点 [sub_workflow] 执行完毕
--- [主图] 步骤: 后处理 (postprocessing) ---

✅ 节点 [postprocessing] 执行完毕
[1] User: 你好，请用一句话介绍什么是量子计算。
[2] AI: [预处理系统] 开始处理用户请求...
[3] AI: 量子计算是一种利用量子位（qubits）进行信息处理的计算方式，能够在某些特定问题上比经典计算机更快地解决复杂计算。
[4] AI: [分析结果: 此消息长度为 58 个字符]
[5] AI: [后处理系统] 流程全部结束。
==================================================
'''


try:
    llm = ChatOpenAI(model=os.getenv("LLM_MODEL", "gpt-4o-mini"), temperature=0)

    # 将复杂子流程封装为子图，在主图中复用
    sub_builder = StateGraph(MessagesState)
    sub_builder.add_node("step1", step1_node)
    sub_builder.add_node("step2", step2_node)

    sub_builder.add_edge(START, "step1")
    sub_builder.add_edge("step1", "step2")
    sub_builder.add_edge("step2", END)
    sub_graph = sub_builder.compile()

    # 在主图中使用子图
    main_builder = StateGraph(MessagesState)
    main_builder.add_node("preprocessing", preprocess_node)
    main_builder.add_node("sub_workflow", sub_graph)  # 直接使用编译好的子图
    main_builder.add_node("postprocessing", postprocess_node)

    main_builder.add_edge(START, "preprocessing")
    main_builder.add_edge("preprocessing", "sub_workflow")
    main_builder.add_edge("sub_workflow", "postprocessing")
    main_builder.add_edge("postprocessing", END)
    # main_graph = main_builder.compile() 

    memory = MemorySaver()
    main_graph = main_builder.compile(checkpointer=memory)

    # 执行程序
    main()

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))