
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
import getpass

# 1. 核心步骤：加载 .env 文件到系统环境变量
load_dotenv()

# 激活 LangChain 官方的“可视化调试与监控服务”（称为 LangSmith），并安全地输入你的服务秘钥
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()

# 2. 验证所有变量是否成功加载（包含模型名称）
required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

try:
    # 3. 实例化模型（传入确定的字符串变量）
    model = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )
    # 4. 准备对话消息
    system_prompt = "Translate the following into {language}:"
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("user", "{text}")]
    )

    # 5. 实例化输出解析器
    parser = StrOutputParser()

    # 6. 使用官方推荐的 LCEL (管道符) 组合成一条链，更加优雅
    # LECL 有顺序要求
    # 这是一个使用 LangChain 表达式 (LCEL) 连接 LangChain 模块的简单示例。这种方法有几个好处，包括优化的流式处理和追踪支持。
    chain = prompt_template  | model | parser

    # 7.打印结果
    response_text = chain.invoke({"language": "chinese", "text": "hi"})
    print(response_text)

    # 或者
    # result = prompt_template.invoke({"language": "chinese", "text": "hi"})
    # result = model.invoke(result.to_messages())
    # response_text = parser.invoke(result)
    # print(response_text)
except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))

