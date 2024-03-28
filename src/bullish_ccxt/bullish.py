import hmac
import json
import urllib.parse
from datetime import datetime, timezone
from hashlib import sha256
from abstract.bullish import ImplicitAPI
import logging

from ccxt.base.errors import BadRequest, PermissionDenied, BadSymbol, OrderNotFillable, NotSupported, \
    ExchangeNotAvailable, ExchangeError, OrderNotFound, AuthenticationError, InsufficientFunds
from ccxt.base.types import Num, OrderSide, Market, OrderType, Str, Int, List
from ccxt.base.exchange import Exchange

HMAC_LOGIN_PATH = "users/hmac/login"

class bullish(Exchange, ImplicitAPI):
    user_id = None
    private_key = None
    public_key = None
    
    apiKey = None
    secret: str|None = None
    account_id = None
    rate_limit_token = None
    creds = None
    last_pagination_metadata = None

    environment = 'PROD' # DEV/UAT to trigger the internal DEV/UAT environment 

    def describe(self):
        # Define metadata
        return self.deep_extend(super(bullish, self).describe(), {
            'id': 'bullish',
            'name': 'Bullish',
            'countries': ['HK', 'SG'],
            'version': 'v0.1',
            'rateLimit': 6000,  # 100 request per second
            'timeout': 10000,
            'has': {
                'cancelAllOrders': False,
                'cancelOrder': False,
                'createOrder': True,
                'fetchAccounts': True,
                'fetchCurrencies': True,
                'fetchBalance': True,
                'fetchClosedOrders': True,
                'fetchDepositAddress': False,
                'fetchDeposits': False,
                'fetchMarkets': True,
                'fetchMyTrades': True,
                'fetchOHLCV': True,
                'fetchOpenOrders': True,
                'fetchOrder': True,
                'fetchOrders': True,
                'fetchOrderBook': True,
                'fetchTicker': True,
                'fetchTickers': True,
                'fetchTime': True,
                'fetchTrades': False,
                'fetchWithdrawals': False,
                'withdraw': False,
            },
            'timeframes': {
                '1m': '1m',
                '5m': '5m',
                '30m': '30m',
                '1h': '1h',
                '6h': '6h',
                '12h': '12h',
                '1d': '1d',
            },
            'urls': {
                'api': { # the default prod endpoint
                    'public': 'https://api.exchange.bullish.com/trading-api/v1',
                    'publicV2': 'https://api.exchange.bullish.com/trading-api/v2',
                    'private': 'https://api.exchange.bullish.com/trading-api/v1',
                    'privateV2': 'https://api.exchange.bullish.com/trading-api/v2',
                },
                'test': { # this is triggered by setting sandbox mode (set_sandbox_mode) to true
                    'public': 'https://api.simnext.bullish-test.com/trading-api/v1',
                    'publicV2': 'https://api.simnext.bullish-test.com/trading-api/v2',
                    'private': 'https://api.simnext.bullish-test.com/trading-api/v1',
                    'privateV2': 'https://api.simnext.bullish-test.com/trading-api/v2',
                },
                'doc': 'https://api.exchange.bullish.com/docs/api/rest/trading-api'
            },
            'api': { 
                'public': {
                    'get': [
                        'markets',
                        'markets/{symbol}/trades',
                        'markets/{symbol}/candle'
                        'markets/{symbol}/tick'
                        'assets',
                        'nonce',
                        'time',
                        "users/hmac/login"
                    ],
                },
                'private': {
                    'get': [
                        'accounts/trading-accounts',
                        'accounts/asset',
                        'orders',
                        'orders/{id}',
                        'trades'
                    ]
                },
                'privateV2': {
                    'post': [
                        'orders'
                    ]
                }
            },
            'exceptions': {
                'exact': {
                    'EXCHANGE_OFFLINE': ExchangeNotAvailable,
                    'INVALID_ORDERBOOK_REQUEST': BadRequest,
                    'MISSING_ORDER_ID': BadRequest,
                    'INVALID_CANDLE_REQUEST': BadRequest,
                    'MARKET_NOT_SUPPORTED': BadSymbol,
                    'CLIENT_NOT_LOGGED_IN': AuthenticationError,
                    'EosUserNotExistsException': AuthenticationError,
                    'QUANTITY_REMAINING__FOK_LIMIT_ORDER': OrderNotFillable,
                    'QUANTITY_MUST_BE_POSITIVE': BadRequest,
                    'PRICE_MUST_BE_POSITIVE': BadRequest,
                    'ORDER_SIZE_OUTSIDE_VALID_RANGE': BadRequest,
                    'ACCOUNT_MISMATCH': BadRequest,
                    'CONFLICTING_ORDER_FLAGS': BadRequest,
                    'OPEN_ORDER_COUNT_BREACH': BadRequest,
                    'STRICTLY_INCREASING_ORDER_ID': BadRequest,
                    'DUPLICATE_ORDER_ID': BadRequest,
                    'NOT_ENOUGH_FUNDS__BUY_LIMIT_ORDER': InsufficientFunds,
                    'NOT_ENOUGH_FUNDS__SELL_LIMIT_ORDER': InsufficientFunds,
                    'DUPLICATE_ORDER': BadRequest,
                    'UNKNOWN_ORDER': OrderNotFound,
                    'MMS_INSUFFICIENT_BALANCE': InsufficientFunds,
                    'MMS_24_HOUR_SUBMISSION_BREACH': BadRequest,
                    'MMS_UPDATE_LARGER_THAN_SELL_AMOUNT': BadRequest,
                    'PRICE_MUST_BE_OF_TICK_SIZE': BadRequest,
                    'INSUFFICIENT_AVAILABLE_BALANCE': InsufficientFunds,
                    'MMS_UNKNOWN_ORDER': BadRequest,
                    'MARGIN_ACCOUNT_INSUFFICIENT_BALANCE': InsufficientFunds,
                    'UNKNOWN_ACCOUNT': BadRequest,
                    'ORDER_COMMAND_IGNORED': BadRequest,
                    'NO_MARGIN_ACCOUNT': InsufficientFunds,
                    'TRANSACTION_REFERENCE_BLOCK_MISMATCH': BadRequest,
                    'NOT_ENOUGH_FUNDS__BUY_MARGIN_ORDER': InsufficientFunds,
                    'NOT_ENOUGH_FUNDS__SELL_MARGIN_ORDER': InsufficientFunds,
                    'BAD_PRICE_OR_QUANTITY': BadRequest,
                },
                'broad': {
                    'UNKNOWN': ExchangeError,
                    'MALFORMED_ORDER': BadRequest,
                },
            },
            'options': {
                'defaultTimeInForce': 'GTC',
                'defaultAggregation': 10,
                # reverse/forward lookup maps
                'sideMap': {
                    'SELL': 'SELL',
                    'sell': 'SELL',
                    'BUY': 'BUY',
                    'buy': 'BUY',
                    None: None
                },
                'typeMap': {
                    'LMT': 'LIMIT',
                    'LIMIT': 'LIMIT',
                    'limit': 'LIMIT',
                    'MKT': 'MARKET',
                    'MARKET': 'MARKET',
                    'market': 'MARKET',
                    'STOP_LIMIT': 'STOP_LIMIT',
                    'stop_limit': 'STOP_LIMIT',
                    'stop+limit': 'STOP_LIMIT',
                    None: None
                }
            }
        })
    
    ##### public APIs ######

    def fetch_currencies(self, params={}):
        response = self.publicGetAssets(params)
        list_of_currencies = list(map(self.parse_currency, response))
        return {currency['code']: currency for currency in list_of_currencies} 
    
    def fetch_markets(self, params={}):
        response = self.publicGetMarkets(params)
        return list(map(self.parse_market, response))
    
    def fetch_trades(self, symbol: str, since: Int = None, limit: Int = None, params={}):
        if since is not None:
            raise BadRequest("[fetch_trades] The `since` parameter is not supported for this exchange")
        if limit is not None:
            raise BadRequest("[fetch_trades] The `limit` parameter is not supported for this exchange")
        response = self.publicGetMarketTradesBySymbol(self.extend({
            'symbol': symbol
        }, params))
        return list(map(self.parse_trade, response))
    
    def fetch_ticker(self, symbol: str, params={}):
        response = self.publicGetMarketTickerBySymbol(self.extend({
            'symbol': symbol
        }, params))
        return self.parse_ticker(response, symbol)
    
    def fetch_tickers(self, symbols: List[str] = None, params={}):
        if symbols is None:
            self.load_markets()
            symbols = self.symbols
        tickers = list(map(self.fetch_ticker, symbols))
        return {ticker['symbol']: ticker for ticker in tickers} 
    
    def fetch_ohlcv(self, symbol: str, timeframe='1m', since: Int = None, limit: Int = None, params={}):
        if timeframe not in self.timeframes:
            raise BadRequest("[fetch_ohlcv] timeframe '%s' is not supported" % timeframe)
        request = {
            'symbol': symbol,
            'timeBucket': self.timeframes[timeframe],
        }
        if since is None:
            if limit is None:
                limit = 500
            duration = self.parse_timeframe(timeframe) * 1000
            since = self.milliseconds() - duration * limit

        end = self.sum(since, limit * self.parse_timeframe(timeframe) * 1000)
        request['createdAtDatetime[gte]'] = self.iso8601(since)
        request['createdAtDatetime[lte]'] = self.iso8601(end)    

        response = self.publicGetMarketCandleBySymbol(self.extend(request, params))
        return list(map(self.parse_ohlcv, response))
    
    def fetch_order_book(self, symbol: str, limit: Int = None, params={}):
        if limit is not None:
            raise NotSupported('fetch_order_book() with limit is not supported')
        request = {
            'symbol': symbol,
            'aggregationFactor': params['aggregationFactor'] if 'aggregationFactor' in params else self.options[
                'defaultAggregation'],
            'depth': params['depth'] if 'depth' in params else 100
        }
        response = self.publicGetOrderBookForSymbol(self.extend(request, params))
        to_rt = self._parse_order_book(
            response,
            symbol,
            timestamp=int(self.safe_value(response, 'timestamp', 0))
        )
        return to_rt
    
    def fetch_server_nonce(self, params={}):
        response = self.publicGetNonce(params)
        nonce = response["lowerBound"]
        return nonce
    
    def fetch_time(self, params={}):
        return self.publicGetTime(params)
    
    ### Login ########

    def login(self, params={}):
        self.log("Attempting to access private API. Checking if session is also logged in")
        if not self.creds:
            self.check_required_credentials()
            self.log("New login credentials required")
            self.creds = self.publicGetHmacLogin(params)
        else:
            self.log("Login credentials present")
        
        if self.creds and self.creds.get('token'):
            # Only print this for non-server environments
            # TODO: handle case where JWT token expired - for the case of long running clients
            self.log("Login Successfully obtained", self.creds)
        else:
            raise PermissionDenied("Login unsuccessful. Please check apiKey and secret")
        return self.creds
    
    ### Private APIs ########

    def local_nonce(self):
        return str(int(datetime.now(timezone.utc).timestamp() * 1_000_000))
    
    def fetch_accounts(self, params={}):
        response = self.privateGetTradingAccounts(params)
        return list(map(self.parse_account, response))
    
    def fetch_balance(self, params={}):
        response = self.privateGetAccountAssets(params)
        balances = list(map(self.parse_balance, response))
        return {balance['asset']: balance for balance in balances} 
    
    def create_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, params={}):
        next_nonce = self.local_nonce()
        time_in_force = params.get('timeInForce', self.options["defaultTimeInForce"])
        request = {
            "symbol": symbol, 
            "commandType": "V3CreateOrder",
            "side": self.options['sideMap'][side],
            "type": self.options['typeMap'][type],
            "timeInForce": time_in_force,
            "quantity": str(amount),
            "clientOrderId": next_nonce,
            "tradingAccountId": self.account_id,
        }
        if price is not None:
            request['price'] = str(price)
        return self.privateV2PostOrder(self.extend(request, params))
    
    def fetch_my_trades(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        paginated_request = self._make_paginated_private_request(symbol, since, limit, params)
        response = self.privateGetMyTrades(self.extend(paginated_request, params))
        self.last_pagination_metadata = self._parse_pagination_metadata(self.safe_dict(response, 'links'))
        self.log("Pagination datadata updated.", self.last_pagination_metadata)
        return list(map(self.parse_trade, self.safe_list(response, 'data')))
    
    def fetch_orders(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        paginated_request = self._make_paginated_private_request(symbol, since, limit, params)
        response = self.privateGetOrders(self.extend(paginated_request, params))
        self.last_pagination_metadata = self._parse_pagination_metadata(self.safe_dict(response, 'links'))
        self.log("Pagination datadata updated.", self.last_pagination_metadata)
        return list(map(self.parse_order, self.safe_list(response, 'data')))
    
    def fetch_order(self, id: str, symbol: Str = None, params={}):
        if symbol is not None:
            raise BadRequest("[fetch_order] The `symbol` parameter is not supported for this exchange")
        bullish_request = {
            "tradingAccountId": self.account_id,
            "id": id,
        }
        response = self.private_get_order_by_id(self.extend(bullish_request, params))
        return self.parse_order(response)
    
    def fetch_deposits_withdrawals(self, code: Str = None, since: Int = None, limit: Int = None, params={}):
        if code is not None:
            raise BadRequest("[fetch_deposits_withdrawals] The `code` parameter is not supported for this exchange")
        paginated_request = self._make_paginated_wallet_request(since, limit, params)
        response = self.privateGetWalletTransactions(paginated_request)
        self.last_pagination_metadata = self._parse_pagination_metadata(self.safe_dict(response, 'links'))
        self.log("Pagination datadata updated.", self.last_pagination_metadata)
        return list(map(self.parse_depositwithdrawal, self.safe_list(response, 'data')))
    
    def fetch_amm_instructions(self, symbol: Str = None, params={}):
        bullish_request = {
            "tradingAccountId": self.account_id,
        }
        if symbol is not None:
            bullish_request['symbol'] = symbol
        return self.privateGetAMMInstructions(self.extend(bullish_request, params))

    def fetch_amm_instruction(self, instructionId: str, symbol: Str = None, params={}):
        if symbol is not None:
            raise BadRequest("[fetch_order] The `symbol` parameter is not supported for this exchange")
        bullish_request = {
            "tradingAccountId": self.account_id,
            "instructionId": instructionId,
        }
        return self.private_get_amm_instructions_by_instruction_id(self.extend(bullish_request, params))

    ## Request formatting
    ####################

    def _is_private_api(self, api: str) -> bool:
        return api == 'private' or api == 'privateV2'
    
    def _is_public_api(self, api: str) -> bool:
        return api == 'public' or api == 'publicV2'
    
    def _conform_page_size(self, limit):
        if limit <= 5:
            page_size = 5
        elif limit <= 25:
            page_size = 25
        elif limit <= 50:
            page_size = 50
        else:
            page_size = 100
        return page_size
    
    def _make_paginated_wallet_request(self, since: Int = None, limit: Int = None, params={}):
        request = {
            "_metaData": "true"
        }
        if limit is not None:
            limit = self._conform_page_size(limit)
        if since is not None:
            request['createdAtTimestamp[gte]'] = since
        if limit is not None:
            request["_pageSize"] = limit
        if self.safe_string(params, "_nextPage"):
            request["_nextPage"] = self.safe_string(params, "_nextPage")
        if self.safe_string(params, "_previousPage"):
            request["_previousPage"] = self.safe_string(params, "_previousPage")
        if limit is None and self.safe_string(params, "_pageSize"):
            page_size = self._conform_page_size(self.safe_integer(params, "_pageSize"))
            request["_pageSize"] = page_size

        return request
    
    def _make_paginated_private_request(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        request = {
            "tradingAccountId": self.account_id,
            "_metaData": "true"
        }
        if limit is not None:
            limit = self._conform_page_size(limit)
        if since is not None:
            request['createdAtTimestamp[gte]'] = since
        if symbol is not None:
            request["symbol"] = symbol
        if limit is not None:
            request["_pageSize"] = limit
        if self.safe_string(params, "_nextPage"):
            request["_nextPage"] = self.safe_string(params, "_nextPage")
        if self.safe_string(params, "_previousPage"):
            request["_previousPage"] = self.safe_string(params, "_previousPage")
        if limit is None and self.safe_string(params, "_pageSize"):
            page_size = self._conform_page_size(self.safe_integer(params, "_pageSize"))
            request["_pageSize"] = page_size

        return request

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = "/" + self.implode_params(path, params)
        signing_path = urllib.parse.urlparse(self.urls['api'][api] + request).path
        
        query = self.keysort(self.omit(params, self.extract_params(path)))
        if self._is_private_api(api):
            creds = self.login()
            if method == 'GET':
                headers = {
                    'Accept': 'application/json',
                    'Accept-Charset': 'UTF-8',
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.safe_string(creds, 'token'),
                    'BM-AUTH-APIKEY': self.apiKey
                }
                request += '?' + self.urlencode(query)
            if method == 'POST':
                body = self.json(query)
                body_string = json.dumps(query, separators=(",", ":"))
                secret_bytes = bytes(self.secret, 'utf-8')
                nonce = str(self.nonce())
                next_nonce = self.local_nonce()
                timestamp = str(int(datetime.now(timezone.utc).timestamp() * 1000))
                payload = timestamp + next_nonce + "POST" + signing_path + body_string
                digest = sha256(payload.encode("utf-8")).hexdigest().encode('utf-8')
                signature = hmac.new(secret_bytes, digest, sha256).hexdigest()
                headers = {
                    "Content-type": "application/json",
                    "Authorization": 'Bearer ' + self.safe_string(creds, 'token'),
                    "BX-SIGNATURE": signature,
                    "BX-TIMESTAMP": timestamp,
                    "BX-NONCE": next_nonce,
                    'BM-AUTH-APIKEY': self.apiKey,
                    "BX-RATELIMIT-TOKEN": f"{self.rate_limit_token}"
                }

        elif self._is_public_api(api):
            if query and method == 'GET':
                request += '?' + self.urlencode(query)

            # Special case to handle login using the HMAC flow    
            if HMAC_LOGIN_PATH == path:
                nonce = str(self.nonce())
                ts = str(int(datetime.now(timezone.utc).timestamp() * 1000))
                message = ts + nonce + "GET" + signing_path
                signature = hmac.new(bytes(self.secret, 'utf-8'), message.encode("utf-8"), sha256).hexdigest()
                headers = {
                    'BX-PUBLIC-KEY': self.apiKey,
                    'BX-NONCE': nonce,
                    'BX-SIGNATURE': signature,
                    'BX-TIMESTAMP': ts
                }
        # This gives the ability to switch from PROD to UAT/DEV accounts
        url_key = 'api'
        if self.environment == 'DEV':
            url_key = 'dev'
        if self.environment == 'UAT':
            url_key = 'uat'
        url = self.urls[url_key][api] + request
        return {'url': url, 'method': method, 'body': body, 'headers': headers}


    ### Response parsing
    ####################    

    def _parse_pagination_metadata(self, metadata):
        return {
            "previous": self._linkToParams(self.safe_string(metadata, "previous")),
            "next": self._linkToParams(self.safe_string(metadata, "next"))
        }
    

    def _linkToParams(self, link):
        if link is None:
            return None
        return dict(urllib.parse.parse_qsl(urllib.parse.urlparse(link).query))
    
    def fetch_positions(self, symbols: List[str] = None, params={}):
        self.log("Warning - only Derivative positions are available", log_level='INFO')
        response = self.privateGetDerivativesPositions(params)
        return self.parse_positions(response, symbols, params)
    
    def fetch_position(self, symbol: str, params={}):
        self.log("Warning - only Derivative positions are available")
        response = self.privateGetDerivativesPositions(self.extend({
            'symbol': symbol
        }, params))
        positions = self.parse_positions(response, None, params)
        position_map = {position['symbol']: position for position in positions} 
        return self.safe_value(position_map, symbol)

    
    def parse_ticker(self, ticker, symbol):
        return {
            'symbol': symbol,
            'timestamp': self.safe_integer(ticker, 'createdAtTimestamp'),
            'datetime': self.safe_string(ticker, 'createdAtDatetime'),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'bestBid'),
            'bidVolume': self.safe_float(ticker, 'bidVolume'),
            'ask': self.safe_float(ticker, 'bestAsk'),
            'askVolume': self.safe_float(ticker, 'askVolume'),
            'vwap': self.safe_float(ticker, 'vwap'),
            'open': self.safe_float(ticker, 'open'),
            'close': self.safe_float(ticker, 'close'),
            'last': self.safe_float(ticker, 'last'),
            'previousClose': self.safe_float(ticker, 'previousClose'),
            'change': self.safe_float(ticker, 'change'),
            'percentage': self.safe_float(ticker, 'percentage'),
            'average': self.safe_float(ticker, 'average'),
            'baseVolume': self.safe_float(ticker, 'baseVolume'),
            'quoteVolume': self.safe_float(ticker, 'quoteVolume'),
            'info': ticker,
        }

    def parse_ohlcv(self, ohlcv, market=None):
        return [
            self.safe_integer(ohlcv, 'createdAtTimestamp', None),
            self.safe_float(ohlcv, 'open'),
            self.safe_float(ohlcv, 'high'),
            self.safe_float(ohlcv, 'low'),
            self.safe_float(ohlcv, 'close'),
            self.safe_float(ohlcv, 'volume'),
        ]

    def parse_currency(self, currency):
        return {
            'id': self.safe_string(currency, 'assetId'),
            'code': self.safe_string(currency, 'symbol'),
            'precision': self.safe_integer(currency, 'precision'),
            'name': self.safe_string(currency, 'symbol'),
            'active': True,
            'fee': self.safe_float(currency, 'minFee'),
            'limits': {
                'amount': {
                    'min': None,
                    'max': None
                },
                'withdraw': {
                    'min': None,
                    'max': None
                },
            },
            'info': currency,
        }
    
    def parse_market(self, market):
        return {
            'id': self.safe_string(market, 'marketId'),
            'symbol': self.safe_string(market, 'symbol'),
            'base': self.safe_string(market, 'baseSymbol'),
            'quote': self.safe_string(market, 'quoteSymbol'),
            'baseId': self.safe_string(market, 'baseAssetId'),
            'quoteId': self.safe_string(market, 'quoteAssetId'),
            'active': self.safe_bool(market, 'marketEnabled'),
            'type': self.safe_string(market, 'marketType'),
            'subType': self.safe_string(market, 'marketType'),
            'spot': self.safe_string(market, 'marketType') == 'SPOT' and self.safe_bool(market, 'spotTradingEnabled'),
            'margin': self.safe_string(market, 'marketType') == 'SPOT' and self.safe_bool(market, 'marginTradingEnabled'),
            'swap': False,
            'future': self.safe_string(market, 'marketType') == 'PERPETUAL',
            'option': False,
            'contract': self.safe_string(market, 'marketType') == 'PERPETUAL',
            'taker': self.safe_float(market, 'takerFee'),
            'maker': self.safe_float(market, 'makerFee'),
            'percentage': True,
            'tierBased': False,
            'precision': {
                'price': self.safe_integer(market, 'pricePrecision'),
                'amount': self.safe_integer(market, 'quantityPrecision'),
                'cost': self.safe_integer(market, 'costPrecision')
            },
            'limits': {
                'price': {
                    'min': self.safe_float(market, 'minPriceLimit'),
                    'max': self.safe_float(market, 'maxPriceLimit'),
                },
                'amount': {
                    'min': self.safe_float(market, 'minQuantityLimit'),
                    'max': self.safe_float(market, 'maxQuantityLimit'),
                },
                'cost': {
                    'min': self.safe_float(market, 'minCostLimit'),
                    'max': self.safe_float(market, 'maxCostLimit'),
                },
            },
            'info': market
        }
    
    def parse_trade(self, trade):
        amount = self.safe_float(trade, 'quantity', 0.0)
        price = self.safe_float(trade, 'price', 0.0)
        is_taker = self.safe_bool(trade, "isTaker")
        if is_taker:
            taker_or_maker = 'taker'
        else:
            taker_or_maker = "maker"
        return {
            'id': self.safe_string(trade, 'tradeId'),
            'datetime': self.safe_string(trade, 'createdAtDatetime', None),
            'timestamp': self.safe_integer(trade, 'createdAtTimestamp', None),
            'symbol': self.safe_string(trade, 'symbol', None),
            'order': self.safe_string(trade, 'orderId', None),
            'side': self.parse_side(self.safe_string(trade, 'side')),
            'price': price,
            'amount': amount,
            'cost': amount * price,
            'takerOrMaker': taker_or_maker,
            'info': trade,
        }
    
    def parse_account(self, account):
        return {
            'id': self.safe_string(account, 'tradingAccountId'),
            'type': self.safe_string(account, 'tradingAccountName'),
            'base': None,
            'code': self.safe_string(account, 'rateLimitToken'),
            'info': account,
        }
    
    def parse_balance(self, balance):
        return {
            'asset': self.safe_string(balance, 'assetSymbol'),
            'datetime': self.safe_string(balance, 'updatedAtDatetime'),
            'timestamp': self.safe_integer(balance, 'updatedAtTimestamp'),
            'free': self.safe_number(balance, 'availableQuantity'),
            'used': self.safe_number(balance, 'lockedQuantity'),
            'accountId': self.safe_string(balance, 'tradingAccountId'),
            'info': balance,
        }
    
    def parse_order(self, order, market: Market = None):
        fee = self.safe_number(order, 'baseFee', 0.0) + self.safe_number(order, 'quoteFee', 0.0)
        avg_price = self.safe_number(order, 'avgPrice', self.safe_number(order, 'price', 0.0))
        quantity = self.safe_number(order, 'quantity', 0.0)
        cost = avg_price * quantity
        return {
            'id': self.safe_string(order, 'orderId'),
            'clientOrderId': self.safe_string(order, 'clientOrderId'),
            'datetime': self.safe_string(order, 'createdAtDatetime'),
            'timestamp': self.safe_integer(order, 'createdAtTimestamp'),
            'lastTradeTimestamp': None,
            'status': self.parse_order_status(self.safe_string(order, 'status')),
            'symbol': self.safe_string(order, 'symbol'),
            'type': self.parse_order_type(self.safe_string(order, 'type')),
            'timeInForce': self.safe_string(order, 'timeInForce'),
            'side': self.parse_side(self.safe_string(order, 'side')),
            'price': self.safe_number(order, 'price'),
            'average': avg_price,
            'amount': self.safe_number(order, 'quantity', 0.0),
            'filled': self.safe_number(order, 'quantityFilled', '0.0'),
            'remaining': self.safe_number(order, 'quantity', 0.0) - self.safe_number(order, 'quantityFilled', '0.0'),
            'stopPrice': self.safe_number(order, 'stopPrice'),
            'takeProfitPrice': self.safe_number(order, 'takeProfitPrice'),
            'cost': cost,
            'trades': [],
            'fee': {
                'currency': self.safe_string(market, 'quote'),
                'cost': fee,
                'rate': None,
            },
            'info': order,
        }
    
    def parse_position(self, position, market: Market = None):
        return {
            'symbol': self.safe_string(position, 'symbol'),
            'side': self.parse_position_side(self.safe_string(position, 'side')),
            'timestamp': self.safe_integer(position, 'updatedAtTimestamp', self.safe_integer(position, 'createdAtTimestamp')),
            'datetime': self.safe_string(position, 'updatedAtDatetime', self.safe_string(position, 'createdAtDatetime')),
            'contracts': self.safe_number(position, 'quantity'),
            'notional': self.safe_number(position, 'notional'),
            'unrealizedPnl': self.safe_number(position, 'mtmPnl'),
            'realizedPnl': self.safe_number(position, 'realizedPnl'),
            'info': position
        }
    
    def parse_order_status(self, status):
        statuses = {
            'NEW': 'open',
            'LIVE': 'open',
            'PARTIAL': 'open',
            'FILLED': 'closed',
            'REJECTED': 'closed',
            'CANCELLED': 'canceled',
        }
        return self.safe_string(statuses, status) if status is not None else None
    
    def parse_order_type(self, type):
        if type is None:
            return None
        if type == 'MARKET' or type == 'MKT':
            return 'market'
        return 'limit'
    
    def parse_depositwithdrawal(self, payload):
        transaction_details = self.safe_dict(payload, 'transactionDetails')
        return {
            'id': self.safe_symbol(payload, 'custodyTransactionId'),
            'txid': self.safe_symbol(transaction_details, 'blockchainTxId'),
            'type': self.parse_transaction_direction(self.safe_string(payload, 'direction')),
            'amount': self.safe_string(payload, 'quantity'),
            'currency': self.safe_string(payload, 'symbol'),
            'address': self.safe_string(transaction_details, 'address'),
            "status": self.parse_transaction_status(self.safe_string(payload, 'status')),
            'tag': self.safe_string(payload, 'memo'),
            'datetime': self.safe_string(payload, 'createdAtDateTime'),
            'info': payload
        }
    
    def parse_side(self, side):
        if side == 'BUY':
            return 'buy'
        if side == 'SELL':
            return 'sell'
        return None
    
    def parse_position_side(self, side):
        if side == 'BUY':
            return 'long'
        if side == 'SELL':
            return 'short'
        return None
    
    def parse_transaction_direction(self, direction):
        if direction == 'DEPOSIT':
            return 'deposit'
        if direction == 'WITHDRAWAL':
            return 'withdrawal'
        return None
    
    def parse_transaction_status(self, status):
        if status == 'PENDING':
            return None # No status yet
        if status == 'COMPLETE':
            return 'ok'
        if status == 'CANCELLED':
            return 'canceled'
        if status == 'FAILED':
            return 'failed'
        return None
    
    
    # Unfortunately the bullish API doesn't return price and quantity in an ordered list form, so slight changes necessary here
    def _parse_order_book(self, orderbook: object, symbol: str, timestamp: Int = None, bidsKey='bids', asksKey='asks', priceKey: str = 'price', amountKey: str = 'priceLevelQuantity'):
        bids = self._parse_bids_asks(self.safe_value(orderbook, bidsKey, []), priceKey, amountKey)
        asks = self._parse_bids_asks(self.safe_value(orderbook, asksKey, []), priceKey, amountKey)
        return {
            'symbol': symbol,
            'bids': self.sort_by(bids, 0, True),
            'asks': self.sort_by(asks, 0),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'nonce': self.safe_integer(orderbook, 'sequenceNumber'),
        }

    def _parse_bids_asks(self, bidasks, priceKey: str, amountKey: str):
        bidasks = self.to_array(bidasks)
        result = []
        for i in range(0, len(bidasks)):
            result.append(self.parse_bid_ask(bidasks[i], priceKey, amountKey))
        return result
    
    def _parse_bid_ask(self, bidask, priceKey: str, amountKey: str):
        price = self.safe_number(bidask, priceKey)
        amount = self.safe_number(bidask, amountKey)
        return [price, amount]
    
    ### Error handling #####
    
    def handle_errors(self, statusCode, statusText, url, method, responseHeaders, responseBody, response, requestHeaders, requestBody):
        if response is None:
            return None # fallback to default error handler

        code = self.safe_string(response, 'errorCode')
        message = self.safe_string(response, 'message')
        if code:
            feedback = self.id + ' ' + responseBody
            self.throw_exactly_matched_exception(self.exceptions['exact'], message, feedback)
            self.throw_exactly_matched_exception(self.exceptions['exact'], code, feedback)
            self.throw_broadly_matched_exception(self.exceptions['broad'], message, feedback)
            raise ExchangeError(feedback)  # unknown message
        
        return None # Again, fallback to default handler if an appropriate error mapping cannot be done
    
    def log(self, msg, log_level = logging.INFO, *args):
        if log_level == logging.DEBUG:
            self.logger.debug(msg, *args)
        elif log_level == logging.WARN:
            self.logger.warn(msg, *args)
        elif log_level == logging.ERROR:
           self.logger.error(msg, *args)
        else:
            self.logger.info(msg, *args)