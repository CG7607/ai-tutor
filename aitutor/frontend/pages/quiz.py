"""Adaptive quiz page with account system, wrong-answer bank, and auto-next."""
import json
import os
import streamlit as st
import requests
from datetime import datetime
from pathlib import Path

from aitutor.frontend.components.quiz_card import render_quiz_card, render_feedback

BACKEND_URL = "http://localhost:8000"
# 用户数据存储根目录
USER_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "users"

TOPICS = [
    "梯度下降", "反向传播", "CNN", "RNN/LSTM", "Transformer",
    "过拟合与正则化", "损失函数", "优化算法", "生成式模型",
    "K-means聚类", "SVM", "决策树",
]


def _get_user_dir(username: str) -> Path:
    return USER_DATA_DIR / username


def _load_user_data(username: str) -> dict:
    """加载用户的所有数据"""
    user_dir = _get_user_dir(username)
    user_dir.mkdir(parents=True, exist_ok=True)

    history_file = user_dir / "quiz_history.json"
    wrong_file = user_dir / "wrong_answers.json"

    history = []
    wrong_answers = []

    if history_file.exists():
        try:
            history = json.loads(history_file.read_text())
        except (json.JSONDecodeError, Exception):
            history = []
    if wrong_file.exists():
        try:
            wrong_answers = json.loads(wrong_file.read_text())
        except (json.JSONDecodeError, Exception):
            wrong_answers = []

    return {
        "history": history,
        "wrong_answers": wrong_answers,
    }


def _save_user_data(username: str, history: list, wrong_answers: list) -> None:
    """保存用户数据到磁盘"""
    user_dir = _get_user_dir(username)
    user_dir.mkdir(parents=True, exist_ok=True)

    (user_dir / "quiz_history.json").write_text(
        json.dumps(history, ensure_ascii=False, indent=2)
    )
    (user_dir / "wrong_answers.json").write_text(
        json.dumps(wrong_answers, ensure_ascii=False, indent=2)
    )


def _extract_answer_letter(user_selection: str) -> str:
    """从用户选择的完整选项文字中提取字母，如 'B. xxx' → 'B'"""
    if not user_selection:
        return ""
    user_selection = user_selection.strip()
    if user_selection and user_selection[0].upper() in "ABCD":
        return user_selection[0].upper()
    return user_selection


def _check_answer(user_selection: str, correct_answer: str) -> bool:
    """对比用户选择和正确答案"""
    user_letter = _extract_answer_letter(user_selection)
    correct_letter = correct_answer.strip().upper()
    if len(correct_letter) > 1:
        correct_letter = correct_letter[0]
    return user_letter == correct_letter


