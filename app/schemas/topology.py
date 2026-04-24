from pydantic import BaseModel, Field


class TopologyNode(BaseModel):
    id: str
    label: str
    kind: str
    group: str
    title: str | None = None
    metadata: dict = Field(default_factory=dict)


class TopologyEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str | None = None
    kind: str
    metadata: dict = Field(default_factory=dict)


class TopologyGraphResponse(BaseModel):
    nodes: list[TopologyNode] = Field(default_factory=list)
    edges: list[TopologyEdge] = Field(default_factory=list)
    filters: dict = Field(default_factory=dict)
    supported_overlays: list[str] = Field(default_factory=lambda: ["subnet", "ip"])

