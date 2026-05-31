"""自适应测验页面——布鲁姆认知层次 + 错题库 + 下一题."""
import streamlit as st
import requests
from datetime import datetime

from aitutor.frontend.components.quiz_card import render_quiz_card, render_feedback
from aitutor.frontend.user_data import 保存用户数据

BACKEND_URL = "http://localhost:8000"

知识点列表 = [
    "梯度下降", "反向传播", "CNN", "RNN/LSTM", "Transformer",
    "过拟合与正则化", "损失函数", "优化算法", "生成式模型",
    "K-means聚类", "SVM", "决策树",
]


def _提取答案字母(用户选择: str) -> str:
    """从完整选项文字中提取答案字母，如 'B. 目标函数的负梯度方向' → 'B'."""
    if not 用户选择:
        return ""
    s = 用户选择.strip()
    if s and s[0].upper() in "ABCD":
        return s[0].upper()
    return s


def _判断对错(用户选择: str, 正确答案: str) -> bool:
    """对比用户选择和正确答案."""
    用户字母 = _提取答案字母(用户选择)
    答案字母 = 正确答案.strip().upper()
    if len(答案字母) > 1:
        答案字母 = 答案字母[0]
    return 用户字母 == 答案字母


def render_quiz_page():
    """渲染自适应测验页面."""
    st.header("自适应测验")

    if not st.session_state.get("logged_in"):
        st.info("👈 请先在左侧边栏登录或注册")
        return

    st.caption("基于布鲁姆认知目标分类的动态测验系统")

    # 初始化
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

    history = st.session_state.quiz_history
    wrong = st.session_state.wrong_answers
    level = st.session_state.student_level

    # ============ 学习进度栏 ============
    c_total = len(history)
    c_correct = sum(1 for h in history if h.get("correct")) if history else 0
    c_rate = c_correct / c_total * 100 if c_total > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("布鲁姆层次", f"L{level}")
    with col2:
        st.metric("已答题数", c_total)
    with col3:
        st.metric("准确率", f"{c_rate:.0f}%" if c_total > 0 else "—")
    with col4:
        st.metric("错题库", len(wrong))

    # 状态徽章行
    if c_total > 0:
        if c_rate >= 80:
            st.markdown(
                "<span style='background:rgba(92,184,92,0.15);color:#5CB85C;"
                "padding:4px 14px;border-radius:20px;font-size:0.82rem;font-weight:500;"
                "border:1px solid rgba(92,184,92,0.3)'>▲ 准确率优秀，难度已提升</span>",
                unsafe_allow_html=True)
        elif c_rate < 50:
            st.markdown(
                "<span style='background:rgba(224,85,85,0.12);color:#E05555;"
                "padding:4px 14px;border-radius:20px;font-size:0.82rem;font-weight:500;"
                "border:1px solid rgba(224,85,85,0.3)'>▼ 需巩固基础，回到上一层次</span>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                "<span style='background:rgba(91,155,213,0.12);color:#5B9BD5;"
                "padding:4px 14px;border-radius:20px;font-size:0.82rem;font-weight:500;"
                "border:1px solid rgba(91,155,213,0.3)'>● 稳步推进中</span>",
                unsafe_allow_html=True)

    # ============ 操作栏 ============
    st.divider()
    col_op1, col_op2, _ = st.columns([1, 1, 2])
    with col_op1:
        if history and st.button("重置进度", use_container_width=True):
            st.session_state.quiz_history = []
            st.session_state.wrong_answers = []
            st.session_state.student_level = 1
            st.session_state.current_question = None
            st.session_state.show_feedback = False
            保存用户数据(
                st.session_state.username, st.session_state.chat_history, [], []
            )
            st.rerun()
    with col_op2:
        if wrong and st.button("清空错题库", use_container_width=True):
            st.session_state.wrong_answers = []
            保存用户数据(
                st.session_state.username, st.session_state.chat_history,
                st.session_state.quiz_history, [],
            )
            st.rerun()

    # 错题本（直接展开，不包在 expander 里）
    if wrong:
        st.divider()
        st.subheader(f"📌 错题库（共 {len(wrong)} 题）")
        for i, wa in enumerate(reversed(wrong[-10:])):
            idx = len(wrong) - min(len(wrong), 10) + i + 1
            with st.expander(f"错题 {idx}：{wa.get('question', '')[:40]}…", expanded=False):
                st.caption(f"知识点：{wa.get('topic', '')}　|　你的答案：{wa.get('user_answer', '')}")
                st.markdown(f"**正确答案：{wa.get('correct_answer', '')}**")
                st.markdown(wa.get("explanation", ""))

    st.divider()

    # ============ 出题区域 ============
    topic = st.selectbox("选择知识点", 知识点列表, key="topic_select")
    if st.button("生成题目", type="primary", use_container_width=True):
            with st.spinner("正在生成题目…"):
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
                        st.error(f"生成失败（状态码 {response.status_code}），请重试。")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ 无法连接到后端，请确认 FastAPI 已启动。")
                except requests.exceptions.Timeout:
                    st.error("⏰ 生成超时，请重试。")

    # ============ 显示题目 ============
    q = st.session_state.current_question
    if q:
        st.divider()

        # 自适应提示
        action = q.get("adaptive_action", "maintain")
        if action == "upgrade":
            st.info("📈 准确率超过 80%，难度已升级！")
        elif action == "downgrade":
            st.warning("📉 准确率低于 50%，回到上一层次巩固基础。")

        answer = render_quiz_card(
            question=q["question"],
            options=q.get("options"),
            question_type=q.get("question_type", "single_choice"),
            bloom_level=q.get("bloom_level", 1),
            question_id=q.get("question_id", "unknown"),
        )

        # ============ 处理提交 ============
        if answer is not None and not st.session_state.show_feedback:
            correct = _判断对错(answer, q.get("answer", ""))
            st.session_state.show_feedback = True
            st.session_state.last_correct = correct

            q_topic = q.get("topic", topic)

            # 记录历史
            st.session_state.quiz_history.append({
                "question_id": q["question_id"],
                "topic": q_topic,
                "question": q["question"],
                "correct": correct,
                "bloom_level": q.get("bloom_level", 1),
                "timestamp": datetime.now().isoformat(),
            })

            # 错题入库
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

            # 自适应调节
            if action == "upgrade":
                st.session_state.student_level = min(6, st.session_state.student_level + 1)
            elif action == "downgrade":
                st.session_state.student_level = max(1, st.session_state.student_level - 1)

            # 持久化
            保存用户数据(
                st.session_state.username,
                st.session_state.chat_history,
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

            # 下一题按钮
            st.divider()
            if st.button("生成下一题", type="primary", use_container_width=True):
                with st.spinner("正在生成新题目…"):
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
                            st.error(f"生成失败（状态码 {response.status_code}），请重试。")
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ 无法连接到后端。")
                    except requests.exceptions.Timeout:
                        st.error("⏰ 生成超时，请重试。")
