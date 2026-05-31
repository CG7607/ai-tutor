"""AI导师入口——基于多智能体协作的《人工智能导论》课程助教."""
import hashlib
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


def _hash_password(password: str) -> str:
    """SHA-256 哈希密码."""
    return hashlib.sha256(password.encode()).hexdigest()


def _user_exists(name: str) -> bool:
    """检查用户是否已注册."""
    return (_get_user_dir(name) / "profile.json").exists()


def _register_user(name: str, password: str) -> bool:
    """注册新用户，返回是否成功."""
    d = _get_user_dir(name)
    d.mkdir(parents=True, exist_ok=True)
    profile = {"password_hash": _hash_password(password)}
    (d / "profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2))
    return True


def _verify_password(name: str, password: str) -> bool:
    """验证用户密码."""
    fp = _get_user_dir(name) / "profile.json"
    if not fp.exists():
        return False
    try:
        profile = json.loads(fp.read_text())
        return profile.get("password_hash") == _hash_password(password)
    except Exception:
        return False


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

# ============ 侧边栏：登录/注册 + 导航 ============
with st.sidebar:
    st.subheader("👤 账号")

    # 初始化
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
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

    # ============ 已登录状态 ============
    if st.session_state.logged_in:
        st.success(f"✅ {st.session_state.username}")
        qh = st.session_state.quiz_history
        if qh:
            c = sum(1 for h in qh if h.get("correct"))
            st.caption(f"已答 {len(qh)} 题  |  正确 {c} 题  |  错题 {len(st.session_state.wrong_answers)} 道")

        if st.button("🚪 退出登录", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.chat_history = []
            st.session_state.quiz_history = []
            st.session_state.wrong_answers = []
            st.session_state.student_level = 1
            st.session_state.current_question = None
            st.rerun()

        st.divider()
        st.subheader("🧭 导航")
        page = st.radio(
            "选择功能",
            ["💬 智能问答", "🕸️ 知识图谱", "📝 自适应测验"],
            label_visibility="collapsed",
        )

    # ============ 未登录状态 ============
    else:
        login_tab, reg_tab = st.tabs(["🔑 登录", "📝 注册"])

        with login_tab:
            login_user = st.text_input("用户名", key="login_user", placeholder="输入用户名")
            login_pass = st.text_input("密码", type="password", key="login_pass", placeholder="输入密码")

            col_btn, _ = st.columns([1, 2])
            with col_btn:
                if st.button("登录", type="primary", use_container_width=True):
                    if not login_user or not login_pass:
                        st.error("用户名和密码不能为空。")
                    elif not _user_exists(login_user):
                        st.error("该用户不存在，请先注册。")
                    elif not _verify_password(login_user, login_pass):
                        st.error("密码错误，请重试。")
                    else:
                        data = load_user_data(login_user)
                        st.session_state.logged_in = True
                        st.session_state.username = login_user
                        st.session_state.chat_history = data["chat_history"]
                        st.session_state.quiz_history = data["quiz_history"]
                        st.session_state.wrong_answers = data["wrong_answers"]
                        st.session_state.current_question = None
                        st.session_state.show_feedback = False
                        st.rerun()

        with reg_tab:
            reg_user = st.text_input("用户名", key="reg_user", placeholder="3-20个字符")
            reg_pass = st.text_input("密码", type="password", key="reg_pass", placeholder="至少4位")
            reg_pass2 = st.text_input("确认密码", type="password", key="reg_pass2", placeholder="再次输入密码")

            col_btn, _ = st.columns([1, 2])
            with col_btn:
                if st.button("注册", type="primary", use_container_width=True):
                    if not reg_user or not reg_pass:
                        st.error("用户名和密码不能为空。")
                    elif len(reg_user) < 3 or len(reg_user) > 20:
                        st.error("用户名需 3-20 个字符。")
                    elif len(reg_pass) < 4:
                        st.error("密码至少需要 4 位。")
                    elif reg_pass != reg_pass2:
                        st.error("两次密码不一致。")
                    elif _user_exists(reg_user):
                        st.error("该用户名已被注册，请换一个。")
                    else:
                        _register_user(reg_user, reg_pass)
                        data = load_user_data(reg_user)
                        st.session_state.logged_in = True
                        st.session_state.username = reg_user
                        st.session_state.chat_history = data["chat_history"]
                        st.session_state.quiz_history = data["quiz_history"]
                        st.session_state.wrong_answers = data["wrong_answers"]
                        st.session_state.current_question = None
                        st.session_state.show_feedback = False
                        st.success("注册成功！")
                        st.rerun()

        # 未登录也显示导航，但点击会提示
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
