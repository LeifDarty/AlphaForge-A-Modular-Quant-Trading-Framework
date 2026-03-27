import pandas as pd
from itertools import product

from indicator_engine import IndicatorEngine
from signal_engine import SignalEngine
from bt import ExecutionEngine


class StrategyOptimizer:

    def __init__(self, data):

        self.raw_data = data
        self.results = []

    # signal run pipeline

    def run_single(self, window, k, rr, capital, lot, brokerage, slippage):

        data = self.raw_data.copy()

        # indicator
        ind = IndicatorEngine(data)
        data = ind.add_mad_bands(window=window, k=k)

        # signal
        sig = SignalEngine(data)
        data = sig.generate_signals()

        # execution
        engine = ExecutionEngine(data=data,initial_capital=capital,lot=lot,brokerage=brokerage,slippage=slippage,rr=rr)

        final_capital, long_log, short_log, equity = engine.run()

        return final_capital, equity


    # basic KPI

    def calculate_return(self, initial, final):
        return (final / initial) - 1

    # MAIN OPTIMIZATION

    def optimize(self, window_range, k_range, rr_range, capital, lot, brokerage, slippage):

        combinations = list(product(window_range, k_range, rr_range))

        for window, k, rr in combinations:

            try:
                final_capital, equity = self.run_single(
                    window, k, rr,
                    capital, lot, brokerage, slippage
                )

                if final_capital == capital:
                    continue  # no trades case

                total_return = self.calculate_return(capital, final_capital)

                self.results.append({'window': window,'k': k,'rr': rr,'final_capital': final_capital,'return': total_return})

            except Exception as e:
                print(f"Error in combo {window, k, rr}: {e}")
                continue

        return pd.DataFrame(self.results)


    # best parameter
    def get_best(self):

        df = pd.DataFrame(self.results)

        if df.empty:
            return None

        return df.sort_values(by='return', ascending=False).iloc[0]