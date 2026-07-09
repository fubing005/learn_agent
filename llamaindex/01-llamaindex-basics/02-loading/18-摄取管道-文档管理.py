from llama_config import init_settings, get_llm
init_settings()
import os
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.node_parser import SentenceSplitter

llm, embed_model = get_llm()

# 配置
STORAGE_DIR = "pipeline_storage"
DATA_DIR = "data1"

# 自动创建文件夹，防止报错
os.makedirs(DATA_DIR, exist_ok=True)

def run_incremental_ingestion(data_path, storage_path):
    # 永远先创建一个新的空 docstore
    docstore = SimpleDocumentStore()

    # 如果目录存在 + 里面有文件，才尝试加载
    if os.path.exists(storage_path):
        try:
            # 只有文件存在才加载
            if os.path.exists(os.path.join(storage_path, "docstore.json")):
                docstore = SimpleDocumentStore.from_persist_dir(storage_path)
                print("--- 加载已存在的文档存储成功 ---")
            else:
                print("--- 目录为空，使用全新存储 ---")
        except Exception as e:
            print("--- 加载失败，使用全新文档存储 ---")

    # 构建管道
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=512, chunk_overlap=20),
            embed_model,
        ],
        docstore=docstore,
        docstore_strategy="upserts",
    )

    # 读取文件
    documents = SimpleDirectoryReader(data_path, filename_as_id=True).load_data()

    # 运行
    nodes = pipeline.run(documents=documents, show_progress=True)

    # 持久化（一定会生成 docstore.json）
    pipeline.persist(storage_path)

    return nodes


# --- 运行 ---
print("\n[第一轮运行]")
nodes1 = run_incremental_ingestion(DATA_DIR, STORAGE_DIR)
print(f"实际新增/更新节点数: {len(nodes1)}")

# 新增测试文件
with open(f"{DATA_DIR}/t4.txt", "w", encoding="utf-8") as f:
    f.write("这是测试文件4 —— 新增内容")

print("\n[第二轮运行]")
nodes2 = run_incremental_ingestion(DATA_DIR, STORAGE_DIR)
print(f"实际新增/更新节点数: {len(nodes2)}")