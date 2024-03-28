from tests.exchange import exchange
from tests.schema_utils import matches_schema, create_order_schema, orders_schema, pagination_metadata_schema
import pytest

@pytest.fixture(autouse=True)
def check_credentials():
    if not exchange.check_required_credentials(error=False):
        print("WARNING. apiKey and secret needs to be set before running this test")

def test_create_order():
    create_order_response = exchange.create_limit_buy_order("BTCUSDC", 0.1, 123.0)
    assert matches_schema(create_order_response, create_order_schema)

def test_can_fetch_orders():
    fetch_orders_response = exchange.fetch_orders()
    assert matches_schema(fetch_orders_response, orders_schema)

def test_can_fetch_orders_with_page_size():
    fetch_orders_response = exchange.fetch_orders(limit=5)
    assert matches_schema(fetch_orders_response, orders_schema)
    assert len(fetch_orders_response) <= 5

def test_will_fill_pagination_parameters():
    exchange.fetch_orders(limit=5)
    assert matches_schema(exchange.last_pagination_metadata, pagination_metadata_schema)

