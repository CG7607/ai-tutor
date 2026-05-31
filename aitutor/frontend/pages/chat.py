"""Chat interface page — main Q&A interaction with multi-agent system."""
import streamlit as st
import requests
import json

BACKEND_URL = "http://localhost:8000"

AGENT_AVATARS = {
    "math": "🔢",
    "algorithm": "💻",
    "concept": "🧠",
}


def render_chat_page():
    """Render the main chat interface."""
    from aitutor.frontend.components.agent_badge import render_agent_badge

    st.title("💬 智能问答")
    st.caption("向 AITutor 提问，AI 导师组将为你解答《人工智能导论》相关问题")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar")):
            if msg["role"] == "assistant" and "agent_name" in msg:
                render_agent_badge(msg["agent_name"])
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("输入你的问题，比如「梯度下降和SGD有什么区别？」"):
        # Display user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call backend
        with st.chat_message("assistant"):
            with st.spinner("AI 导师思考中..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/chat",
                        json={
                            "message": prompt,
                            "history": [
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages[-6:]
                            ],
                        },
                        timeout=60,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        agent_name = data.get("agent_used", "concept")
                        render_agent_badge(agent_name)
                        st.markdown(data["reply"])

                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": data["reply"],
                            "agent_name": agent_name,
                            "avatar": AGENT_AVATARS.get(agent_name, "🤖"),
                        })

                        # Show sub-replies if any
                        if data.get("sub_replies"):
                            with st.expander("📋 相关子问题解答"):
                                for sub in data["sub_replies"]:
                                    st.caption(f"**{sub['agent']}**")
                                    st.markdown(sub["reply"])
                    else:
                        st.error(f"后端错误: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ 无法连接到后端服务。请确保 FastAPI 服务已启动（`uvicorn backend.main:app --reload`）")
                except requests.exceptions.Timeout:
                    st.error("⏰ 请求超时，请重试。")

    # Sidebar tips
    with st.sidebar:
        st.subheader("💡 试试这些问题")
        st.markdown("""
        **数学推导：**
        - 推导反向传播中链式法则的具体计算过程
        - 为什么交叉熵损失对分类问题比 MSE 更好？

        **算法实现：**
        - 用 NumPy 从零实现 K-means 聚类
        - 手写一个简单的 CNN 前向传播

        **概念辨析：**
        - 生成式模型和判别式模型的本质区别是什么？
        - L1 正则化和 L2 正则化在实际效果上有什么不同？

        **混合提问：**
        - 解释 Adam 优化器的原理并用代码实现
        """)
