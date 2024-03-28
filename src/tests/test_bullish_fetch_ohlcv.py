from tests.exchange import exchange
from tests.schema_utils import matches_schema, candle_schema

def test_can_fetch_ohlcv():
    ret = exchange.fetch_ohlcv('BTCUSDC', timeframe='30m')
    assert matches_schema(ret, candle_schema)
