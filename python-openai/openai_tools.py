from openai import OpenAI,APIConnectionError, RateLimitError
import json
from dotenv import load_dotenv
import os
from typing import Union,cast
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam,ChatCompletionMessageToolCall


# 加载环境变量
load_dotenv()

# 从环境变量中获取配置，避免硬编码泄露
# 也可以直接在这里赋值，但绝不推荐上传到代码仓库
API_KEY = os.getenv("OPENAI_API_KEY", None)
BASE_URL = os.getenv("OPENAI_BASE_URL",None)
MODEL = os.getenv("MODEL",None)

# 2. 定义一个本地的实际工具函数
def get_current_weather(location, unit="celsius"):
    """模拟在本地数据库或第三方API查询天气的函数"""
    if "北京" in location:
        return json.dumps({"location": "北京", "temperature": "22", "unit": unit, "condition": "晴朗"})
    elif "东京" in location:
        return json.dumps({"location": "东京", "temperature": "18", "unit": unit, "condition": "下雨"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

def main():
    MODEL: Union[str, None] = os.getenv("MODEL", None)
    assert MODEL is not None, "MODEL 不能为 None，必须为 Union[ChatModel, str] 中的合法值"

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        # 3. 让大模型知晓这个工具的“描述信息”
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "获取指定城市的实时天气数据",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "城市名称，例如：北京、东京"},
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        },
                        "required": ["location"],
                    },
                },
            }
        ]

        # 4. 第一次调用大模型：提出一个需要实时信息的问题
        messages = [{"role": "user", "content": "请问现在北京的天气怎么样？"}]

        response = client.chat.completions.create(
            model=MODEL,  # 或使用 gpt-3.5-turbo 等支持 tool 的模型
            messages=cast(list[ChatCompletionMessageParam], messages),
            tools=cast(list[ChatCompletionToolParam], tools),
            tool_choice="auto"  # 让模型自主决定是否调函数
        )

        response_message  = response.choices[0].message
        tool_calls = response_message.tool_calls

        # 5. 检查大模型是否触发了 Function Calling
        if tool_calls:
            print("【模型决策】需要调用外部工具！")
            
            # 模拟在本地执行函数的过程
            available_functions = {"get_current_weather": get_current_weather}
            
            # 将模型的回复加入对话历史（必须）
            messages.append(response_message.model_dump())
            
            for tool_call in tool_calls:
                # if tool_call.type != "function":
                #     continue
                standard_call = cast(ChatCompletionMessageToolCall, tool_call)
                function_name = standard_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(ChatCompletionMessageToolCall.function.arguments)
                
                # 本地真正执行函数
                print(f"【本地执行】调用函数 {function_name}，参数为: {function_args}")
                function_response = function_to_call(
                    location=function_args.get("location"),
                    unit=function_args.get("unit", "celsius"),
                )
                
                # 6. 将函数执行结果拼回 messages 传给模型
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })
            
            # 7. 第二次调用大模型：让模型根据函数结果组织语言
            second_response = client.chat.completions.create(
                model="gpt-4o",
                messages=cast(list[ChatCompletionMessageParam], messages),
            )
            print("【最终回复】:", second_response.choices[0].message.content)
        else:
            print("【最终回复】:", response_message.content)
    except APIConnectionError as e:
        print(f"网络连接错误，请检查代理或网络: {e}")
    except RateLimitError as e:
        print(f"触发速率限制或余额不足: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == '__main__':
    main()