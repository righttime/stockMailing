# Stock Mailing (주식 분석 및 리포트 자동 발송 봇)

매일 한국 증시(KOSPI, KOSDAQ) 데이터를 수집하고, 지정된 매매 전략에 맞는 종목들을 필터링하여 일봉 차트와 관련 뉴스를 포함한 리포트를 자동으로 이메일로 발송하는 자동화 스크립트 모음입니다.

## 주요 기능
- **시장 데이터 수집 (`fetch_market_data.py`)**: `FinanceDataReader`를 이용하여 전 종목의 시세 및 시가총액 데이터를 수집합니다.
- **전략 엔진 (`strategy_processor.py`)**: 커스텀 매매 전략(눌림목, 스프링 등)을 적용하여 종목을 스크리닝학고 점수를 매깁니다.
- **차트 생성 (`generate_charts.py`)**: 필터링된 상위 종목들에 대해 일봉 차트 이미지를 생성합니다.
- **뉴스 검색 (`search_news.py`)**: 네이버 검색 API 등을 활용해 각 종목별 최신 뉴스 및 컨텍스트를 수집합니다.
- **메일 발송 (`gmail_sender.py`)**: 구글 Gmail API를 사용하여 반응형 HTML 이메일 포맷으로 차트 이미지와 순위를 함께 수신자들에게 발송합니다.
- **통합 파이프라인 (`run_all.py`)**: 위 모든 과정을 순차적으로 실행하며, 좀비 프로세스 방지를 위해 각 작업 단위(Step)마다 타임아웃 방어 로직이 적용되어 있습니다.

## 사전 요구사항 (Prerequisites)
- **Python 3.9+**
- **가상환경 (Virtual Environment)**
- **구글 Gmail API 권한 파일** (`credentials.json` 및 인증을 통해 생성되는 `token.json`)

## 설치 및 세팅
1. 저장소를 클론하고 폴더로 이동합니다.
2. 가상환경을 생성하고 접속한 뒤 의존성 패키지를 설치합니다. (아래 주요 의존성 참고)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install pandas FinanceDataReader matplotlib beautifulsoup4 google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```
3. GCP(Google Cloud Platform) 내에서 Gmail API를 활성화하고 얻어낸 `credentials.json` 파일을 프로젝트 루트에 위치시킵니다. (최초 실행 시 구글 로그인 프롬프트 팝업 창이 뜨며 `token.json`이 자동 생성됩니다.)

## 사용 방법

### 1. 프로세스 전체 실행
```bash
python run_all.py
```
- 오늘 날짜로 이미 수집된 주식 데이터(`.tmp/market_data.pkl`)가 존재할 경우, 크롤링 단계를 건너뛰고 캐시된 데이터로 분석 및 메일 발송이 진행됩니다.

### 2. 주식 데이터 강제 갱신 실행
오후나 장 마감 후 등 최신 데이터를 다시 스크래핑하여 처음부터 실행하고자 할 때는 `--force-refresh` 플래그를 사용합니다.
```bash
python run_all.py --force-refresh
```

### 3. 전략 변경
`run_all.py` 스크립트 파일 내에서 `ACTIVE_STRATEGY` 변수의 값을 수정하여 사용할 전략을 변경할 수 있습니다.
- `"nul_lim_mok"`: 눌림목 전략
- `"spring"`: 스프링 (이동평균선 밀집 및 정배열) 전략

## 자동화 (Cron)
매일 정해진 시각(예: 장 마감 후)에 프로그램이 백그라운드에서 동작할 수 있도록 `cron_run.sh` 쉘 스크립트가 준비되어 있습니다. 서버의 `crontab`에 스크립트 경로를 등록하여 사용하세요.
```bash
# 예시: 평일 오후 16시 정각에 매일 실행
0 16 * * 1-5 /root/project/stockMailing/cron_run.sh
```

## 로그 확인
모든 자동화 작업 중 발생하는 출력은 `cron.log` 파일에 누적되어 저장됩니다. 진행 상황이나 에러 발생 여부는 해당 로그 파일을 모니터링하여 파악할 수 있습니다.
