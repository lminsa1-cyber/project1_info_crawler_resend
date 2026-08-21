import os
import csv
import sys

# Windows 콘솔 한글 인코딩 지원 설정
sys.stdout.reconfigure(encoding='utf-8')

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "cleaned_policy_news.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "recommended_policy_news.csv")

# ==============================================================================
# 1. 추천 키워드 및 가중치 정의
# ==============================================================================
RECOMMEND_CATEGORIES = {
    "AI": {
        "weight": 1.5,
        "keywords": ["ai", "인공지능", "생성형", "chatgpt", "llm", "gpt", "클로드", "인텔리전스"]
    },
    "Automation": {
        "weight": 1.2,
        "keywords": ["자동화", "로봇", "rpa", "오토메이션", "ax", "피지컬ai"]
    },
    "Cloud": {
        "weight": 1.1,
        "keywords": ["클라우드", "cloud", "saas", "paas", "iaas"]
    },
    "Data": {
        "weight": 1.0,
        "keywords": ["데이터", "data", "빅데이터", "db", "데이터베이스"]
    },
    "Security": {
        "weight": 1.3,
        "keywords": ["보안", "시큐리티", "해킹", "랜섬웨어", "보호", "방화벽", "악성코드", "백신", "스팸"]
    },
    "DX": {
        "weight": 1.2,
        "keywords": ["디지털 전환", "dx", "디지털혁신", "디지털트랜스포메이션", "전동화"]
    }
}

def calculate_article_score(title, content):
    """
    제목과 본문의 키워드 빈도를 가중치와 매칭하여 최종 추천 점수를 계산합니다.
    제목의 키워드는 본문보다 5배 더 중요하게 취급합니다.
    """
    if not title and not content:
        return 0.0
        
    title_lower = title.lower() if title else ""
    content_lower = content.lower() if content else ""
    
    total_score = 0.0
    
    for cat_name, cat_info in RECOMMEND_CATEGORIES.items():
        weight = cat_info["weight"]
        keywords = cat_info["keywords"]
        
        cat_title_count = 0
        cat_content_count = 0
        
        for kw in keywords:
            # 제목 키워드 카운트
            cat_title_count += title_lower.count(kw)
            # 본문 키워드 카운트
            cat_content_count += content_lower.count(kw)
            
        # 점수 산정: 가중치 * (5 * 제목 빈도 + 1 * 본문 빈도)
        cat_score = weight * (5 * cat_title_count + 1 * cat_content_count)
        total_score += cat_score
        
    return round(total_score, 2)


# ==============================================================================
# 2. 추천 시스템 실행 엔진
# ==============================================================================

def run_recommender():
    print("==================================================")
    print("🎯 추천 시스템(Recommender) 프로세스 작동 시작")
    print("==================================================")
    
    # 1. 정제 파일 존재 여부 확인
    if not os.path.exists(INPUT_FILE):
        print(f"❌ [에러] 정제 완료 파일이 존재하지 않습니다: {INPUT_FILE}")
        print("     정제(cleaner.py)를 먼저 실행해 주세요.")
        return

    # 2. 데이터 로드
    cleaned_articles = []
    try:
        with open(INPUT_FILE, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            cleaned_articles = list(reader)
        print(f"로드 완료: 정제 완료 데이터 {len(cleaned_articles)}건 확보")
    except Exception as e:
        print(f"❌ [에러] 정제 완료 파일 로드 중 오류 발생: {e}")
        return

    # 3. 점수 계산 수행
    scored_articles = []
    for art in cleaned_articles:
        title = art.get("title", "")
        content = art.get("content", "")
        
        score = calculate_article_score(title, content)
        
        # 원본 정보에 점수 컬럼 추가
        recommended_row = dict(art)
        recommended_row["recommendation_score"] = score
        scored_articles.append(recommended_row)

    # 4. 추천 점수 내림차순 정렬
    # 점수가 높은 순으로 정렬하며, 점수가 같으면 최신 날짜순으로 정렬합니다.
    scored_articles.sort(key=lambda x: (x["recommendation_score"], x["date"]), reverse=True)

    # 5. 상위 20건 기사 추출
    top_recommended = scored_articles[:20]
    print(f"추천 완료: 정렬된 데이터 중 상위 {len(top_recommended)}건을 엄선하였습니다.")

    # 6. 추천 결과 CSV 저장
    headers_list = ["article_id", "title", "date", "content", "summary", "source_url", "source_name", "collected_at", "has_null", "recommendation_score"]
    try:
        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers_list)
            writer.writeheader()
            for row in top_recommended:
                writer.writerow(row)
        print(f"💾 추천 결과 데이터 저장 성공! 경로: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ [에러] 추천 결과 데이터 저장 중 오류 발생: {e}")
        return

    # 7. 추천 상위 5건 출력 (USER_REQUEST 내 Evaluate 항목 충족)
    print("\n==================================================")
    print("🏆 [추천 우수 기사 TOP 5 리포트]")
    print("==================================================")
    for idx, art in enumerate(top_recommended[:5], 1):
        title = art["title"]
        score = art["recommendation_score"]
        source = art["source_name"]
        date = art["date"]
        print(f"[{idx}등] [점수: {score:5.2f}점] {title} ({source} / {date})")
    print("==================================================")


if __name__ == "__main__":
    run_recommender()
