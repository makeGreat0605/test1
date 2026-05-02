import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def analyze_relative_strength(ticker_symbol, benchmark_symbol, period="1y"):
    print(f"데이터 분석 시작: {ticker_symbol} vs {benchmark_symbol}...")
    
    # 1. 데이터 다운로드
    # 시가총액 계산을 위해 종가(Close)뿐만 아니라 발행주식수 정보가 필요합니다.
    target = yf.Ticker(ticker_symbol)
    bench = yf.Ticker(benchmark_symbol)
    
    df_target = target.history(period=period)['Close']
    df_bench = bench.history(period=period)['Close']
    
    # 2. 시가총액 데이터 생성 (Price * Shares Outstanding)
    # yfinance의 info에서 발행주식수를 가져옵니다.
    target_shares = target.info.get('sharesOutstanding', 1)
    bench_shares = bench.info.get('sharesOutstanding', 1)
    
    mcap_target = df_target * target_shares
    mcap_bench = df_bench * bench_shares
    
    # 3. 시가총액 변화율(Cumulative Return) 계산
    # 시작 시점의 시총을 1.0으로 정규화하여 변화율을 비교합니다.
    target_returns = mcap_target / mcap_target.iloc[0]
    bench_returns = mcap_bench / mcap_bench.iloc[0]
    
    # 4. Relative Strength (RS) 계산
    # RS = (종목 시총 변화율) / (지수 시총 변화율)
    rs_line = target_returns / bench_returns
    
    # 5. 시각화 (VSCode에서는 plt.show()가 필수입니다)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # 상단: 시가총액 변화율 비교
    ax1.plot(target_returns, label=f'{ticker_symbol} Cap Growth', color='blue', lw=2)
    ax1.plot(bench_returns, label=f'{benchmark_symbol} Cap Growth', color='orange', linestyle='--')
    ax1.set_title(f"Market Cap Growth Comparison ({period})")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 하단: RS Line (상대적 강도)
    ax2.plot(rs_line, label='Relative Strength (Cap-based)', color='purple', lw=2)
    ax2.axhline(1.0, color='red', linestyle='--', alpha=0.6) # 시장 평균선
    ax2.fill_between(rs_line.index, 1, rs_line, where=(rs_line > 1), color='purple', alpha=0.1)
    ax2.set_title(f"RS Line: {ticker_symbol} vs {benchmark_symbol}")
    ax2.set_ylabel("Strength Ratio")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# 예시: 엔비디아(NVDA)와 나스닥100(QQQ) 비교
analyze_relative_strength("SNDK", "QQQ", period="1y")