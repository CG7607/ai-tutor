# 🤖 AI导师 —— 基于多智能体协作的《人工智能导论》课程助教

> 深夜自习室主题 · 多智能体协作 · 知识图谱 · 自适应测验

## 项目简介

AI导师是一个面向《人工智能导论》课程的智能教学辅助系统。系统通过三个专用 Agent 分工协作，结合课程知识图谱和自适应测验引擎，为学生提供个性化的学习体验。

## 核心功能

| 功能 | 说明 |
|------|------|
| 🤖 **多智能体问答** | Router 自动分类问题，调度数学推导/算法实现/概念辨析三个专家 Agent，支持文件上传作为上下文 |
| 🕸️ **交互知识图谱** | 26 个核心概念 + 20 条关系，点击节点弹出详情，LLM 生成七维度深度解读（核心思想/数学基础/历史/洞察/误区/应用/延伸） |
| 📝 **自适应测验** | 布鲁姆 6 层认知体系，LLM 生成题目 + 对抗式验证，准确率自适应调节难度，内建错题库 |
| 👤 **用户系统** | 注册/登录/密码加密，对话历史按会话管理，测验进度独立存储，每次登录自动新对话 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Streamlit |
| 后端 | FastAPI |
| LLM | OpenAI-compatible API（DeepSeek / 通义千问 / OpenAI） |
| 知识图谱 | NetworkX + Pyvis |
| 数据存储 | JSON 文件 + 用户独立目录 |
| 密码加密 | SHA-256 |

## 快速开始

```bash
# 1. 安装依赖
pip install -r aitutor/requirements.txt

# 2. 配置 API Key
cp aitutor/.env.example aitutor/.env
# 编辑 .env 填入 LLM_API_KEY

# 3. 启动
cd aitutor && bash run.sh

# 4. 打开浏览器
# http://localhost:8501
```

## 项目结构

```
aitutor/
├── backend/           # FastAPI 后端
│   ├── agents/        # 多智能体（Router + Math/Algo/Concept Agent）
│   ├── api/           # API 路由（chat / kg / quiz）
│   ├── knowledge_graph/  # 知识图谱引擎
│   ├── quiz/          # 自适应测验引擎
│   └── llm/           # LLM 客户端
├── frontend/          # Streamlit 前端
│   ├── pages/         # 页面（问答 / 图谱 / 测验）
│   ├── components/    # UI 组件（样式 / 徽章 / 渲染器 / 卡片）
│   └── user_data.py   # 用户数据管理
├── data/              # 数据文件
│   ├── syllabus.json  # 课程知识图谱种子数据
│   └── users/         # 用户数据（自动生成）
├── requirements.txt
├── run.sh
└── .env.example
```

## 界面主题

**深夜自习室** —— 深色背景 + 琥珀金点缀，自定义 CSS 注入，页面入场动画，全中文界面零英文。

## License

MIT
