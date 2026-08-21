# 📊 AI & IT 핵심 뉴스/정책 수집 및 이메일 리포팅 파이프라인

본 프로젝트는 초보자도 쉽게 실행하고 이해할 수 있도록 설계된 **자동화 뉴스 수집, 정제, 중요도 추천 및 이메일 뉴스레터/실무 대시보드 시각화 파이프라인**입니다.  
IT 핵심 도메인 키워드(AI, 생성형 AI, 자동화, 클라우드, 데이터, 보안, 디지털 전환)를 기반으로 하여 실무 의사결정에 즉각 투입할 수 있는 인사이트를 제공합니다.

---

## 📁 1. 프로젝트 폴더 구조 (Directory Structure)

본 프로젝트는 실무 표준 규격을 완벽하게 따르며 아래와 같이 배치되어 있습니다:

```text
project1_info_crawler_resend/
├── data/
│   ├── raw/
│   │   └── crawled_policy_news.csv       <-- [수집 원본 데이터]
│   └── processed/
│       ├── cleaned_policy_news.csv       <-- [텍스트 정제 가공 데이터]
│       └── recommended_policy_news.csv   <-- [추천 알고리즘 상위 20선]
├── reports/
│   ├── email_preview.html                <-- [고급 비즈니스 이메일 HTML 파일]
│   ├── email_preview.txt                 <-- [이메일 텍스트 포맷 미리보기 파일]
│   └── resend_send_log.csv               <-- [실제 메일 발송 성공 누적 이력]
├── logs/
│   ├── crawler_error_log.txt             <-- [크롤러 수집 진행 상황 기록 로그]
│   └── resend_error_log.txt              <-- [실제 메일 전송 실패 및 예외 로그]
├── app/
│   └── streamlit_app.py                  <-- [실무형 웹 대시보드 어플리케이션]
├── crawler.py                            <-- [1단계: 자동화 정보 수집기]
├── cleaner.py                            <-- [2단계: 데이터 정제 프로그램]
├── recommender.py                        <-- [3단계: 가중치 점수 산출 및 추천기]
├── email_report_builder.py               <-- [4단계: 이메일 템플릿 변환기 (TOP 10 제한)]
├── send_resend_email.py                  <-- [5단계: Resend API 이메일 발송 모듈]
├── requirements.txt                      <-- [설치 필요 외부 라이브러리 리스트]
├── .env.example                          <-- [환경 설정 샘플 파일]
└── README.md                             <-- [본 가이드 문서]
```

---

## 🛠️ 2. 초보자용 환경 설정 및 가동 방법 (Installation & Run)

초보자도 터미널 명령어를 입력하여 순서대로 동작시킬 수 있습니다.

### 1단계: 필수 라이브러리 원클릭 설치
컴퓨터의 명령 프롬프트(PowerShell 또는 CMD)를 열어 프로젝트 폴더가 위치한 경로로 이동한 뒤, 아래 명령어를 실행하여 설치를 완료합니다.
```powershell
pip install -r requirements.txt
```

### 2단계: 환경 설정 파일 (.env) 준비
1. 폴더 안에 있는 `.env.example` 파일을 복사하여 똑같은 위치에 **`.env`**로 이름을 변경합니다.
2. 메모장으로 `.env` 파일을 열어 수강생님의 **실제 Resend API Key**와 **이메일 정보**를 입력하고 저장합니다.
```ini
RESEND_API_KEY=re_실제발급받은API키 입력
SENDER_EMAIL=onboarding@resend.dev
RECEIVER_EMAIL=ms_lee@gbsa.iceu.kr
ENABLE_REAL_EMAIL_SEND=true
```

---

## 🏃 3. 파이프라인 단계별 가동 명령어 (Pipeline Commands)

아래 명령어들을 순서대로 터미널에 복사 및 입력해 주시면 모든 자동화 처리가 일사천리로 동작합니다.

### [1단계] 뉴스 데이터 크롤링 수집
웹사이트로부터 최신 IT 뉴스 정책 자료를 자동 수집합니다.
```powershell
python crawler.py
```

### [2단계] 쓸모없는 데이터 정제 (Cleaner)
결측값, 짧은 글, 광고 문구를 제거하고 제목 유사도를 분석하여 중복 기사를 완전 정제합니다.
```powershell
python cleaner.py
```

### [3단계] 기술 테마별 추천 점수 계산 (Recommender)
AI, 클라우드, 보안 등 주요 가중치를 연산하여 점수를 부여하고 내림차순 정렬을 수행합니다.
```powershell
python recommender.py
```

