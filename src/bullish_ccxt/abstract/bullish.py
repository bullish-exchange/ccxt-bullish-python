from ccxt.base.types import Entry

# These ought to be code-generated, but they are written by hand for now.
class ImplicitAPI:
    ## Login not required
    public_get_markets = publicGetMarkets = Entry('markets', 'public', 'GET', {})
    public_get_market_trades_by_symbol = publicGetMarketTradesBySymbol = Entry('markets/{symbol}/trades', 'public', 'GET', {})
    public_get_market_candle_by_symbol = publicGetMarketCandleBySymbol = Entry('markets/{symbol}/candle', 'public', 'GET', {})
    public_get_market_ticker_by_symbol = publicGetMarketTickerBySymbol = Entry('markets/{symbol}/tick', 'public', 'GET', {})
    public_get_assets = publicGetAssets = Entry('assets', 'public', 'GET', {})
    public_get_order_book_for_symbol = publicGetOrderBookForSymbol = Entry('markets/{symbol}/orderbook/hybrid', 'public', 'GET', {})
    public_get_nonce = publicGetNonce = Entry('nonce', 'public', 'GET', {})
    public_get_hmac_login = publicGetHmacLogin = Entry("users/hmac/login", 'public', 'GET', {})
    public_get_time = publicGetTime = Entry("time", 'public', 'GET', {})
    
    ## Login required. Only HMAC is supported for now
    private_get_tradingaccounts = privateGetTradingAccounts = Entry('accounts/trading-accounts', 'private', 'GET', {})
    private_get_orders = privateGetOrders = Entry('orders', 'privateV2', 'GET', {})
    private_get_derivatives_positions = privateGetDerivativesPositions = Entry('derivatives-positions', 'private', 'GET', {})
    private_get_order_by_id = privateGetOrderById = Entry('orders/{id}', 'privateV2', 'GET', {})
    privateV2_post_order = privateV2PostOrder = Entry('orders', 'privateV2', 'POST', {})
    private_get_my_trades = privateGetMyTrades = Entry('trades', 'private', 'GET', {})
    private_get_account_assets = privateGetAccountAssets = Entry('accounts/asset', 'privateV2', 'GET', {})
    private_get_wallet_transactions = privateGetWalletTransactions = Entry('wallets/transactions', 'private', 'GET', {})
    private_get_amm_instructions = privateGetAMMInstructions = Entry('amm-instructions', 'privateV2', 'GET', {})
    private_get_amm_instructions_by_instruction_id = privateGetAMMInstructionsByInstructionId = Entry('amm-instructions/{instructionid}', 'privateV2', 'GET', {})