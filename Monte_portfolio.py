import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. Market Engine (Fat-Tail & Long-Term)
# ==========================================
class FatTailMarket:
    def __init__(self, tickers, mu, vol, corr_matrix, df=2.0): # df를 더 낮춰 블랙스완 빈도 유지
        self.tickers = tickers
        self.mu, self.vol, self.corr, self.df = np.array(mu), np.array(vol), np.array(corr_matrix), df

    def generate(self, steps, paths):
        n_assets = len(self.tickers)
        cov = np.outer(self.vol, self.vol) * self.corr
        L = np.linalg.cholesky(cov)
        z = np.random.standard_t(self.df, size=(steps, paths, n_assets))
        returns = np.zeros_like(z)
        for p in range(paths):
            returns[:, p, :] = (z[:, p, :] @ L.T) + self.mu
        return returns

# ==========================================
# 2. Switching Simulator (Dynamic Rebalancing)
# ==========================================
class SwitchingSimulator:
    def __init__(self, initial_cash, monthly_inflow, base_w, agg_w, threshold=-0.30):
        self.initial_cash = initial_cash
        self.monthly_inflow = monthly_inflow
        self.base_w = np.array(base_w)
        self.agg_w = np.array(agg_w)
        self.threshold = threshold

    def run(self, all_returns):
        steps, paths, _ = all_returns.shape
        val_history = np.zeros((steps + 1, paths))
        dd_history = np.zeros((steps + 1, paths))

        for p in range(paths):
            assets = self.initial_cash * self.base_w
            peak = self.initial_cash
            history = [self.initial_cash]
            
            for t in range(steps):
                current_val = np.sum(assets)
                if current_val > peak: peak = current_val
                drawdown = (current_val - peak) / peak if peak > 0 else 0
                
                # 낙폭 -30% 도달 시에만 공격적 비중(agg_w)으로 전환
                target_w = self.agg_w if drawdown <= self.threshold else self.base_w
                
                # 리밸런싱 및 월별 입금액 반영
                assets = (current_val + self.monthly_inflow) * target_w
                assets *= (1 + all_returns[t, p, :])
                
                new_val = np.sum(assets)
                history.append(new_val)
                if new_val > peak: peak = new_val
                dd_history[t+1, p] = (new_val - peak) / peak
            
            val_history[:, p] = history
        return val_history, dd_history

# ==========================================
# 3. Parameters & 120-Month Execution
# ==========================================

tickers = ['SCHO', 'SOXQ', 'IAU', 'BTC', 'AIPO']
corr = [[1.0, -0.1, 0.1, 0.0, -0.1], [-0.1, 1.0, 0.2, 0.4, 0.7], 
        [0.1, 0.2, 1.0, 0.1, 0.1], [0.0, 0.4, 0.1, 1.0, 0.3], [-0.1, 0.7, 0.1, 0.3, 1.0]]

# 장기 관점의 기대수익률(mu)과 변동성(vol)
mu = [0.002, 0.012, 0.005, 0.040, 0.015]
vol = [0.005, 0.15, 0.06, 0.30, 0.20]

# 120개월(10년) 시장 생성
market_long = FatTailMarket(tickers, mu, vol, corr, df=2.5) 
rets_long = market_long.generate(steps=120, paths=1000)

scenarios = {
    "Ultra-Safe (80%)": [0.80, 0.10, 0.04, 0.03, 0.03],
    "Balanced (60%)":   [0.60, 0.20, 0.08, 0.06, 0.06],
    "Risk-Taker (40%)": [0.40, 0.30, 0.10, 0.10, 0.10]
}

plt.figure(figsize=(12, 6))
results_list = []

for name, base_w in scenarios.items():
    # 공격적 비중(agg_w): SCHO의 70%를 깎아 위험자산에 강력하게 배분
    agg_w = np.array(base_w).copy()
    reduction = agg_w[0] * 0.7
    agg_w[0] -= reduction
    agg_w[1:] += (reduction / 4)
    
    # 임계치 -30% 적용
    sim = SwitchingSimulator(10000, 1000, base_w, agg_w, threshold=-0.30)
    vals, dds = sim.run(rets_long)
    
    mean_final = np.mean(vals[-1, :])
    avg_mdd = np.mean(np.min(dds, axis=0))
    results_list.append({"Strategy": name, "Final Value": f"${mean_final:,.0f}", "Avg MDD": f"{avg_mdd:.2%}"})
    
    plt.plot(np.median(vals, axis=1), label=f"{name} (Median)")

plt.title("10-Year Growth Comparison (Switching Threshold: -30%)", fontsize=14)
plt.ylabel("Portfolio Value ($)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

print(pd.DataFrame(results_list))