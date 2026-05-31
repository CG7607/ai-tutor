"""AI导师入口——基于多智能体协作的《人工智能导论》课程助教."""
import streamlit as st

from aitutor.frontend.user_data import (
    用户存在, 注册用户, 验证密码, 加载用户数据, 保存用户数据,
)

st.set_page_config(
    page_title="AI导师——人工智能导论课程助教",
    page_icon="🤖",
    layout="wide",
)

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
                    elif not 用户存在(login_user):
                        st.error("该用户不存在，请先注册。")
                    elif not 验证密码(login_user, login_pass):
                        st.error("密码错误，请重试。")
                    else:
                        data = 加载用户数据(login_user)
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
                    elif 用户存在(reg_user):
                        st.error("该用户名已被注册，请换一个。")
                    else:
                        注册用户(reg_user, reg_pass)
                        data = 加载用户数据(reg_user)
                        st.session_state.logged_in = True
                        st.session_state.username = reg_user
                        st.session_state.chat_history = data["chat_history"]
                        st.session_state.quiz_history = data["quiz_history"]
                        st.session_state.wrong_answers = data["wrong_answers"]
                        st.session_state.current_question = None
                        st.session_state.show_feedback = False
                        st.success("注册成功！")
                        st.rerun()

        # 未登录时也显示导航（但功能和KG可用）
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
