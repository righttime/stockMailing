from abc import ABC, abstractmethod
import pandas as pd


class BaseStrategy(ABC):
    """모든 전략의 공통 인터페이스."""

    @property
    @abstractmethod
    def name(self) -> str:
        """전략의 한글 이름 (이메일 제목 등에 사용)."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """전략에 대한 간단한 설명."""
        ...

    @abstractmethod
    def apply(self, df: pd.DataFrame) -> bool:
        """
        단일 종목의 일봉 DataFrame을 받아 전략 조건 충족 여부를 반환.

        Args:
            df: 날짜 인덱스, 최소 컬럼: 시가, 고가, 저가, 종가, 거래대금
        Returns:
            True if the stock matches this strategy's criteria.
        """
        ...

    @property
    def min_data_days(self) -> int:
        """전략이 필요로 하는 최소 데이터 일수 (기본 21일)."""
        return 21
