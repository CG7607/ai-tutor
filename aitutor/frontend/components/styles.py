"""全局自定义样式注入——深夜自习室主题."""


def 注入样式():
    """注入全应用的自定义 CSS 和 JS."""
    import streamlit as st

    st.markdown("""
    <style>
    /* ============================================
       深夜自习室 —— 全局主题
       ============================================ */

    /* ---------- 导入字体 ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

    /* ---------- 根变量 ---------- */
    :root {
        --amber: #F5A623;
        --amber-soft: rgba(245, 166, 35, 0.12);
        --amber-glow: rgba(245, 166, 35, 0.25);
        --bg-deep: #1A1D23;
        --bg-card: #252830;
        --bg-card-hover: #2C3039;
        --bg-input: #1E2026;
        --text-primary: #E8E6E3;
        --text-secondary: #9B9A96;
        --text-muted: #6B6A67;
        --border: #363840;
        --border-active: #F5A623;
        --green: #5CB85C;
        --red: #E05555;
        --blue: #5B9BD5;
        --purple: #9B7ED8;
        --radius: 8px;
        --radius-lg: 14px;
        --shadow: 0 2px 8px rgba(0,0,0,0.25);
        --shadow-lg: 0 8px 24px rgba(0,0,0,0.35);
    }

    /* ---------- 全局字体 ---------- */
    body, .stApp, .stMarkdown, p, span, div, button, input, textarea, select {
        font-family: 'Noto Sans SC', -apple-system, sans-serif !important;
    }
    code, pre, .stCodeBlock, .stCode {
        font-family: 'JetBrains Mono', 'Noto Sans SC', monospace !important;
    }

    /* ---------- 主背景 ---------- */
    .stApp {
        background: linear-gradient(160deg, #1A1D23 0%, #1F2229 50%, #1A1D23 100%);
    }

    /* ---------- 侧边栏 ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E2127 0%, #1A1D23 100%);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        color: var(--text-primary);
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.95rem;
        font-weight: 500;
        color: var(--text-secondary);
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    /* ---------- 标题 ---------- */
    h1 {
        font-weight: 700 !important;
        font-size: 2rem !important;
        letter-spacing: -0.02em !important;
        color: var(--text-primary) !important;
    }
    h2 {
        font-weight: 600 !important;
        font-size: 1.4rem !important;
        letter-spacing: -0.01em !important;
    }
    h3 {
        font-weight: 500 !important;
        font-size: 1.1rem !important;
    }

    /* ---------- 主标题区域 ---------- */
    .app-header {
        padding: 1.5rem 0 0.5rem 0;
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--amber);
        display: inline-block;
    }

    /* ---------- 卡片容器 ---------- */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }
    .card:hover {
        box-shadow: var(--shadow-lg);
        border-color: var(--border-active);
    }
    .card-accent {
        border-left: 3px solid var(--amber);
    }

    /* ---------- 指标卡片 ---------- */
    [data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 0.8rem 1rem !important;
        box-shadow: var(--shadow);
    }
    [data-testid="stMetric"] label {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.05em !important;
        color: var(--text-muted) !important;
        text-transform: uppercase;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: var(--amber) !important;
    }

    /* ---------- 按钮 ---------- */
    .stButton > button {
        font-family: 'Noto Sans SC', sans-serif !important;
        font-weight: 500 !important;
        border-radius: var(--radius) !important;
        border: 1px solid var(--border) !important;
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        transition: all 0.15s ease !important;
        letter-spacing: 0.02em;
    }
    .stButton > button:hover {
        border-color: var(--amber) !important;
        background: var(--amber-soft) !important;
        color: var(--amber) !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--amber) !important;
        border-color: var(--amber) !important;
        color: #1A1D23 !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #F7B84E !important;
        box-shadow: 0 0 20px var(--amber-glow);
    }

    /* ---------- 输入框 ---------- */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: var(--bg-input) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--text-primary) !important;
        font-family: 'Noto Sans SC', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--amber) !important;
        box-shadow: 0 0 0 2px var(--amber-soft) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }

    /* ---------- 密码框 ---------- */
    input[type="password"] {
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: 0.1em;
    }

    /* ---------- 选择框下拉 ---------- */
    .stSelectbox [data-baseweb="select"] {
        background: var(--bg-input) !important;
    }

    /* ---------- 聊天消息 ---------- */
    [data-testid="stChatMessage"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1rem 1.2rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: var(--shadow);
    }
    /* 用户消息特殊样式 */
    [data-testid="stChatMessage"][data-testid="stChatMessage"] {
        border-left: 3px solid var(--amber);
    }

    /* ---------- Agent 徽章 ---------- */
    .agent-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.03em;
        margin-bottom: 0.5rem;
    }

    /* ---------- 展开面板 ---------- */
    .streamlit-expanderHeader {
        font-weight: 500 !important;
        border-radius: var(--radius) !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
    }
    .streamlit-expanderHeader:hover {
        border-color: var(--amber) !important;
    }

    /* ---------- 单选框 ---------- */
    .stRadio > div {
        gap: 0.3rem;
    }
    .stRadio label {
        padding: 0.5rem 0.8rem !important;
        border-radius: var(--radius) !important;
        transition: background 0.12s ease;
    }
    .stRadio label:hover {
        background: var(--bg-card-hover) !important;
    }

    /* ---------- 分割线 ---------- */
    hr, .stDivider {
        border-color: var(--border) !important;
        margin: 0.8rem 0 !important;
    }

    /* ---------- 成功/警告/错误/信息 ---------- */
    .stAlert {
        border-radius: var(--radius) !important;
        border: none !important;
    }
    [data-testid="stSuccess"] { background: rgba(92,184,92,0.12) !important; color: var(--green) !important; }
    [data-testid="stWarning"] { background: rgba(245,166,35,0.12) !important; color: var(--amber) !important; }
    [data-testid="stError"]   { background: rgba(224,85,85,0.12) !important; color: var(--red) !important; }
    [data-testid="stInfo"]    { background: rgba(91,155,213,0.12) !important; color: var(--blue) !important; }

    /* ---------- 滚动条 ---------- */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    /* ---------- 隐藏默认组件 ---------- */
    [data-testid="stToolbar"] { display: none; }
    header[data-testid="stHeader"] { background: transparent !important; }
    .stDeployButton { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* ---------- 标签页 ---------- */
    .stTabs [data-baseweb="tab"] {
        font-family: 'Noto Sans SC', sans-serif !important;
        font-weight: 500;
        color: var(--text-secondary) !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--amber) !important;
        border-bottom-color: var(--amber) !important;
    }

    /* ---------- 响应式：移动端 ---------- */
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        .card { padding: 1rem; }
    }

    /* ---------- 动画 ---------- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stChatMessage {
        animation: fadeInUp 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)
