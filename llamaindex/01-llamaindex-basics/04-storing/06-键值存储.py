from llama_config import get_llm
llm, embed_model = get_llm()

from llama_index.core.storage.kvstore import SimpleKVStore

# 准备一些示例文档数据
documents = {
    "doc_1": {
        "content": "Python是一种高级编程语言，以其简洁的语法和强大的功能而闻名。",
        "source": "python_intro.txt",
        "category": "programming",
        "author": "张三"
    },
    "doc_2": {
        "content": "机器学习是人工智能的一个重要分支，通过算法让计算机从数据中学习。",
        "source": "ml_basics.txt",
        "category": "AI",
        "author": "李四"
    },
    "doc_3": {
        "content": "数据科学结合了统计学、计算机科学和领域专业知识来从数据中提取洞察。",
        "source": "data_science.txt",
        "category": "data",
        "author": "王五"
    }
}
# 初始化 SimpleKVStore
kvstore = SimpleKVStore()  # 实际上是 dict 封装
# 将数据手动存入SimpleKVStore
for doc_id, doc in documents.items():
    kvstore.put(doc_id, doc)
# 本地化持久保存
kvstore.persist("./KV_data")

# 从本地加载数据
new_kv_store = SimpleKVStore.from_persist_path("./KV_data")
# 获取所有数据
print(new_kv_store.get_all())