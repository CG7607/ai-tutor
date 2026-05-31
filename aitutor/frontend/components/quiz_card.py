"""Quiz question card component."""
import streamlit as st

BLOOM_LABELS = {
    1: ("📋", "记忆"),
    2: ("💡", "理解"),
    3: ("🔧", "应用"),
    4: ("🔍", "分析"),
    5: ("⚖️", "评价"),
    6: ("🚀", "创造"),
}


def render_quiz_card(
    question: str,
    options: list[str] | None,
    question_type: str,
    bloom_level: int,
    question_id: str,
) -> str | None:
    """Render a quiz question card and return the student's answer.

    Returns:
        The student's answer string, or None if not yet answered.
    """
    icon, label = BLOOM_LABELS.get(bloom_level, ("📋", "未知"))

    st.markdown(f"### {icon} {label}层次")
    st.markdown(question)

    answer_key = f"answer_{question_id}"
    submitted_key = f"submitted_{question_id}"

    if options:
        answer = st.radio(
            "请选择你的答案：",
            options,
            key=answer_key,
            index=None,
            format_func=lambda x: x,
        )
        if st.button("提交答案", key=submitted_key, disabled=answer is None):
            return answer
    else:
        answer = st.text_area("请输入你的答案：", key=answer_key, height=100)
        if st.button("提交答案", key=submitted_key, disabled=not answer.strip()):
            return answer.strip()

    return None


def render_feedback(correct: bool, correct_answer: str, explanation: str) -> None:
    """Render answer feedback."""
    if correct:
        st.success("✅ 回答正确！")
    else:
        st.error(f"❌ 回答错误。正确答案是：**{correct_answer}**")

    with st.expander("📖 查看解析"):
        st.markdown(explanation)
