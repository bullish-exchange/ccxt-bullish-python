from tests.exchange import exchange
from tests.schema_utils import matches_schema, markets_schema

def test_can_fetch_markets():
    ret = exchange.fetch_markets()
    assert matches_schema(ret, markets_schema)
