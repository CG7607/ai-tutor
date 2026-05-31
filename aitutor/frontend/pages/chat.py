"""智能问答页面——多智能体协作对话."""
import streamlit as st
import requests

from aitutor.frontend.user_data import 保存用户数据

BACKEND_URL = "http://localhost:8000"

AGENT_头像 = {
    "math": "🔢",
    "algorithm": "💻",
    "concept": "🧠",
}


def render_chat_page():
    """渲染智能问答页面."""
    from aitutor.frontend.components.agent_badge import render_agent_badge

    st.header("💬 智能问答")

    if not st.session_state.get("logged_in"):
        st.info("👈 请先在左侧边栏登录或注册")
        return

    st.caption("向 AI 导师组提问，三位专家为你解答《人工智能导论》相关问题")

    # ============ 提问建议（可折叠） ============
    with st.expander("💡 试试这些问题", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔢 数学推导：**")
            st.markdown("""
            - 推导反向传播中链式法则的计算过程
            - 为什么交叉熵损失比均方误差更适合分类？
            """)
            st.markdown("**💻 算法实现：**")
            st.markdown("""
            - 用 NumPy 从零实现 K-means 聚类
            - 手写一个简单的 CNN 前向传播
            """)
        with col2:
            st.markdown("**🧠 概念辨析：**")
            st.markdown("""
            - 生成式模型和判别式模型的本质区别？
            - 梯度消失和梯度爆炸有什么不同？
            """)
            st.markdown("**🔀 混合提问：**")
            st.markdown("""
            - 解释 Adam 优化器的原理并用代码实现
            """)

    # ============ 加载用户聊天记录 ============
    if not st.session_state.chat_history:
        st.session_state.chat_history = []

    # ============ 显示历史对话 ============
    for msg in st.session_state.chat_history:
        avatar = msg.get("avatar")
        with st.chat_message(msg["role"], avatar=avatar if avatar else None):
            if msg["role"] == "assistant" and "agent_name" in msg:
                render_agent_badge(msg["agent_name"])
            st.markdown(msg["content"])

    # ============ 聊天输入 ============
    if prompt := st.chat_input("输入你的问题，比如「梯度下降和随机梯度下降有什么区别？」"):
        # 显示用户消息
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt,
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        # 调用后端
        with st.chat_message("assistant"):
            with st.spinner("AI 导师思考中…"):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/chat",
                        json={
                            "message": prompt,
                            "history": [
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.chat_history[-7:-1]
                            ],
                        },
                        timeout=90,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        agent_name = data.get("agent_used", "concept")
                        render_agent_badge(agent_name)
                        st.markdown(data["reply"])

                        # 保存到全局聊天记录
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": data["reply"],
                            "agent_name": agent_name,
                            "avatar": AGENT_头像.get(agent_name, "🤖"),
                        })

                        # 持久化
                        保存用户数据(
                            st.session_state.username,
                            st.session_state.chat_history,
                            st.session_state.quiz_history,
                            st.session_state.wrong_answers,
                        )

                        # 显示子问题解答
                        if data.get("sub_replies"):
                            with st.expander("📋 相关子问题解答"):
                                for sub in data["sub_replies"]:
                                    st.caption(f"**{sub['agent']}**")
                                    st.markdown(sub["reply"])

                    else:
                        st.error(f"后端异常（状态码 {response.status_code}），请稍后重试。")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ 无法连接到后端服务，请确认 FastAPI 已启动。")
                except requests.exceptions.Timeout:
                    st.error("⏰ 请求超时，请重试。")
