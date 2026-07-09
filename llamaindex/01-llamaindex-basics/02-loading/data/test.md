# 📚 RAG Document Assistant

基于 LangChain + Streamlit 的智能文档检索助手，采用**父子文档索引**与**上下文压缩**技术，实现高精度、低幻觉的文档问答系统。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🔍 **父子文档检索** | 子文档向量匹配 → 父文档完整召回，兼顾精度与上下文完整性 |
| 🗜️ **上下文压缩** | LLM 自动提取关键片段，减少噪音，提升回答准确率 |
| 📄 **多格式支持** | PDF、DOCX、TXT、Markdown 等主流文档格式 |
| 💾 **双存储架构** | Chroma（向量检索）+ MySQL（元数据 & 聊天记录） |
| 💬 **多轮对话** | 自动关联历史消息，支持上下文连续问答 |
| 🐳 **一键部署** | Docker Compose 完整编排，开箱即用 |
| 🔒 **生产就绪** | Nginx 反向代理、HTTPS、服务监控、日志轮转 |

---

## 🏗️ 系统架构

```
┌─────────────────┐     ┌─────────────────────────────────────┐
│   Streamlit     │────▶│         Document Processing           │
│    (Frontend)   │     │  Loader → Parent/Child Chunker      │
└─────────────────┘     │        → Chroma + MySQL Store       │
         │              └─────────────────────────────────────┘
         │                           │
         ▼                           ▼
┌─────────────────┐     ┌─────────────────────────────────────┐
│  User Question  │────▶│         Retrieval Pipeline          │
│  (+ History)    │     │  Child Search → Parent Recall       │
└─────────────────┘     │  → Context Compress → LLM Prompt  │
         ▲              └─────────────────────────────────────┘
         │                           │
┌─────────────────┐                  ▼
│  LLM Response   │◄────    OpenAI / Compatible API
│  (+ Sources)    │
└─────────────────┘
```

### 技术栈

