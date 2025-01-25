import pytest
from pymilvus import CollectionSchema, DataType, FieldSchema

from lego.db.vector_db.embed.openai_model import OpenAIEmbedModel
from lego.db.vector_db.milvus import MilvusDBConnector
from lego.db.vector_db.models import MilvusDBSettings
from lego.settings import MilvusConnection

TEST_COLLECTION = "test_collection"
MAXLEN = 128
DIM = 512


@pytest.fixture(scope="module")
def db():
    connection = MilvusConnection(uri="http://localhost:19530")
    settings = MilvusDBSettings(collection=TEST_COLLECTION)
    schema = CollectionSchema(
        fields=[
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=MAXLEN,
            ),
            FieldSchema(name="sql", dtype=DataType.VARCHAR, max_length=MAXLEN),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DIM),
        ]
    )
    return MilvusDBConnector(
        settings=settings,
        connection=connection,
        embed_model=OpenAIEmbedModel(embed_dim=DIM),
        schema=schema,
    )


@pytest.fixture(scope="module", autouse=True)
def setup(db):
    db.drop_collection()
    db.ensure_built()
    yield
    db.drop_partition()
    db.close()


def test_register_one(db):
    meta = {
        "id": "provide me the total sales",
        "sql": "SELECT SUM(sales) FROM sales",
    }
    item = meta.copy()
    item["vector"] = db.embed_model(item["id"])[0]
    assert db.count() == 0
    assert db.register_one(item)
    db.flush()
    assert db.get(item["id"], output_fields=["id", "sql"]) == [meta]
    assert db.count() == 1
    assert db.register_one(item) is False
    assert db.count() == 1


def test_register_many(db):
    metas = [
        {
            "id": "provide me the total sales",
            "sql": "SELECT SUM(sales) FROM sales",
        },
        {
            "id": "show me the sales by region",
            "sql": "SELECT region, SUM(sales) FROM sales GROUP BY region",
        },
    ]
    items = [meta.copy() for meta in metas]
    ids = [item["id"] for item in metas]
    vecs = db.embed_model(ids)
    for item, vec in zip(items, vecs):
        item["vector"] = vec

    count = db.count()
    assert db.register_many(items) == 1
    db.flush()
    assert db.get(ids, output_fields=["id", "sql"]) == metas
    assert db.count() == count + 1
