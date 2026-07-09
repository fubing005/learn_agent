from llama_config import get_llm
llm, embed_model = get_llm()

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.storage.index_store.redis import RedisIndexStore
from llama_index.storage.docstore.redis import RedisDocumentStore
from llama_index.vector_stores.redis import RedisVectorStore
from llama_index.core import VectorStoreIndex
from redisvl.schema import IndexSchema


# print("-------------------先测试向量维度，redis配置的向量存储规则中的向量维度和嵌入模型的维度得一致----------------------")
# test_text = "测试"
# embedding = embed_model.get_text_embedding(test_text)
# print(f"向量维度: {len(embedding)}")  # 这就是 dims 的值

# 设置向量存储的规则
custom_schema = IndexSchema.from_dict(
    {
        "index": {"name": "redis_vector_store", "prefix": "doc"},
        # 自定义被索引的字段
        "fields": [
            # llamaIndex的必填字段
            {"type": "tag", "name": "id"},
            {"type": "tag", "name": "doc_id"},
            {"type": "text", "name": "text"},
            {
                "type": "vector",
                "name": "vector",
                "attrs": {
                    "dims": 512,  # 向量维度
                    "algorithm": "hnsw",  # 算法
                    "distance_metric": "cosine",  # 相似度计算：余弦
                },
            },
        ],
    }
)


def create_and_store_index():
    """创建并存储索引的完整流程"""

    # 重新加载文档（确保数据新鲜）
    documents = SimpleDirectoryReader(input_files=["data/小说.txt"]).load_data()
    nodes = SentenceSplitter().get_nodes_from_documents(documents)

    # 创建存储组件
    storage_context = StorageContext.from_defaults(
        index_store=RedisIndexStore.from_host_and_port(
            host="127.0.0.1", port=6379, namespace="novel_index"
        ),
        docstore=RedisDocumentStore.from_host_and_port(
            host="127.0.0.1", port=6379, namespace="novel_docs"
        ),
        vector_store=RedisVectorStore(
            schema=custom_schema,
            redis_url="redis://127.0.0.1:6379",
        )
    )

    # 创建索引
    index = VectorStoreIndex(nodes, storage_context=storage_context)
    print(f"✅ 索引创建并存储完成，ID: {index.index_id}")
    # 测试查询
    print(index.as_retriever(similarity_top_k=5).retrieve("小说中古河是个什么样的人？"))
    response = index.as_query_engine().query("小说中古河是个什么样的人？")
    print(f"✅ 加载成功！查询结果: {response}")

    return index.index_id


def load_and_query_index(index_id=None):
    """加载并查询索引"""

    # 创建相同配置的存储上下文
    storage_context = StorageContext.from_defaults(
        index_store=RedisIndexStore.from_host_and_port(
            host="127.0.0.1", port=6379, namespace="novel_index"
        ),
        docstore=RedisDocumentStore.from_host_and_port(
            host="127.0.0.1", port=6379, namespace="novel_docs"
        ),
        vector_store=RedisVectorStore(
            schema=custom_schema,
            redis_url="redis://127.0.0.1:6379"
        )
    )

    try:
        # 加载索引
        if index_id:
            loaded_index = load_index_from_storage(storage_context, index_id=index_id)
        else:
            loaded_index = load_index_from_storage(storage_context)

        # 测试查询
        response = loaded_index.as_query_engine().query("是谁要被退婚？")
        print(f"✅ 加载成功！查询结果: {response}")

        return loaded_index

    except Exception as e:
        print(f"❌ 加载失败: {e}")
        return None


# 1. 创建和存储
stored_index_id = create_and_store_index()

# 2. 加载和查询
loaded_index = load_and_query_index(stored_index_id)

if loaded_index:
    print("🎉 完整流程成功！")
else:
    print("❌ 流程失败")