import pandas as pd
from .base import BaseStrategy


class SpringStrategy(BaseStrategy):
    """
    스프링 전략: 모든 주요 이동평균선 위에서 밀착 정렬된 종목 포착.

    조건 (일봉 기준, 14개):
     1. 시가 or 종가 > 5MA
     2. 시가 or 종가 > 10MA
     3. 시가 or 종가 > 20MA
     4. 시가 or 종가 > 60MA
     5. 시가 or 종가 > 120MA
     6. 거래대금 ≥ 10억
     7. 종가 ~ 5MA 3% 이내
     8. 종가 ~ 10MA 4% 이내
     9. 5MA ~ 10MA 3% 이내
    10. 5MA ~ 20MA 5% 이내
    11. ETF/ETN 제외 (strategy_processor에서 처리)
    12. 오늘 종가 vs 어제 종가 ±3%
    13. 어제 종가 vs 그제 종가 ±3%
    14. 20봉전 60MA < 오늘 60MA
    """

    @property
    def name(self) -> str:
        return "스프링"

    @property
    def description(self) -> str:
        return "모든 주요 이평선(5/10/20/60/120) 위에서 밀착 정렬, 60MA 상승 추세"

    @property
    def min_data_days(self) -> int:
        # 120MA 계산에 120일 + iloc[-21]로 20봉전 60MA 참조 → 최소 121일
        return 121

    def apply(self, df: pd.DataFrame) -> bool:
        col_map = {
            '시가': '시가', '고가': '고가', '저가': '저가', '종가': '종가',
            'open': '시가', 'high': '고가', 'low': '저가', 'close': '종가',
        }
        df = df.rename(columns=col_map)

        required = ['시가', '종가', '거래대금']
        if not all(c in df.columns for c in required):
            return False

        if len(df) < self.min_data_days:
            return False

        # --- 이동평균 계산 ---
        df['ma5'] = df['종가'].rolling(window=5).mean()
        df['ma10'] = df['종가'].rolling(window=10).mean()
        df['ma20'] = df['종가'].rolling(window=20).mean()
        df['ma60'] = df['종가'].rolling(window=60).mean()
        df['ma120'] = df['종가'].rolling(window=120).mean()

        # 최신 봉 (0봉전)
        today = df.iloc[-1]
        yesterday = df.iloc[-2]   # 1봉전
        day_before = df.iloc[-3]  # 2봉전

        시가 = today['시가']
        종가 = today['종가']
        ma5 = today['ma5']
        ma10 = today['ma10']
        ma20 = today['ma20']
        ma60 = today['ma60']
        ma120 = today['ma120']

        # NaN 체크 (이평 계산 불가 시)
        if pd.isna(ma120) or pd.isna(df.iloc[-21]['ma60']):
            return False

        # --- 조건 1~5: 시가 or 종가 > 각 이평선 ---
        if not (시가 > ma5 or 종가 > ma5):
            return False
        if not (시가 > ma10 or 종가 > ma10):
            return False
        if not (시가 > ma20 or 종가 > ma20):
            return False
        if not (시가 > ma60 or 종가 > ma60):
            return False
        if not (시가 > ma120 or 종가 > ma120):
            return False

        # --- 조건 6: 거래대금 10억 이상 ---
        if today['거래대금'] < 1_000_000_000:
            return False

        # --- 조건 7: 종가가 5MA 대비 3% 이내 근접 ---
        if abs(종가 - ma5) / ma5 > 0.03:
            return False

        # --- 조건 8: 종가가 10MA 대비 4% 이내 근접 ---
        if abs(종가 - ma10) / ma10 > 0.04:
            return False

        # --- 조건 9: 5MA가 10MA 대비 3% 이내 근접 ---
        if abs(ma5 - ma10) / ma10 > 0.03:
            return False

        # --- 조건 10: 5MA가 20MA 대비 5% 이내 근접 ---
        if abs(ma5 - ma20) / ma20 > 0.05:
            return False

        # --- 조건 12: 오늘 종가 vs 어제 종가 ±3% ---
        change_today = abs(종가 - yesterday['종가']) / yesterday['종가']
        if change_today > 0.03:
            return False

        # --- 조건 13: 어제 종가 vs 그제 종가 ±3% ---
        change_yesterday = abs(yesterday['종가'] - day_before['종가']) / day_before['종가']
        if change_yesterday > 0.03:
            return False

        # --- 조건 14: 20봉전 60MA < 오늘 60MA (60MA 상승 추세) ---
        ma60_20_ago = df.iloc[-21]['ma60']
        if ma60_20_ago >= ma60:
            return False

        return True
