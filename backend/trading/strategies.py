import pandas as pd

def rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def sma(prices, period=50):
    return prices.rolling(window=period).mean()

def rsi_sma_strategy(historical_data, params):
    """
    Décision de trading basée sur le RSI et une SMA.
    - ACHAT: RSI < 30 et prix au-dessus de la SMA.
    - VENTE: RSI > 70 et prix en-dessous de la SMA.
    """
    prices = pd.Series([float(d['c']) for d in historical_data['candles']])
    
    current_price = prices.iloc[-1]
    rsi_val = rsi(prices, params.get('rsi_period', 14)).iloc[-1]
    sma_val = sma(prices, params.get('sma_period', 50)).iloc[-1]

    decision = 'HOLD'
    if rsi_val < 30 and current_price > sma_val:
        decision = 'BUY'
    elif rsi_val > 70 and current_price < sma_val:
        decision = 'SELL'
        
    return {
        'decision': decision,
        'current_price': current_price,
        'rsi': rsi_val,
        'sma': sma_val
    }
