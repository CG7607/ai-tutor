# AITutor —— 基于多智能体协作的《人工智能导论》课程助教

> 设计文档 | 2026-05-31 | 版本 v1.0

## 1. 项目概述

### 1.1 目标

构建一个基于多智能体协作的 AI 教学辅助系统，服务《人工智能导论》课程。系统通过三个专用 Agent（数学推导、算法实现、概念辨析）分工协作，结合课程知识图谱和自适应测验引擎，为学生提供个性化的学习体验。

### 1.2 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Streamlit | Python 原生 Web UI，chat 组件 + 可视化组件 |
| 后端 | FastAPI | 异步 RESTful API，适合多 Agent 并发调度 |
| LLM API | DeepSeek / 通义千问 | 国内模型，中文好、性价比高 |
| 知识图谱 | NetworkX + JSON | 轻量内存图引擎，无需外部图数据库 |
| 图表渲染 | Matplotlib + Pyvis + Mermaid | 公式图、交互式图谱、概念关系图 |
| 数据存储 | JSON 文件 | 课程大纲、知识图谱、测验题库持久化 |

### 1.3 项目结构

```
aitutor/
├── backend/
│   ├── main.py                # FastAPI 入口，挂载所有路由
│   ├── agents/
│   │   ├── router.py          # 路由 Agent — 问题分类与调度
│   │   ├── math_agent.py      # 数学推导 Agent
│   │   ├── algorithm_agent.py # 算法实现 Agent
│   │   └── concept_agent.py   # 概念辨析 Agent
│   ├── knowledge_graph/
│   │   ├── builder.py         # LLM 驱动的图谱构建
│   │   ├── query.py           # 图谱检索（1-hop 扩展）
│   │   └── models.py          # 实体/关系 Pydantic 模型
│   ├── quiz/
│   │   ├── generator.py       # 测验生成 Pipeline
│   │   ├── bloom.py           # 布鲁姆认知层次分类器
│   │   └── models.py          # 题目/答案 Pydantic 模型
│   └── llm/
│       └── client.py          # LLM API 统一封装（多 provider 适配）
├── frontend/
│   ├── app.py                 # Streamlit 入口 + 页面路由
│   ├── pages/
│   │   ├── chat.py            # 聊天界面（主导航）
│   │   ├── knowledge_graph.py # 知识图谱可视化面板
│   │   └── quiz.py            # 自适应测验交互面板
│   └── components/
│       ├── agent_badge.py     # Agent 身份标识组件
│       ├── kg_renderer.py     # 知识图谱渲染组件
│       └── quiz_card.py       # 测验题目卡组件
└── data/
    ├── syllabus.json           # 课程大纲结构（种子数据）
    ├── knowledge_graph.json    # 知识图谱持久化文件
    └── quiz_history.json       # 学生答题记录
```

---

## 2. 多智能体协作系统

### 2.1 架构

```
用户提问 → Router Agent（分类+调度）
                │
      ┌─────────┼─────────┐
      ▼         ▼         ▼
   MathAgent  AlgoAgent  ConceptAgent
      │         │         │
      └─────────┼─────────┘
                ▼
           格式化 → 返回前端
```

### 2.2 三个 Specialist Agent

#### 数学推导 Agent (`math_agent`)
- **职责**：公式推导、线性代数/概率论/信息论讲解
- **系统提示词核心**：「你是 AI 数学教授，用 LaTeX 严谨推导公式，同时给出直觉解释」
- **输出**：Markdown + LaTeX 公式块，必要时生成 matplotlib 图表（梯度下降路径、概率分布图等）

#### 算法实现 Agent (`algorithm_agent`)
- **职责**：从零手写 K-means、CNN、反向传播、Transformer 等经典算法
- **系统提示词核心**：「你是算法导师，用纯 Python/NumPy 实现，逐行注释物理意义，不允许调 sklearn 等高层 API」
- **输出**：完整可运行代码 + 逐行注释 + 复杂度分析 + 算例运行结果

#### 概念辨析 Agent (`concept_agent`)
- **职责**：对比易混淆概念对（生成式 vs 判别式、梯度消失 vs 梯度爆炸、Bagging vs Boosting）
- **系统提示词核心**：「你是概念架构师，用对比表格揭示本质差异，结合知识图谱展示概念在课程体系中的位置」
- **输出**：对比表格 + Mermaid 知识图谱子图 + 通俗类比

### 2.3 Router 调度逻辑

Router 本身也是一个 LLM 调用，使用分类 Prompt：

```
分析以下问题，输出 JSON：
{
  "primary_agent": "math" | "algorithm" | "concept",
  "sub_questions": ["子问题1", "子问题2"],  // 如需要多 Agent
  "knowledge_graph_nodes": ["相关概念1", "相关概念2"]
}

判定规则：
- 包含公式/推导/概率/矩阵/证明 → math
- 包含"实现/手写/代码/how to code" → algorithm
- 包含"区别/对比/辨析/区别是什么" → concept
- 混合提问 → 拆分子问题，依次调用对应 Agent
```

### 2.4 API 接口

```
POST /api/chat
Request:
{
  "message": "梯度下降和随机梯度下降有什么区别？",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}

Response:
{
  "agent_used": "concept_agent",
  "router_analysis": {
    "primary_agent": "concept",
    "knowledge_graph_nodes": ["梯度下降", "SGD", "优化算法"]
  },
  "reply": "## 梯度下降 vs 随机梯度下降\n\n...",
  "kg_context": {
    "nodes": ["梯度下降", "SGD"],
    "relations": [{"source": "梯度下降", "target": "SGD", "type": "VARIANT_OF"}]
  }
}
```

