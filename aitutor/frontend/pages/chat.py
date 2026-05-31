"""智能问答——文件上传 + 历史对话管理."""
import json
import uuid
from datetime import datetime
from pathlib import Path
import streamlit as st
import requests

from aitutor.frontend.user_data import 保存用户数据

BACKEND_URL = "http://localhost:8000"

头像 = {"math": "🔢", "algorithm": "💻", "concept": "🧠"}


def _对话目录() -> Path:
    u = st.session_state.username
    d = Path(__file__).parent.parent.parent / "data" / "users" / u / "conversations"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _加载对话列表() -> list[dict]:
    """加载所有历史对话的摘要."""
    d = _对话目录()
    convs = []
    for fp in sorted(d.glob("*.json"), reverse=True):
        try:
            data = json.loads(fp.read_text())
            convs.append({
                "id": data.get("id", fp.stem),
                "title": data.get("title", "未命名对话"),
                "created_at": data.get("created_at", ""),
                "message_count": len(data.get("messages", [])),
            })
        except Exception:
            pass
    return convs


def _保存对话(conv_id: str, title: str, messages: list):
    """保存当前对话到磁盘."""
    fp = _对话目录() / f"{conv_id}.json"
    fp.write_text(json.dumps({
        "id": conv_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "messages": messages,
    }, ensure_ascii=False, indent=2))


def _删除对话(conv_id: str):
    fp = _对话目录() / f"{conv_id}.json"
    if fp.exists():
        fp.unlink()


