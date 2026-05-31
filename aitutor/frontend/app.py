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
    from aitutor.frontend.pages.knowledge_graph import render_kg_page
    render_kg_page()
elif page == "📝 自适应测验":
    from aitutor.frontend.pages.quiz import render_quiz_page
    render_quiz_page()
