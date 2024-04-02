from tests.exchange import exchange
from tests.schema_utils import matches_schema, create_order_schema, order_schema, position_schema, positions_schema

def test_can_create_perp_position():
    # Note: Trading account needs to support margin for this to work
    create_order_response = exchange.create_market_buy_order("BTC/USDC:USDC", 0.01)
    assert matches_schema(create_order_response, create_order_schema)
    
    order_id = create_order_response['orderId']
    fetch_order_response = exchange.fetch_order(id=order_id)
    assert matches_schema(fetch_order_response, order_schema)

def test_can_fetch_positions():
    ret = exchange.fetch_positions()
    assert matches_schema(ret, positions_schema)

def test_can_fetch_position():
    ret = exchange.fetch_position('BTC/USDC:USDC')
    assert matches_schema(ret, position_schema)
