from celery import shared_task
import pandas as pd
from .oanda import OandaAPI
from .strategies import rsi_sma_strategy
from apps.apitrading.models import Backtest

class Backtester:
    def __init__(self, api_key, account_id, asset, start_date, end_date, strategy_name, params):
        self.client = OandaAPI(api_key, account_id)
        self.asset = asset
        self.start_date = start_date
        self.end_date = end_date
        self.strategy_name = strategy_name
        self.params = params
        self.trades = []
        self.balance = 10000  # Starting balance for simulation

    def run(self):
        # 1. Fetch historical data
        # Note: OANDA has limits on data points per request. This might need pagination for long periods.
        data = self.client.get_historical_data(
            instrument=self.asset,
            granularity='H1', # Using 1-hour candles for backtesting
            from_time=self.start_date.isoformat(),
            to_time=self.end_date.isoformat()
        )

        if data.empty:
            raise ValueError("No historical data found for the given period.")

        # 2. Apply strategy to get signals
        if self.strategy_name == 'rsi_sma':
            df_with_signals = rsi_sma_strategy(data, **self.params)
        else:
            raise ValueError(f"Strategy '{self.strategy_name}' not supported.")

        # 3. Simulate trades based on signals
        position_open = False
        for i in range(len(df_with_signals)):
            if df_with_signals['signal'][i] == 1 and not position_open:
                # Buy signal
                self.trades.append({'type': 'buy', 'price': df_with_signals['close'][i], 'time': df_with_signals.index[i]})
                position_open = True
            elif df_with_signals['signal'][i] == -1 and position_open:
                # Sell signal
                self.trades.append({'type': 'sell', 'price': df_with_signals['close'][i], 'time': df_with_signals.index[i]})
                position_open = False

        # Ensure the last open trade is closed at the end
        if position_open:
            self.trades.append({'type': 'sell', 'price': df_with_signals['close'].iloc[-1], 'time': df_with_signals.index[-1]})

        return self.calculate_results()

    def calculate_results(self):
        if not self.trades or len(self.trades) < 2:
            return {
                'profit_loss': 0,
                'total_trades': 0,
                'win_rate': 0,
                'final_balance': self.balance
            }

        profit_loss = 0
        wins = 0
        total_trades = len(self.trades) // 2

        for i in range(0, len(self.trades), 2):
            buy_trade = self.trades[i]
            # Ensure there is a corresponding sell trade
            if i + 1 < len(self.trades):
                sell_trade = self.trades[i+1]
                pnl = (sell_trade['price'] - buy_trade['price']) * 1000 # Simplified P/L calculation
                profit_loss += pnl
                if pnl > 0:
                    wins += 1

        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
        final_balance = self.balance + profit_loss

        return {
            'profit_loss': round(profit_loss, 2),
            'total_trades': total_trades,
            'win_rate': round(win_rate, 2),
            'final_balance': round(final_balance, 2)
        }