def render_chat_page():
    """渲染问答页面."""
    from aitutor.frontend.components.agent_badge import render_agent_badge

    st.header("智能问答")

    if not st.session_state.get("logged_in"):
        st.info("请先在左侧边栏登录")
        return

    # 初始化会话状态
    if "active_conv_id" not in st.session_state:
        st.session_state.active_conv_id = str(uuid.uuid4())
    if "conv_title" not in st.session_state:
        st.session_state.conv_title = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_file_content" not in st.session_state:
        st.session_state.uploaded_file_content = None
    if "uploaded_file_name" not in st.session_state:
        st.session_state.uploaded_file_name = None

    # ============ 侧边栏扩展：对话管理 ============
    with st.sidebar:
        st.divider()
        st.subheader("对话历史")

        if st.button("＋ 新建对话", use_container_width=True):
            当前对话 = st.session_state.messages
            if 当前对话:
                title = st.session_state.conv_title or "未命名对话"
                _保存对话(st.session_state.active_conv_id, title, 当前对话)
            st.session_state.active_conv_id = str(uuid.uuid4())
            st.session_state.conv_title = ""
            st.session_state.messages = []
            st.session_state.uploaded_file_content = None
            st.session_state.uploaded_file_name = None
            st.rerun()

        # 历史对话列表
        convs = _加载对话列表()
        if convs:
            for c in convs[:15]:
                is_active = c["id"] == st.session_state.active_conv_id
                label = f"{'●' if is_active else '○'} {c['title'][:20]}"
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(
                        label, key=f"conv_{c['id']}",
                        use_container_width=True,
                        help=f"{c['message_count']} 条消息 · {c['created_at'][:16]}",
                    ):
                        # 先保存当前对话
                        当前对话 = st.session_state.messages
                        if 当前对话:
                            title = st.session_state.conv_title or "未命名对话"
                            _保存对话(st.session_state.active_conv_id, title, 当前对话)
                        # 加载选中的对话
                        fp = _对话目录() / f"{c['id']}.json"
                        data = json.loads(fp.read_text())
                        st.session_state.active_conv_id = c["id"]
                        st.session_state.conv_title = data.get("title", "")
                        st.session_state.messages = data.get("messages", [])
                        st.session_state.uploaded_file_content = None
                        st.session_state.uploaded_file_name = None
                        st.rerun()
                with col2:
                    if st.button("🗑", key=f"del_{c['id']}", help="删除此对话"):
                        _删除对话(c["id"])
                        if c["id"] == st.session_state.active_conv_id:
                            st.session_state.active_conv_id = str(uuid.uuid4())
                            st.session_state.messages = []
                        st.rerun()

    # ============ 主区域 ============
    st.caption("向 AI 导师组提问，支持上传文件作为上下文")

    # 显示对话标题
    if st.session_state.conv_title:
        st.markdown(f"*当前对话：{st.session_state.conv_title}*")

    # ============ 消息列表 ============
    for msg in st.session_state.messages:
        avatar = msg.get("avatar")
        with st.chat_message(msg["role"], avatar=avatar if avatar else None):
            if msg["role"] == "assistant" and "agent_name" in msg:
                render_agent_badge(msg["agent_name"])
            if msg.get("file_name"):
                st.caption(f"📎 已上传：{msg['file_name']}")
            st.markdown(msg["content"])

    # ============ 输入区域 ============
    # 文件上传
    uploaded_file = st.file_uploader(
        "上传文件（可选）",
        type=["txt", "md", "py", "pdf", "json", "csv", "c", "cpp", "java", "js", "html", "css", "sh", "sql", "tex"],
        key="file_uploader",
        label_visibility="collapsed",
    )
    if uploaded_file:
        try:
            content = uploaded_file.read()
            st.session_state.uploaded_file_content = content.decode("utf-8", errors="replace")
        except Exception:
            st.session_state.uploaded_file_content = "[二进制文件，无法预览]"
        st.session_state.uploaded_file_name = uploaded_file.name
        st.success(f"已上传：{uploaded_file.name}")
        # 文件内容预览
        with st.expander("📎 文件内容预览", expanded=False):
            preview = st.session_state.uploaded_file_content
            st.text(preview[:2000] + ("..." if len(preview) > 2000 else ""))

    # 聊天输入
    if prompt := st.chat_input("输入你的问题…"):
        file_content = st.session_state.uploaded_file_content
        file_name = st.session_state.uploaded_file_name

        # 自动生成对话标题（用第一条用户消息）
        if not st.session_state.conv_title and st.session_state.messages == []:
            title = prompt[:40] + ("…" if len(prompt) > 40 else "")
            st.session_state.conv_title = title

        # 添加用户消息
        user_msg = {
            "role": "user",
            "content": prompt,
            "file_name": file_name,
        }
        st.session_state.messages.append(user_msg)

        with st.chat_message("user"):
            if file_name:
                st.caption(f"📎 {file_name}")
            st.markdown(prompt)

        # 清空文件状态
        st.session_state.uploaded_file_content = None
        st.session_state.uploaded_file_name = None

        # 调用后端
        with st.chat_message("assistant"):
            with st.spinner("思考中…"):
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/api/chat",
                        json={
                            "message": prompt,
                            "history": [
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages[-7:-1]
                            ],
                            "file_content": file_content,
                            "file_name": file_name,
                        },
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        agent = data.get("agent_used", "concept")
                        render_agent_badge(agent)
                        st.markdown(data["reply"])

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": data["reply"],
                            "agent_name": agent,
                            "avatar": 头像.get(agent, "🤖"),
                        })

                        # 每次对话后保存
                        _保存对话(
                            st.session_state.active_conv_id,
                            st.session_state.conv_title,
                            st.session_state.messages,
                        )
                        保存用户数据(
                            st.session_state.username,
                            st.session_state.chat_history,
                            st.session_state.quiz_history,
                            st.session_state.wrong_answers,
                        )

                        if data.get("sub_replies"):
                            with st.expander("相关子问题解答"):
                                for sub in data["sub_replies"]:
                                    st.caption(f"**{sub['agent']}**")
                                    st.markdown(sub["reply"])
                    else:
                        st.error(f"后端异常（{resp.status_code}），请重试")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ 无法连接到后端")
                except requests.exceptions.Timeout:
                    st.error("⏰ 请求超时，文件过大时请减少内容")

        st.rerun()
