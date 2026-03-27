from data_load import DataHandler
from optimizer_engine import StrategyOptimizer

file_path = 'final_df.csv'
# Load data
data = DataHandler(file_path).get_data()

optimizer = StrategyOptimizer(data)

results = optimizer.optimize(window_range=[15, 30, 45],k_range=[1.5, 2, 2.5],rr_range=[1, 1.5, 2],capital=100000,lot=30,brokerage=20,slippage=5)

best = optimizer.get_best()

print(results)
print("BEST:\n", best)