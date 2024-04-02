from tests.exchange import exchange
from tests.schema_utils import matches_schema, tickers_schema

def test_can_fetch_tickers():
    ret = exchange.fetch_tickers(['BTC/USDC'])
    assert matches_schema(ret, tickers_schema)
