import yfinance as yf
import pandas as pd
import numpy as np
import itertools
import ta

class AlgorithmicTradingRefactored:
    def __init__(self, initial_balance=100000):
        self.initial_balance = initial_balance
        self.reset()

    def reset(self):
        """Resets the trading state to the initial balance and clears trades."""
        self.balance = self.initial_balance
        self.trades = []
        self.position = None
        self.entry_price = 0

    def exchange_extraction(self, symbols, interval="5m", period="1mo"):
        """
        Downloads exchange rate data for given symbols using yfinance.

        Parameters:
            symbols (list): List of currency pair symbols to download.
            interval (str): Data interval.
            period (str): Data period.

        Returns:
            exchange_rates (dict): Dictionary of DataFrames containing exchange rates.
        """
        exchange_rates = {}
        for symbol in symbols:
            data = yf.download(symbol, interval=interval, period=period)
            if not data.empty:
                exchange_rates[symbol] = data['Close']
        return exchange_rates

    def flatten_data(self, data):
        """Flattens multi-level columns in the DataFrame."""
        flat_data = data.copy()
        flat_data.columns = ['_'.join(filter(None, col)) for col in flat_data.columns]
        flat_data = flat_data.reset_index()
        return flat_data

    def create_moving_average(self, data, column_name, window=20):
        """Adds a moving average column to the DataFrame."""
        data[f'MA_{window}'] = data[column_name].rolling(window=window).mean()
        return data

    def calculate_trend(self, data, price_column, short_window, long_window):
        """Calculates short and long-term moving averages for trend detection."""
        data['Short_MA'] = data[price_column].rolling(window=short_window).mean()
        data['Long_MA'] = data[price_column].rolling(window=long_window).mean()
        data['Trend'] = np.where(data['Short_MA'] > data['Long_MA'], 'uptrend',
                          np.where(data['Short_MA'] < data['Long_MA'], 'downtrend', 'no_trend'))
        return data

    def calculate_rsi(self, data, price_column, window):
        """Calculates the RSI indicator."""
        rsi_indicator = ta.momentum.RSIIndicator(data[price_column], window=window)
        data['RSI'] = rsi_indicator.rsi()
        return data

    def backtest_strategy(self, data, price_column, z_score_column, z_score_threshold, profit_target, stop_loss,
                          window=20, strategy_type='momentum', use_trend_alignment=False, rsi_condition=False,
                          rsi_lower_threshold=35, rsi_upper_threshold=65):
        """
        General backtesting method supporting multiple strategies and conditions.

        Parameters:
            data (DataFrame): Input DataFrame containing price data and Z-Score.
            price_column (str): Column name for price data.
            z_score_column (str): Column name for Z-Score data.
            z_score_threshold (float): Threshold for z-score to enter trades.
            profit_target (float): The profit target as a decimal.
            stop_loss (float): The stop loss as a decimal.
            window (int): Window size for indicators.
            strategy_type (str): 'momentum' or 'reversion'.
            use_trend_alignment (bool): Whether to use trend alignment.
            rsi_condition (bool): Whether to use RSI condition.
            rsi_lower_threshold (float): Lower threshold for RSI.
            rsi_upper_threshold (float): Upper threshold for RSI.

        Returns:
            trades_df (DataFrame): DataFrame containing trade details.
            metrics_df (DataFrame): DataFrame containing performance metrics.
        """
        self.reset()

        if use_trend_alignment:
            short_window = 2 * window
            long_window = 4 * window
            data = self.calculate_trend(data, price_column, short_window, long_window)

        if rsi_condition:
            data = self.calculate_rsi(data, price_column, window)

        data = data.reset_index(drop=True)

        for i, row in data.iterrows():
            price = row[price_column]
            z_score = row[z_score_column]

            # Get additional indicators if used
            trend = row['Trend'] if use_trend_alignment else None
            rsi = row['RSI'] if rsi_condition else None

            # Entry Logic
            if self.position is None:
                enter_trade = False

                if strategy_type == 'momentum':
                    if z_score >= z_score_threshold:
                        signal = 'buy'
                        enter_trade = True
                    elif z_score <= -z_score_threshold:
                        signal = 'short'
                        enter_trade = True
                elif strategy_type == 'reversion':
                    if z_score <= -z_score_threshold:
                        signal = 'buy'
                        enter_trade = True
                    elif z_score >= z_score_threshold:
                        signal = 'short'
                        enter_trade = True

                # Apply trend alignment
                if use_trend_alignment and enter_trade:
                    if (signal == 'buy' and trend != 'uptrend') or (signal == 'short' and trend != 'downtrend'):
                        enter_trade = False

                # Apply RSI condition
                if rsi_condition and enter_trade:
                    if (signal == 'buy' and (pd.isna(rsi) or rsi > rsi_lower_threshold)) or \
                       (signal == 'short' and (pd.isna(rsi) or rsi < rsi_upper_threshold)):
                        enter_trade = False

                if enter_trade:
                    self.position = signal
                    self.entry_price = price
                    self.trades.append({'Type': 'Buy' if signal == 'buy' else 'Short',
                                        'Entry Price': self.entry_price,
                                        'Exit Price': None,
                                        'PnL': None})

            # Exit Logic
            else:
                if self.position == 'buy':
                    if price >= self.entry_price * (1 + profit_target):
                        pnl = (price - self.entry_price)
                        self.close_trade(price, pnl)
                    elif price <= self.entry_price * (1 - stop_loss):
                        pnl = (price - self.entry_price)
                        self.close_trade(price, pnl)
                elif self.position == 'short':
                    if price <= self.entry_price * (1 - profit_target):
                        pnl = (self.entry_price - price)
                        self.close_trade(price, pnl)
                    elif price >= self.entry_price * (1 + stop_loss):
                        pnl = (self.entry_price - price)
                        self.close_trade(price, pnl)

        # Close any open positions at the last available price
        if self.position is not None:
            price = data.iloc[-1][price_column]
            if self.position == 'buy':
                pnl = price - self.entry_price
            else:
                pnl = self.entry_price - price
            self.close_trade(price, pnl)

        trades_df, metrics_df = self.calculate_metrics()
        return trades_df, metrics_df

    def close_trade(self, exit_price, pnl):
        """Closes the current trade and updates the balance."""
        self.balance += pnl
        self.trades[-1].update({'Exit Price': exit_price, 'PnL': pnl})
        self.position = None

    def calculate_metrics(self):
        """Calculates performance metrics based on executed trades."""
        trades_df = pd.DataFrame(self.trades)
        if trades_df.empty:
            trades_df = pd.DataFrame(columns=['Type', 'Entry Price', 'Exit Price', 'PnL'])
            total_pnl = 0
            win_rate = 0
            num_trades = 0
        else:
            total_pnl = trades_df['PnL'].sum()
            win_rate = (trades_df['PnL'] > 0).mean()
            num_trades = len(trades_df)
        metrics_df = pd.DataFrame({
            'Total PnL': [total_pnl],
            'Win Rate': [win_rate],
            'Number of Trades': [num_trades],
        })
        return trades_df, metrics_df

    def optimize_parameters(self, data, price_column, z_score_column, z_score_values, profit_targets, stop_losses,
                            strategy_type='momentum', use_trend_alignment=False, rsi_condition=False,
                            rsi_lower_threshold=35, rsi_upper_threshold=65):
        """
        Optimizes parameters for the backtesting strategy.

        Parameters:
            data (DataFrame): The input data containing prices and indicators.
            price_column (str): Column name for price data.
            z_score_column (str): Column name for Z-Score data.
            z_score_values (list): List of z-score thresholds to test.
            profit_targets (list): List of profit targets to test.
            stop_losses (list): List of stop losses to test.
            strategy_type (str): 'momentum' or 'reversion'.
            use_trend_alignment (bool): Whether to use trend alignment.
            rsi_condition (bool): Whether to use RSI condition.
            rsi_lower_threshold (float): Lower threshold for RSI.
            rsi_upper_threshold (float): Upper threshold for RSI.

        Returns:
            best_params (tuple): The best parameters.
            results_df (DataFrame): DataFrame containing results of all parameter combinations.
        """
        best_pnl = float('-inf')
        best_params = None
        results = []

        # Iterate over all combinations of parameters
        for z, pt, sl in itertools.product(z_score_values, profit_targets, stop_losses):
            trades_df, metrics_df = self.backtest_strategy(
                data.copy(), price_column, z_score_column, z, pt, sl,
                strategy_type=strategy_type,
                use_trend_alignment=use_trend_alignment,
                rsi_condition=rsi_condition,
                rsi_lower_threshold=rsi_lower_threshold,
                rsi_upper_threshold=rsi_upper_threshold
            )
            total_pnl = metrics_df.loc[0, 'Total PnL']
            win_rate = metrics_df.loc[0, 'Win Rate']
            num_trades = metrics_df.loc[0, 'Number of Trades']

            results.append({
                'Z-Score Threshold': z,
                'Profit Target': pt,
                'Stop Loss': sl,
                'Total PnL': total_pnl,
                'Win Rate': win_rate,
                'Number of Trades': num_trades
            })

            if total_pnl > best_pnl:
                best_pnl = total_pnl
                best_params = (z, pt, sl)

        results_df = pd.DataFrame(results)
        return best_params, results_df
