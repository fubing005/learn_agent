from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event,
    Context,
)
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.indices.vector_store.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.response_synthesizers.type import ResponseMode
from typing import List
import asyncio
from llama_config import get_llm
llm, embed_model = get_llm()


# 定义工作流事件
class QueryProcessedEvent(Event):
    """查询处理完成事件"""
    query: str


class VectorRetrievalEvent(Event):
    """向量检索完成事件"""
    nodes: List[NodeWithScore]
    query: str


class BM25RetrievalEvent(Event):
    """BM25检索完成事件"""
    nodes: List[NodeWithScore]
    query: str


class RetrievalCompletedEvent(Event):
    """所有检索完成事件"""
    all_nodes: List[NodeWithScore]
    query: str


class PostProcessedEvent(Event):
    """后处理完成事件"""
    processed_nodes: List[NodeWithScore]
    query: str


class ProgressEvent(Event):
    """进度事件 - 用于流式输出"""
    msg: str
    step: str = ""
    metadata: dict = None


class StreamingRAGWorkflow(Workflow):
    """使用get_response_synthesizer的流式RAG工作流"""

    def __init__(self, retriever: VectorIndexRetriever, bm25_retriever: BM25Retriever, **kwargs):
        super().__init__(**kwargs)
        self.retriever = retriever
        self.bm25_retriever = bm25_retriever
        self.postprocessor = SimilarityPostprocessor(similarity_cutoff=0.5)

        # 使用get_response_synthesizer创建支持流式输出的响应合成器
        self.response_synthesizer = get_response_synthesizer(
            response_mode=ResponseMode.COMPACT,  # 使用紧凑模式
            streaming=True,  # 启用流式输出
            use_async=True  # 启用异步
        )

    @step
    async def process_query(self, ctx: Context, ev: StartEvent) -> QueryProcessedEvent:
        """步骤1: 处理用户查询"""
        query = ev.query
        ctx.write_event_to_stream(ProgressEvent(
            msg=f"🔍 开始处理查询: {query}\n",
            step="query_processing"
        ))

        processed_query = query.strip()

        ctx.write_event_to_stream(ProgressEvent(
            msg="✅ 查询处理完成，开始并行检索...\n",
            step="query_processing"
        ))

        return QueryProcessedEvent(query=processed_query)

    @step
    async def vector_retrieval(self, ctx: Context, ev: QueryProcessedEvent) -> VectorRetrievalEvent:
        """步骤2a: 向量检索"""
        ctx.write_event_to_stream(ProgressEvent(
            msg="📚 正在进行向量检索...\n",
            step="vector_retrieval"
        ))

        query_bundle = QueryBundle(query_str=ev.query)
        retrieved_nodes = await self.retriever.aretrieve(query_bundle)

        ctx.write_event_to_stream(ProgressEvent(
            msg=f"✅ 向量检索完成，找到 {len(retrieved_nodes)} 个相关文档\n",
            step="vector_retrieval",
            metadata={"count": len(retrieved_nodes)}
        ))

        return VectorRetrievalEvent(nodes=retrieved_nodes, query=ev.query)

    @step
    async def bm25_retrieval(self, ctx: Context, ev: QueryProcessedEvent) -> BM25RetrievalEvent:
        """步骤2b: BM25检索"""
        ctx.write_event_to_stream(ProgressEvent(
            msg="🔎 正在进行关键词检索...\n",
            step="bm25_retrieval"
        ))

        query_bundle = QueryBundle(query_str=ev.query)
        retrieved_nodes = await self.bm25_retriever.aretrieve(query_bundle)

        ctx.write_event_to_stream(ProgressEvent(
            msg=f"✅ 关键词检索完成，找到 {len(retrieved_nodes)} 个相关文档\n",
            step="bm25_retrieval",
            metadata={"count": len(retrieved_nodes)}
        ))

        return BM25RetrievalEvent(nodes=retrieved_nodes, query=ev.query)

    @step
    async def combine_retrievals(
            self,
            ctx: Context,
            ev: VectorRetrievalEvent | BM25RetrievalEvent
    ) -> RetrievalCompletedEvent:
        """步骤3: 合并检索结果"""
        ctx.write_event_to_stream(ProgressEvent(
            msg="🔧 正在收集检索结果...\n",
            step="combining_results"
        ))

        # 收集两种检索事件
        events = ctx.collect_events(ev, [VectorRetrievalEvent, BM25RetrievalEvent])

        if not events or len(events) < 2:
            # 还没收集到所有事件，继续等待
            return None

        ctx.write_event_to_stream(ProgressEvent(
            msg=f"✅ 已收集到 {len(events)} 个检索结果，开始合并...\n",
            step="combining_results"
        ))

        # 合并所有检索结果
        all_nodes = []
        query = ""
        vector_count = 0
        bm25_count = 0

        for event in events:
            if isinstance(event, VectorRetrievalEvent):
                all_nodes.extend(event.nodes)
                vector_count = len(event.nodes)
                query = event.query
            elif isinstance(event, BM25RetrievalEvent):
                all_nodes.extend(event.nodes)
                bm25_count = len(event.nodes)
                query = event.query

        ctx.write_event_to_stream(ProgressEvent(
            msg=f"📋 合并完成: 向量检索 {vector_count} 个 + 关键词检索 {bm25_count} 个 = 总共 {len(all_nodes)} 个文档\n",
            step="combining_results",
            metadata={"vector_count": vector_count, "bm25_count": bm25_count, "total": len(all_nodes)}
        ))

        return RetrievalCompletedEvent(all_nodes=all_nodes, query=query)

    @step
    async def post_process(self, ctx: Context, ev: RetrievalCompletedEvent) -> PostProcessedEvent:
        """步骤4: 后处理检索结果"""
        ctx.write_event_to_stream(ProgressEvent(
            msg="🔄 正在优化和过滤检索结果...\n",
            step="postprocessing"
        ))

        if not ev.all_nodes:
            ctx.write_event_to_stream(ProgressEvent(
                msg="⚠️ 没有找到相关文档，无法生成答案\n",
                step="postprocessing"
            ))
            return PostProcessedEvent(processed_nodes=[], query=ev.query)

        # 创建查询束用于后处理
        query_bundle = QueryBundle(query_str=ev.query)

        # 执行后处理
        processed_nodes = self.postprocessor.postprocess_nodes(
            nodes=ev.all_nodes, query_bundle=query_bundle
        )

        ctx.write_event_to_stream(ProgressEvent(
            msg=f"✅ 文档优化完成，从 {len(ev.all_nodes)} 个文档中选出 {len(processed_nodes)} 个最相关的\n",
            step="postprocessing",
            metadata={"original_count": len(ev.all_nodes), "filtered_count": len(processed_nodes)}
        ))

        # 显示文档片段预览
        if processed_nodes:
            ctx.write_event_to_stream(ProgressEvent(
                msg="📋 最相关的文档片段:\n",
                step="postprocessing"
            ))

            for i, node in enumerate(processed_nodes[:3]):
                score = node.score if node.score else 0
                preview = node.text[:80] + "..." if len(node.text) > 80 else node.text
                ctx.write_event_to_stream(ProgressEvent(
                    msg=f"  {i + 1}. [相似度: {score:.3f}] {preview}\n",
                    step="postprocessing"
                ))

        return PostProcessedEvent(processed_nodes=processed_nodes, query=ev.query)

    @step
    async def synthesize_response(self, ctx: Context, ev: PostProcessedEvent) -> StopEvent:
        """步骤5: 使用response_synthesizer进行流式生成"""
        if not ev.processed_nodes:
            ctx.write_event_to_stream(ProgressEvent(
                msg="❌ 抱歉，没有找到相关信息来回答的问题。\n",
                step="synthesis"
            ))
            return StopEvent(result={
                "response": "抱歉，没有找到相关信息来回答的问题。",
                "source_nodes": [],
                "metadata": {"query": ev.query}
            })

        ctx.write_event_to_stream(ProgressEvent(
            msg="🤖 正在基于相关文档生成答案...\n\n",
            step="synthesis"
        ))

        # 创建查询束
        query_bundle = QueryBundle(query_str=ev.query)

        try:
            # 使用response_synthesizer进行异步流式合成
            streaming_response = await self.response_synthesizer.asynthesize(
                query=query_bundle,
                nodes=ev.processed_nodes
            )

            full_response = ""

            # 方法1: 如果响应对象有response_gen属性（流式生成器）
            if hasattr(streaming_response, 'response_gen') and streaming_response.response_gen:
                try:
                    async for chunk in streaming_response.response_gen:
                        chunk_text = str(chunk)
                        full_response += chunk_text

                        # 将每个块写入流
                        ctx.write_event_to_stream(ProgressEvent(
                            msg=chunk_text,
                            step="synthesis"
                        ))

                        # 添加小延迟以获得更好的流式效果
                        await asyncio.sleep(0.02)

                except Exception as e:
                    print(f"流式生成出错: {e}")
                    # 如果流式生成失败，使用完整响应
                    full_response = str(streaming_response)
                    ctx.write_event_to_stream(ProgressEvent(
                        msg=full_response,
                        step="synthesis"
                    ))

            # 方法2: 如果没有流式生成器，但有async_response_gen
            elif hasattr(streaming_response, 'async_response_gen') and streaming_response.async_response_gen:
                try:
                    async for chunk in streaming_response.async_response_gen():
                        chunk_text = str(chunk)
                        full_response += chunk_text

                        ctx.write_event_to_stream(ProgressEvent(
                            msg=chunk_text,
                            step="synthesis"
                        ))

                        await asyncio.sleep(0.02)

                except Exception as e:
                    print(f"异步流式生成出错: {e}")
                    full_response = str(streaming_response)
                    ctx.write_event_to_stream(ProgressEvent(
                        msg=full_response,
                        step="synthesis"
                    ))

            # 方法3: 如果都没有，则分块输出完整响应
            else:
                full_response = str(streaming_response)

                # 将完整响应分块进行流式输出
                chunk_size = 50  # 每块字符数
                for i in range(0, len(full_response), chunk_size):
                    chunk = full_response[i:i + chunk_size]
                    ctx.write_event_to_stream(ProgressEvent(
                        msg=chunk,
                        step="synthesis"
                    ))
                    await asyncio.sleep(0.1)

        except Exception as e:
            error_msg = f"❌ 生成答案时出错: {str(e)}\n"
            ctx.write_event_to_stream(ProgressEvent(
                msg=error_msg,
                step="synthesis"
            ))
            return StopEvent(result={
                "response": "抱歉，生成答案时出现错误。",
                "source_nodes": ev.processed_nodes,
                "metadata": {"query": ev.query, "error": str(e)}
            })

        ctx.write_event_to_stream(ProgressEvent(
            msg=f"\n\n✅ 答案生成完成！使用了 {len(ev.processed_nodes)} 个文档片段。\n",
            step="synthesis"
        ))

        return StopEvent(result={
            "response": full_response,
            "source_nodes": ev.processed_nodes,
            "metadata": {
                "num_sources": len(ev.processed_nodes),
                "query": ev.query
            }
        })


