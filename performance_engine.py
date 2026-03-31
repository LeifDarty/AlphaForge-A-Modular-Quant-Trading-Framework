import pandas as pd
import numpy as np


class PerformanceAnalyzer:

    def __init__(self, long_log, short_log, equity, brokerage):

        self.long_df = pd.DataFrame(long_log)
        self.short_df = pd.DataFrame(short_log)
        self.all_trades = pd.concat([self.long_df, self.short_df], ignore_index=True)

        self.equity = pd.Series(equity)
        self.brokerage = brokerage

        if not self.all_trades.empty:
            self.all_trades['date'] = pd.to_datetime(self.all_trades['date'])

    # BASIC COUNTS

    def total_trades(self):
        return len(self.all_trades)

    def total_long_trades(self):
        return len(self.long_df)

    def total_short_trades(self):
        return len(self.short_df)

    def total_brokerage(self):
        return self.total_trades() * self.brokerage

    # ACCURACY

    def accuracy(self, df):
        if df.empty:
            return 0
        return (df['status'] == 'target').sum() / len(df)

    # EXPECTANCY

    def expectancy(self, df):
        if df.empty:
            return 0

        wins = df[df['pnl'] > 0]['pnl']
        losses = df[df['pnl'] < 0]['pnl']

        win_rate = len(wins) / len(df)

        avg_win = wins.mean() if not wins.empty else 0
        avg_loss = losses.mean() if not losses.empty else 0

        return (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

    # PROFIT FACTOR

    def profit_factor(self):
        profit = self.all_trades[self.all_trades['pnl'] > 0]['pnl'].sum()
        loss = abs(self.all_trades[self.all_trades['pnl'] < 0]['pnl'].sum())

        if loss == 0:
            return np.inf

        return profit / loss

    # MAX DRAWDOWN

    def max_drawdown(self):
        peak = self.equity.cummax()
        dd = (self.equity - peak) / peak
        return dd.min()

    # SHARPE

    def sharpe(self):
        r = self.equity.pct_change().dropna()
        if r.std() == 0:
            return 0
        return (r.mean() / r.std()) * np.sqrt(252)


    # SORTINO

    def sortino(self):
        r = self.equity.pct_change().dropna()
        downside = r[r < 0]

        if downside.std() == 0:
            return 0

        return (r.mean() / downside.std()) * np.sqrt(252)


    # MAX PROFIT / LOSS

    def max_profit_loss(self, df):
        if df.empty:
            return 0, 0
        return df['pnl'].max(), df['pnl'].min()


    # TIME ANALYSIS

    def time_analysis(self):

        df = self.all_trades.copy()
        df.set_index('date', inplace=True)

        daily = df['pnl'].resample('D').sum()
        weekly = df['pnl'].resample('W').sum()
        monthly = df['pnl'].resample('M').sum()

        return {
            "max_profit_day": daily.max(),
            "max_loss_day": daily.min(),
            "max_profit_week": weekly.max(),
            "max_loss_week": weekly.min(),
            "max_profit_month": monthly.max(),
            "max_loss_month": monthly.min(),
        }

    # FULL REPORT

    def report(self):

        report = {}

        report['total_trades'] = self.total_trades()
        report['total_long_trades'] = self.total_long_trades()
        report['total_short_trades'] = self.total_short_trades()
        report['total_brokerage'] = self.total_brokerage()

        report['accuracy'] = self.accuracy(self.all_trades)
        report['long_accuracy'] = self.accuracy(self.long_df)
        report['short_accuracy'] = self.accuracy(self.short_df)

        report['expectancy'] = self.expectancy(self.all_trades)
        report['long_expectancy'] = self.expectancy(self.long_df)
        report['short_expectancy'] = self.expectancy(self.short_df)

        report['profit_factor'] = self.profit_factor()
        report['max_drawdown'] = self.max_drawdown()
        report['sharpe'] = self.sharpe()
        report['sortino'] = self.sortino()

        report['max_profit'], report['max_loss'] = self.max_profit_loss(self.all_trades)
        report['max_long_profit'], report['max_long_loss'] = self.max_profit_loss(self.long_df)
        report['max_short_profit'], report['max_short_loss'] = self.max_profit_loss(self.short_df)

        report.update(self.time_analysis())

        return report