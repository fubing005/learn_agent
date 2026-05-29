import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
# import getpass

load_dotenv()

# 激活 LangChain 官方的“可视化调试与监控服务”（称为 LangSmith），并安全地输入你的服务秘钥
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

try:
    search = TavilySearchResults(max_results=2)
    search_results = search.invoke("what is the weather in SF")
    tools = [search]

    model = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )

    # 不绑定工具
    response = model.invoke([HumanMessage(content="hi!")])
    print(response.content)

    # 绑定工具
    # model_with_tools = model.bind_tools(tools)

    # response = model_with_tools.invoke([HumanMessage(content="Hi!")])
    # print(f"ContentString: {response.content}")
    # print(f"ToolCalls: {response.tool_calls}")
    # '''
    # ContentString: Hello! How can I assist you today?
    # ToolCalls: []
    # '''
    
    # response = model_with_tools.invoke([HumanMessage(content="What's the weather in SF?")])
    # print(f"ContentString: {response.content}")
    # print(f"ToolCalls: {response.tool_calls}")
    # '''
    # ContentString: 
    # ToolCalls: [{'name': 'tavily_get_research', 'args': {'request_id': 'weather_SF'}, 'id': 'call_5LVmiguT6zPqZWQDsXrES1mO', 'type': 'tool_call'}]
    # '''

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))