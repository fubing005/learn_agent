# from llama_index.core import PromptTemplate
#
# context_str = """
#     DeepSeek，全称杭州深度求索人工智能基础技术研究有限公司 [40]。DeepSeek是一家创新型科技公司 [3]，成立于2023年7月17日 [40]，使用数据蒸馏技术 [41]，得到更为精练、有用的数据 [41]。
#     由知名私募巨头幻方量化孕育而生 [3]，专注于开发先进的大语言模型（LLM）和相关技术 [40]。注册地址 [6]：浙江省杭州市拱墅区环城北路169号汇金国际大厦西1幢1201室 [6]。法定代表人为裴湉 [6]，
#     经营范围包括技术服务、技术开发、软件开发等 [6]。
# """
# question = 'deepseek成立于哪一年？'
# template = (
#     "我们在下面提供了上下文信息"
#     "---------------------"
#     "{context_str}"
#     " ---------------------"
#     " 请根据上下文，回答问题: {query_str}"
# )
# qa_template = PromptTemplate(template)
#
# print("============================== 格式化后的纯字符串Prompt ==============================")
# # 将提示格式设置为字符串
# prompt = qa_template.format(context_str=context_str, query_str=question)
# print(prompt)
# print("\n============================== 格式化后的聊天消息列表 ==============================")
# # 将提示格式设置为聊天消息列表。
# messages = qa_template.format_messages(context_str=context_str, query_str=question)
# print(messages)


from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import ChatMessage, MessageRole
# 从聊天消息中定义模板
message_templates = [
    ChatMessage(content="你是一个智能助手.", role=MessageRole.SYSTEM),
    ChatMessage(
        content="帮我生成一个关于{topic}的故事",
        role=MessageRole.USER,
    ),
]
chat_template = ChatPromptTemplate(message_templates=message_templates)

# 格式化为聊天消息列表
messages = chat_template.format_messages(topic="狮子")
print("============================== 格式化后的聊天消息列表 ==============================")
print(messages)
# 格式化为字符串
print("\n============================== 格式化后的纯字符串Prompt ==============================")
prompt = chat_template.format(topic="老虎")
print(prompt)