"""AI导师入口——基于多智能体协作的《人工智能导论》课程助教."""
import json
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="AI导师——人工智能导论课程助教",
    page_icon="🤖",
    layout="wide",
)

# ============ 全局用户数据管理 ============
USER_DATA_DIR = Path(__file__).parent.parent / "data" / "users"


def _get_user_dir(name: str) -> Path:
    return USER_DATA_DIR / name


def load_user_data(name: str) -> dict:
    """加载用户全部数据."""
    d = _get_user_dir(name)
    d.mkdir(parents=True, exist_ok=True)

    def _read(filename):
        fp = d / filename
        if fp.exists():
            try:
                return json.loads(fp.read_text())
            except Exception:
                return []
        return []

    return {
        "chat_history": _read("chat_history.json"),
        "quiz_history": _read("quiz_history.json"),
        "wrong_answers": _read("wrong_answers.json"),
    }


def save_user_data(name: str, chat_history: list, quiz_history: list, wrong_answers: list) -> None:
    """保存用户全部数据到磁盘."""
    d = _get_user_dir(name)
    d.mkdir(parents=True, exist_ok=True)
    (d / "chat_history.json").write_text(json.dumps(chat_history, ensure_ascii=False, indent=2))
    (d / "quiz_history.json").write_text(json.dumps(quiz_history, ensure_ascii=False, indent=2))
    (d / "wrong_answers.json").write_text(json.dumps(wrong_answers, ensure_ascii=False, indent=2))


# ============ 页面头部 ============
st.title("🤖 AI导师")
st.caption("基于多智能体协作的《人工智能导论》课程助教")

# ============ 侧边栏：全局账号 + 导航 ============
with st.sidebar:
    st.subheader("👤 账号")

    # 初始化 session state
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "quiz_history" not in st.session_state:
        st.session_state.quiz_history = []
    if "wrong_answers" not in st.session_state:
        st.session_state.wrong_answers = []
    if "student_level" not in st.session_state:
        st.session_state.student_level = 1

    username = st.text_input(
        "输入用户名",
        value=st.session_state.username,
        placeholder="例如：张三",
        key="global_username",
    )

    if username and username != st.session_state.username:
        data = load_user_data(username)
        st.session_state.username = username
        st.session_state.chat_history = data["chat_history"]
        st.session_state.quiz_history = data["quiz_history"]
        st.session_state.wrong_answers = data["wrong_answers"]
        # 清除临时状态
        st.session_state.current_question = None
        st.session_state.show_feedback = False
        st.rerun()

    if not username:
        st.warning("👈 请输入用户名开始使用")
    else:
        st.success(f"✅ 当前用户：{username}")
        qh = st.session_state.quiz_history
        if qh:
            c = sum(1 for h in qh if h.get("correct"))
            st.caption(f"已答 {len(qh)} 题  |  正确 {c} 题  |  错题 {len(st.session_state.wrong_answers)} 道")

    st.divider()
    st.subheader("🧭 导航")
    page = st.radio(
        "选择功能",
        ["💬 智能问答", "🕸️ 知识图谱", "📝 自适应测验"],
        label_visibility="collapsed",
    )


# ============ 页面路由 ============
if page == "💬 智能问答":
    from aitutor.frontend.pages.chat import render_chat_page
    render_chat_page()
elif page == "🕸️ 知识图谱":
    from aitutor.frontend.pages.knowledge_graph import render_kg_page
    render_kg_page()
elif page == "📝 自适应测验":
    from aitutor.frontend.pages.quiz import render_quiz_page
    render_quiz_page()