- **前端**: [Streamlit](https://streamlit.io/) —— 快速构建数据应用界面
- **LLM 框架**: [LangChain](https://python.langchain.com/) —— 编排检索与生成流程
- **向量数据库**: [Chroma](https://www.trychroma.com/) —— 轻量级本地向量存储
- **关系数据库**: [MySQL 8.0](https://www.mysql.com/) —— 文档元数据与聊天记录持久化
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) —— 数据库操作
- **容器化**: [Docker](https://www.docker.com/) + Docker Compose
- **反向代理**: [Nginx](https://nginx.org/) —— 负载均衡、HTTPS、静态资源

---

## 🚀 快速开始

### 环境要求

- Python ≥ 3.10
- Docker & Docker Compose（可选，推荐）
- OpenAI API Key 或兼容的 LLM 服务

### 1. 克隆项目

```bash
git clone https://github.com/your-username/rag-document-assistant.git
cd rag-document-assistant
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=rag_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=rag_assistant

# Chroma
CHROMA_PERSIST_DIR=./data/chroma

# LLM API
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo

# Retrieval
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5
```

### 3. 启动基础设施（Docker）

```bash
docker-compose up -d
```

将启动：
- MySQL 8.0（端口 3306）
- Chroma Server（端口 8000）

### 4. 安装 Python 依赖

```bash
# 创建虚拟环境（推荐）
conda create -n rag_axing python=3.11 -y
conda activate rag_axing

# 安装项目依赖
pip install -e ".[dev]"
```

### 5. 初始化数据库

```bash
python -c "from src.db.mysql_store import init_db; init_db()"
```

### 6. 启动应用

```bash
streamlit run src/ui/app.py
```

访问 http://localhost:8501 开始使用！

---

## 📁 项目结构

```
rag-document-assistant/
├── .env                      # 环境变量（本地配置，不提交）
├── .env.example              # 环境变量模板
├── docker-compose.yml        # Docker 编排配置
├── docker-compose.prod.yml   # 生产环境编排配置
├── Dockerfile                # 应用容器镜像
├── nginx/
│   ├── nginx.conf            # Nginx 配置文件
│   └── ssl/                  # SSL 证书目录
├── README.md                 # 项目说明
│
├── data/
│   ├── chroma/               # Chroma 向量数据持久化目录
│   └── .gitkeep
│
├── docs/
│   ├── architecture.md       # 架构设计文档
│   └── api_reference.md      # API 接口文档
│
├── src/
│   ├── main.py               # 应用入口
│   │
│   ├── config/
│   │   ├── settings.py       # Pydantic 配置管理
│   │   ├── prompts.py        # LLM 提示词模板
│   │   └── __init__.py
│   │
│   ├── core/                 # 核心业务逻辑
│   │   ├── document_loader.py    # 多格式文档加载器
│   │   ├── chunker.py            # 父子文档分块器 ⭐
│   │   ├── compressor.py       # 上下文压缩器 ⭐
│   │   ├── retriever.py        # 父子索引检索器 ⭐
│   │   ├── rag_chain.py        # RAG 完整链路
│   │   └── __init__.py
│   │
│   ├── db/                   # 数据持久化层
│   │   ├── models.py           # SQLAlchemy 数据模型
│   │   ├── mysql_store.py      # MySQL 连接与会话管理
│   │   ├── chroma_store.py     # Chroma 向量存储封装
│   │   ├── chat_history.py     # 聊天记录 CRUD
│   │   └── __init__.py
│   │
│   ├── ui/
│   │   └── app.py              # Streamlit 前端界面
│   │
│   └── utils/
│       ├── helpers.py          # 通用工具函数
│       └── __init__.py
│
└── tests/                    # 测试套件
    ├── test_document_loader.py
    ├── test_compressor.py
    ├── test_retriever.py
    └── __init__.py
```

---

## 🔧 核心模块说明

### 父子文档分块（`core/chunker.py`）

```python
# 父块：大粒度（2000字符），保留完整语义
# 子块：小粒度（512字符），用于向量精确匹配
# 检索时：子块命中 → 返回父块完整内容

chunker = ParentChildChunker(
    parent_chunk_size=2000,
    child_chunk_size=512
)
parent_child_pairs = chunker.split(documents)
```

### 上下文压缩（`core/compressor.py`）

```python
# 从检索到的父文档中提取与问题相关的关键片段
# 减少 Token 消耗，降低幻觉风险

compressor = ContextCompressor()
compressed_docs = compressor.compress(query, parent_documents)
```

### 父子索引检索（`core/retriever.py`）

```python
# 1. 子文档向量相似度检索（高精度）
# 2. 关联提取父文档内容（完整性）
# 3. 去重 + 压缩 → 送入 LLM

retriever = ParentDocumentRetriever(
    vector_store=chroma_store,
    compressor=compressor
)
context = retriever.retrieve_as_context(query)
```

---

## 🧪 测试

```bash
# 运行全部测试
pytest tests/ -v

# 运行指定模块
pytest tests/test_retriever.py -v

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

---

## 🖥️ 服务器部署指南

### 方案一：Docker Compose 全栈部署（推荐）

适用于：快速上线、单机部署、中小规模使用

#### 1. 服务器准备

```bash
# 系统要求
# - Ubuntu 20.04+ / CentOS 7+
# - Docker 20.10+
# - Docker Compose 2.0+
# - 域名已解析到服务器（如需 HTTPS）

# 安装 Docker（如未安装）
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 项目部署

```bash
# 克隆项目
git clone https://github.com/your-username/rag-document-assistant.git
cd rag-document-assistant

# 配置生产环境变量
cp .env.example .env
nano .env  # 编辑配置

# 启动生产环境（包含 Nginx、SSL）
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f app
```

#### 3. 生产环境配置说明

`.env` 生产环境关键配置：

```env
# === 数据库 ===
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=rag_user
MYSQL_PASSWORD=your_strong_password_here
MYSQL_DATABASE=rag_assistant

# === Chroma ===
CHROMA_PERSIST_DIR=/app/data/chroma

# === LLM API ===
OPENAI_API_KEY=sk-your-production-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo

# === 应用配置 ===
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false

# === 安全 ===
# 如需访问控制，配置 Streamlit 认证
STREAMLIT_SERVER_COOKIE_SECRET=your-random-secret-key
```

### 方案二：手动部署（自定义程度高）

适用于：已有数据库、需要集成现有基础设施

#### 1. 环境准备

```bash
# 创建应用目录
sudo mkdir -p /opt/rag-assistant
cd /opt/rag-assistant

# 克隆代码
sudo git clone https://github.com/your-username/rag-document-assistant.git .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -e ".[dev]"
```

#### 2. 配置 Systemd 服务

创建 `/etc/systemd/system/rag-assistant.service`：

```ini
[Unit]
Description=RAG Document Assistant
After=network.target mysql.service

[Service]
Type=simple
User=raguser
Group=raguser
WorkingDirectory=/opt/rag-assistant
Environment=PATH=/opt/rag-assistant/venv/bin
EnvironmentFile=/opt/rag-assistant/.env
ExecStart=/opt/rag-assistant/venv/bin/streamlit run src/ui/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable rag-assistant
sudo systemctl start rag-assistant
sudo systemctl status rag-assistant
```

#### 3. 配置 Nginx 反向代理

创建 `/etc/nginx/sites-available/rag-assistant`：

```nginx
upstream rag_assistant {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name your-domain.com;

    # 强制跳转 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书（使用 Let's Encrypt 或自签名）
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # 文件上传大小限制
    client_max_body_size 100M;

    location / {
        proxy_pass http://rag_assistant;
        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置（大文件上传/长文本生成）
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 静态资源缓存
    location /static {
        alias /opt/rag-assistant/static;
        expires 30d;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/rag-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. 配置 SSL（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

### 方案三：云服务器部署（阿里云/腾讯云/AWS）

#### 阿里云 ECS 部署示例

```bash
# 1. 购买 ECS 实例（建议配置）
# - 2核 4G 起步（生产建议 4核 8G）
# - Ubuntu 22.04 LTS
# - 带宽 5Mbps+
# - 系统盘 40GB + 数据盘 100GB（存储向量数据）

# 2. 安全组配置
# - 入方向：80, 443, 22 端口开放
# - 出方向：全部开放（访问 LLM API）

# 3. 数据盘挂载（如有）
sudo mkfs -t ext4 /dev/vdb
sudo mkdir /data
sudo mount /dev/vdb /data

# 4. 部署应用（使用 Docker Compose 方案）
cd /data
git clone https://github.com/your-username/rag-document-assistant.git
cd rag-document-assistant
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔒 生产环境安全建议

| 措施 | 说明 |
|------|------|
| **HTTPS 强制** | Nginx 配置 80 跳转 443，使用 Let's Encrypt 免费证书 |
| **访问控制** | 配置 Streamlit 认证或 Nginx Basic Auth |
| **API Key 保护** | `.env` 文件权限 600，不提交到 Git |
| **数据库安全** | MySQL 仅监听本地/内网，强密码，定期备份 |
| **防火墙** | 仅开放 80/443，关闭 8501 直接访问 |
| **日志监控** | 配置日志轮转，集成阿里云 SLS 或 ELK |

---

## 🐳 Docker 部署

### 开发环境

```bash
# 启动所有服务（MySQL + Chroma + App）
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

### 生产环境

```bash
# 使用生产配置（含 Nginx、SSL）
docker-compose -f docker-compose.prod.yml up -d

# 更新部署
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --build

# 查看资源使用
docker stats
```

---

## 📌 开发路线图

- [x] Phase 1: 基础设施搭建（配置管理、Docker 环境）
- [x] Phase 2: 数据库层（MySQL 模型、聊天记录、Chroma 封装）
- [x] Phase 3: 文档处理核心（加载器、父子分块、向量化）
- [x] Phase 4: 检索与 RAG 链路（父子索引、压缩器、Chain 组装）
- [x] Phase 5: Streamlit 前端（上传、对话、历史展示）
- [x] Phase 6: 生产部署（Docker Compose、Nginx、SSL、Systemd）
- [ ] Phase 7: 高级功能（多知识库、权限管理、文档解析优化）
- [ ] Phase 8: 性能优化（并发检索、缓存策略、Embedding 模型替换）

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

---

## 📄 许可证

[MIT License](LICENSE)

---

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) —— LLM 应用开发框架
- [Chroma](https://github.com/chroma-core/chroma) —— 开源向量数据库
- [Streamlit](https://github.com/streamlit/streamlit) —— 数据应用前端框架

---

> 💡 **提示**: 首次使用请确保 `.env` 文件已正确配置，并执行数据库初始化命令。生产部署前请务必修改默认密码和 API Key。
