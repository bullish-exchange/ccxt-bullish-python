from bullish_ccxt import bullish
import pprint

exchange = bullish()
markets = exchange.load_markets()
pprint.pprint(markets['BTCUSDC'], compact=True)