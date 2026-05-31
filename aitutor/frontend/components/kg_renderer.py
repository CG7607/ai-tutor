"""知识图谱可视化组件——Pyvis 交互式网络图 + 点击详情弹窗."""
import json
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import requests

BACKEND_URL = "http://localhost:8000"

实体颜色 = {
    "Concept": "#5CB85C",
    "Person": "#9B7ED8",
    "Algorithm": "#5B9BD5",
    "Prerequisite": "#F5A623",
}

类型中文 = {
    "Concept": "概念",
    "Person": "人物",
    "Algorithm": "算法",
    "Prerequisite": "前置知识",
}

关系中文 = {
    "PREREQUISITE_OF": "前置知识 →",
    "VARIANT_OF": "变体 ←",
    "DERIVES_FROM": "推导来源 ←",
    "PROPOSED": "提出者 ←",
    "APPLIED_IN": "应用领域 →",
    "CONTRASTS_WITH": "概念对比 ⟷",
}


def render_kg_html(nodes: list[dict], edges: list[dict]) -> str:
    """生成带点击交互的 Pyvis 图谱 HTML."""
    # 构建节点详情字典
    node_details = {}
    for n in nodes:
        nid = n["id"]
        # 收集该节点的邻居和关系
        neighbors = []
        for e in edges:
            if e["source"] == nid:
                neighbors.append({
                    "direction": "out",
                    "relation": e.get("label", ""),
                    "target": e["target"],
                })
            if e["target"] == nid:
                neighbors.append({
                    "direction": "in",
                    "relation": e.get("label", ""),
                    "source": e["source"],
                })
        # 构建名称到ID的映射
        name_to_id = {nd["label"]: nd["id"] for nd in nodes}
        node_details[nid] = {
            "name": n.get("label", nid),
            "type": n.get("type", "Concept"),
            "desc": n.get("description", ""),
            "category": n.get("category", ""),
            "neighbors": neighbors,
            "nameToId": name_to_id,
        }

    details_json = json.dumps(node_details, ensure_ascii=False)

    # 构建 Pyvis 网络
    net = Network(
        height="620px", width="100%",
        bgcolor="#1A1D23", font_color="#E8E6E3",
    )
    net.set_options(f"""
    var options = {{
      "nodes": {{
        "font": {{"size": 13, "face": "sans-serif", "color": "#E8E6E3"}},
        "borderWidth": 2, "borderWidthSelected": 4,
        "color": {{"border": "#363840", "background": "#252830",
                   "highlight": {{"border": "#F5A623", "background": "#2C3039"}}}}
      }},
      "edges": {{
        "color": {{"inherit": false, "color": "#4A4D55", "highlight": "#F5A623"}},
        "smooth": {{"type": "continuous"}},
        "font": {{"size": 9, "color": "#6B6A67"}}, "arrows": {{"to": {{"enabled": true}}}}
      }},
      "physics": {{
        "barnesHut": {{"gravitationalConstant": -4000, "springLength": 180}},
        "stabilization": {{"iterations": 120}}
      }},
      "interaction": {{"hover": true, "tooltipDelay": 100}}
    }}
    """)

    for n in nodes:
        color = 实体颜色.get(n.get("type", "Concept"), "#999")
        net.add_node(
            n["id"],
            label=n.get("label", n["id"]),
            title=n.get("description", "")[:100],
            color={"background": color, "border": "#1A1D23"},
            shape="dot", size=22,
        )

    for e in edges:
        net.add_edge(
            e["source"], e["target"],
            title=e.get("label", ""),
            label=e.get("label", ""),
            arrows="to",
        )

    html = net.generate_html()

    # 注入点击交互 JS 和详情弹窗 CSS
    inject = f"""
    <style>
    #kg-popup {{
        display: none; position: fixed; top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        background: #252830; border: 1px solid #F5A623;
        border-radius: 14px; padding: 1.5rem;
        max-width: 480px; width: 90%; max-height: 70vh; overflow-y: auto;
        box-shadow: 0 16px 48px rgba(0,0,0,0.5); z-index: 10000;
        font-family: 'Noto Sans SC', sans-serif; color: #E8E6E3;
    }}
    #kg-popup h3 {{ color: #F5A623; margin-top: 0; font-size: 1.2rem; }}
    #kg-popup .popup-type {{ font-size: 0.75rem; color: #9B9A96; letter-spacing: 0.06em; }}
    #kg-popup .popup-desc {{ margin: 0.8rem 0; line-height: 1.6; color: #B0AEAA; }}
    #kg-popup .popup-neighbors {{ margin-top: 1rem; }}
    #kg-popup .popup-neighbor {{
        padding: 0.4rem 0.6rem; margin: 3px 0; border-radius: 6px;
        background: #1E2026; font-size: 0.85rem; border-left: 2px solid #F5A623;
    }}
    #kg-popup .popup-neighbor .rel {{ color: #F5A623; font-size: 0.75rem; }}
    #kg-popup .popup-close {{
        position: absolute; top: 10px; right: 14px;
        background: none; border: none; color: #6B6A67;
        font-size: 1.4rem; cursor: pointer;
    }}
    #kg-popup .popup-close:hover {{ color: #E8E6E3; }}
    #kg-overlay {{
        display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.5); z-index: 9999;
    }}
    </style>
    <div id="kg-overlay" onclick="closePopup()"></div>
    <div id="kg-popup">
        <button class="popup-close" onclick="closePopup()">✕</button>
        <div id="kg-popup-content"></div>
    </div>
    <script>
    var details = {details_json};
    function closePopup() {{
        document.getElementById('kg-popup').style.display = 'none';
        document.getElementById('kg-overlay').style.display = 'none';
    }}
    // 监听 Pyvis 网络中的点击事件
    setTimeout(function() {{
        var canvas = document.querySelector('canvas');
        var network = null;
        // Pyvis 把 network 实例挂载在 window 上，遍历查找
        for (var key in window) {{
            if (window[key] && window[key].body && window[key].body.data) {{
                network = window[key]; break;
            }}
        }}
        if (network) {{
            network.on('click', function(params) {{
                if (params.nodes.length > 0) {{
                    var nid = params.nodes[0];
                    var d = details[nid];
                    if (!d) return;
                    var nbs = '';
                    if (d.neighbors && d.neighbors.length > 0) {{
                        d.neighbors.forEach(function(nb) {{
                            var targetId = nb.target || nb.source;
                            var targetName = (d.nameToId && Object.entries(d.nameToId).find(
                                function(e) {{ return e[1] === targetId; }}
                            ) || [targetId])[0];
                            var dir = nb.direction === 'out' ? '→' : '←';
                            nbs += '<div class="popup-neighbor">' +
                                   '<span class="rel">' + dir + ' ' + nb.relation + '</span> ' +
                                   targetName + '</div>';
                        }});
                    }} else {{
                        nbs = '<p style="color:#6B6A67;font-size:0.85rem;">无关联节点</p>';
                    }}
                    document.getElementById('kg-popup-content').innerHTML =
                        '<span class="popup-type">' + (d.type || '') + ' · ' + (d.category || '') + '</span>' +
                        '<h3>' + d.name + '</h3>' +
                        '<p class="popup-desc">' + (d.desc || '暂无描述') + '</p>' +
                        '<div class="popup-neighbors"><strong style="font-size:0.8rem;color:#9B9A96;">关联概念</strong>' +
                        nbs + '</div>';
                    document.getElementById('kg-popup').style.display = 'block';
                    document.getElementById('kg-overlay').style.display = 'block';
                }}
            }});
        }}
    }}, 800);
    </script>
    """

    # 把注入内容塞到 </body> 之前
    if "</body>" in html:
        html = html.replace("</body>", inject + "</body>")
    else:
        html += inject

    return html


