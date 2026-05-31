"""Agent identity badge component for Streamlit."""
import streamlit as st

AGENT_CONFIG = {
    "math": {"icon": "🔢", "label": "数学推导 Agent", "color": "#4CAF50"},
    "algorithm": {"icon": "💻", "label": "算法实现 Agent", "color": "#2196F3"},
    "concept": {"icon": "🧠", "label": "概念辨析 Agent", "color": "#FF9800"},
}


def render_agent_badge(agent_name: str) -> None:
    """Render a colored badge showing which agent is responding."""
    config = AGENT_CONFIG.get(agent_name, AGENT_CONFIG["concept"])
    st.markdown(
        f"""<span style="
            background-color: {config['color']};
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 500;
        ">{config['icon']} {config['label']}</span>""",
        unsafe_allow_html=True,
    )
