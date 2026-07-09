"""
根据文档id去删除文档
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
# 删除
index.delete_ref_doc("doc_id_0", delete_from_docstore=True)
print(index.docstore.docs)