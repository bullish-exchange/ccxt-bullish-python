from bullish_ccxt import bullish
import pprint

exchange = bullish()
markets = exchange.load_markets()
pprint.pprint(markets['BTC/USDC'], compact=True)