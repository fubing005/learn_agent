import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


required_env_vars = ["OLLAMA_API_KEY", "OLLAMA_BASE_URL", "OLLAMA_LLM_MODEL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def use_in_chain(vectorstore,model,question):
    prompt = ChatPromptTemplate.from_template(
        "Summarize the main themes in these retrieved docs: {docs}"
    )
    chain = {"docs": format_docs} | prompt | model | StrOutputParser()
    docs = vectorstore.similarity_search(question)
    print(chain.invoke(docs))

def ask_and_answer(question, vectorstore, model):
    RAG_TEMPLATE = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

    <context>
    {context}
    </context>

    Answer the following question:

    {question}"""

    rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

    chain = (
        RunnablePassthrough.assign(context=lambda input: format_docs(input["context"]))
        | rag_prompt
        | model
        | StrOutputParser()
    )

    docs = vectorstore.similarity_search(question)

    # Run
    print(chain.invoke({"context": docs, "question": question}))

def answer_with_retriever(question, vectorstore, model):
    RAG_TEMPLATE = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

    <context>
    {context}
    </context>

    Answer the following question:

    {question}"""

    rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

    retriever = vectorstore.as_retriever()

    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | model
        | StrOutputParser()
    )

    qa_chain.invoke(question)

try:
    model = ChatOllama(
        model=os.getenv("OLLAMA_LLM_MODEL","llama3.1:8b"),
    )

    loader = WebBaseLoader(web_path="https://lilianweng.github.io/posts/2023-06-23-agent/")
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(data)

    local_embeddings = OllamaEmbeddings(model=os.getenv("OLLAMA_EMBEDDING_MODEL","nomic-embed-text"))
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=local_embeddings)

    question = "What are the approaches to Task Decomposition?"
    docs = vectorstore.similarity_search(question)
    # print(len(docs))
    # print(docs[0])

    # response_message = model.invoke(
    #     "Simulate a rap battle between Stephen Colbert and John Oliver"
    # )
    # print(response_message.content)

    # 在链中使用
    # question = "What are the approaches to Task Decomposition?"
    # use_in_chain(vectorstore,model,question)

    # 问答
    # question = "What are the approaches to Task Decomposition?"
    # ask_and_answer(question, vectorstore, model)

    # 带检索的回答
    # question = "What are the approaches to Task Decomposition?"
    # answer_with_retriever(question, vectorstore, model)

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))