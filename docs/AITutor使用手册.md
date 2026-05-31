# 🤖 AITutor 使用手册

> 基于多智能体协作的《人工智能导论》课程助教 | v1.0 | 2026-05-31

---

## 目录

1. [项目简介](#1-项目简介)
2. [环境要求](#2-环境要求)
3. [快速开始](#3-快速开始)
4. [架构概览](#4-架构概览)
5. [功能一：智能问答](#5-功能一智能问答)
6. [功能二：知识图谱](#6-功能二知识图谱)
7. [功能三：自适应测验](#7-功能三自适应测验)
8. [API 接口文档](#8-api-接口文档)
9. [配置说明](#9-配置说明)
10. [项目文件结构](#10-项目文件结构)
11. [常见问题](#11-常见问题)
12. [扩展指南](#12-扩展指南)

---

## 1. 项目简介

AITutor 是一个基于**多智能体协作**的 AI 教学辅助系统，专为《人工智能导论》课程设计。系统通过三个专用 Agent 分工协作，结合课程知识图谱和自适应测验引擎，为学生提供个性化的学习体验。

### 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 多智能体协作 | Router 自动分类问题，调度数学推导/算法实现/概念辨析三个专家 Agent |
| 🕸️ 课程知识图谱 | 26 个核心概念 + 20 条关系，NetworkX 索引 + Pyvis 交互式可视化 |
| 📝 自适应测验 | 布鲁姆 6 层认知体系，LLM 生成题目 + 对抗式验证 |
| 🎨 现代化 UI | Streamlit Web 界面，三页导航，响应式布局 |

### 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | Streamlit | 1.41.1 |
| 后端 | FastAPI | 0.115.6 |
| LLM API | OpenAI-compatible（DeepSeek/通义千问等） | — |
| 知识图谱 | NetworkX + Pyvis | 3.4.2 / 0.3.2 |
| 数据存储 | JSON 文件 | — |
| Python | 3.11+ | — |

---

## 2. 环境要求

- **Python**：3.11 或更高版本
- **操作系统**：macOS / Linux / Windows
- **网络**：需要访问 LLM API（DeepSeek 或通义千问等）
- **浏览器**：Chrome / Safari / Edge 等现代浏览器

---

## 3. 快速开始

### 3.1 获取 API Key

1. 前往 [DeepSeek 开放平台](https://platform.deepseek.com) 注册账号
2. 在「API Keys」页面创建一个新的 API Key
3. 复制 Key（格式：`sk-xxxxxxxxxxxxxxxx`）

> 💡 新用户通常有免费额度。也可使用其他 OpenAI-compatible 的 API 服务。

### 3.2 安装依赖

```bash
# 进入项目目录
cd aitutor

# 安装 Python 依赖
pip3 install -r requirements.txt
```

### 3.3 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# LLM_API_KEY=sk-你的真实key
```

`.env` 文件说明：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_API_KEY` | API 密钥（必填） | — |
| `LLM_BASE_URL` | API 服务地址 | `https://api.deepseek.com` |
| `LLM_MODEL` | 模型名称 | `deepseek-chat` |
| `LLM_MAX_TOKENS` | 最大输出 token 数 | `4096` |
| `LLM_TEMPERATURE` | 生成温度（0-1） | `0.7` |

### 3.4 启动服务

**一键启动：**

```bash
cd aitutor && bash run.sh
```

**或分别启动：**

```bash
# 终端 1：启动后端
cd aitutor/backend
PYTHONPATH=/项目根目录 uvicorn main:app --reload --port 8000

# 终端 2：启动前端
cd aitutor/frontend
PYTHONPATH=/项目根目录 streamlit run app.py --server.port 8501 --server.headless true
```

### 3.5 打开界面

浏览器访问：**http://localhost:8501**

停止服务：在启动终端按 `Ctrl+C`。

---

## 4. 架构概览

```
┌─────────────────────────────────────────────────┐
│                Streamlit 前端 (:8501)             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ 智能问答  │  │ 知识图谱  │  │  自适应测验   │   │
│  └────┬─────┘  └────┬─────┘  └───────┬──────┘   │
└───────┼────────────┼───────────────┼────────────┘
        │  HTTP POST               │
┌───────┼────────────┼───────────────┼────────────┐
│       ▼            ▼               ▼            │
│              FastAPI 后端 (:8000)                │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐     │
│  │ Router   │  │ KG Query │  │ Quiz Gen  │     │
│  │ Agent    │  │ Engine   │  │ Engine    │     │
│  └────┬─────┘  └────┬─────┘  └───────┬─────┘   │
│       │             │               │           │
│  ┌────┴─────┐  ┌────┴─────┐  ┌──────┴──────┐   │
│  │ Math     │  │ NetworkX │  │ Bloom L1-L6 │   │
│  │ Algo     │  │ 图引擎    │  │ 自适应调节   │   │
│  │ Concept  │  └──────────┘  └─────────────┘   │
│  └────┬─────┘                                   │
│       ▼                                         │
│  LLM API (DeepSeek)                             │
└─────────────────────────────────────────────────┘
```

### 数据流

1. **学生提问** → Router 分析问题类型 → 调度对应 Agent → 查询知识图谱 → 注入上下文 → LLM 生成回答 → 返回前端
2. **测验请求** → 选择知识点 → 布鲁姆层次判定 → LLM 生成题目 → 对抗式验证 → 返回题目 → 学生作答 → 自适应调节难度

---

## 5. 功能一：智能问答

### 5.1 页面入口

在左侧导航栏选择 **💬 智能问答**。

### 5.2 三个导师介绍

| Agent | 图标 | 专长 | 适用场景 |
|-------|------|------|---------|
| 数学推导 Agent | 🔢 | 公式推导、数学原理 | 问公式/推导/概率/矩阵/求导 |
| 算法实现 Agent | 💻 | 从零手写算法代码 | 问实现/手写/代码/how to code |
| 概念辨析 Agent | 🧠 | 对比易混淆概念 | 问区别/对比/辨析/vs |

### 5.3 路由判定规则

Router 会自动分析你的问题并派给最合适的导师：

```
包含「公式/推导/概率/矩阵/求导」 → 🔢 数学推导 Agent
包含「实现/手写/代码/怎么写」   → 💻 算法实现 Agent
包含「区别/对比/辨析/vs」      → 🧠 概念辨析 Agent
混合提问                       → 拆分子问题，依次调用多个 Agent
```

### 5.4 使用技巧

**向数学推导 Agent 提问：**
- "请推导反向传播中的链式法则"
- "为什么交叉熵损失更适合分类问题？"
- "SVM 的拉格朗日对偶推导过程"

**向算法实现 Agent 提问：**
- "用 NumPy 从零实现 K-means 聚类"
- "手写一个简单的 CNN 前向传播"
- "用纯 Python 实现梯度下降并可视化"

**向概念辨析 Agent 提问：**
- "生成式模型和判别式模型的本质区别是什么？"
- "梯度消失和梯度爆炸有什么区别？"
- "L1 和 L2 正则化在实际效果上有什么不同？"

### 5.5 对话功能

- **多轮对话**：自动保留最近 6 轮对话历史
- **子问题展开**：混合提问会被自动拆分，点击「📋 相关子问题解答」查看
- **Agent 标识**：每条回复都会显示来源 Agent 的彩色徽章
- **侧边栏提示**：左侧提供示例问题，点击可复制

---

## 6. 功能二：知识图谱

### 6.1 页面入口

在左侧导航栏选择 **🕸️ 知识图谱**。

> 💡 知识图谱功能**不需要** API Key，离线也能用！

### 6.2 页面布局

页面分为左右两栏：

| 区域 | 功能 | 操作方式 |
|------|------|---------|
| 左侧 | 概念搜索 + 关联探索 | 输入关键词 → 点「查看关联」 |
| 右侧 | 知识体系全览 | 可拖拽、缩放、悬停查看描述 |

### 6.3 知识图谱内容

种子数据包含 **26 个实体**和 **20 条关系**：

**实体类型：**

| 类型 | 颜色 | 示例 |
|------|------|------|
| Concept（概念） | 🟢 绿色 | 过拟合、正则化、损失函数 |
| Algorithm（算法） | 🔵 蓝色 | K-means、CNN、Transformer |
| Person（人物） | 🟣 紫色 | Hinton、LeCun |
| Prerequisite（前置知识） | 🟠 橙色 | 线性代数、概率论、微积分 |

**关系类型：**

| 关系 | 含义 | 示例 |
|------|------|------|
| `PREREQUISITE_OF` | 前置依赖 | 线性代数 → 梯度下降 |
| `VARIANT_OF` | 变体关系 | SGD 是梯度下降的变体 |
| `DERIVES_FROM` | 推导来源 | Adam 从 SGD 推导 |
| `PROPOSED` | 提出者 | Hinton 提出 Dropout |
| `CONTRASTS_WITH` | 对比关系 | 生成式 vs 判别式 |

### 6.4 使用技巧

1. **搜索概念**：输入"梯度"或"神经网络"等关键词
2. **探索关联**：点击「查看关联」看一个概念的前置知识、变体和相关概念
3. **全局浏览**：右侧图谱可拖拽、缩放，悬停节点查看详细描述
4. **颜色区分**：快速识别实体类型

### 6.5 种子数据包含的概念

| 分类 | 包含概念 |
|------|---------|
| 数学基础 | 线性代数、概率论、微积分 |
| 机器学习 | 梯度下降、SGD、Adam、损失函数、交叉熵、过拟合、正则化、K-means、KNN、决策树、SVM、生成式模型、判别式模型 |
| 深度学习 | 反向传播、CNN、RNN、LSTM、Transformer、梯度消失、梯度爆炸 |
| 人物 | Geoffrey Hinton、Yann LeCun |

---

## 7. 功能三：自适应测验

### 7.1 页面入口

在左侧导航栏选择 **📝 自适应测验**。

> 💡 需要配置 API Key。

### 7.2 布鲁姆认知层次

系统根据[布鲁姆认知目标分类](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy)将题目分为 6 个层次：

| 层级 | 名称 | 能力要求 | 题型示例 |
|------|------|---------|---------|
| **L1** 📋 | 记忆 | 回忆基本事实和术语 | 单选题、填空题 |
| **L2** 💡 | 理解 | 用自己的话解释概念 | 单选题、多选题、简答 |
| **L3** 🔧 | 应用 | 运用知识解决具体问题 | 选择题、简答 |
| **L4** 🔍 | 分析 | 分解问题、识别关系 | 多选题、简答 |
| **L5** ⚖️ | 评价 | 基于标准做出判断 | 简答、开放题 |
| **L6** 🚀 | 创造 | 综合知识设计新方案 | 开放设计题 |

### 7.3 可选知识点

- 梯度下降、反向传播、CNN、RNN/LSTM、Transformer
- 过拟合与正则化、损失函数、优化算法、生成式模型
- K-means 聚类、SVM、决策树

### 7.4 自适应调节机制

```
准确率 > 80%  → 📈 升级到下一层次
准确率 < 50%  → 📉 降级到上一层次
准确率 50-80% → ➡️ 保持当前层次
（答题数 < 3 时不调整）
```

### 7.5 使用流程

1. 在下拉框选择知识点
2. 点击 **🎲 生成题目**（系统会根据你的当前层次生成匹配难度的题目）
3. 阅读题目和选项，提交答案
4. 查看对错和详细解析
5. 系统自动调整后续难度
6. 侧边栏实时显示学习进度

### 7.6 对抗式验证

每道题目生成后，会经过第二道 LLM 检查：
- 答案是否正确？
- 题面是否有歧义？
- 难度是否匹配指定的布鲁姆层次？
- 选项是否合理？

如果有问题会自动修正，确保题目质量。

---

## 8. API 接口文档

启动后端后，访问 **http://localhost:8000/docs** 查看交互式 Swagger 文档。

### 8.1 健康检查

```
GET /api/health
→ {"status": "ok", "service": "aitutor"}
```

### 8.2 智能问答

```
POST /api/chat

请求体:
{
  "message": "梯度下降和SGD有什么区别？",
  "history": [                           // 可选
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}

响应体:
{
  "agent_used": "concept",               // 使用的 Agent: math/algorithm/concept
  "agent_display": "🧠 概念辨析 Agent",
  "router_analysis": {
    "primary_agent": "concept",
    "sub_questions": [],
    "knowledge_graph_nodes": ["梯度下降", "SGD"]
  },
  "reply": "## 🔍 概念对比：梯度下降 vs SGD\n\n...",
  "sub_replies": []                      // 子问题解答（如有）
}
```

### 8.3 知识图谱

**搜索概念：**
```
POST /api/kg/search
{"query": "梯度"}
→ {"results": [{"id":"gradient_descent","name":"梯度下降","type":"Algorithm",...}, ...]}
```

**查询邻域：**
```
POST /api/kg/neighborhood
{"node_id": "gradient_descent"}
→ {"center": {...}, "neighbors": [{...relation info...}, ...]}
```

**获取全图：**
```
GET /api/kg/full
→ {"nodes": [...], "edges": [...]}
```

### 8.4 自适应测验

**生成题目：**
```
POST /api/quiz/generate

请求体:
{
  "topic": "梯度下降",
  "student_level": 2,                    // Bloom 层次 1-6
  "history": [                           // 可选
    {"question_id":"q1","correct":true,"topic":"线性回归"}
  ]
}

响应体:
{
  "question_id": "q_a1b2c3d4",
  "question": "以下关于 SGD 的描述正确的是？",
  "options": ["A...", "B...", "C...", "D..."],
  "question_type": "single_choice",
  "answer": "B",
  "explanation": "SGD 每次只用一个小批量样本...",
  "bloom_level": 2,
  "adaptive_action": "maintain"          // upgrade/maintain/downgrade
}
```

**提交答案：**
```
POST /api/quiz/submit
{"question_id": "q_a1b2c3d4", "student_answer": "B", "correct": true}
→ {"acknowledged": true, "new_level": 0, "next_action": "pending"}
```

---

## 9. 配置说明

### 9.1 切换 LLM 服务商

修改 `.env` 中的 `LLM_BASE_URL` 和 `LLM_MODEL`：

```env
# DeepSeek（默认）
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# 通义千问（阿里云百炼）
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus

# OpenAI
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o

# 本地 Ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen2.5:7b
```

### 9.2 调整生成参数

```env
LLM_MAX_TOKENS=4096     # 回答最大长度
LLM_TEMPERATURE=0.7     # 创造性（0=确定性，1=创造性）
```

### 9.3 修改端口

启动时指定不同端口：

```bash
# 后端
uvicorn main:app --port 8000  # 改为其他端口

# 前端
streamlit run app.py --server.port 8501  # 改为其他端口
```

> ⚠️ 修改端口后需要同步更新 `frontend/pages/chat.py`、`frontend/components/kg_renderer.py`、`frontend/pages/quiz.py` 中的 `BACKEND_URL`。

---

## 10. 项目文件结构

```
aitutor/
├── .env                      # 环境变量配置（需自行创建）
├── .env.example              # 配置模板
├── requirements.txt          # Python 依赖
├── run.sh                    # 一键启动脚本
├── backend/                  # FastAPI 后端
│   ├── main.py               # 应用入口，路由注册
│   ├── agents/               # 多智能体模块
│   │   ├── __init__.py
│   │   ├── base.py           # AgentBase 抽象基类 + AgentResult
│   │   ├── router.py         # RouterAgent 问题分类与调度
│   │   ├── math_agent.py     # 🔢 数学推导 Agent
│   │   ├── algorithm_agent.py # 💻 算法实现 Agent
│   │   └── concept_agent.py  # 🧠 概念辨析 Agent
│   ├── api/                  # API 路由
│   │   ├── chat.py           # /api/chat 端点
│   │   ├── kg.py            # /api/kg/* 端点
│   │   └── quiz.py          # /api/quiz/* 端点
│   ├── knowledge_graph/      # 知识图谱模块
│   │   ├── models.py         # Pydantic 数据模型
│   │   └── query.py          # NetworkX 查询引擎
│   ├── quiz/                 # 测验模块
│   │   ├── models.py         # Pydantic 数据模型
│   │   ├── bloom.py          # 布鲁姆分类器
│   │   └── generator.py      # 测验生成 + 对抗验证
│   └── llm/                  # LLM 客户端
│       ├── config.py         # 环境变量配置
│       └── client.py         # OpenAI-compatible API 客户端
├── frontend/                 # Streamlit 前端
│   ├── app.py                # 入口 + 页面路由
│   ├── pages/                # 页面模块
│   │   ├── chat.py           # 智能问答页面
│   │   ├── knowledge_graph.py # 知识图谱页面
│   │   └── quiz.py           # 自适应测验页面
│   └── components/           # UI 组件
│       ├── agent_badge.py    # Agent 身份徽章
│       ├── kg_renderer.py    # Pyvis 图谱渲染
│       └── quiz_card.py      # 测验题目卡片
└── data/                     # 数据文件
    └── syllabus.json         # 课程知识图谱种子数据
```

---

## 11. 常见问题

### Q1：启动时提示端口被占用

```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 杀掉进程
kill -9 <PID>

# 或用其他端口启动
uvicorn main:app --port 8001
```

### Q2：前端显示「无法连接到后端」

1. 确认后端已启动：访问 http://localhost:8000/api/health
2. 确认端口一致：前端的 `BACKEND_URL` 变量必须和后端端口一致

### Q3：聊天返回 401 错误

API Key 未配置或无效。检查 `.env` 中 `LLM_API_KEY` 是否正确。

### Q4：知识图谱不显示

1. 确认后端已启动
2. 检查 `data/syllabus.json` 是否存在
3. 检查 Pyvis 是否安装：`pip3 install pyvis`

### Q5：Streamlit 首次启动卡在 email 提示

加 `--server.headless true` 参数：

```bash
streamlit run app.py --server.headless true
```

### Q6：如何添加新的知识图谱概念

编辑 `aitutor/data/syllabus.json`，在 `entities` 和 `relations` 数组中添加新条目，然后重启后端。

### Q7：如何添加新的测验知识点

编辑 `aitutor/frontend/pages/quiz.py` 中的 `TOPICS` 列表，添加新的知识点名称。

---

## 12. 扩展指南

### 12.1 添加新的 Specialist Agent

1. 在 `backend/agents/` 下创建新的 Agent 文件
2. 继承 `AgentBase`，设置 `name`、`display_name`、`system_prompt`
3. 在 `router.py` 中注册新 Agent
4. 更新 Router 的判定规则

```python
# 示例：新建 database_agent.py
from aitutor.backend.agents.base import AgentBase

class DatabaseAgent(AgentBase):
    name = "database"
    display_name = "🗄️ 数据库 Agent"
    system_prompt = "你是数据库专家..."
```

### 12.2 添加新的关系类型

编辑 `backend/knowledge_graph/models.py`，在 `RelationType` 枚举中添加新类型：

```python
class RelationType(str, Enum):
    # 现有类型...
    BUILDS_ON = "BUILDS_ON"  # 新增
```

### 12.3 接入其他 LLM

只要 API 兼容 OpenAI 格式，只需修改 `.env` 中的 `LLM_BASE_URL` 和 `LLM_MODEL`。代码层面无需改动。

### 12.4 添加对话历史持久化

在 `backend/api/chat.py` 中集成数据库（如 SQLite）：

```python
import sqlite3
# 保存每次对话到数据库
# 下次加载时从数据库读取历史
```

### 12.5 部署到服务器

```bash
# 后端（生产环境用 gunicorn）
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

# 前端（用 nginx 反代）
streamlit run app.py --server.port 8501 --server.enableCORS false

# 或使用 Docker（自行编写 Dockerfile）
```

---

## 附录：快速参考卡片

```
┌─────────────────────────────────────────────────────────┐
│                    AITutor 速查                         │
├─────────────────────────────────────────────────────────┤
│  启动服务          cd aitutor && bash run.sh            │
│  前端地址          http://localhost:8501                │
│  后端地址          http://localhost:8000                │
│  API 文档          http://localhost:8000/docs           │
│  配置文件          aitutor/.env                         │
│  日志文件          /tmp/aitutor-*.log                   │
├─────────────────────────────────────────────────────────┤
│  聊天路由：                                             │
│    公式/推导/数学  → 🔢 数学推导 Agent                  │
│    代码/实现/手写  → 💻 算法实现 Agent                   │
│    对比/区别/辨析  → 🧠 概念辨析 Agent                   │
├─────────────────────────────────────────────────────────┤
│  测验层次：                                             │
│    L1📋记忆  L2💡理解  L3🔧应用                         │
│    L4🔍分析  L5⚖️评价  L6🚀创造                         │
│    准确率>80%→升级  <50%→降级                           │
├─────────────────────────────────────────────────────────┤
│  知识图谱：                                             │
│    26 个实体  20 条关系  4 种实体类型                    │
│    5 种关系类型  Pyvis 交互式可视化                      │
│    无需 API Key 也能使用                                 │
└─────────────────────────────────────────────────────────┘
```

---

*文档版本 v1.0 · 如有问题请查看项目 README 或联系开发者*
