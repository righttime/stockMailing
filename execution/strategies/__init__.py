"""
전략 레지스트리.
새 전략을 추가하려면: 1) 모듈 작성  2) 여기에 import & 등록
"""
from .nul_lim_mok import NulLimMokStrategy
from .spring import SpringStrategy

STRATEGY_REGISTRY = {
    "nul_lim_mok": NulLimMokStrategy,
    "spring": SpringStrategy,
}
