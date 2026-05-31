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

from aitutor.frontend.components.styles import 注入样式
注入样式()

# ============ 页面头部 ============
st.title("AI导师")
st.caption("基于多智能体协作的《人工智能导论》课程助教")

# ============ 侧边栏 ============
with st.sidebar:
    st.subheader("账号")

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

    # ---------- 已登录 ----------
    if st.session_state.logged_in:
        st.success(f"已登录：{st.session_state.username}")
        qh = st.session_state.quiz_history
        if qh:
            c = sum(1 for h in qh if h.get("correct"))
            st.caption(f"已答 {len(qh)} 题  ·  正确 {c} 题  ·  错题 {len(st.session_state.wrong_answers)} 道")

        if st.button("退出登录", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.chat_history = []
            st.session_state.quiz_history = []
            st.session_state.wrong_answers = []
            st.session_state.student_level = 1
            st.session_state.current_question = None
            st.rerun()

        st.divider()
        st.subheader("导航")
        page = st.radio(
            "选择模块",
            ["问答", "图谱", "测验"],
            label_visibility="collapsed",
        )

    # ---------- 未登录 ----------
    else:
        登录页, 注册页 = st.tabs(["登录", "注册"])

        with 登录页:
            u = st.text_input("用户名", key="login_u", placeholder="输入用户名")
            p = st.text_input("密码", type="password", key="login_p", placeholder="输入密码")
            if st.button("登录", type="primary", use_container_width=True):
                if not u or not p:
                    st.error("用户名和密码不能为空")
                elif not 用户存在(u):
                    st.error("用户不存在，请先注册")
                elif not 验证密码(u, p):
                    st.error("密码错误")
                else:
                    d = 加载用户数据(u)
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.chat_history = d["chat_history"]
                    st.session_state.quiz_history = d["quiz_history"]
                    st.session_state.wrong_answers = d["wrong_answers"]
                    st.session_state.current_question = None
                    st.session_state.show_feedback = False
                    st.rerun()

        with 注册页:
            u2 = st.text_input("用户名", key="reg_u", placeholder="3—20 个字符")
            p2 = st.text_input("密码", type="password", key="reg_p", placeholder="至少 4 位")
            p3 = st.text_input("确认密码", type="password", key="reg_p2", placeholder="再次输入")
            if st.button("注册", type="primary", use_container_width=True):
                if not u2 or not p2:
                    st.error("用户名和密码不能为空")
                elif len(u2) < 3 or len(u2) > 20:
                    st.error("用户名需 3—20 个字符")
                elif len(p2) < 4:
                    st.error("密码至少 4 位")
                elif p2 != p3:
                    st.error("两次密码不一致")
                elif 用户存在(u2):
                    st.error("该用户名已被注册")
                else:
                    注册用户(u2, p2)
                    d = 加载用户数据(u2)
                    st.session_state.logged_in = True
                    st.session_state.username = u2
                    st.session_state.chat_history = d["chat_history"]
                    st.session_state.quiz_history = d["quiz_history"]
                    st.session_state.wrong_answers = d["wrong_answers"]
                    st.session_state.current_question = None
                    st.rerun()

        st.divider()
        st.subheader("导航")
        page = st.radio(
            "选择模块",
            ["问答", "图谱", "测验"],
            label_visibility="collapsed",
        )


# ============ 页面路由 ============
if page == "问答":
    from aitutor.frontend.pages.chat import render_chat_page
    render_chat_page()
elif page == "图谱":
    from aitutor.frontend.pages.knowledge_graph import render_kg_page
    render_kg_page()
elif page == "测验":
    from aitutor.frontend.pages.quiz import render_quiz_page
    render_quiz_page()
