import pandas as pd
import numpy as np

def rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def sma(prices, period=50):
    return prices.rolling(window=period).mean()

def ema(prices, period=12):
    """Calcule la moyenne mobile exponentielle"""
    return prices.ewm(span=period, adjust=False).mean()

def macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """
    Calcule le MACD (Moving Average Convergence Divergence)
    Retourne: macd_line, signal_line, histogram
    """
    ema_fast = ema(prices, fast_period)
    ema_slow = ema(prices, slow_period)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal_period)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

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
        'price': current_price,
        'rsi': rsi_val,
        'sma': sma_val,
        'details': f'RSI: {rsi_val:.2f}, SMA: {sma_val:.2f}, Price: {current_price:.5f}'
    }

def macd_strategy(historical_data, params):
    """
    Stratégie basée sur le MACD
    - ACHAT: MACD croise au-dessus de la ligne de signal (histogram > 0 et en augmentation)
    - VENTE: MACD croise en-dessous de la ligne de signal (histogram < 0 et en diminution)
    """
    prices = pd.Series([float(d['c']) for d in historical_data['candles']])
    
    current_price = prices.iloc[-1]
    fast_period = params.get('fast_period', 12)
    slow_period = params.get('slow_period', 26)
    signal_period = params.get('signal_period', 9)
    
    macd_line, signal_line, histogram = macd(prices, fast_period, slow_period, signal_period)
    
    # Valeurs actuelles et précédentes
    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]
    current_histogram = histogram.iloc[-1]
    
    # Vérifier s'il y a assez de données pour la comparaison précédente
    if len(histogram) > 1:
        prev_histogram = histogram.iloc[-2]
    else:
        prev_histogram = 0
    
    decision = 'HOLD'
    
    # Signal d'achat: MACD croise au-dessus de la ligne de signal
    if current_histogram > 0 and prev_histogram <= 0:
        decision = 'BUY'
    # Signal de vente: MACD croise en-dessous de la ligne de signal
    elif current_histogram < 0 and prev_histogram >= 0:
        decision = 'SELL'
    
    return {
        'decision': decision,
        'price': current_price,
        'macd': current_macd,
        'signal': current_signal,
        'histogram': current_histogram,
        'details': f'MACD: {current_macd:.5f}, Signal: {current_signal:.5f}, Histogram: {current_histogram:.5f}, Price: {current_price:.5f}'
    }

def ema_cross_strategy(historical_data, params):
    """
    Stratégie basée sur le croisement de deux EMA
    - ACHAT: EMA rapide croise au-dessus de l'EMA lente
    - VENTE: EMA rapide croise en-dessous de l'EMA lente
    """
    prices = pd.Series([float(d['c']) for d in historical_data['candles']])
    
    current_price = prices.iloc[-1]
    fast_period = params.get('fast_ema_period', 12)
    slow_period = params.get('slow_ema_period', 26)
    
    ema_fast = ema(prices, fast_period)
    ema_slow = ema(prices, slow_period)
    
    # Valeurs actuelles et précédentes
    current_ema_fast = ema_fast.iloc[-1]
    current_ema_slow = ema_slow.iloc[-1]
    
    # Vérifier s'il y a assez de données pour la comparaison précédente
    if len(ema_fast) > 1 and len(ema_slow) > 1:
        prev_ema_fast = ema_fast.iloc[-2]
        prev_ema_slow = ema_slow.iloc[-2]
    else:
        prev_ema_fast = current_ema_fast
        prev_ema_slow = current_ema_slow
    
    decision = 'HOLD'
    
    # Signal d'achat: EMA rapide croise au-dessus de l'EMA lente
    if current_ema_fast > current_ema_slow and prev_ema_fast <= prev_ema_slow:
        decision = 'BUY'
    # Signal de vente: EMA rapide croise en-dessous de l'EMA lente
    elif current_ema_fast < current_ema_slow and prev_ema_fast >= prev_ema_slow:
        decision = 'SELL'
    
    return {
        'decision': decision,
        'price': current_price,
        'ema_fast': current_ema_fast,
        'ema_slow': current_ema_slow,
        'details': f'EMA Fast: {current_ema_fast:.5f}, EMA Slow: {current_ema_slow:.5f}, Price: {current_price:.5f}'
    }

# Dictionnaire pour mapper les stratégies
STRATEGIES = {
    'RSI_SMA': rsi_sma_strategy,
    'MACD': macd_strategy,
    'EMA_CROSS': ema_cross_strategy
}
