"""Streamlit entry point for AITutor."""
import streamlit as st

st.set_page_config(
    page_title="AITutor - AI导论课程助教",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AITutor")
st.caption("基于多智能体协作的《人工智能导论》课程助教")

st.sidebar.title("导航")
page = st.sidebar.radio(
    "选择功能",
    ["💬 智能问答", "🕸️ 知识图谱", "📝 自适应测验"],
)

if page == "💬 智能问答":
    from aitutor.frontend.pages.chat import render_chat_page
    render_chat_page()
elif page == "🕸️ 知识图谱":
    st.info("知识图谱可视化即将上线...")
elif page == "📝 自适应测验":
    st.info("自适应测验即将上线...")
