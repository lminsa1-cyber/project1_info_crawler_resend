import os
import csv
import re
import sys
from difflib import SequenceMatcher

# Windows 콘솔 한글 인코딩 지원 설정
sys.stdout.reconfigure(encoding='utf-8')

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "crawled_policy_news.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "cleaned_policy_news.csv")

# ==============================================================================
# 1. 텍스트 정제 패턴 정의 (정규식 및 문자열 패턴)
# ==============================================================================

# 본문에서 제거할 불필요한 노이즈 패턴들입니다.
CLEANING_PATTERNS = [
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # 이메일 주소 제거
    r"\[.*기자\]",                                       # 기자명 브라켓 형태 제거 (예: [서울=뉴시스] 홍길동 기자)
    r"\([a-zA-Z가-힣\s]*기자\)",                          # 소괄호 기자명 제거
    r"Copyrights\s*.*",                                 # Copyright 문구 제거
    r"무단\s*전재\s*및\s*재배포\s*금지",                   # 무단 전재 금지 제거
    r"저작권자\s*.*금지",                                # 저작권자 금지 문구 제거
    r"▶.*",                                            # 기사 하단 링크나 안내 제거
    r"구독하기.*",                                      # 구독 유도 제거
    r"네이버\s*채널.*",                                   # 네이버 채널 유도 제거
    r"\[사진.*\]",                                      # 사진 설명 텍스트 제거
    r"사진제공.*"                                        # 사진 출처 제거
]

def clean_body_text(text):
    """
    기사 본문의 광고 문구, 이메일, 기자 서명 등 노이즈 패턴을 지우고 깔끔하게 정리합니다.
    """
    if not text:
        return ""
    
    cleaned = text
    # 정규식 패턴 순차 적용
    for pattern in CLEANING_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        
    # 앞뒤 불필요한 공백 및 여러 개의 연속된 공백 정리
    cleaned = " ".join(cleaned.strip().split())
    return cleaned


# ==============================================================================
# 2. 정제 실행 엔진
# ==============================================================================

def run_cleaner():
    print("==================================================")
    print("🧹 데이터 정제(Cleaner) 프로세스 작동 시작")
    print("==================================================")
    
    # 1. 원본 파일 존재 여부 확인
    if not os.path.exists(INPUT_FILE):
        print(f"❌ [에러] 원본 파일이 저장 경로에 존재하지 않습니다: {INPUT_FILE}")
        print("     수집(crawler.py)을 먼저 실행해 주세요.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 2. 원본 데이터 로드
    raw_articles = []
    try:
        with open(INPUT_FILE, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            raw_articles = list(reader)
        print(f"로드 완료: 원본 데이터 {len(raw_articles)}건 확보")
    except Exception as e:
        print(f"❌ [에러] 원본 파일 로드 중 오류 발생: {e}")
        return

    # 3. 정제 작업 수행
    cleaned_articles = []
    
    # 통계 카운터
    missing_removed_count = 0  # 결측치 또는 짧은 글로 제거된 기사 수
    duplicate_removed_count = 0  # 유사 기사로 제거된 기사 수
    
    for art in raw_articles:
        title = art.get("title", "").strip()
        content = art.get("content", "").strip()
        date = art.get("date", "").strip()
        url = art.get("source_url", "").strip()
        source_name = art.get("source_name", "").strip()
        collected_at = art.get("collected_at", "").strip()

        # 3.1. 결측치 및 지나치게 짧은 기사 필터링
        # 제목이 비어있거나, 본문이 비어있거나, 본문이 100자 미만인 기사는 가치가 없으므로 필터링합니다.
        if not title or not content or len(content) < 100:
            missing_removed_count += 1
            continue

        # 3.2. 본문 텍스트 광고 및 노이즈 정제
        cleaned_content = clean_body_text(content)
        
        # 정제 후 다시 100자 이하가 되었다면 제거
        if len(cleaned_content) < 100:
            missing_removed_count += 1
            continue

        # 요약(Summary) 역시 정제된 본문을 기준으로 앞부분 재산출
        cleaned_summary = cleaned_content[:150].strip()
        if len(cleaned_content) > 150:
            cleaned_summary += "..."

        # 3.3. 유사 기사 중복 제거 (difflib.SequenceMatcher 활용)
        # 이미 담긴 정제 완료 기사들과 현재 기사의 제목 유사도를 구해 80% 이상 겹치면 중복 처리합니다.
        is_duplicate = False
        for existing in cleaned_articles:
            similarity = SequenceMatcher(None, title, existing["title"]).ratio()
            if similarity >= 0.8:
                is_duplicate = True
                duplicate_removed_count += 1
                break
                
        if is_duplicate:
            continue

        # 3.4. 저장 데이터 구축
        cleaned_row = {
            "article_id": art.get("article_id", ""),
            "title": title,
            "date": date,
            "content": cleaned_content,
            "summary": cleaned_summary,
            "source_url": url,
            "source_name": source_name,
            "collected_at": collected_at,
            "has_null": "False" if (title and cleaned_content) else "True"
        }
        cleaned_articles.append(cleaned_row)

    # 4. 정제된 파일 CSV 저장
    headers_list = ["article_id", "title", "date", "content", "summary", "source_url", "source_name", "collected_at", "has_null"]
    try:
        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers_list)
            writer.writeheader()
            for row in cleaned_articles:
                writer.writerow(row)
        print(f"💾 정제 완료 데이터 저장 성공! 경로: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ [에러] 정제 완료 데이터 저장 중 오류 발생: {e}")
        return

    # 5. 최종 정제 리포트 출력 (USER_REQUEST 내 Evaluate 항목 충족)
    print("\n==================================================")
    print("📊 [데이터 정제 결과 리포트]")
    print("==================================================")
    print(f"원본 데이터 건수   : {len(raw_articles)} 건")
    print(f"결측 및 짧은기사 제거: {missing_removed_count} 건")
    print(f"유사 기사 중복 제거: {duplicate_removed_count} 건")
    print(f"정제 완료 유효 건수 : {len(cleaned_articles)} 건")
    print("==================================================")


if __name__ == "__main__":
    run_cleaner()
