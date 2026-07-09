from llama_index.readers.json import JSONReader
from llama_index.core.node_parser import JSONNodeParser, SentenceSplitter

reader = JSONReader()

documents = reader.load_data(input_file="data/request.json")
print(documents)
# 如果想使用JSONNodeParser，需要设置 JSONReader(clean_json=False)
# print(JSONNodeParser().get_nodes_from_documents(documents))
s = SentenceSplitter(chunk_size=10, chunk_overlap=5)
print(s.get_nodes_from_documents(documents))