---

## 3. 课程知识图谱

### 3.1 实体与关系模型

**实体类型：**

| 类型 | 说明 | 示例 |
|------|------|------|
| Concept | 核心概念 | 梯度下降、CNN、反向传播 |
| Person | 领域人物 | Hinton、LeCun、李飞飞 |
| Algorithm | 具体算法 | K-means, SVM, Transformer |
| Prerequisite | 前置知识 | 线性代数、概率论、Python |

**关系类型：**
- `PREREQUISITE_OF` — 前置依赖（线性代数 → 梯度下降）
- `VARIANT_OF` — 变体关系（SGD → 梯度下降）
- `DERIVES_FROM` — 推导来源（Adam → SGD）
- `PROPOSED` — 提出者（Hinton → Dropout）
- `APPLIED_IN` — 应用领域（CNN → 图像识别）
- `CONTRASTS_WITH` — 对比关系（生成式 ⟷ 判别式）

### 3.2 构建流程

```
syllabus.json（人工整理的种子数据，20-30 个核心概念）
        │
        ▼
  LLM 实体抽取（从概念描述中自动提取新实体和关系）
        │
        ▼
  人工审核（检查抽取质量，去重纠错）
        │
        ▼
  knowledge_graph.json（NetworkX 图持久化）
```

### 3.3 查询流程

1. 解析用户问题，提取关键词
2. 在图谱中匹配实体节点
3. 执行 1-hop 邻居扩展（找出所有直接关联的概念）
4. 将图谱上下文注入 Agent 的系统提示词
5. Agent 生成回答时，附带知识图谱子图的可视化数据

### 3.4 前端可视化

- 使用 **Pyvis** 渲染交互式网络图（可拖拽、缩放）
- 概念节点按类别着色
- 1-hop 相关节点高亮，其余半透明
- 点击节点可展开/折叠子图

---

## 4. 自适应测验生成

### 4.1 布鲁姆认知层次体系

| 层次 | 关键词 | 题型 | 计分权重 |
|------|--------|------|---------|
| L1 记忆 | 列举、定义、复述 | 单选题/填空题 | 1 |
| L2 理解 | 解释、总结、举例 | 多选题/简答 | 1.5 |
| L3 应用 | 计算、实现、求解 | 计算题/编程题 | 2 |
| L4 分析 | 对比、区分、解构 | 对比题/案例分析 | 2.5 |
| L5 评价 | 评判、论证、推荐 | 论证题 | 3 |
| L6 创造 | 设计、构建、综合 | 开放设计题 | 4 |

### 4.2 自适应调节算法

```
学生当前层次 = L
准确率 = 最近N题答对数 / N

IF 准确率 > 80% → 升级到 L+1
ELSE IF 准确率 < 50% → 降级到 L-1（最低 L1）
ELSE → 保持当前层次

下次出题时：优先覆盖学生未答过的知识点
```

### 4.3 生成 Pipeline

```
知识点 + 布鲁姆层次 + 学生薄弱点
        │
        ▼
  LLM 题面生成（指定层次、题型、知识点）
        │
        ▼
  LLM 答案+解析生成（同步生成标准答案和详细解析）
        │
        ▼
  对抗式验证（另一个 LLM 调用检查：答案是否正确、题面是否有歧义）
        │
        ▼
  返回 → { 题面, 选项, 答案, 解析, 布鲁姆层次, 自适应建议 }
```

### 4.4 API 接口

```
POST /api/quiz/generate
Request:
{
  "topic": "梯度下降",
  "student_level": 2,
  "history": [
    {"question_id": "q1", "correct": true, "topic": "线性回归"},
    {"question_id": "q2", "correct": false, "topic": "梯度下降"}
  ]
}

Response:
{
  "question": "以下关于 SGD 的描述正确的是？",
  "options": ["A...", "B...", "C...", "D..."],
  "answer": "B",
  "explanation": "SGD 每次只用一个小批量样本...",
  "bloom_level": 2,
  "adaptive_action": "maintain"
}

POST /api/quiz/submit
Request:
{
  "question_id": "q3",
  "student_answer": "B",
  "correct": true
}

Response:
{
  "acknowledged": true,
  "new_level": 2,
  "next_action": "maintain"
}
```

---

## 5. 数据流全景

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│ syllabus.json│────▶│ kg/builder  │────▶│ knowledge_   │
│ (种子数据)   │     │ (LLM 抽取)  │     │ graph.json   │
└─────────────┘     └─────────────┘     └──────┬───────┘
                                               │
                    ┌─────────────┐            │
 用户提问 ────────▶│ router.py   │◀───────────┘
                    │ (分类+调度)  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         math_agent  algo_agent  concept_agent
              │            │            │
              └────────────┼────────────┘
                           ▼
                     格式化 → Streamlit 前端
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              聊天面板显示   知识图谱子图渲染
```

---

## 6. 错误处理策略

| 场景 | 处理方式 |
|------|---------|
| LLM API 超时/不可用 | 返回友好提示「AI 导师暂时繁忙」，前端显示重试按钮 |
| Router 分类模糊 | 默认降级到 Concept Agent（最通用），同时提示用户澄清问题 |
| 知识图谱未命中 | 返回空图谱上下文，Agent 仅凭自身知识回答 |
| 测验验证失败 | 丢弃该题，重新生成并记录日志 |
| 图谱构建抽取异常 | 人工审核队列 + 降级到纯种子数据 |

---

## 7. 后续扩展（v2）

- 对话历史持久化（SQLite）
- 多学生身份与进度追踪
- PDF 教材自动解析
- Agent 回答质量评分与反馈闭环
- Docker 沙盒执行算法代码
