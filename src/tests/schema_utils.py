from schema import Schema, SchemaError, Optional, Or

def matches_schema(values, schema: Schema) -> bool:
    try:
        schema.validate(values)
        return True
    except SchemaError as e:
        print(e)
        return False

_limit_schema = Schema({
    'min': Or(None, float),
    'max': Or(None, float),
})

_limit_schema = Schema({
    'min': Or(None, float),
    'max': Or(None, float),
})

#### CURRENCY #####

_currency_limit_schema = Schema({
    'amount': _limit_schema,
    'withdraw': _limit_schema,
})

currency_schema = Schema({
    'id': str,
    'code': str,
    'name': str,
    'active': bool,
    'fee': Or(None, float),
    'precision': int,
    'limits': _currency_limit_schema,
    'info': object,
})

currencies_schema = Schema({str: currency_schema})

#### MARKETS #######

_precision_schema = Schema({
    'price': int,
    'amount': int,
    'cost': int,
})

_market_limits_schema = Schema({
    'amount': _limit_schema,
    'price': _limit_schema,
    'cost': _limit_schema,
})

market_schema = Schema({
    'id': str,
    'symbol': str,
    'base': str,
    'quote': str,
    'baseId': str,
    'quoteId': str,
    'active': bool,
    'taker': float,
    'maker': float,
    'percentage': bool,
    'tierBased': bool,
    'contract': bool,
    'future': bool,
    'margin': bool,
    'spot': bool,
    'option': bool,
    'swap': bool,
    'type': str,
    'subType': str,
    'precision': _precision_schema,
    'limits': _market_limits_schema,
    'info': object
})

markets_schema = Schema([market_schema])

### TRADES

trade_schema = {
    'id': str,
    'timestamp': int,
    'datetime': str,
    'symbol': str,
    'order': Schema(Or(None, str)),
    'side': Schema(Or('buy', 'sell')),
    'price': float,
    'amount': float,
    'cost': float,
    Optional('type'): Schema(Or('market', 'limit')),
    Optional('takerOrMaker'): Schema(Or('taker', 'maker')),
    'info': object,
}

trades_schema = Schema([trade_schema])

### POSITIONS

position_schema = Schema({
    'timestamp': int,
    'datetime': str,
    'symbol': str,
    'side': Schema(Or('long', 'short')),
    'notional': float,
    'unrealizedPnl': float,
    'realizedPnl': float,
    'contracts': float,
    'info': object,
})

positions_schema = Schema([position_schema])

### TICKERS

ticker_schema = Schema({
    'symbol': str,
    'timestamp': int,
    'datetime': str,
    'high': Or(float, None),
    'low': Or(float, None),
    'bid': Or(float, None),
    'bidVolume': Or(float, None),
    'ask': Or(float, None),
    'askVolume': Or(float, None),
    'vwap': Or(float, None),
    'open': Or(float, None),
    'close': Or(float, None),
    'last': Or(float, None),
    'previousClose': Or(float, None),
    'change': Or(float, None),
    'percentage': Or(float, None),
    'average': Or(float, None),
    'baseVolume': Or(float, None),
    'quoteVolume': Or(float, None),
    'info': object,
})

tickers_schema = Schema({str: ticker_schema})

### ORDER BOOK

orderbook_schema = Schema({
    'symbol': str,
    'bids': [[float, float]],
    'asks': [[float, float]],
    'timestamp': int,
    'datetime': str,
    'nonce': int
})

### CANDLE, a.k.a ohlcv

candle_schema = Schema([Schema([int, float, float, float, float, float])])


### ORDERS

create_order_schema = Schema({
    'message': str,
    'requestId': str,
    'orderId': str,
    'clientOrderId': str
})


order_schema = Schema({
    'id': str,
    'clientOrderId': Or(None, str),
    'datetime': str,
    'timestamp': int,
    'lastTradeTimestamp': Or(None, int),
    'status': Schema(Or('open', 'closed', 'canceled', None)),
    'symbol': str,
    'type': Schema(Or('market', 'limit')),
    'timeInForce': Or(None, 'GTC', 'IOC', 'FOK', 'PO'),
    'side': Schema(Or('buy', 'sell')),
    'price': float,
    'stopPrice': Or(None, float),
    'takeProfitPrice': Or(None, float),
    'average': Or(None, float),
    'amount': float,
    'filled': float,
    'remaining': float,
    'cost': float,
    'trades': Schema(Or(list, None)),
    'fee': {
        'currency': Or(None, str),
        'cost': Or(None, float),
        'rate': Or(None, float),
    },
    'info': dict
})

orders_schema = Schema([order_schema])

# pagination

_page_schema = Schema({
    '_metaData': str,
    Optional('symbol'): str,
    Optional('tradingAccountId'): str,
    Optional('_previousPage'): str,
    Optional('_nextPage'): str,
    Optional('_pageSize'): str,
})

pagination_metadata_schema = Schema({
    'previous': Or(None, _page_schema),
    'next': Or(None, _page_schema),
})