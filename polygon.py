from massive import RESTClient

client = RESTClient(api_key="4k681fjoyXS9uAa6EEvaibz4sjpKM6iL")

tickers = ["AAPL", "MSFT", "GOOGL"]
comparison_data = []

for t in tickers:
    # 1. 마지막 종가 가져오기
    last_trade = client.get_last_trade(ticker=t)
    price = last_trade.price
    
    # 2. 기업 상세 정보에서 시총 관련 데이터 가져오기 (메서드 명은 SDK에 따라 다를 수 있음)
    details = client.get_ticker_details(t)
    market_cap = price * details.weighted_shares_outstanding 
    
    comparison_data.append({"ticker": t, "price": price, "mkt_cap": market_cap})

# 이후 pandas로 분석