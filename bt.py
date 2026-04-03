from datetime import time
import pandas as pd
from risk_engine import RiskManager
import numpy as np



class ExecutionEngine:

    def __init__(self, data, initial_capital, lot, brokerage, slippage, rr=1,per_trade_risk=1000, max_daily_loss=3000):

        self.data = data
        self.capital = initial_capital

        self.lot = lot
        self.brokerage = brokerage
        self.slippage = slippage
        self.rr = rr

        self.target_time = time(15, 24)

        self.long_trade_log = []
        self.short_trade_log = []
        self.daily_trade_log = []
        self.equity = []

        self.risk = RiskManager(per_trade_risk, max_daily_loss)

    def run(self):

        data = self.data.copy()

        # STATE VARIABLES

        long_position = 0
        short_position = 0

        long_entry_price = 0
        short_entry_price = 0

        long_target = 0
        long_stoploss = 0

        short_target = 0
        short_stoploss = 0
        long_mad = 0
        short_mad =0

        for day, day_df in data.groupby(data.index.date):

            self.risk.reset_day()

            daily_long_trade_number = 0
            daily_short_trade_number = 0
            daily_trade_number = 0


            # LOOP
            for index, row in day_df.iterrows():

                date = index
                close = row['close']
                high = row['high']
                low = row['low']
                mad = row['mad']
                upper = row['upper']
                lower = row['lower']

                current_time = index.time()

                # ENTRY LONG
                if long_position == 0 and low < lower and current_time < self.target_time and not np.isnan(mad) :
                    if not self.risk.can_take_trade():
                        continue
                    long_mad = row['mad'] / close
                    long_entry_price = lower + self.slippage
                    daily_long_trade_number += 1
                    daily_trade_number += 1

                    long_target = (long_entry_price + (mad * self.rr))
                    long_stoploss = (long_entry_price - mad)

                    qty = self.risk.get_position_size(long_entry_price, long_stoploss, self.lot)
                    if qty == 0:
                        continue
                    long_position = 1


                # ENTRY SHORT
                elif short_position == 0 and high > upper and current_time < self.target_time and not np.isnan(mad):
                    if not self.risk.can_take_trade():
                        continue
                    short_mad = row['mad'] / close
                    short_entry_price = upper - self.slippage
                    daily_short_trade_number += 1
                    daily_trade_number += 1

                    short_target = (short_entry_price - (mad * self.rr))
                    short_stoploss = (short_entry_price + mad)

                    qty = self.risk.get_position_size(short_entry_price, short_stoploss, self.lot)
                    if qty == 0:
                        continue
                    short_position = 1


                # EXIT LONG
                if long_position == 1:
                    # target
                    if high >= long_target:
                        long_exit_price = long_target - self.slippage
                        pnl = ((long_exit_price - long_entry_price) * self.lot) - self.brokerage
                        self.capital += pnl
                        long_position = 0

                        self.long_trade_log.append({'date': date,
                                                    'lower' : lower,
                                                    'entry price': long_entry_price,
                                                    'exit price': long_exit_price,
                                                    'target': long_target,
                                                    'stoploss': long_stoploss,
                                                    'status': 'target',
                                                    'pnl': pnl,
                                                    'mad': long_mad
                                                    })

                        self.daily_trade_log.append({'date' : date,
                                                     'daily long trade number' : daily_long_trade_number,
                                                     'status' : 'target',
                                                     'daily trade number' : daily_trade_number
                                                     })

                        self.equity.append(self.capital)
                        self.risk.update_pnl(pnl)



                    #     time exit
                    elif current_time >= self.target_time:

                        long_time_exit_price = close - self.slippage
                        pnl = ((long_time_exit_price - long_entry_price) * self.lot) - self.brokerage
                        self.capital += pnl
                        long_position = 0

                        self.long_trade_log.append({'date': date,
                                                    'lower' : lower,
                                                    'entry price': long_entry_price,
                                                    'exit price': long_time_exit_price,
                                                    'target': long_target,
                                                    'stoploss': long_stoploss,
                                                    'status': 'time exit',
                                                    'pnl': pnl,
                                                    'mad': long_mad
                                                    })

                        self.daily_trade_log.append({'date': date,
                                                     'daily long trade number': daily_long_trade_number,
                                                     'status': 'time exit',
                                                     'daily trade number': daily_trade_number
                                                     })

                        self.equity.append(self.capital)
                        self.risk.update_pnl(pnl)



                    # stoploss
                    elif low <= long_stoploss:
                        long_exit_price = long_stoploss - self.slippage
                        pnl = ((long_exit_price - long_entry_price) * self.lot) - self.brokerage
                        self.capital += pnl
                        long_position = 0

                        self.long_trade_log.append({'date': date,
                                                    'lower': lower,
                                                    'entry price': long_entry_price,
                                                    'exit price': long_exit_price,
                                                    'target': long_target,
                                                    'stoploss': long_stoploss,
                                                    'status': 'stoploss',
                                                    'pnl': pnl,
                                                    'mad': long_mad
                                                    })

                        self.daily_trade_log.append({'date': date,
                                                     'daily long trade number': daily_long_trade_number,
                                                     'status': 'stoploss',
                                                     'daily trade number': daily_trade_number
                                                     })

                        self.equity.append(self.capital)
                        self.risk.update_pnl(pnl)



                # EXIT SHORT
                if short_position == 1:
                    # target
                    if low <= short_target:
                        short_exit_price = short_target + self.slippage
                        pnl = ((short_entry_price - short_exit_price) * self.lot) - self.brokerage
                        self.capital += pnl
                        short_position = 0

                        self.short_trade_log.append({'date': date,
                                                     'upper':upper,
                                                    'entry price': short_entry_price,
                                                    'exit price': short_exit_price,
                                                    'target': short_target,
                                                    'stoploss': short_stoploss,
                                                    'status': 'target',
                                                    'pnl': pnl,
                                                    'mad': short_mad
                                                    })

                        self.daily_trade_log.append({'date': date,
                                                     'daily short trade number': daily_short_trade_number,
                                                     'status': 'target',
                                                     'daily trade number': daily_trade_number
                                                     })

                        self.equity.append(self.capital)
                        self.risk.update_pnl(pnl)



                    # time exit
                    elif current_time >= self.target_time:

                        short_time_exit_price = close + self.slippage
                        pnl = ((short_entry_price - short_time_exit_price) * self.lot) - self.brokerage
                        self.capital += pnl
                        short_position = 0

                        self.short_trade_log.append({'date': date,
                                                     'upper': upper,
                                                     'entry price': short_entry_price,
                                                     'exit price': short_time_exit_price,
                                                     'target': short_target,
                                                     'stoploss': short_stoploss,
                                                     'status': 'time exit',
                                                     'pnl': pnl,
                                                     'mad': short_mad
                                                     })

                        self.daily_trade_log.append({'date': date,
                                                     'daily short trade number': daily_short_trade_number,
                                                     'status': 'time exit',
                                                     'daily trade number': daily_trade_number
                                                     })

                        self.equity.append(self.capital)
                        self.risk.update_pnl(pnl)



                    # stoploss
                    elif high >= short_stoploss:

                        short_exit_price = short_stoploss + self.slippage
                        pnl = ((short_entry_price - short_exit_price) * self.lot) - self.brokerage
                        self.capital += pnl
                        short_position = 0

                        self.short_trade_log.append({'date': date,
                                                     'upper': upper,
                                                     'entry price': short_entry_price,
                                                     'exit price': short_exit_price,
                                                     'target': short_target,
                                                     'stoploss': short_stoploss,
                                                     'status': 'stoploss',
                                                     'pnl': pnl,
                                                     'mad': short_mad
                                                     })

                        self.daily_trade_log.append({'date': date,
                                                     'daily short trade number': daily_short_trade_number,
                                                     'status': 'stoploss',
                                                     'daily trade number': daily_trade_number
                                                     })

                        self.equity.append(self.capital)
                        self.risk.update_pnl(pnl)




        print(self.capital)
        return self.capital , self.long_trade_log, self.short_trade_log, self.equity

