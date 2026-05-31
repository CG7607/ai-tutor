"""Knowledge graph visualization component using Pyvis."""
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import requests

BACKEND_URL = "http://localhost:8000"

ENTITY_COLORS = {
    "Concept": "#4CAF50",
    "Person": "#9C27B0",
    "Algorithm": "#2196F3",
    "Prerequisite": "#FF9800",
}


def render_knowledge_graph_html(nodes: list[dict], edges: list[dict]) -> str:
    """Generate an interactive Pyvis network HTML string."""
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#333333")
    net.set_options("""
    var options = {
      "nodes": {
        "font": {"size": 14, "face": "sans-serif"},
        "borderWidth": 2,
        "borderWidthSelected": 4
      },
      "edges": {
        "color": {"inherit": false, "color": "#999999", "highlight": "#2196F3"},
        "smooth": {"type": "continuous"},
        "font": {"size": 10, "color": "#666666"}
      },
      "physics": {
        "barnesHut": {"gravitationalConstant": -5000, "springLength": 200},
        "stabilization": {"iterations": 100}
      }
    }
    """)

    for node in nodes:
        color = ENTITY_COLORS.get(node.get("type", "Concept"), "#999999")
        net.add_node(
            node["id"],
            label=node.get("label", node["id"]),
            title=node.get("description", ""),
            color=color,
            shape="dot",
            size=25,
        )

    for edge in edges:
        net.add_edge(
            edge["source"],
            edge["target"],
            title=edge.get("label", ""),
            label=edge.get("label", ""),
            arrows="to",
        )

    return net.generate_html()


def render_kg_page():
    """Render the knowledge graph exploration page."""
    st.title("🕸️ 课程知识图谱")
    st.caption("探索《人工智能导论》课程的知识体系结构")

    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("🔍 概念搜索")
        query = st.text_input("输入概念名称", placeholder="例如：梯度下降")

        if query:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/kg/search",
                    json={"query": query},
                    timeout=10,
                )
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results:
                        for r in results:
                            entity_type = r.get("type", "Concept")
                            color = ENTITY_COLORS.get(entity_type, "#999999")
                            st.markdown(
                                f"**{r['name']}** "
                                f"<span style='color:{color}'>[{entity_type}]</span>",
                                unsafe_allow_html=True,
                            )
                            st.caption(r.get("description", ""))

                            # Show neighborhood
                            if st.button(f"查看关联 →", key=f"explore_{r['id']}"):
                                st.session_state.selected_node = r["id"]
                                st.rerun()
                    else:
                        st.info("未找到匹配概念")
            except requests.exceptions.ConnectionError:
                st.error("⚠️ 无法连接到后端")

        # Show selected node neighborhood
        if "selected_node" in st.session_state:
            node_id = st.session_state.selected_node
            st.divider()
            st.subheader("📌 关联概念")
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/kg/neighborhood",
                    json={"node_id": node_id},
                    timeout=10,
                )
                if response.status_code == 200:
                    data = response.json()
                    center = data.get("center", {})
                    if center:
                        st.markdown(f"**中心概念：{center.get('name', node_id)}**")
                        st.caption(center.get("description", ""))
                    for nb in data.get("neighbors", []):
                        entity = nb["entity"]
                        rel = nb["relation"]
                        direction = "→" if nb["direction"] == "outgoing" else "←"
                        etype = entity.get("type", "Concept")
                        st.markdown(f"- {direction} **{rel}** → [{etype}] **{entity.get('name', '')}**")
                        st.caption(entity.get("description", ""))
            except requests.exceptions.ConnectionError:
                st.error("⚠️ 无法连接到后端")

    with col2:
        st.subheader("🗺️ 知识体系全览")
        try:
            response = requests.get(f"{BACKEND_URL}/api/kg/full", timeout=10)
            if response.status_code == 200:
                data = response.json()
                html = render_knowledge_graph_html(
                    data.get("nodes", []),
                    data.get("edges", []),
                )
                components.html(html, height=650, scrolling=True)

                # Legend
                st.caption("图例：")
                cols = st.columns(4)
                for i, (etype, color) in enumerate(ENTITY_COLORS.items()):
                    cols[i].markdown(
                        f"<span style='color:{color};font-weight:bold'>●</span> {etype}",
                        unsafe_allow_html=True,
                    )
        except requests.exceptions.ConnectionError:
            st.error("⚠️ 无法连接到后端")
