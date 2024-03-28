from tests.exchange import exchange
from tests.schema_utils import matches_schema, create_order_schema, order_schema

def test_can_create_and_fetch_order():
    if not exchange.check_required_credentials(error=False):
        print("WARNING. apiKey and secret needs to be set before running this test")

    create_order_response = exchange.create_limit_buy_order("BTCUSDC", 0.1, 123.0)
    assert matches_schema(create_order_response, create_order_schema)
    
    order_id = create_order_response['orderId']
    fetch_order_response = exchange.fetch_order(id=order_id)
    assert matches_schema(fetch_order_response, order_schema)