from tests.exchange import exchange
from tests.schema_utils import matches_schema, orderbook_schema

def test_can_fetch_orderbook():
    ret = exchange.fetch_order_book('BTCUSDC')
    assert matches_schema(ret, orderbook_schema)
