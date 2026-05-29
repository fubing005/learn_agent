import sys
import pysqlite3
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain

load_dotenv()

required_env_vars = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL","NEO4J_URI","NEO4J_USERNAME","NEO4J_PASSWORD"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"请检查 .env 文件！缺失以下配置: {', '.join(missing_vars)}")

# 创建与Neo4j数据库的连接，并用关于电影及其演员的示例数据填充它
def create_graph(graph):
    # 从指定的 GitHub 链接下载 CSV 文件，并将每一行数据转化为一个名为 row 的字典，键名就是 CSV 的表头
    '''
    MERGE (m:Movie ...)：创建电影节点。如果该 movieId 的电影已存在则匹配它，不存在则新建。SET：为电影节点设置属性，并将日期和评分分别转换为 date 类型和浮点数 toFloat 类型。pythonFOREACH (director in split(row.director, '|') | 
    MERGE (p:Person {name:trim(director)})
    MERGE (p)-[:DIRECTED]->(m))
    请谨慎使用此类代码。split(..., '|')：CSV 中的导演字段可能包含多个名字（用 | 分割），这里将其切分成列表。FOREACH：循环遍历每个导演。trim(...)：去除名字前后的空格。MERGE ... -[:DIRECTED]-> ...：创建导演的人员节点（Person），并建立 (Person)-[:DIRECTED]->(Movie) 的关系。
    '''
    movies_query = """
    LOAD CSV WITH HEADERS FROM 
    'https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv'
    AS row
    MERGE (m:Movie {id:row.movieId})
    SET m.released = date(row.released),
        m.title = row.title,
        m.imdbRating = toFloat(row.imdbRating)
    FOREACH (director in split(row.director, '|') | 
        MERGE (p:Person {name:trim(director)})
        MERGE (p)-[:DIRECTED]->(m))
    FOREACH (actor in split(row.actors, '|') | 
        MERGE (p:Person {name:trim(actor)})
        MERGE (p)-[:ACTED_IN]->(m))
    FOREACH (genre in split(row.genres, '|') | 
        MERGE (g:Genre {name:trim(genre)})
        MERGE (m)-[:IN_GENRE]->(g))
    """

    graph.query(movies_query) #在 Neo4j 数据库中实际执行上述 Cypher 语句，写入数据。
    graph.refresh_schema()  # 让连接对象重新扫描数据库，更新它对当前图结构（有哪些标签、属性和关系）的认知。
    print(graph.schema)


try:
    model = ChatOpenAI(
        model=os.getenv("LLM_MODEL","gpt-4o-mini")
    )

    graph = Neo4jGraph() # 连接到 Neo4j 数据库

    # 创建图数据库
    # create_graph(graph) 

    # 使用一个简单的链，它接受一个问题，将其转换为Cypher查询，执行查询，并使用结果回答原始问题。
    # chain = GraphCypherQAChain.from_llm(graph=graph, llm=model, verbose=True,allow_dangerous_requests=True)
    # response = chain.invoke({"query": "What was the cast of the Casino?"})
    # print(response)

    # 验证关系方向
    chain = GraphCypherQAChain.from_llm(graph=graph, llm=model, verbose=True, validate_cypher=True,allow_dangerous_requests=True)
    response = chain.invoke({"query": "What was the cast of the Casino?"})
    print(response)

except Exception as e:
    # 8. 🎯 错误捕获：如果 API key 错了、网络断了或模型名写错了，这里会精准捕获
    print("\n❌ 发生错误，模型调用失败！")
    print("错误类型:", type(e).__name__)
    print("具体错误信息:", str(e))