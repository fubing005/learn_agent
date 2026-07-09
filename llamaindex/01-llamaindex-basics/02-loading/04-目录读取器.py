from llama_index.core import SimpleDirectoryReader


#=======================================================================
# 最简单就是传递一个目录，SimpleDirectoryReader会读取目录下所有支持的文件

from llama_index.core import SimpleDirectoryReader

def main():
    # 使用目录加载器读取文件（PDF文件会按照页面进行分割）,如果要读取子目录下的文件需设置recursive=True
    # reader = SimpleDirectoryReader(input_dir="data", recursive=True)


    # 读取文档
    # documents = reader.load_data()
    # 如果文件比较多可以使用并行处理文档，注意：windows需要在主函数中运行
    # documents = reader.load_data(num_workers=2)
    # print(documents)


    # 在文件加载的时候可以对其迭代
    # all_docs = []
    # for docs in reader.iter_data():
    #     # 有100个文件，读取1个文件的时候花费的时候1分钟，文件读取完成之后在进行向量化，花费30秒  1分30秒
    #     # 使用iter_data可以一边进行文件的读取一边进行向量化
    #     # 可对文档进行操作
    #     print(docs)
    #     print('-' * 100)
    #     # 分割
    #
    #     # 嵌入
    #
    #     # 存入向量数据库中
    #     all_docs.extend(docs)
    # print(all_docs)


    # 限制加载的文件
    # 使用目录加载器读取文件（PDF文件会按照页面进行分割）input_files-传入文件列表进行读取文件
    reader = SimpleDirectoryReader(input_files=["data/deepseek介绍.txt"])
    # 读取文档
    documents = reader.load_data()
    print(documents)

    # 可以指定要排除的文件列表
    reader = SimpleDirectoryReader(input_dir="data", exclude=["deepseek介绍.txt", ])
    # 读取文档
    documents = reader.load_data()
    print(documents)

    # 使用扩展名来确定要加载哪些文件
    reader = SimpleDirectoryReader(
        input_dir="data", recursive=True, required_exts=[".txt"]
    )
    # 读取文档
    documents = reader.load_data()
    print(documents)


if __name__ == '__main__':
    main()