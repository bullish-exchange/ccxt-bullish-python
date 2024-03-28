# CCXT exchange for Bullish (Python)
## Overview
This python [ccxt](https://github.com/ccxt/ccxt) wrapper for the [Bullish Trading API](https://api.exchange.bullish.com/docs/api/rest/trading-api/v2/) is work in progress. This only supports API calls on selected functionality, mainly on the read path. Please see the [known gaps section](#known-gaps) for the features that are not yet available.

## Pre-requisites
A valid [API Key and Secret](https://support.bullish.com/hc/en-us/articles/24233383371033-How-do-I-manage-my-API-keys) pair (HMAC) is required to access private API functionality.

## Installation
This module can be installed using `pip3` via source files in git. In particular:

```
pip3 install git+https://github.com/bullish-exchange/ccxt-bullish-python.git
```
or
```
pip3 install git+ssh://git@github.com/bullish-exchange/ccxt-bullish-python.git
```

## Getting started

As this is not merged into [ccxt](https://github.com/ccxt/ccxt) yet, but available as a module - instantiate the bullish exchange object like the following:
```python
from bullish_ccxt import bullish

my_logger = # Setup your logger...

exchange = bullish({
        'logger': my_logger,
        'apiKey': <API key>,
        'secret': <API secret>,
        'account_id': <Account ID>,
    })

fetch_balance_response = exchange.fetch_balance()
print(fetch_balance_response)
```

## Running Integration tests
This is currently only necessary if you are trying to contribute. Update `tests/exchange.py` with your setup, such as environment and API keys. For example,
```python
from bullish_ccxt import bullish

exchange = bullish({
        'apiKey': <API key>,
        'secret': <API secret>,
        'account_id': <Account ID>,
    })

exchange.set_sandbox_mode(True) # The tests are integration tests
```

At the parent folder of `tests`, trigger the tests with `pytest`

## Available environments
- Prod
- Sandbox (set `exchange.set_sandbox_mode(True)` to activate sandbox)

## Known gaps
- Only supports HMAC API Keys
- [ccxt unified symbols](https://docs.ccxt.com/#/?id=naming-consistency) is not yet implemented. Market symbols are still following Bullish's naming convention. For example, the BTC/USDC spot market have a symbol of `BTCUSDC`.
- WebSocket support is not available
- Only read path functionality is available - such as `fetch_markets` and `fetch_orders`. 
- Wallet/Custody functionality is not available yet

## Feature requests
Please create issues via Github to request features or to report bugs.