import pandas as pd
from .base import BaseStrategy


class NulLimMokStrategy(BaseStrategy):
    """눌림목 전략: 20일선 부근에서 수렴하는 종목 포착."""

    @property
    def name(self) -> str:
        return "눌림목"

    @property
    def description(self) -> str:
        return "20일 이동평균선 상승 중, 5일선과 20일선 수렴, 종가가 20MA 위 5% 이내"

    @property
    def min_data_days(self) -> int:
        return 21

    def apply(self, df: pd.DataFrame) -> bool:
        col_map = {
            '시가': '시가', '고가': '고가', '저가': '저가', '종가': '종가', '등락률': '등락률',
            'open': '시가', 'high': '고가', 'low': '저가', 'close': '종가', 'change_rate': '등락률'
        }
        df = df.rename(columns=col_map)

        if '종가' not in df.columns or len(df) < self.min_data_days:
            return False

        # Calculate MAs
        df['ma5'] = df['종가'].rolling(window=5).mean()
        df['ma20'] = df['종가'].rolling(window=20).mean()

        # Technical conditions
        ma20_upward = df['ma20'].iloc[-1] > df['ma20'].iloc[-2]
        gap_t = abs(df['ma5'].iloc[-1] - df['ma20'].iloc[-1])
        gap_t_1 = abs(df['ma5'].iloc[-2] - df['ma20'].iloc[-2])
        gap_narrowing = gap_t < gap_t_1
        above_ma20 = df['종가'].iloc[-1] > df['ma20'].iloc[-1]
        near_ma20 = (df['종가'].iloc[-1] / df['ma20'].iloc[-1]) < 1.05

        return ma20_upward and gap_narrowing and above_ma20 and near_ma20
