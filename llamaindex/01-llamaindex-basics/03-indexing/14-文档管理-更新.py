"""
根据文档id去更新文档（先删除对应id的文档，再去新增一个文档）
"""

from llama_index.core import SummaryIndex, Document

index = SummaryIndex([])
text_chunks = ["文档1", "文档2", "文档3"]

doc_chunks = []
for i, text in enumerate(text_chunks):
    doc = Document(text=text, id_=f"doc_id_{i}")
    doc_chunks.append(doc)

# 插入
for doc_chunk in doc_chunks:
    index.insert(doc_chunk)

print("更新前", index.docstore.docs)

# 更新
update_doc = Document(text="这是文档1", id_="doc_id_0")
index.update_ref_doc(update_doc)
print("更新后", index.docstore.docs)