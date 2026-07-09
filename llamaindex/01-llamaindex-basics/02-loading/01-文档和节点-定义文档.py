from llama_index.core import SimpleDirectoryReader

# 文档可以通过数据加载器自动创建， 也可以手动构建。
# 默认情况下，我们所有的数据加载器（包括 LlamaHub 上提供的加载器）都通过该load_data函数返回对象。
# documents = SimpleDirectoryReader("../data").load_data()
# print(documents)


# 手动构建文档
from llama_index.core import Document
from llama_index.core import SimpleDirectoryReader
from pathlib import Path

text_list = ["text1", "text2"]
# 创建文档对象，并添加元数据
documents = [Document(text=t, metadata={"filename": "文件名称", "category": "类别"}) for t in text_list]
print(documents)


# 自动设置元数据
def filename_fn(filename: str):
    return {
        "file_name": filename,
        "category": Path(filename).suffix,
    }


documents = SimpleDirectoryReader(input_dir="../data", file_metadata=filename_fn).load_data()
print(documents)