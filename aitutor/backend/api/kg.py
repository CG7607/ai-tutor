"""Knowledge graph API endpoints."""
from pydantic import BaseModel

from aitutor.backend.knowledge_graph.query import kg_query


class KGSearchRequest(BaseModel):
    query: str


class KGNodeRequest(BaseModel):
    node_id: str


class KGSearchResponse(BaseModel):
    results: list[dict]


class KGNeighborhoodResponse(BaseModel):
    center: dict | None
    neighbors: list[dict]


class KGFullGraphResponse(BaseModel):
    nodes: list[dict]
    edges: list[dict]


async def search_kg(request: KGSearchRequest) -> KGSearchResponse:
    """Search for concepts in the knowledge graph."""
    results = kg_query.search_concepts(request.query)
    return KGSearchResponse(results=results)


async def get_neighborhood(request: KGNodeRequest) -> KGNeighborhoodResponse:
    """Get 1-hop neighborhood for a specific node."""
    neighborhood = kg_query.get_one_hop_neighbors(request.node_id)
    return KGNeighborhoodResponse(
        center=neighborhood["center"],
        neighbors=neighborhood["neighbors"],
    )


async def get_full_graph() -> KGFullGraphResponse:
    """Get the full knowledge graph for visualization."""
    data = kg_query.get_full_graph_data()
    return KGFullGraphResponse(nodes=data["nodes"], edges=data["edges"])
