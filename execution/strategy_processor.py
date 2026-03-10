import os
import sys
import json
import argparse
import pandas as pd
import numpy as np

# strategies 패키지가 execution/ 안에 있으므로 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strategies import STRATEGY_REGISTRY


def process_strategies(strategy_name="nul_lim_mok", data_path=".tmp/market_data.pkl"):
    """
    지정된 전략을 적용하여 종목을 필터링하고 순위를 매김.

    Args:
        strategy_name: STRATEGY_REGISTRY에 등록된 전략 키
        data_path: market_data.pkl 경로
    Returns:
        상위 100 종목 리스트 (dict)
    """
    if strategy_name not in STRATEGY_REGISTRY:
        available = ", ".join(STRATEGY_REGISTRY.keys())
        print(f"[ERROR] 알 수 없는 전략: '{strategy_name}'. 사용 가능: {available}")
        return []

    strategy = STRATEGY_REGISTRY[strategy_name]()
    print(f"전략 적용: [{strategy.name}] - {strategy.description}")

    if not os.path.exists(data_path):
        print(f"Data not found at {data_path}")
        return []

    full_df = pd.read_pickle(data_path)
    tickers_df = pd.read_csv(".tmp/tickers.csv")
    ticker_map = dict(zip(tickers_df['code'].astype(str).str.zfill(6), tickers_df['name']))

    # ETF/ETN 제외 목록 (tickers.csv에 is_etf 컬럼이 있으면 활용)
    etf_set = set()
    if 'is_etf' in tickers_df.columns:
        etf_set = set(tickers_df[tickers_df['is_etf'] == True]['code'].astype(str).str.zfill(6))

    # 종목별 평균 거래대금 계산
    avg_value = full_df.groupby('code')['거래대금'].mean()

    # Get the latest day's data for display
    latest_date = full_df.index.max()
    latest_market = full_df.loc[latest_date].copy()

    # Filter candidates
    candidates = []
    grouped = full_df.groupby('code')
    print(f"Analyzing {len(grouped)} stocks for [{strategy.name}] strategy...")

    for code, group in grouped:
        code_str = str(code).zfill(6)

        # ETF/ETN 제외
        if code_str in etf_set:
            continue

        if strategy.apply(group):
            # Get latest day info for display
            stock_info = latest_market[latest_market['code'] == code]
            if not stock_info.empty:
                info = stock_info.iloc[0]
                avg_val = int(avg_value.get(code, 0))
                candidates.append({
                    "code": code_str,
                    "name": ticker_map.get(code_str, "알수없음"),
                    "price": int(info['종가']),
                    "change": round(float(info['등락률']), 2),
                    "cap": int(info['시가총액']),
                    "value": int(info['거래대금']),
                    "avg_value": avg_val,
                })

    # 평균 거래대금 내림차순 정렬 (거래대금 많은 순)
    sorted_candidates = sorted(candidates, key=lambda x: x['avg_value'], reverse=True)
    top_100 = sorted_candidates[:100]

    # 순위 부여
    for rank, c in enumerate(top_100, 1):
        c['rank'] = rank

    print(f"Found {len(candidates)} matching [{strategy.name}]. Picked Top {len(top_100)} by avg trading value.")

    # 전략 메타데이터 저장 (이메일에서 사용)
    meta = {
        "key": strategy_name,
        "name": strategy.name,
        "description": strategy.description,
        "matched": len(candidates),
        "picked": len(top_100),
    }
    with open(".tmp/strategy_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return top_100


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="종목 전략 필터링")
    parser.add_argument(
        "--strategy", "-s",
        default="nul_lim_mok",
        choices=list(STRATEGY_REGISTRY.keys()),
        help=f"적용할 전략 ({', '.join(STRATEGY_REGISTRY.keys())})"
    )
    args = parser.parse_args()

    results = process_strategies(strategy_name=args.strategy)
    pd.DataFrame(results).to_csv(".tmp/filtered_stocks.csv", index=False, encoding='utf-8-sig')
    print("Results with ranking saved to .tmp/filtered_stocks.csv")
