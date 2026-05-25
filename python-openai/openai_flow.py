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

# print(f"API_KEY: {API_KEY}, BASE_URL: {BASE_URL}")
# exit()

def get_response():
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': '你是谁？'}],
            stream=True,
            temperature=0.1,
            stream_options={"include_usage": True}
            )
        for chunk in completion:
            # chunk 里可能没有 choices 或 delta
            if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                choice = chunk.choices[0]
                if hasattr(choice, "delta") and hasattr(choice.delta, "content"):
                    print(choice.delta.content, end='', flush=True)
    except APIConnectionError as e:
        print(f"网络连接错误，请检查代理或网络: {e}")
    except RateLimitError as e:
        print(f"触发速率限制或余额不足: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == '__main__':
    get_response()