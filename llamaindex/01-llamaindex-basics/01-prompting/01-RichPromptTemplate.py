"""
通过利用 Jinja 语法，可以构建包含变量、逻辑、解析对象等的提示模板。
"""

from llama_index.core.prompts import RichPromptTemplate

context_str = """
【企业基础信息】
公司全称：杭州深度求索人工智能基础技术研究有限公司
成立时间：2023年7月17日（工商注册日期）
核心技术：数据蒸馏技术（用于优化大语言模型训练数据）
股东背景：由幻方量化（知名私募机构）孵化
注册地址：浙江省杭州市拱墅区环城北路169号汇金国际大厦西1幢1201室
法定代表人：裴湉
核心业务：大语言模型（LLM）研发、技术服务、软件开发、技术转让

【补充说明】
1. 公司成立后6个月内完成首轮融资，估值超10亿人民币；
2. 数据蒸馏技术为公司核心专利，已应用于多款自研大模型。
"""


question = 'DeepSeek公司的工商注册成立年份是哪一年？请仅给出数字答案'

template = RichPromptTemplate(
    """
# 任务说明
你是企业信息问答助手，需严格基于提供的上下文信息回答问题，不得编造内容。

# 上下文信息
---------------------
{{ context_str }}
---------------------

# 待回答问题
{{ query_str }}

# 回答要求
1. 严格按照问题要求的格式回答；
2. 仅使用上下文里的信息，不添加额外解释；
3. 若上下文无相关信息，回复："未查询到相关信息"。
    """
)

# 格式化为纯字符串（适用于非聊天型大模型/API）
prompt_str = template.format(context_str=context_str, query_str=question)
print("============================== 格式化后的纯字符串Prompt ==============================")
print(prompt_str)

# 格式化聊天消息列表（适用于ChatGPT/文心一言等聊天型大模型）
messages = template.format_messages(context_str=context_str, query_str=question)
print("\n============================== 格式化后的聊天消息列表 ==============================")
# 优化点4：美化输出格式，清晰展示消息结构
for msg in messages:
    print(f"角色：{msg.role}")
    print(f"内容：{msg.content}\n")