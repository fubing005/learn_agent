import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain.agents import create_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
import asyncio
from langchain_core.runnables import RunnableConfig

load_dotenv()


required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")


async def stream_event(agent_executor):
    # global agent_executor

    # 流式令牌
    async for event in agent_executor.astream_events(
        {"messages": [HumanMessage(content="whats the weather in beijing?")]}, version="v1"
    ):
        kind = event["event"]
        print(kind)

        if kind == "on_chain_start":
            if (
                event["name"] == "Agent"
            ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                print(
                    f"Starting agent: {event['name']} with input: {event['data'].get('input')}"
                )
        elif kind == "on_chain_end":
            if (
                event["name"] == "Agent"
            ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                print()
                print("--")

                output_data = event['data'].get('output') or {}
                agent_output = output_data.get('output', '无输出内容')
                print(
                    f"Done agent: {event['name']} with output: {agent_output}"
                )
        if kind == "on_chat_model_stream":
            chunk = event["data"].get("chunk")
            if chunk and hasattr(chunk, 'content'):
                content = chunk.content
                if content:
                    # Empty content in the context of OpenAI means
                    # that the model is asking for a tool to be invoked.
                    # So we only print non-empty content
                    print(content, end="|")
        elif kind == "on_tool_start":
            print("--")
            print(
                f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
            )
        elif kind == "on_tool_end":
            print(f"Done tool: {event['name']}")
            print(f"Tool output was: {event['data'].get('output')}")
            print("--")

try:
    model = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )

    search = TavilySearchResults(max_results=2)
    tools = [search]

    # agent_executor = create_agent(model, tools)

    # 未调用工具
    # response = agent_executor.invoke({"messages": [HumanMessage(content="hi!")]})
    # print(response["messages"])

    # 调用工具
    # response = agent_executor.invoke(
    #     {"messages": [HumanMessage(content="whats the weather in beijing?")]}
    # )
    # print(response["messages"])

    # 流式消息
    # for chunk in agent_executor.stream(
    #     {"messages": [HumanMessage(content="whats the weather in sf?")]}
    # ):
    #     print(chunk)
    #     print("----")

    # 流式令牌
    # asyncio.run(stream_event(agent_executor))
    # 如果在 Jupyter Notebook 中，由于环境特殊，直接执行：
    # await stream_event()

    # 添加内存
    memory = MemorySaver()
    agent_executor = create_agent(model, tools, checkpointer=memory)
    config: RunnableConfig = {"configurable": {"thread_id": "abc123"}}

    for chunk in agent_executor.stream(
        {"messages": [HumanMessage(content="hi im bob!")]}, config
    ):
        print(chunk)
        print("----")
    
    for chunk in agent_executor.stream(
        {"messages": [HumanMessage(content="whats my name?")]}, config
    ):
        print(chunk)
        print("----")

    config = {"configurable": {"thread_id": "xyz123"}}
    for chunk in agent_executor.stream(
        {"messages": [HumanMessage(content="whats my name?")]}, config
    ):
        print(chunk)
        print("----")

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))