# 使用示例
async def main():
    """主函数示例"""
    print("📖 正在构建向量索引...")

    # 初始化LLM
    get_llm()

    # 加载文档并构建索引
    documents = SimpleDirectoryReader(input_files=["data/小说.txt"]).load_data()
    splitter = SentenceSplitter(chunk_size=512)
    nodes = splitter.get_nodes_from_documents(documents)

    index = VectorStoreIndex(nodes)
    retriever = VectorIndexRetriever(index, similarity_top_k=5)
    bm25_retriever = BM25Retriever.from_defaults(
        nodes=nodes,
        similarity_top_k=3
    )

    print("✅ 向量索引构建完成\n")

    # 创建工作流
    workflow = StreamingRAGWorkflow(
        retriever=retriever,
        bm25_retriever=bm25_retriever,
        timeout=120,  # 增加超时时间
        verbose=True
    )

    # 测试查询
    test_queries = [
        "萧炎的爸爸是谁？",
        "萧炎有什么特殊能力？"
    ]

    for query in test_queries:
        print(f"{'=' * 70}")
        print(f"🎯 测试查询: {query}")
        print(f"{'=' * 70}")

        # 启动工作流
        handler = workflow.run(query=query)

        # 处理流式事件
        async for ev in handler.stream_events():
            if isinstance(ev, ProgressEvent):
                print(ev.
                      msg, end='', flush=True)

        # 获取最终结果
        final_result = await handler

        print(f"\n📊 工作流执行完成:")
        print(f"- 使用了 {final_result['metadata']['num_sources']} 个文档片段")
        print(f"- 原始查询: {final_result['metadata']['query']}")
        print(f"- 响应长度: {len(final_result['response'])} 字符")
        print("\n")


if __name__ == "__main__":
    # 运行主示例
    asyncio.run(main())