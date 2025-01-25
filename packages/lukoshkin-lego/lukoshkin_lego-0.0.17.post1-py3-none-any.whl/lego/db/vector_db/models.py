from typing import Callable, Protocol

from numpy.typing import NDArray
from pydantic import BaseModel

from lego.lego_types import JSONDict, OneOrMany


class MilvusDBSettings(BaseModel):
    """Settings for MilvusDBConnector."""

    collection: str
    partition: str = "_default"
    index_params: JSONDict = {"index_type": "AUTOINDEX", "metric_type": "IP"}
    search_params: JSONDict = {"metric_type": "IP"}
    sim_threshold_to_add: float | None = None
    enable_dynamic_field: bool = False
    embedding_field: str = "vector"
    more_similar_op: str = "gt"  # x (more_similar_op) threshold
    # ↑ likely, is redundant since we have `radius` and `range_filter` ↑
    primary_key: str = "id"


class EmbedModel(Protocol):
    """Embedding model protocol."""

    embed_fn: Callable
    embed_dim: int

    def __call__(self, texts: OneOrMany[str]) -> list[NDArray[float]]:
        """Return embeddings for the input texts."""
        return self.embed_fn(texts)

    def inspect_embed_dim(self) -> int:
        """Measure the embedding dimension."""
        return self.embed_fn(["test"])[0].shape[0]