def analyze_mad_by_outcome(long_log, short_log):



    # convert to dataframe
    long_df = pd.DataFrame(long_log)
    short_df = pd.DataFrame(short_log)

    # safety check
    if long_df.empty:
        print("No trades available long side")
        return

    if short_df.empty:
        print("No trades available in short side")

    # filter by outcome
    long_target_trades = long_df[long_df['status'] == 'target']
    long_stoploss_trades = long_df[long_df['status'] == 'stoploss']

    short_target_trades = short_df[short_df['status'] == 'target']
    short_stoploss_trades = short_df[short_df['status'] == 'stoploss']

    # calculate means
    long_target_mad_mean = long_target_trades['mad'].mean()
    long_stoploss_mad_mean = long_stoploss_trades['mad'].mean()

    short_target_mad_mean = short_target_trades['mad'].mean()
    short_stoploss_mad_mean = short_stoploss_trades['mad'].mean()

    print("MAD Analysis:")
    print(f"LONG Mean MAD (TARGET trades): {long_target_mad_mean}")
    print(f"LONG Mean MAD (STOPLOSS trades): {long_stoploss_mad_mean}")

    print(f"SHORT Mean MAD (TARGET trades): {short_target_mad_mean}")
    print(f"SHORT mean MAD (STOPLOSS trades): {short_stoploss_mad_mean}")

    return long_target_mad_mean, long_stoploss_mad_mean, short_target_mad_mean, short_stoploss_mad_mean
