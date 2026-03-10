# SOP: Daily Stock Analysis & Report

## Goal
To analyze the Korean stock market daily using a **pluggable strategy**, and send a consolidated report via email.

## Strategy System
전략은 `execution/strategies/` 폴더에 독립 모듈로 관리됩니다.

| 전략 키 | 이름 | 설명 |
|---------|------|------|
| `nul_lim_mok` | 눌림목 | 20MA 수렴 + 상승 |
| `spring` | 스프링 | 전 이평선 위 밀착 정렬 + 60MA 상승 |

**전략 교체**: `run_all.py` 상단의 `ACTIVE_STRATEGY` 값만 변경하면 됩니다.

**새 전략 추가**:
1. `execution/strategies/`에 새 파일 생성 (`BaseStrategy` 상속)
2. `execution/strategies/__init__.py`의 `STRATEGY_REGISTRY`에 등록

## Inputs
- `credentials.json`: Google OAuth credentials (required for Gmail API).
- Internet connection for stock data and news.

## Workflow Step-by-Step

### 1. Fetch Market Data
Run the fetching script to download OHLCV data for KOSPI and KOSDAQ.
```bash
python execution/fetch_market_data.py
```
*Outputs stored in `.tmp/market_data.pkl`. 기본 200일치 수집 (120MA용).*

### 2. Apply Analysis Strategy
Process the downloaded data using the active strategy.
```bash
python execution/strategy_processor.py --strategy spring
```
*Outputs filtered list to `.tmp/filtered_stocks.csv` and strategy metadata to `.tmp/strategy_meta.json`.*

### 3. Generate Charts
```bash
python execution/generate_charts.py
```

### 4. Gather News & Context
```bash
python execution/search_news.py
```
*Outputs context to `.tmp/news_context.json`.*

### 5. Send Email Report
Format the collected information into an HTML email and send it via Gmail.
```bash
python execution/gmail_sender.py
```
*이메일 제목에 전략 이름이 자동 반영됩니다.*

## Troubleshooting
- **No data found**: Check if the market was open or if FinanceDataReader is working.
- **Gmail Auth Error**: Ensure `credentials.json` is present and `token.json` is refreshed.
- **Performance**: Fetching 2500+ stocks × 200 days can be slow; ensure the script completes before timeout.
- **전략 오류**: `python execution/strategy_processor.py --strategy spring` 으로 직접 실행하여 디버깅.

## Maintenance
- 전략 조건 수정: `execution/strategies/` 내 해당 전략 파일 수정
- 신규 전략 추가: `BaseStrategy` 상속 → 레지스트리 등록
