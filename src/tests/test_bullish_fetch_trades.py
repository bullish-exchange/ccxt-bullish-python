from tests.exchange import exchange
from tests.schema_utils import matches_schema, trades_schema

def test_can_fetch_trades():
    ret = exchange.fetch_trades(symbol='BTC/USDC')
    assert matches_schema(ret, trades_schema)
