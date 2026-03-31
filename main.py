from data_load import DataHandler
from indicator_engine import IndicatorEngine
from signal_engine import SignalEngine
from bt import ExecutionEngine
from optimizer_engine import StrategyOptimizer
from performance_engine import PerformanceAnalyzer

def run_pipeline():
    # CONFIG

    FILE_PATH = "data_2023.csv"

    INITIAL_CAPITAL = 100000
    LOT_SIZE = 30
    BROKERAGE = 20
    SLIPPAGE = 1

    PER_TRADE_RISK = 1000
    MAX_DAILY_LOSS = 3000

    # OPTIMIZATION RANGES
    WINDOW_RANGE = [10, 15, 20]
    K_RANGE = [1.5, 2, 2.5]
    RR_RANGE = [1, 1.5, 2]

    # 1. LOAD DATA

    data_handler = DataHandler(FILE_PATH)
    raw_data = data_handler.get_data()

    print("Data Loaded:", raw_data.shape)

    # 2. OPTIMIZATION

    print("\nRunning Optimization...")

    optimizer = StrategyOptimizer(raw_data)

    results_df = optimizer.optimize(
        window_range=WINDOW_RANGE,
        k_range=K_RANGE,
        rr_range=RR_RANGE,
        capital=INITIAL_CAPITAL,
        lot=LOT_SIZE,
        brokerage=BROKERAGE,
        slippage=SLIPPAGE
    )

    best = optimizer.get_best()

    if best is None:
        print("No valid strategy found")
        return

    print("\nBEST PARAMETERS FOUND:")
    print(best)

    best_window = int(best['window'])
    best_k = float(best['k'])
    best_rr = float(best['rr'])

    # 3. APPLY BEST STRATEGY

    print("\nRunning Final Backtest with Best Params")

    data = raw_data.copy()

    # indicator
    indicator = IndicatorEngine(data)
    data = indicator.add_mad_bands(window=best_window, k=best_k)

    # signal
    signal = SignalEngine(data)
    data = signal.generate_signals()

    # execution (WITH RISK)
    engine = ExecutionEngine(
        data=data,
        initial_capital=INITIAL_CAPITAL,
        lot=LOT_SIZE,
        brokerage=BROKERAGE,
        slippage=SLIPPAGE,
        rr=best_rr,
        per_trade_risk=PER_TRADE_RISK,
        max_daily_loss=MAX_DAILY_LOSS
    )

    final_capital, long_log, short_log, equity = engine.run()

    # KPI ANALYSIS

    analyzer = PerformanceAnalyzer(
        long_log=long_log,
        short_log=short_log,
        equity=equity,
        brokerage=BROKERAGE
    )

    report = analyzer.report()

    print("\nFINAL KPI REPORT")
    for k, v in report.items():
        print(f"{k}: {v}")

    print("\n========== FINAL RESULTS ==========")
    print(f"Initial Capital: {INITIAL_CAPITAL}")
    print(f"Final Capital: {final_capital}")
    print(f"Net Profit: {final_capital - INITIAL_CAPITAL}")

    return {
        "best_params": best,
        "final_capital": final_capital,
        "equity": equity
    }
# RUN

if __name__ == "__main__":
    results = run_pipeline()

