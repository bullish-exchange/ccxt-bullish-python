from tests.exchange import exchange
from tests.schema_utils import matches_schema, currencies_schema

def test_can_fetch_currencies():
    ret = exchange.fetch_currencies()
    assert matches_schema(ret, currencies_schema)