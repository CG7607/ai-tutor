"""全局自定义样式注入——深夜自习室主题 v2."""


def 注入样式():
    """注入全应用的自定义 CSS."""
    import streamlit as st

    st.markdown("""<style>
    /* ============================================
       深夜自习室 v2 —— 精修主题
       ============================================ */

    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --amber: #F5A623;
        --amber-soft: rgba(245,166,35,0.10);
        --amber-glow: rgba(245,166,35,0.20);
        --amber-bright: #F7C04A;
        --bg-deep: #1A1D23;
        --bg-card: #252830;
        --bg-card-hover: #2C3039;
        --bg-input: #1E2026;
        --bg-elevated: #2A2D35;
        --text-primary: #E8E6E3;
        --text-secondary: #9B9A96;
        --text-muted: #6B6A67;
        --border: #363840;
        --border-light: #2E3139;
        --border-active: #F5A623;
        --green: #5CB85C;
        --green-bg: rgba(92,184,92,0.10);
        --red: #E05555;
        --red-bg: rgba(224,85,85,0.10);
        --blue: #5B9BD5;
        --blue-bg: rgba(91,155,213,0.10);
        --purple: #9B7ED8;
        --radius: 8px;
        --radius-lg: 14px;
        --radius-xl: 20px;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.2);
        --shadow: 0 2px 8px rgba(0,0,0,0.30);
        --shadow-lg: 0 8px 30px rgba(0,0,0,0.40);
        --transition: 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ============ 全局 ============ */
    body, .stApp, .stMarkdown, p, span, div, button, input, textarea, select {
        font-family: 'Noto Sans SC', -apple-system, 'PingFang SC', sans-serif !important;
    }
    code, pre, .stCodeBlock, .stCode, kbd {
        font-family: 'JetBrains Mono', 'Noto Sans SC', monospace !important;
    }
    .stApp {
        background: linear-gradient(165deg, #1A1D23 0%, #1C1F26 40%, #181B20 100%);
    }
    /* 微妙噪点纹理 */
    .stApp::before {
        content: '';
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
        pointer-events: none; z-index: 9999;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    /* ============ 隐藏默认 UI ============ */
    [data-testid="stToolbar"], .stDeployButton, #MainMenu, footer, header[data-testid="stHeader"] {
        display: none !important;
    }
    [data-testid="stDecoration"] { display: none; }

    /* ============ 标题层级 ============ */
    h1 {
        font-weight: 700 !important; font-size: 2rem !important;
        letter-spacing: -0.02em !important; color: var(--text-primary) !important;
        padding-bottom: 0.5rem; border-bottom: 2px solid var(--amber);
        display: inline-block; margin-bottom: 0.3rem;
    }
    h2 { font-weight: 600 !important; font-size: 1.35rem !important; letter-spacing: -0.01em !important; }
    h3 { font-weight: 500 !important; font-size: 1.05rem !important; }
    .stCaption { color: var(--text-muted) !important; font-size: 0.85rem; }

    /* ============ 侧边栏 ============ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1C1F26 0%, #181B20 100%);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 1rem; font-weight: 600; letter-spacing: 0.03em;
        color: var(--text-primary); border-bottom: 1px solid var(--border);
        padding-bottom: 0.5rem; margin-bottom: 0.8rem;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.06em;
        color: var(--text-muted); text-transform: uppercase;
    }

    /* 导航菜单——极简轻盈 */
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
        display: flex; flex-direction: column; gap: 2px;
    }
    [data-testid="stSidebar"] .stRadio label {
        padding: 0.45rem 0.6rem !important; margin: 0 !important;
        border-radius: 6px !important; font-size: 0.88rem;
        color: var(--text-secondary) !important;
        transition: all var(--transition); border: none;
        font-weight: 400;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: transparent !important; color: var(--text-primary) !important;
    }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: transparent !important; border: none !important;
        box-shadow: none !important;
        color: var(--amber) !important; font-weight: 600;
    }
    /* 选中态——左侧小圆点指示器 */
    [data-testid="stSidebar"] .stRadio label:has(input:checked)::before {
        content: '●'; font-size: 0.5rem; margin-right: 0.35rem;
        color: var(--amber); vertical-align: middle;
    }

    /* ============ 标签页 (登录/注册) ============ */
    .stTabs [data-baseweb="tab"] {
        font-weight: 500; color: var(--text-secondary) !important;
        padding: 0.5rem 0.8rem !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--amber) !important; border-bottom: 2px solid var(--amber) !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 0.8rem; }

    /* ============ 按钮体系 ============ */
    .stButton > button {
        font-family: 'Noto Sans SC', sans-serif !important; font-weight: 500 !important;
        border-radius: var(--radius) !important; border: 1px solid var(--border) !important;
        background: var(--bg-card) !important; color: var(--text-primary) !important;
        transition: all var(--transition) !important; letter-spacing: 0.02em;
    }
    .stButton > button:hover {
        border-color: var(--amber) !important; background: var(--amber-soft) !important;
        color: var(--amber) !important; transform: translateY(-1px);
    }
    .stButton > button:active { transform: translateY(0); }
    .stButton > button[kind="primary"] {
        background: var(--amber) !important; border-color: var(--amber) !important;
        color: #1A1D23 !important; font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--amber-bright) !important;
        box-shadow: 0 0 24px var(--amber-glow);
    }

    /* ============ 输入框 ============ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-input) !important; border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important; color: var(--text-primary) !important;
        font-size: 0.92rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--amber) !important;
        box-shadow: 0 0 0 3px var(--amber-soft) !important;
    }
    .stTextInput > div > div > input::placeholder { color: var(--text-muted) !important; }
    input[type="password"] { font-family: 'JetBrains Mono', monospace !important; letter-spacing: 0.12em; }
    .stSelectbox [data-baseweb="select"] { background: var(--bg-input) !important; border-radius: var(--radius) !important; }

    /* ============ 聊天消息 ============ */
    [data-testid="stChatMessage"] {
        background: var(--bg-card) !important; border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important; padding: 1rem 1.2rem !important;
        margin: 0.5rem 0 !important; box-shadow: var(--shadow-sm);
        animation: messageIn 0.25s ease;
    }
    [data-testid="stChatMessage"]:has(.stChatMessageAvatarUser),
    [data-testid="stChatMessage"][data-testid="stChatMessage"] {
        border-left: 3px solid var(--amber);
    }
    .stChatInput textarea {
        background: var(--bg-card) !important; border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important; color: var(--text-primary) !important;
        font-size: 0.95rem !important; padding: 0.8rem 1rem !important;
    }
    .stChatInput textarea:focus {
        border-color: var(--amber) !important; box-shadow: 0 0 0 3px var(--amber-soft) !important;
    }
    @keyframes messageIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ============ 指标卡片 ============ */
    [data-testid="stMetric"] {
        background: var(--bg-card); border: 1px solid var(--border);
        border-radius: var(--radius-lg); padding: 0.7rem 1rem !important;
        box-shadow: var(--shadow-sm); transition: all var(--transition);
    }
    [data-testid="stMetric"]:hover { border-color: var(--border-active); box-shadow: var(--shadow); }
    [data-testid="stMetric"] label {
        font-size: 0.7rem !important; font-weight: 600 !important;
        letter-spacing: 0.08em !important; color: var(--text-muted) !important;
        text-transform: uppercase;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.5rem !important; font-weight: 700 !important; color: var(--amber) !important;
    }

    /* ============ 展开面板 ============ */
    .streamlit-expanderHeader {
        font-weight: 500 !important; border-radius: var(--radius) !important;
        background: var(--bg-card) !important; border: 1px solid var(--border) !important;
        transition: all var(--transition);
    }
    .streamlit-expanderHeader:hover { border-color: var(--amber) !important; }
    .streamlit-expanderContent { border: 1px solid var(--border) !important;
        border-top: none !important; border-radius: 0 0 var(--radius) var(--radius) !important;
        padding: 1rem !important; }

    /* ============ 分割线 ============ */
    hr, .stDivider { border-color: var(--border) !important; margin: 0.6rem 0 !important; }

    /* ============ 提示框 ============ */
    .stAlert { border-radius: var(--radius) !important; border: none !important; font-weight: 450; }
    [data-testid="stSuccess"] { background: var(--green-bg) !important; color: var(--green) !important; border-left: 3px solid var(--green) !important; }
    [data-testid="stWarning"] { background: var(--amber-soft) !important; color: var(--amber) !important; border-left: 3px solid var(--amber) !important; }
    [data-testid="stError"]   { background: var(--red-bg) !important; color: var(--red) !important; border-left: 3px solid var(--red) !important; }
    [data-testid="stInfo"]    { background: var(--blue-bg) !important; color: var(--blue) !important; border-left: 3px solid var(--blue) !important; }

    /* ============ 单选/多选 ============ */
    .stRadio [role="radiogroup"] { gap: 3px; }
    .stRadio label { padding: 0.5rem 0.8rem !important; border-radius: var(--radius) !important; transition: background var(--transition); }
    .stRadio label:hover { background: var(--bg-card-hover) !important; }

    /* 测验选项美化 */
    [data-testid="stVerticalBlock"] .stRadio label {
        background: var(--bg-card); border: 1px solid var(--border);
        padding: 0.7rem 1rem !important; margin: 2px 0; border-radius: var(--radius) !important;
    }
    [data-testid="stVerticalBlock"] .stRadio label:hover {
        border-color: var(--amber) !important; background: var(--bg-card-hover) !important;
    }

    /* ============ 滚动条 ============ */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    /* ============ 表格 ============ */
    .stTable { border-radius: var(--radius); overflow: hidden; }
    .stTable th { background: var(--bg-card) !important; color: var(--amber) !important; font-weight: 600; }
    .stTable td { background: var(--bg-input) !important; border-color: var(--border) !important; }

    /* ============ 下拉菜单 popover ============ */
    [data-baseweb="popover"] { background: var(--bg-elevated) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; }
    [data-baseweb="menu"] [role="option"] { color: var(--text-primary) !important; }
    [data-baseweb="menu"] [role="option"]:hover { background: var(--bg-card-hover) !important; }

    /* ============ 响应式 ============ */
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
        .main .block-container { padding: 1rem; }
    }
    </style>""", unsafe_allow_html=True)
