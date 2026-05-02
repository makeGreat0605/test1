"""
S&P 500 PEG 밸류에이션 스크리너
=============================
설명: sp500_companies.csv 내 기업들의 PEG Ratio를 수집하고 저평가 순으로 정렬합니다.
"""

import pandas as pd
import yfinance as yf
import time
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 1. 유니버스 로드 (sp500_companies.csv)
# ─────────────────────────────────────────────
def get_tickers_from_csv() -> list[str]:
    try:
        # 업로드하신 sp500_companies.csv 파일을 읽습니다.
        df = pd.read_csv("sp500_companies.csv")
        # 첫 번째 열에 티커가 있다고 가정합니다 (사용자 기존 코드 방식 유지)
        tickers = df.iloc[:, 0].dropna().str.strip().tolist()
        # 헤더가 포함되어 있을 경우를 대비해 필터링
        tickers = [t for t in tickers if t.upper() not in ["TICKER", "SYMBOL"]]
        return tickers
    except FileNotFoundError:
        print("[오류] sp500_companies.csv 파일을 찾을 수 없습니다.")
        return []

# ─────────────────────────────────────────────
# 2. PEG 및 관련 데이터 수집
# ─────────────────────────────────────────────
def fetch_peg_data(ticker: str) -> dict | None:
    try:
        t = yf.Ticker(ticker)
        info = t.info
        
        peg = info.get("pegRatio")
        
        # PEG가 없거나 데이터가 유효하지 않은 경우 제외
        if peg is None:
            return None

        return {
            "티커": ticker,
            "종목명": info.get("shortName", ticker),
            "섹터": info.get("sector", "N/A"),
            "현재가": info.get("currentPrice"),
            "PEG": peg,
            "Forward_PE": info.get("forwardPE"),
            "이익성장률(%)": info.get("earningsGrowth", 0) * 100 if info.get("earningsGrowth") else "N/A",
            "시가총액": info.get("marketCap")
        }
    except Exception:
        return None

# ─────────────────────────────────────────────
# 3. 메인 실행부
# ─────────────────────────────────────────────
def main():
    print("\n=== S&P 500 PEG 저평가 종목 스크리닝 ===\n")
    
    tickers = get_tickers_from_csv()
    if not tickers:
        return

    print(f"[분석 시작] 총 {len(tickers)}개 종목 분석 중...\n")
    
    results = []
    # API 과부하 방지를 위해 적절한 지연 시간을 둡니다.
    for ticker in tqdm(tickers, desc="데이터 수집"):
        data = fetch_peg_data(ticker)
        if data:
            results.append(data)
        time.sleep(0.2)  # 요청 간격 조절

    if not results:
        print("수집된 데이터가 없습니다.")
        return

    # DataFrame 생성 및 정렬
    df = pd.DataFrame(results)
    
    # PEG가 양수인 종목 중 낮은 순서대로 정렬 (음수는 보통 이익 감소 등으로 왜곡된 데이터)
    df_filtered = df[df["PEG"] > 0].sort_values(by="PEG", ascending=True).reset_index(drop=True)
    df_filtered.insert(0, "순위", df_filtered.index + 1)

    # 출력 포맷팅
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)
    
    print(f"\n{'='*100}")
    print(f"  PEG 기반 저평가 순위 (상위 20개 종목)")
    print(f"{'='*100}\n")
    
    # 시가총액 읽기 편하게 변경 ($B 단위)
    display_df = df_filtered.head(20).copy()
    display_df["시가총액"] = display_df["시가총액"].apply(lambda x: f"${x/1e9:.1f}B" if pd.notna(x) else "N/A")
    
    print(display_df.to_string(index=False))

    # 결과 저장
    df_filtered.to_csv("sp500_peg_ranking.csv", index=False, encoding="utf-8-sig")
    print(f"\n[저장 완료] 전체 결과가 'sp500_peg_ranking.csv'로 저장되었습니다.")

if __name__ == "__main__":
    main()