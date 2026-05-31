"""错题库独立页面——分页浏览全部错题，支持逐条删除和清空."""
import streamlit as st

from aitutor.frontend.user_data import 保存用户数据


def render_wrong_answers_page():
    """渲染错题库独立页面."""
    st.header("📌 错题库")

    if not st.session_state.get("logged_in"):
        st.info("👈 请先在左侧边栏登录或注册")
        return

    st.caption("这里记录了所有答错的题目，方便你回顾和复习薄弱知识点。")

    # 初始化
    if "wrong_answers" not in st.session_state:
        st.session_state.wrong_answers = []
    if "wrong_page_num" not in st.session_state:
        st.session_state.wrong_page_num = 1
    if "confirm_clear" not in st.session_state:
        st.session_state.confirm_clear = False

    wrong = st.session_state.wrong_answers

    if not wrong:
        st.info("🎉 错题库为空，继续保持！去「测验」模块挑战更多题目吧～")
        return

    PAGE_SIZE = 10
    total_pages = max(1, (len(wrong) + PAGE_SIZE - 1) // PAGE_SIZE)
    current_page = st.session_state.wrong_page_num
    if current_page > total_pages:
        current_page = total_pages
        st.session_state.wrong_page_num = current_page

    start_idx = (current_page - 1) * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, len(wrong))
    page_items = list(enumerate(wrong[start_idx:end_idx], start=start_idx + 1))

    # ============ 顶栏：统计 + 操作 ============
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    with col_metric1:
        st.metric("错题总数", len(wrong))
    with col_metric2:
        # 统计知识点覆盖
        topics = set(wa.get("topic", "未知") for wa in wrong)
        st.metric("涉及知识点", len(topics))
    with col_metric3:
        st.metric("当前页", f"{current_page}/{total_pages}")

    st.divider()

    # 清空操作
    col_clear, _ = st.columns([1, 3])
    with col_clear:
        if st.button("🗑 清空全部错题", type="secondary", use_container_width=True):
            st.session_state.confirm_clear = True

    if st.session_state.get("confirm_clear"):
        st.warning("⚠️ 确定要清空全部错题吗？此操作不可恢复。")
        col_y, col_n = st.columns([1, 4])
        with col_y:
            if st.button("✅ 确认清空", type="primary"):
                st.session_state.wrong_answers = []
                st.session_state.confirm_clear = False
                st.session_state.wrong_page_num = 1
                保存用户数据(
                    st.session_state.username, st.session_state.chat_history,
                    st.session_state.quiz_history, [],
                )
                st.rerun()
        with col_n:
            if st.button("❌ 取消"):
                st.session_state.confirm_clear = False
                st.rerun()

    st.divider()

    # ============ 题目列表 ============
    for num, wa in page_items:
        q_text = wa.get("question", "")
        if len(q_text) > 80:
            q_text = q_text[:80] + "…"

        with st.expander(
            f"错题 {num}　·　{wa.get('topic', '未知')}　·　{q_text}",
            expanded=False,
        ):
            # 题目详情
            st.markdown(f"**📝 题目：** {wa.get('question', '未知')}")

            options = wa.get("options", [])
            if options:
                st.caption("选项：")
                for opt in options:
                    st.caption(f"　　{opt}")

            col_ans, col_del = st.columns([5, 1])
            with col_ans:
                st.markdown(f"❌ **你的答案：** {wa.get('user_answer', '无')}")
                st.markdown(f"✅ **正确答案：** {wa.get('correct_answer', '无')}")
                if wa.get("explanation"):
                    st.markdown(f"💡 **解析：** {wa.get('explanation', '')}")
                st.caption(
                    f"布鲁姆层次 L{wa.get('bloom_level', '?')}　·　"
                    f"{wa.get('timestamp', '')[:19]}"
                )
            with col_del:
                if st.button("🗑", key=f"del_wrong_{num}", help="删除此条"):
                    actual_idx = num - 1
                    if 0 <= actual_idx < len(st.session_state.wrong_answers):
                        st.session_state.wrong_answers.pop(actual_idx)
                        保存用户数据(
                            st.session_state.username, st.session_state.chat_history,
                            st.session_state.quiz_history, st.session_state.wrong_answers,
                        )
                        st.session_state.wrong_page_num = min(
                            current_page, max(1, total_pages - 1)
                        )
                        st.rerun()

    st.divider()

    # ============ 底部分页导航 ============
    col_prev, col_page_info, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("← 上一页", disabled=(current_page <= 1), use_container_width=True):
            st.session_state.wrong_page_num = current_page - 1
            st.rerun()
    with col_page_info:
        st.caption(
            f"第 {current_page} / {total_pages} 页　·　"
            f"共 {len(wrong)} 条记录",
        )
    with col_next:
        if st.button("下一页 →", disabled=(current_page >= total_pages), use_container_width=True):
            st.session_state.wrong_page_num = current_page + 1
            st.rerun()
