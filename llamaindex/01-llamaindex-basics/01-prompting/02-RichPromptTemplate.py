"""
Jinja 提示和 f 字符串之间的主要区别在于变量现在有双括号{{ }}而不是单括号{ }
"""

from llama_index.core.prompts import RichPromptTemplate

template = RichPromptTemplate(
    """
{% chat role="system" %}
你是多模态文档分析助手，需要结合图片内容和文本描述回答用户问题。
核心规则：
1. 优先基于图片对应的文本描述分析信息；
2. 若图片路径包含"合同"关键词，重点关注文本中的金额、日期信息；
3. 回答需简洁明了，分点说明关键信息。
{% endchat %}

{% chat role="user" %}
请分析以下图片和对应的文本信息，总结每份文件的核心内容：
{% for img_path, text_content in multi_modal_data %}
- 文件路径：{{ img_path }}
- 文本描述：{{ text_content }}
- 图片内容：{{ img_path | image }}
{% endfor %}

我的问题：这些文件中是否包含合同类文件？如果有，核心信息是什么？
{% endchat %}
"""
)

messages = template.format_messages(
    multi_modal_data=[
        ("data/contract_202403.png", "2024年3月采购合同：甲方为XX科技，乙方为YY制造，合同金额50万元，有效期1年"),
        ("data/contract_202403.png", "2024年Q1销售报告：总销售额1200万元，同比增长15%，覆盖3个省份"),
        ("data/invoice_202404.png", "2024年4月发票：金额8.5万元，对应项目为服务器采购")
    ]
)

print("=== 格式化后的多模态聊天消息列表 ===")
for idx, msg in enumerate(messages):
    print(f"\n【消息{idx + 1}】")
    print(f"角色：{msg.role}")
    if isinstance(msg.content, str):
        print(f"内容：{msg.content.strip()}")
    for block in msg.blocks:
        block_type = getattr(block, "block_type", type(block).__name__)
        if block_type == "text":
            text = getattr(block, "text", "").strip()
            if text:
                print(f"[文本块]：{text}")
        elif block_type == "image":
            url = str(getattr(block, "url", ""))
            mime, data = url.split(",", 1) if "," in url else (url, "")
            print(f"[图片块]：{mime}, base64={data[:40]}...")



#  该{% chat %}块用于将消息格式化为聊天消息并设置角色
#  循环{% for %}用于迭代multi_modal_data传入的列表
#  该{{ image_path | image }}语法用于将图像路径格式化为图像内容块。此处，|用于对变量应用“过滤器”，以帮助将其识别为图像。