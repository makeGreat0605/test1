import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def analyze_rs_fixed(ticker_symbol, benchmark_symbol="QQQ", period="1y"):
    # 1. 데이터 다운로드 (Adj Close 사용으로 분할/배당 이슈 해결)
    print(f"데이터 수집 중: {ticker_symbol} & {benchmark_symbol}")
    data = yf.download([ticker_symbol, benchmark_symbol], period=period)['Close']
    
    # 2. 데이터 정제 (결측치 제거 및 날짜 동기화)
    data = data.dropna()
    
    # 3. 변화율 계산 (시작 시점 1.0으로 정규화)
    # 이것이 곧 '시가총액 변화율'과 논리적으로 동일한 결과를 줍니다.
    normalized_data = data / data.iloc[0]
    
    # 4. Relative Strength Ratio 계산
    # RS > 1 이면 시작 시점 대비 시장보다 높은 수익률을 기록 중
    rs_ratio = normalized_data[ticker_symbol] / normalized_data[benchmark_symbol]
    
    # 5. 시각화
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # 상단: 누적 수익률 비교 (로그 스케일 적용 가능)
    ax1.plot(normalized_data[ticker_symbol], label=f'{ticker_symbol} Perf', color='blue', lw=2)
    ax1.plot(normalized_data[benchmark_symbol], label=f'{benchmark_symbol} Perf', color='gray', linestyle='--')
    ax1.set_title(f"Cumulative Performance (Starting from 1.0)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 하단: RS Line
    ax2.plot(rs_ratio, label='Relative Strength Line', color='red', lw=2)
    ax2.axhline(1.0, color='black', linestyle='-', alpha=0.5)
    # RS Line의 이동평균선을 추가하면 추세 확인이 더 쉽습니다.
    ax2.plot(rs_ratio.rolling(window=20).mean(), label='RS 20MA', color='orange', alpha=0.8)
    ax2.fill_between(rs_ratio.index, 1, rs_ratio, where=(rs_ratio > 1), color='red', alpha=0.1)
    ax2.set_title("Relative Strength Ratio (Target / Benchmark)")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 최근 액면분할이 있었던 NVDA로 테스트해도 논리적 오류가 발생하지 않습니다.
    analyze_rs_fixed("NET", "QQQ")