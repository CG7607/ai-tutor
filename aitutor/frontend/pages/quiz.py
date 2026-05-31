"""Adaptive quiz page."""
import streamlit as st
import requests

from aitutor.frontend.components.quiz_card import render_quiz_card, render_feedback

BACKEND_URL = "http://localhost:8000"

TOPICS = [
    "梯度下降", "反向传播", "CNN", "RNN/LSTM", "Transformer",
    "过拟合与正则化", "损失函数", "优化算法", "生成式模型",
    "K-means聚类", "SVM", "决策树",
]


def render_quiz_page():
    """Render the adaptive quiz page."""
    st.title("📝 自适应测验")
    st.caption("基于布鲁姆认知目标分类的动态测验系统")

    # Initialize session state
    if "quiz_history" not in st.session_state:
        st.session_state.quiz_history = []
    if "student_level" not in st.session_state:
        st.session_state.student_level = 1
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "show_feedback" not in st.session_state:
        st.session_state.show_feedback = False

    # Sidebar: student progress
    with st.sidebar:
        st.subheader("📊 学习进度")

        level = st.session_state.student_level
        st.metric("当前布鲁姆层次", f"L{level}")

        history = st.session_state.quiz_history
        if history:
            correct_count = sum(1 for h in history if h.get("correct"))
            accuracy = correct_count / len(history) * 100
            st.metric("准确率", f"{accuracy:.0f}%")
            st.metric("已答题数", len(history))

            if accuracy >= 80:
                st.success("🎉 准备升级！")
            elif accuracy < 50:
                st.warning("📚 需要巩固基础")
            else:
                st.info("👍 继续加油")
        else:
            st.caption("尚未答题")

        st.divider()
        if st.button("🔄 重置进度"):
            st.session_state.quiz_history = []
            st.session_state.student_level = 1
            st.session_state.current_question = None
            st.session_state.show_feedback = False
            st.rerun()

    # Main area: topic selection
    st.subheader("🎯 选择知识点")
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.selectbox("", TOPICS, label_visibility="collapsed")
    with col2:
        if st.button("🎲 生成题目", type="primary", use_container_width=True):
            with st.spinner("生成题目中..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/quiz/generate",
                        json={
                            "topic": topic,
                            "student_level": st.session_state.student_level,
                            "history": st.session_state.quiz_history,
                        },
                        timeout=60,
                    )
                    if response.status_code == 200:
                        st.session_state.current_question = response.json()
                        st.session_state.show_feedback = False
                        st.rerun()
                    else:
                        st.error(f"生成失败: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ 无法连接到后端")
                except requests.exceptions.Timeout:
                    st.error("⏰ 生成超时，请重试")

    # Display current question
    q = st.session_state.current_question
    if q:
        st.divider()

        # Show adaptive action
        action = q.get("adaptive_action", "maintain")
        if action == "upgrade":
            st.info("📈 你在当前层次表现优异，难度已提升！")
        elif action == "downgrade":
            st.warning("📉 返回上一层次巩固基础")

        answer = render_quiz_card(
            question=q["question"],
            options=q.get("options"),
            question_type=q.get("question_type", "single_choice"),
            bloom_level=q.get("bloom_level", 1),
            question_id=q.get("question_id", "unknown"),
        )

        # Handle answer submission
        if answer is not None and not st.session_state.show_feedback:
            correct = answer == q["answer"]
            st.session_state.show_feedback = True
            st.session_state.last_correct = correct  # 保存结果，供重渲染后使用

            # Record in history (使用生成题目时的 topic，防止切换)
            st.session_state.quiz_history.append({
                "question_id": q["question_id"],
                "topic": q.get("topic", topic),
                "correct": correct,
                "bloom_level": q["bloom_level"],
            })

            # Update level based on adaptive action
            if action == "upgrade":
                st.session_state.student_level = min(6, st.session_state.student_level + 1)
            elif action == "downgrade":
                st.session_state.student_level = max(1, st.session_state.student_level - 1)

            render_feedback(correct, q["answer"], q["explanation"])
            st.rerun()

        elif st.session_state.show_feedback and q:
            render_feedback(
                st.session_state.get("last_correct", False),
                q["answer"],
                q["explanation"],
            )
