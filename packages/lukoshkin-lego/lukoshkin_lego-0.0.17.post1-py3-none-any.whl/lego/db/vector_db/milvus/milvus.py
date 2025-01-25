"""
MilvusDB connector

By default, connects to an existing collection with the _default or specified
partition or creates a new one.
"""

from typing import Any

from loguru import logger
from pymilvus import CollectionSchema, MilvusClient
from pymilvus.client.types import ExtraList

from lego.db.vector_db.models import EmbedModel, MilvusDBSettings
from lego.lego_types import OneOrMany
from lego.settings import MilvusConnection


class MilvusDBConnector:
    """
    A Vector index that works with just one partition.

    If no partition is specified, it will use the default partition.
    """

    def __init__(
        self,
        schema: CollectionSchema,
        settings: MilvusDBSettings,
        connection: MilvusConnection,
        embed_model: EmbedModel,
    ):
        self._sanity_checks(settings, schema, embed_model)

        self.schema = schema
        self.settings = settings
        self.client = MilvusClient(**connection.model_dump())
        self.embed_model = embed_model

        self.sim_threshold_to_add = settings.sim_threshold_to_add
        self._more_similar_op = settings.more_similar_op

    def ensure_built(self) -> None:
        """Build the collection, partition, and index."""
        if not self.client.has_collection(self.settings.collection):
            self.client.create_collection(
                collection_name=self.settings.collection,
                enable_dynamic_field=self.settings.enable_dynamic_field,
                schema=self.schema,
            )
        if not self.client.has_partition(
            collection_name=self.settings.collection,
            partition_name=self.settings.partition,
        ):
            self.client.create_partition(
                collection_name=self.settings.collection,
                partition_name=self.settings.partition,
            )
        if self.settings.embedding_field not in self.client.list_indexes(
            self.settings.collection, self.settings.embedding_field
        ):
            index_params = self.client.prepare_index_params()
            index_params.add_index(
                self.settings.embedding_field,
                **self.settings.index_params,
            )
            self.client.create_index(
                self.settings.collection,
                index_params=index_params,
                sync=True,
            )
        return self.client.load_partitions(
            self.settings.collection, self.settings.partition
        )

    def register_one(self, item: dict[str, Any]) -> bool:
        """Add an item to the collection."""
        if not self.get(
            ids=item[self.settings.primary_key],
            output_fields=[self.settings.primary_key],
        ):
            data = item.copy()
            if isinstance(item[self.settings.embedding_field], str):
                data[self.settings.embedding_field] = self.embed_model(
                    item[self.settings.embedding_field]
                )[0]
            self.client.insert(
                collection_name=self.settings.collection,
                partition_name=self.settings.partition,
                data=data,
            )
            return True
        return False

    def register_many(self, items: list[dict[str, Any]]) -> int:
        """Add multiple items to the collection."""
        existing_ids = {
            d[self.settings.primary_key]
            for d in self.get(
                [item[self.settings.primary_key] for item in items],
                output_fields=[self.settings.primary_key],
            )
        }
        data = [
            item
            for item in items
            if item[self.settings.primary_key] not in existing_ids
        ]
        self.client.insert(
            collection_name=self.settings.collection,
            partition_name=self.settings.partition,
            data=data,
        )
        return len(data)

    def get(self, ids: OneOrMany[str | int], **kwargs) -> ExtraList:
        """Get items by their IDs."""
        return self.client.get(
            collection_name=self.settings.collection,
            partition_names=[self.settings.partition],
            ids=ids,
            **kwargs,
        )

    def query(
        self,
        text_filter: tuple[str, str] | None = None,
        filter: str = "",
        **kwargs,
    ) -> ExtraList:
        """Query the partition."""
        prefix = ""
        if text_filter:
            key, value = text_filter
            safe_text = str(value).replace("'", r"\'")
            prefix = f"{key} == '{safe_text}'"

        if prefix:
            filter = f"{prefix} && {filter}" if filter else prefix

        return self.client.query(
            collection_name=self.settings.collection,
            partition_names=[self.settings.partition],
            filter=filter,
            **kwargs,
        )

    def search(
        self,
        texts: OneOrMany[str],
        filter: str = "",
        limit: int = 10,
        **kwargs,
    ) -> ExtraList:
        """Search for similar items in the collection."""
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        if "" in texts:
            raise ValueError("Empty query text is not allowed.")

        return self.client.search(
            collection_name=self.settings.collection,
            partition_names=[self.settings.partition],
            data=self.embed_model(texts),
            filter=filter,
            limit=limit,
            anns_field=self.settings.embedding_field,
            search_params=kwargs.pop("search_params", {})
            or self.settings.search_params,
            **kwargs,
        )

    def count(self) -> int:
        """Count the number of items in the collection."""
        return self.client.query(
            collection_name=self.settings.collection,
            output_fields=["count(*)"],
        )[0]["count(*)"]

    def drop_collection(self, **kwargs) -> None:
        """Drop the collection."""
        if not self.client.has_collection(self.settings.collection):
            logger.warning(
                f"Collection '{self.settings.collection}' cannot be removed"
                ", since not found."
            )
            return
        self.client.release_collection(self.settings.collection, **kwargs)
        self.client.drop_collection(self.settings.collection)

    def drop_partition(self, **kwargs) -> None:
        """Drop the partition."""
        if self.settings.partition == "_default":
            logger.warning("Cannot drop the default partition.")
            logger.info("Dropping the collection instead.")
            self.drop_collection()
            return

        self.client.release_partitions(
            self.settings.collection,
            self.settings.partition,
            **kwargs,
        )
        self.client.drop_partition(
            self.settings.collection,
            self.settings.partition,
        )

    def flush(self, timeout: float | None = None) -> None:
        """Flush the collection."""
        self.client.flush(
            collection_name=self.settings.collection, timeout=timeout
        )

    def close(self) -> None:
        """Close the connection."""
        self.client.close()

    @staticmethod
    def _sanity_checks(
        settings: MilvusDBSettings,
        schema: CollectionSchema,
        embed_model: EmbedModel,
    ) -> None:
        """Perform sanity checks on the settings and schema."""
        schema_dict = {f.name: f for f in schema.fields}
        if settings.embedding_field not in schema_dict:
            raise ValueError(
                f"Embedding field '{settings.embedding_field=}'"
                " not found in the schema."
            )
        if settings.primary_key not in {f.name for f in schema.fields}:
            raise ValueError(
                f"Primary key '{settings.primary_key=}'"
                " not found in the schema."
            )
        if schema_dict[settings.embedding_field].dim != embed_model.embed_dim:
            raise ValueError(
                f"Embedding field '{settings.embedding_field=}' dimension"
                f" mismatch: {schema_dict[settings.embedding_field].dim}"
                f" != {embed_model.embed_dim}."
            )
