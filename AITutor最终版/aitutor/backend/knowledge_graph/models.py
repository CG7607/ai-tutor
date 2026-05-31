"""Pydantic models for the course knowledge graph."""
from enum import Enum
from pydantic import BaseModel


class EntityType(str, Enum):
    CONCEPT = "Concept"
    PERSON = "Person"
    ALGORITHM = "Algorithm"
    PREREQUISITE = "Prerequisite"


class RelationType(str, Enum):
    PREREQUISITE_OF = "PREREQUISITE_OF"
    VARIANT_OF = "VARIANT_OF"
    DERIVES_FROM = "DERIVES_FROM"
    PROPOSED = "PROPOSED"
    APPLIED_IN = "APPLIED_IN"
    CONTRASTS_WITH = "CONTRASTS_WITH"


class Entity(BaseModel):
    id: str
    name: str
    type: EntityType
    description: str
    category: str  # e.g. "数学基础", "机器学习", "深度学习"


class Relation(BaseModel):
    source: str  # Entity id
    target: str  # Entity id
    type: RelationType
    description: str = ""


class KnowledgeGraphData(BaseModel):
    entities: list[Entity]
    relations: list[Relation]
