from openai import OpenAI,APIConnectionError, RateLimitError
import json
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 从环境变量中获取配置，避免硬编码泄露
# 也可以直接在这里赋值，但绝不推荐上传到代码仓库
API_KEY = os.getenv("OPENAI_API_KEY", None)
BASE_URL = os.getenv("OPENAI_BASE_URL",None)
MODEL = os.getenv("MODEL",None)

# print(f"API_KEY: {API_KEY}, BASE_URL: {BASE_URL}")
# exit()

def get_response():
    if MODEL is None:
        raise ValueError("环境变量 MODEL 未设置，请在 .env 文件中配置有效的模型名称。")
    
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': '你是谁？'}]
            )
        # 打印完整的 JSON 响应数据
        print(completion.model_dump_json())
        print("-------------------------------")

        # 提取并打印模型回复内容
        assistant_reply = completion.choices[0].message.content
        print(assistant_reply)
        print("-------------------------------")

        # 打印 Token 消耗情况
        if completion.usage is not None:
            print(f"本次消耗 Token: Prompt={completion.usage.prompt_tokens}, Completion={completion.usage.completion_tokens}")
        else:
            print("本次消耗 Token: 未获取到用量数据")
    except APIConnectionError as e:
        print(f"网络连接错误，请检查代理或网络: {e}")
    except RateLimitError as e:
        print(f"触发速率限制或余额不足: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == '__main__':
    get_response()