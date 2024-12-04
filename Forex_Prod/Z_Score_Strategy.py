import yfinance as yf
import pandas as pd
import numpy as np
import itertools

class Algorithmic_Trading:
    def __init__(self, initial_balance=100000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.trades = []
        self.position = None
        self.entry_price = 0
        
    def exchange_extraction(self, symbols, interval="5m", period="1mo"):
        """
        symbols (list): List of currency pair symbols to download.
        interval (str): Data Interval
        period (str): Data Period
        
        Returns:
        exchange_rates (dict): Dictionary of DataFrames containing exchange rates.
        """
        exchange_rates = {}
        for symbol in symbols:
            # Download Data
            data = yf.download(symbol, interval=interval, period=period)
            if not data.empty:
                # Store the series of closing rates
                exchange_rates[symbol] = data['Close']
        return exchange_rates
    
    def flatten_data(self, data): # Escale this Function
        flat_data = data.copy()
        flat_data.columns = ['_'.join(filter(None, col)) for col in flat_data.columns] # Flatten multi level
        flat_data = flat_data.reset_index()
        return flat_data
    
    def create_moving_average(self, flat_data, close_column, column_name, window=20):
        flat_data[column_name] = flat_data[close_column].rolling(window=window).mean()
        return flat_data
    
    def z_score_backtesting(self, data, column_value, z_score_threshold, profit_target, stop_loss, window=20):
        """
        Performs backtesting using z-score strategy.

        Parameters:
        data: Input Data
        column_value (str): Column Name
        z_score_threshold (float): Threshold for z-score to enter trades.
        profit_target (float): The profit target as decimal (e.g., 0.005 for 0.5%)
        stop_loss (float): The stop loss as a decimal (e.g., 0.005 for 0.5%)

        Returns:
        trades_df: DataFrame containing trade details
        metrics_df: DataFrame containing performance metrics.
        """
        # Calculate Moving Averages for Trendt Detection
        short_window = window * 2 # Arbitrary
        long_window = window * 4 # Arbitrary
        
        data['Short_MA'] = data[column_value].rolling(window=short_window, min_periods=1).mean()
        data['Long_MA'] = data[column_value].rolling(window=long_window, min_periods=1).mean()
        
        self.balance = self.initial_balance
        self.trades = []
        self.position = None
        self.entry_price = 0

        for i in range(len(data)):
            # Current Row
            row = data.iloc[i]
            # Values
            price = row[column_value]
            z_score = row['Z-Score']
            

            # Entry Logic
            if self.position is None:
                if z_score >= z_score_threshold:  # Buy Signal
                    self.position = "buy"
                    self.entry_price = price
                    self.trades.append({'Type': 'Buy', 'Entry Price': self.entry_price, 'Exit Price': None, 'PnL': None})
                elif z_score <= -z_score_threshold:  # Short Signal
                    self.position = "short"
                    self.entry_price = price
                    self.trades.append({'Type': "Short", 'Entry Price': self.entry_price, 'Exit Price': None, 'PnL': None})

            # Exit Logic
            elif self.position == "buy":
                if price >= self.entry_price * (1 + profit_target):  # Profit Target
                    pnl = price - self.entry_price
                    self.balance += pnl
                    self.trades[-1]['Exit Price'] = price
                    self.trades[-1]['PnL'] = pnl
                    self.position = None  # Close Position
                elif price <= self.entry_price * (1 - stop_loss):  # Stop Loss
                    pnl = price - self.entry_price
                    self.balance += pnl
                    self.trades[-1]['Exit Price'] = price
                    self.trades[-1]['PnL'] = pnl
                    self.position = None  # Close Position

            elif self.position == "short":
                if price <= self.entry_price * (1 - profit_target):  # Profit Target
                    pnl = self.entry_price - price
                    self.balance += pnl
                    self.trades[-1]['Exit Price'] = price
                    self.trades[-1]['PnL'] = pnl
                    self.position = None  # Close position
                elif price >= self.entry_price * (1 + stop_loss):  # Stop Loss
                    pnl = self.entry_price - price
                    self.balance += pnl
                    self.trades[-1]['Exit Price'] = price
                    self.trades[-1]['PnL'] = pnl
                    self.position = None  # Close position

        # Close any open positions at the last available price
        if self.position is not None:
            # Get the last price
            price = data.iloc[-1][column_value]
            if self.position == 'buy':
                pnl = price - self.entry_price
            elif self.position == 'short':
                pnl = self.entry_price - price
            self.balance += pnl
            self.trades[-1]['Exit Price'] = price
            self.trades[-1]['PnL'] = pnl
            self.position = None  # Reset Position

        # Convert Trades to DataFrame
        trades_df = pd.DataFrame(self.trades)

        # Ensure trades_df has the necessary columns
        if trades_df.empty:
            trades_df = pd.DataFrame(columns=['Type', 'Entry Price', 'Exit Price', 'PnL'])

        # Calculate Metrics
        if not trades_df.empty:
            total_pnl = trades_df['PnL'].sum()
            win_rate = (trades_df['PnL'] > 0).mean()
            num_trades = len(trades_df)
        else:
            total_pnl = 0
            win_rate = 0
            num_trades = 0

        risk_reward_ratio = profit_target / stop_loss if stop_loss != 0 else np.nan

        metrics_df = pd.DataFrame({
            "Total PnL": [total_pnl],
            "Win Rate": [win_rate],
            "Number of Trades": [num_trades],
            "Risk Reward Ratio": [risk_reward_ratio]
        })

        return trades_df, metrics_df

    def optimize_zscore_parameters(self, data, column_value, z_score_values, profit_targets, stop_losses, use_trend_alignment=False):
        """
        Optimizes parameters for the moving average backtesting
        
        Parameters:
        data (DataFrame): The input data containing prices and z-scores.
        column_value (str): The column name for price data.
        z_score_values (list): List of z-score threshold to test.
        profit_targets (list): List of profit targets to test.
        stop_losses (list): List of stop losses to test.
        
        Returns:
        best_params (tuple): The best parameters (incomplete)
        results_df (DataFrame): DataFrame containing results of all parameter combinations
        """
        best_pnl = float('-inf')
        best_params = None
        results = []

        # Iterate over all combinations of parameters
        for z, pt, sl in itertools.product(z_score_values, profit_targets, stop_losses):
            trades_df, metrics_df = self.z_score_backtesting_trend_alignment(data, column_value, z, pt, sl, use_trend_alignment=use_trend_alignment)
            total_pnl = metrics_df.loc[0, 'Total PnL']
            win_rate = metrics_df.loc[0, 'Win Rate']
            num_trades = metrics_df.loc[0, 'Number of Trades']
            risk_reward_ratio = metrics_df.loc[0, 'Risk Reward Ratio']
            
            results.append({
                'Z-Score Threshold': z,
                'Profit Target': pt,
                'Stop Loss': sl,
                'Total PnL': total_pnl,
                'Win Rate': win_rate,
                'Number of Trades': num_trades,
                'Risk Reward Ratio': risk_reward_ratio})

            # Decision based on Total PnL
            if total_pnl > best_pnl:
                best_pnl = total_pnl
                best_params = (z, pt, sl)
        
        results_df = pd.DataFrame(results)
        return best_params, results_df
    
    def z_score_backtesting_trend_alignment(self, data, column_value, z_score_threshold, profit_target, stop_loss, window=20, use_trend_alignment=False):
        self.balance = self.initial_balance
        self.trades = []
        self.position = None
        self.entry_price = 0

        # If trend alignment is True
        if use_trend_alignment == True:
            short_window = round(2 * window)
            long_window = round(4 * window)  # Adjust as needed
            # Calculate Moving Averages for Trend Detection
            data['Short_MA'] = data[column_value].rolling(window=short_window, min_periods=1).mean()
            data['Long_MA'] = data[column_value].rolling(window=long_window, min_periods=1).mean()

        for i in range(len(data)):
            # Current Row
            row = data.iloc[i]
            # Values
            price = row[column_value]
            z_score = row['Z-Score']

            # Determine Trend if trend alignment is used
            if use_trend_alignment == True:
                short_ma = row['Short_MA']
                long_ma = row['Long_MA']
                if pd.isna(short_ma) or pd.isna(long_ma):
                    trend = None  # Not enough data to determine trend
                elif short_ma > long_ma:
                    trend = 'uptrend'
                elif short_ma < long_ma:
                    trend = 'downtrend'
                else:
                    trend = 'no_trend'
            else:
                trend = 'no_trend'  # Default when not using trend alignment

            # Entry Logic
            if self.position is None:
                if use_trend_alignment == True:
                    if z_score >= z_score_threshold and trend == 'uptrend':  # Buy Signal with Trend Alignment
                        self.position = "buy"
                        self.entry_price = price
                        self.trades.append({"Type": "Buy", "Entry Price": self.entry_price, "Exit Price": None, "PnL": None})
                    elif z_score <= -z_score_threshold and trend == "downtrend":  # Short Signal with Trend Alignment
                        self.position = "short"
                        self.entry_price = price
                        self.trades.append({"Type": "Short", "Entry Price": self.entry_price, "Exit Price": None, "PnL": None})
                    # Do nothing if trend is not aligned
                else:
                    if z_score >= z_score_threshold:  # Buy Signal without Trend Alignment
                        self.position = "buy"
                        self.entry_price = price
                        self.trades.append({"Type":"Buy", "Entry Price": self.entry_price, "Exit Price": None, "PnL": None})
                    elif z_score <= -z_score_threshold:  # Short Signal without Trend Alignment
                        self.position = "short"
                        self.entry_price = price
                        self.trades.append({"Type": "Short", "Entry Price": self.entry_price, "Exit Price": None, "PnL": None})
            # Exit Logic remains the same
            elif self.position == "buy":
                if price >= self.entry_price * (1 + profit_target):  # Profit Target Hit
                    pnl = price - self.entry_price
                    self.balance += pnl
                    self.trades[-1].update({"Exit Price": price, "PnL": pnl})
                    self.position = None
                elif price <= self.entry_price * (1 - stop_loss):  # Stop Loss Hit
                    pnl = price - self.entry_price
                    self.balance += pnl
                    self.trades[-1].update({"Exit Price": price, "PnL": pnl})
                    self.position = None
            elif self.position == "short":
                if price <= self.entry_price * (1 - profit_target):  # Profit Target Hit
                    pnl = self.entry_price - price
                    self.balance += pnl
                    self.trades[-1].update({"Exit Price": price, "PnL": pnl})
                    self.position = None
                elif price >= self.entry_price * (1 + stop_loss):  # Stop Loss Hit
                    pnl = self.entry_price - price
                    self.balance += pnl
                    self.trades[-1].update({"Exit Price": price, "PnL": pnl})
                    self.position = None

        # Close any open positions at the last available price
        if self.position is not None:
            price = data.iloc[-1][column_value]
            if self.position == "buy":
                pnl = price - self.entry_price
            elif self.position == "short":
                pnl = self.entry_price - price
            self.balance += pnl
            self.trades[-1].update({"Exit Price": price, "PnL": pnl})
            self.position = None

        # Convert Trades to DataFrame
        trades_df = pd.DataFrame(self.trades)
        if trades_df.empty:
            trades_df = pd.DataFrame(columns=['Type', 'Entry Price', 'Exit Price', 'PnL'])
        # Calculate Metrics
        if not trades_df.empty:
            total_pnl = trades_df['PnL'].sum()
            win_rate = (trades_df['PnL'] > 0).mean()
            num_trades = len(trades_df)
        else:
            total_pnl = 0
            win_rate = 0
            num_trades = 0
        risk_reward_ratio = profit_target / stop_loss if stop_loss != 0 else np.nan
        metrics_df = pd.DataFrame({
            "Total PnL": [total_pnl],
            "Win Rate": [win_rate],
            "Number of Trades": [num_trades],
            "Risk Reward Ratio": [risk_reward_ratio]})
        return trades_df, metrics_df
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                