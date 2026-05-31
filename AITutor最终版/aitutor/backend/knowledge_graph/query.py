"""Knowledge graph query engine — loads, queries, and navigates the course KG."""
import json
from pathlib import Path
from typing import Optional

import networkx as nx

from aitutor.backend.knowledge_graph.models import (
    KnowledgeGraphData,
    Entity,
    Relation,
    EntityType,
)

DATA_DIR = Path(__file__).parent.parent.parent / "data"
KG_FILE = DATA_DIR / "knowledge_graph.json"
SYLLABUS_FILE = DATA_DIR / "syllabus.json"


class KnowledgeGraphQuery:
    """Query engine for the course knowledge graph.

    Loads the graph from JSON, provides 1-hop neighbor search
    and context generation for agents.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._loaded = False

    def load(self, file_path: Path | None = None) -> None:
        """Load the knowledge graph from a JSON file.

        If no file path is given, tries knowledge_graph.json first,
        then falls back to syllabus.json.
        """
        path = file_path or KG_FILE
        if not path.exists():
            path = SYLLABUS_FILE

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for entity in data["entities"]:
            self.graph.add_node(
                entity["id"],
                name=entity["name"],
                type=entity["type"],
                description=entity.get("description", ""),
                category=entity.get("category", ""),
            )

        for relation in data["relations"]:
            self.graph.add_edge(
                relation["source"],
                relation["target"],
                type=relation["type"],
                description=relation.get("description", ""),
            )

        self._loaded = True

    def ensure_loaded(self) -> None:
        """Ensure the graph is loaded, loading from default file if needed."""
        if not self._loaded:
            self.load()

    def find_node(self, keyword: str) -> Optional[str]:
        """Find a node ID by fuzzy matching on name or description.

        Args:
            keyword: A keyword to search for in node names/descriptions.

        Returns:
            The matching node ID, or None if not found.
        """
        self.ensure_loaded()
        keyword_lower = keyword.lower()
        for node_id, attrs in self.graph.nodes(data=True):
            name = attrs.get("name", "").lower()
            desc = attrs.get("description", "").lower()
            if keyword_lower in name or keyword_lower in desc:
                return node_id
        return None

    def get_one_hop_neighbors(self, node_id: str) -> dict:
        """Get the 1-hop neighborhood of a node.

        Args:
            node_id: The ID of the center node.

        Returns:
            Dict with 'center' entity and lists of 'neighbors' with relation info.
        """
        self.ensure_loaded()
        if node_id not in self.graph:
            return {"center": None, "neighbors": []}

        center = dict(self.graph.nodes[node_id])
        center["id"] = node_id

        neighbors = []
        # Outgoing edges
        for _, target, edge_data in self.graph.out_edges(node_id, data=True):
            target_attrs = dict(self.graph.nodes[target])
            target_attrs["id"] = target
            neighbors.append({
                "entity": target_attrs,
                "relation": edge_data["type"],
                "relation_desc": edge_data.get("description", ""),
                "direction": "outgoing",
            })
        # Incoming edges
        for source, _, edge_data in self.graph.in_edges(node_id, data=True):
            source_attrs = dict(self.graph.nodes[source])
            source_attrs["id"] = source
            neighbors.append({
                "entity": source_attrs,
                "relation": edge_data["type"],
                "relation_desc": edge_data.get("description", ""),
                "direction": "incoming",
            })

        return {"center": center, "neighbors": neighbors}

    def get_context_for_agent(self, keywords: list[str]) -> str:
        """Generate knowledge graph context text for agent prompts.

        Args:
            keywords: List of concept names to look up in the graph.

        Returns:
            A text summary of relevant knowledge graph context.
        """
        self.ensure_loaded()
        lines = []
        seen = set()

        for kw in keywords:
            node_id = self.find_node(kw)
            if not node_id:
                continue

            neighborhood = self.get_one_hop_neighbors(node_id)
            center = neighborhood["center"]
            if center and node_id not in seen:
                seen.add(node_id)
                entity_type = center.get("type", "Concept")
                lines.append(f"- [{entity_type}] **{center.get('name', node_id)}**: {center.get('description', '')}")

            for nb in neighborhood["neighbors"]:
                nid = nb["entity"]["id"]
                if nid not in seen:
                    seen.add(nid)
                    etype = nb["entity"].get("type", "Concept")
                    rel = nb["relation"]
                    lines.append(
                        f"  - {rel} → [{etype}] **{nb['entity'].get('name', nid)}**: "
                        f"{nb['entity'].get('description', '')}"
                    )

        if not lines:
            return "（未在知识图谱中找到相关信息）"

        return "## 课程知识图谱上下文\n" + "\n".join(lines)

    def get_full_graph_data(self) -> dict:
        """Export the full graph for frontend visualization.

        Returns:
            Dict with nodes and edges ready for Pyvis/Streamlit rendering.
        """
        self.ensure_loaded()
        nodes = []
        for node_id, attrs in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": attrs.get("name", node_id),
                "type": attrs.get("type", "Concept"),
                "category": attrs.get("category", ""),
                "description": attrs.get("description", ""),
            })

        edges = []
        for source, target, edge_data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "label": edge_data.get("type", ""),
                "description": edge_data.get("description", ""),
            })

        return {"nodes": nodes, "edges": edges}

    def search_concepts(self, query: str) -> list[dict]:
        """Search for concepts matching a query string.

        Args:
            query: Search string.

        Returns:
            List of matching entities with their IDs.
        """
        self.ensure_loaded()
        results = []
        query_lower = query.lower()
        for node_id, attrs in self.graph.nodes(data=True):
            name = attrs.get("name", "").lower()
            desc = attrs.get("description", "").lower()
            if query_lower in name or query_lower in desc:
                results.append({
                    "id": node_id,
                    "name": attrs.get("name", node_id),
                    "type": attrs.get("type", "Concept"),
                    "description": attrs.get("description", ""),
                })
        return results


# Singleton instance
kg_query = KnowledgeGraphQuery()
