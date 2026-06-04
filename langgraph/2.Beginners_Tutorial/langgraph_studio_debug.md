## LangGraph Studio 可视化调试

LangGraph Studio 是官方提供的可视化开发环境，让你实时查看 Agent 的执行过程，大幅提升开发和调试效率。

### 安装 LangGraph CLI

```
# 💡 填坑提示：[inmem] 参数非常重要，它允许 LangGraph CLI 在本地内存中直接运行开发服务器，而不需要配置复杂的远程 Graph 部署服务。
pip install -U "langgraph-cli[inmem] -i https://mirrors.aliyun.com/pypi/simple/
```

### 创建项目配置文件

在项目根目录创建 `langgraph.json` 配置文件：

```
{
  "dependencies": ["."],
  "graphs": {
    "my_agent": "./langgraph_studio_debug.py:graph"
  },
  "env": ".env"
}
```

### 启动开发服务器

```
langgraph dev
```

启动后访问 
- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs
即可在浏览器中使用 LangGraph Studio。

### Studio 主要功能

- **实时可视化**：图形化展示节点执行过程，直观了解工作流状态
- **状态检查**：在任意节点暂停查看当前 State，方便排查问题
- **时间旅行**：回放历史执行步骤，追踪每一步的状态变化
- **热重载**：修改代码后自动更新图结构，无需重启服务

**环境要求：**LangGraph Studio 需要 Docker 环境支持。请确保已安装 Docker Desktop 并正常运行后再启动开发服务器。

------

## 最佳实践与常见问题

### 最佳实践

**状态设计要点**

- 保持 State 精简，只包含必要字段
- 为复杂字段定义明确的 reducer（如 `add_messages`）
- 使用 Pydantic 模型在生产环境中验证状态类型
- 避免在 State 中存储过大的对象，考虑使用外部存储

**节点设计要点**

- 每个节点职责单一，便于测试和复用
- 节点函数应该是幂等的（相同输入产生相同输出）
- 避免在节点中直接修改传入的 state，而是返回新值
- 合理使用异步节点处理 I/O 密集型操作

**错误处理**

```
def robust_node(state: AgentState) -> dict:
    try:
        result = risky_operation(state)
        return {"messages": [result], "error": None}
    except Exception as e:
        return {
            "error": str(e),
            "messages": [{"role": "assistant", "content": f"操作失败: {e}"}]
        }
```

**避免无限循环**

```
def route_with_limit(state: AgentState) -> str:
    # 设置最大重试次数，防止无限循环
    if state.get("retry_count", 0) >= 3:
        return END
    
    if needs_retry(state):
        return "retry_node"
    return END
```

### 常见问题 FAQ

**Q1：节点返回值格式不对怎么办？**

```
# 错误：直接修改 state 对象
def bad_node(state):
    state["messages"].append(...)  # 不要直接修改
    return state

# 正确：返回需要更新的字段
def good_node(state):
    return {"messages": [new_message]}  # 只返回变更字段
```

**Q2：如何在节点之间传递临时数据？**

将临时数据加入 State 定义，或使用下划线前缀约定为内部字段：

```
from typing import TypedDict

class PublicState(TypedDict):
    messages: list  # 对外暴露

class PrivateState(TypedDict):
    messages: list
    _internal_cache: dict  # 以下划线开头约定为内部使用
```

**Q3：如何调试节点执行过程？**

```
# 使用 stream 模式观察每个节点的输出
for event in graph.stream(initial_state, stream_mode="updates"):
    for node_name, state_update in event.items():
        print(f"\n[节点: {node_name}]")
        print(f"更新: {state_update}")
```

**Q4：StateGraph 和 MessageGraph 的区别？**

`MessageGraph` 是早期版本的 API，功能较为受限。现在推荐统一使用 `StateGraph`，它更灵活、功能更完善。如需处理消息，使用 `StateGraph(MessagesState)` 或自定义包含 `messages` 字段的 State。

**注意：**`MessageGraph` 已被废弃，请统一使用 `StateGraph`。如果你的代码中还在使用 MessageGraph，建议尽早迁移到 StateGraph(MessagesState) 以获得更好的支持和更多功能。

---

# [UI界面操作步骤](https://smith.langchain.com/studio/thread?baseUrl=http%3A%2F%2F127.0.0.1%3A2024&mode=graph&render=interact&assistantId=eac7a2dc-f2ac-5973-91d0-f90689344d99)

1. 准备输入数据 (Input)

在左下角的 **Input** 面板中，你需要填写代码中 `AgentState` 要求的两个必需字段：

- **Messages（消息列表）**
  1. 点击 **+ Message** 按钮。
  2. 在弹出的输入框中输入你的测试问题（例如需要触发乘法工具的问题）：“**3 乘以 5 等于多少？**”。
- **Retry Count（重试计数器）**
  1. 在 **Retry Count** 下方的 `Input` 文本框中输入初始值：`0`。

------

2. 提交并运行 (Submit)

- 点击底部的蓝色 **Submit** 按钮。
- LangGraph 引擎将开始按照控制流执行节点。

------

3. 观察执行流程 (Graph & Trace)

提交后，你可以在界面中观察到以下动态变化：

节点高亮流转

在中间的拓扑图区域，你会看到高亮边框随着执行顺序移动：

1. `__start__` \(\rightarrow \) **`agent`**（模型接收到你的问题，决定调用 `multiply` 工具）。
2. **`agent`** \(\rightarrow \) **`counter`**（触发条件路由，计数器节点执行，`retry_count` 变为 1）。
3. **`counter`** \(\rightarrow \) **`tools`**（进入工具节点，计算 `3 * 5` 并返回 `15`）。
4. **`tools`** \(\rightarrow \) **`agent`**（将计算结果带回模型）。
5. **`agent`** \(\rightarrow \) `__end__`（模型组织最终语言，判断不需要再调工具，结束运行）。

右侧结果输出

- 右侧的 **New Thread** 空白区域将转变为对话流或日志流。
- 你将看到大模型最终输出的文本答案（例如：“3 乘以 5 等于 15。”）。

------

4. 调试与多轮测试 (Optional)

- **查看原始数据**：可以点击 Input 区域的 **View Raw** 下拉菜单，查看当前 State 结构体中的原始 JSON 数据。
- **重置或新测试**：点击顶部的 **New Thread** 可以清空当前状态，开启一轮全新的输入测试。

你想**测试工具调用**还是**触发熔断机制**？告诉我你的目的，我可以为你提供具体的输入数值。