### [4단계] 이메일 뉴스레터 생성 (Email Report Builder)
수집 추천된 기사 중 **상위 10선 (TOP 10)**을 선별하여 비즈니스용 실무 메일 미리보기 양식을 빌드합니다.
```powershell
python email_report_builder.py
```

### [5단계] 실제 메일 발송 전송 (Resend Mailer)
Resend API를 사용하여 미리 생성한 뉴스레터 요약을 지정된 이메일로 전송하고 이력을 보존합니다.
```powershell
python send_resend_email.py
```

### [6단계] 실무 보고용 웹 대시보드 가동 (Streamlit Board)
경영진 보고 및 인터랙티브 탐색을 지원하는 예쁜 실무용 웹 대시보드를 브라우저에 실행합니다.
```powershell
streamlit run app/streamlit_app.py
```

---

## 📊 4. 실습 성공/실패 검증 기준표 (Validation Criteria Matrix)

각 단계별 정상 작동 여부를 판단하고 예외를 격리하기 위한 실무 무결성 체크 기준표입니다:

| 파이프라인 단계 | 성공 판정 기준 (SUCCESS) | 실패/에러 판정 기준 (FAIL) | 조치 및 디버깅 가이드 (Action Guide) |
| :--- | :--- | :--- | :--- |
| **1. 데이터 수집**<br>`(crawler.py)` | - 210건의 기사를 수집 및 Raw CSV 저장 완료<br>- 진행 일지가 `logs/crawler_error_log.txt`에 기록 | - 수집된 데이터가 200건 미만이거나 오류 발생<br>- 수집 CSV 파일 누락 및 네트워크 타임아웃 | - 타겟 RSS 주소가 변경되었는지 인터넷 연결을 확인합니다.<br>- `logs/crawler_error_log.txt`에 기록된 에러 원인을 추적합니다. |
| **2. 데이터 정제**<br>`(cleaner.py)` | - 제목/본문 빈 칸 및 100자 이하 본문 자동 여과<br>- `difflib` 제목 80% 이상 유사 기사 정확히 필터링 완료 | - 정제 후 남은 기사가 없거나 필터 에러<br>- 파일 입출력 인코딩 오류 발생 | - 원본 CSV 파일의 UTF-8 한글 깨짐을 예방하기 위해 인코딩(`utf-8-sig`)을 지정해 주세요. |
| **3. 추천 가중치**<br>`(recommender.py)` | - AI(1.5) 등 6대 키워드 가중치 수식 연산 완료<br>- 제목 매칭에 5배 가중치가 정확히 가산됨 | - 추천 점수가 0점 일괄 계산되거나 정렬 불량<br>- 추천 결과 CSV 파일 저장 실패 | - 키워드 매칭 시 대소문자 구분을 없앴는지 확인하고 가중치 설정 딕셔너리를 점검합니다. |
| **4. 리포트 빌더**<br>`(email_report_builder.py)` | - 비즈니스용 TOP 10 카드 레이아웃의 HTML/TXT 빌드 완료<br>- 흰색, 남색, 연회색, 초록 상태 배지 시각화 적용 | - 출력 기사 수가 10개를 초과하거나 템플릿 미형성<br>- 윈도우 한글 날짜 인코딩 에러 발생 | - `datetime.strftime` 대신 플랫폼 독립적인 순수 파이썬 f-string 날짜 전처리를 사용해 인코딩을 회피합니다. |
| **5. 메일 발송**<br>`(send_resend_email.py)` | - 동일 날짜, 수신자, 제목 기반의 **중복 발송 완전 차단**<br>- 전송 성공 내역 CSV 기록 및 실패 내역 파일 백업 | - 중복 메일의 불필요한 반복 재송출 발생<br>- 403 인증 권한 차단 에러 발생 시 안내 가이드 누락 | - Sandbox 발송자(`onboarding@resend.dev`)는 가입하신 수강생의 메일로만 전송을 받으니 수신 주소를 재차 확인하세요. |
| **6. 웹 대시보드**<br>`(streamlit_app.py)` | - 요약 지표, 추천 TOP 10, 검색 필터 탐색기 구동<br>- 깔끔한 Matplotlib 한글 가로 차트 시각화 표출 | - Streamlit 미설치로 실행 불가<br>- 한글 폰트 미인식으로 인한 차트 라벨 깨짐 현상 | - Windows 환경 내 폰트 라이브러리(`Malgun Gothic`)를 matplotlib 스타일 패치에 올바르게 연동했는지 확인합니다. |