def render_quiz_page():
    """Render the adaptive quiz page with account, wrong-answer bank, and next button."""
    st.title("📝 自适应测验")
    st.caption("基于布鲁姆认知目标分类的动态测验系统")

    # ============ 账号系统 ============
    with st.sidebar:
        st.subheader("👤 账号")

        if "username" not in st.session_state:
            st.session_state.username = ""

        username = st.text_input(
            "输入你的用户名",
            value=st.session_state.username,
            placeholder="例如：张三",
            key="username_input",
        )

        if username and username != st.session_state.username:
            st.session_state.username = username
            # 加载用户存档
            data = _load_user_data(username)
            st.session_state.quiz_history = data["history"]
            st.session_state.wrong_answers = data["wrong_answers"]
            st.session_state.student_level = 1
            st.session_state.current_question = None
            st.session_state.show_feedback = False
            st.session_state.last_correct = False
            st.rerun()

        if not username:
            st.warning("👈 请先输入用户名开始学习")
            st.stop()

        st.divider()

        # ============ 学习进度 ============
        st.subheader("📊 学习进度")

        # Initialize session state
        if "quiz_history" not in st.session_state:
            st.session_state.quiz_history = []
        if "wrong_answers" not in st.session_state:
            st.session_state.wrong_answers = []
        if "student_level" not in st.session_state:
            st.session_state.student_level = 1
        if "current_question" not in st.session_state:
            st.session_state.current_question = None
        if "show_feedback" not in st.session_state:
            st.session_state.show_feedback = False
        if "last_correct" not in st.session_state:
            st.session_state.last_correct = False

        level = st.session_state.student_level
        st.metric("当前布鲁姆层次", f"L{level}")

        history = st.session_state.quiz_history
        if history:
            correct_count = sum(1 for h in history if h.get("correct"))
            total = len(history)
            accuracy = correct_count / total * 100
            st.metric("准确率", f"{accuracy:.0f}%")
            st.metric("已答题数", f"{total}（对{correct_count}错{total - correct_count}）")

            if accuracy >= 80:
                st.success("🎉 准备升级！")
            elif accuracy < 50:
                st.warning("📚 需要巩固基础")
            else:
                st.info("👍 继续加油")
        else:
            st.caption("尚未答题")

        # 错题数量
        wrong_count = len(st.session_state.wrong_answers)
        if wrong_count > 0:
            st.metric("📌 错题库", f"{wrong_count}题")

        st.divider()
        if st.button("🔄 重置进度", use_container_width=True):
            st.session_state.quiz_history = []
            st.session_state.wrong_answers = []
            st.session_state.student_level = 1
            st.session_state.current_question = None
            st.session_state.show_feedback = False
            st.session_state.last_correct = False
            _save_user_data(username, [], [])
            st.rerun()

        # 保存按钮
        if st.button("💾 手动保存", use_container_width=True):
            _save_user_data(username, st.session_state.quiz_history, st.session_state.wrong_answers)
            st.success("已保存！")

        # ============ 错题本 ============
        if st.session_state.wrong_answers:
            st.divider()
            st.subheader("📌 错题库")
            for i, wa in enumerate(st.session_state.wrong_answers[-10:]):
                with st.expander(f"错题{i+1}: {wa.get('question', '')[:30]}...", expanded=False):
                    st.caption(f"知识点：{wa.get('topic', '')}  |  你的答案：{wa.get('user_answer', '')}")
                    st.markdown(f"**正确答案：{wa.get('correct_answer', '')}**")
                    st.markdown(wa.get("explanation", ""))
            if st.button("🗑️ 清空错题库", use_container_width=True):
                st.session_state.wrong_answers = []
                _save_user_data(username, st.session_state.quiz_history, [])
                st.rerun()

    # ============ 主区域 ============
    st.subheader("🎯 选择知识点")
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.selectbox("选择知识点", TOPICS, key="topic_select")
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
                        timeout=90,
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

    # ============ 显示当前题目 ============
    q = st.session_state.current_question
    if q:
        st.divider()

        # 自适应提示
        action = q.get("adaptive_action", "maintain")
        if action == "upgrade":
            st.info("📈 准确率 > 80%，难度已升级！")
        elif action == "downgrade":
            st.warning("📉 准确率 < 50%，回到上一层次巩固")

        answer = render_quiz_card(
            question=q["question"],
            options=q.get("options"),
            question_type=q.get("question_type", "single_choice"),
            bloom_level=q.get("bloom_level", 1),
            question_id=q.get("question_id", "unknown"),
        )

        # ============ 处理答案提交 ============
        if answer is not None and not st.session_state.show_feedback:
            correct = _check_answer(answer, q.get("answer", ""))
            st.session_state.show_feedback = True
            st.session_state.last_correct = correct

            q_topic = q.get("topic", topic)

            # 记录答题历史
            st.session_state.quiz_history.append({
                "question_id": q["question_id"],
                "topic": q_topic,
                "question": q["question"],
                "correct": correct,
                "bloom_level": q.get("bloom_level", 1),
                "timestamp": datetime.now().isoformat(),
            })

            # 如果答错，加入错题库
            if not correct:
                st.session_state.wrong_answers.append({
                    "question_id": q["question_id"],
                    "topic": q_topic,
                    "question": q["question"],
                    "options": q.get("options", []),
                    "user_answer": answer,
                    "correct_answer": q.get("answer", ""),
                    "explanation": q.get("explanation", ""),
                    "bloom_level": q.get("bloom_level", 1),
                    "timestamp": datetime.now().isoformat(),
                })

            # 自适应调整层次
            if action == "upgrade":
                st.session_state.student_level = min(6, st.session_state.student_level + 1)
            elif action == "downgrade":
                st.session_state.student_level = max(1, st.session_state.student_level - 1)

            # 保存到磁盘
            _save_user_data(
                st.session_state.username,
                st.session_state.quiz_history,
                st.session_state.wrong_answers,
            )

            render_feedback(correct, q.get("answer", ""), q.get("explanation", ""))
            st.rerun()

        elif st.session_state.show_feedback and q:
            render_feedback(
                st.session_state.get("last_correct", False),
                q.get("answer", ""),
                q.get("explanation", ""),
            )

            # ============ 「下一题」按钮 ============
            st.divider()
            if st.button("➡️ 生成下一题", type="primary", use_container_width=True):
                with st.spinner("正在生成新题目..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_URL}/api/quiz/generate",
                            json={
                                "topic": topic,
                                "student_level": st.session_state.student_level,
                                "history": st.session_state.quiz_history,
                            },
                            timeout=90,
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
