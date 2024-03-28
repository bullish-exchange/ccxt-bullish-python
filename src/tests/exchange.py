from bullish_ccxt.bullish import bullish

## Important. Setup API keys (HVAC) before running test
'''
exchange = bullish({
        'environment': 'DEV',
        'apiKey': [Enter API Key],
        'secret': [Enter Secret],
        'account_id': [Enter Account Id],
    })
'''
exchange = bullish({
        'environment': 'DEV',
    })