def render_kg_page():
    """渲染知识图谱探索页面."""
    st.header("🕸️ 知识图谱")

    col1, col2 = st.columns([1.2, 3])

    with col1:
        st.caption("探索《人工智能导论》课程的知识体系")

        # 搜索框
        query = st.text_input("搜索概念", placeholder="输入名称，如：梯度下降", key="kg_search")

        if query:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/kg/search",
                    json={"query": query}, timeout=10,
                )
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results:
                        st.caption(f"找到 {len(results)} 个结果")
                        for r in results:
                            etype = r.get("type", "Concept")
                            color = 实体颜色.get(etype, "#999")
                            cname = 类型中文.get(etype, etype)
                            st.markdown(
                                f"**{r['name']}** "
                                f"<span style='font-size:0.7rem;color:{color}'>[{cname}]</span>",
                                unsafe_allow_html=True,
                            )
                            st.caption(r.get("description", ""))
                            if st.button("查看关联 →", key=f"explore_{r['id']}"):
                                st.session_state.kg_selected = r["id"]
                                st.rerun()
                            st.divider()
                    else:
                        st.info("未找到匹配概念")

            except requests.exceptions.ConnectionError:
                st.error("⚠️ 无法连接到后端")

        # 显示选中节点的邻域详情
        if "kg_selected" in st.session_state and st.session_state.kg_selected:
            node_id = st.session_state.kg_selected
            st.divider()
            st.subheader("📌 节点详情")
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/api/kg/neighborhood",
                    json={"node_id": node_id}, timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    center = data.get("center") or {}
                    if center:
                        etype = center.get("type", "Concept")
                        cname = 类型中文.get(etype, etype)
                        st.markdown(f"### {center.get('name', node_id)}")
                        st.caption(f"{cname} · {center.get('category', '')}")
                        st.markdown(center.get("description", ""))

                    if data.get("neighbors"):
                        st.caption("关联节点：")
                        for nb in data["neighbors"]:
                            e = nb["entity"]
                            rel = 关系中文.get(nb["relation"], nb["relation"])
                            st.markdown(
                                f"<span style='font-size:0.8rem;color:#F5A623'>{rel}</span> "
                                f"**{e.get('name', '')}**",
                                unsafe_allow_html=True,
                            )
                            st.caption(e.get("description", "")[:80])
            except requests.exceptions.ConnectionError:
                st.error("⚠️ 无法连接到后端")
            if st.button("✕ 清除选择"):
                del st.session_state.kg_selected
                st.rerun()

    with col2:
        st.caption("💡 点击图中节点查看详情，拖拽可移动，滚轮缩放")
        try:
            response = requests.get(f"{BACKEND_URL}/api/kg/full", timeout=10)
            if response.status_code == 200:
                data = response.json()
                html = render_kg_html(data.get("nodes", []), data.get("edges", []))
                components.html(html, height=660, scrolling=False)

                # 图例
                st.caption("")
                cols = st.columns(4)
                for i, (etype, color) in enumerate(实体颜色.items()):
                    cname = 类型中文.get(etype, etype)
                    cols[i].markdown(
                        f"<span style='color:{color};font-weight:bold;font-size:0.8rem'>● {cname}</span>",
                        unsafe_allow_html=True,
                    )
        except requests.exceptions.ConnectionError:
            st.error("⚠️ 无法连接到后端")
