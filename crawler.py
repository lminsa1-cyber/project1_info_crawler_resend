import os
import csv
import time
import random
import hashlib
import datetime
from urllib.parse import urlparse
import sys

# Windows 콘솔에서 한글 출력이 깨지지 않도록 출력 인코딩을 UTF-8로 설정합니다.
sys.stdout.reconfigure(encoding='utf-8')

# 크롤링에 필요한 핵심 라이브러리들을 임포트합니다.
import requests
import feedparser
from bs4 import BeautifulSoup

# ==============================================================================
# 1. 설정 (Configuration)
# ==============================================================================

# 수집 대상 RSS 피드 주소 목록입니다.
# 공공기관(과기정통부, KISA) 및 대형 IT 언론사(전자신문)의 신뢰할 수 있고 공개된 피드들입니다.
RSS_FEEDS = {
    "ETNews_AI": "http://rss.etnews.com/04046.xml",
    "ETNews_Security": "http://rss.etnews.com/04045.xml",
    "ETNews_IT_Industry": "http://rss.etnews.com/03.xml",
    "ETNews_Today": "http://rss.etnews.com/Section901.xml",
    "ETNews_Breaking": "http://rss.etnews.com/Section902.xml",
    "MSIT_Press_Release": "https://www.msit.go.kr/user/rss/rss.do?bbsSeqNo=94",
    "MSIT_Notice": "https://www.msit.go.kr/user/rss/rss.do?bbsSeqNo=96",
    "MSIT_ICT_Policy": "https://www.msit.go.kr/user/rss/rss.do?bbsSeqNo=67",
    "KISA_Press_Release": "https://www.kisa.or.kr/rss/402"
}

# 서버 차단 방지를 위한 브라우저 우회(User-Agent) 헤더 정보입니다.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 AI-Education-Crawler; contact: student@example.com"
}

# 결과 및 로그 저장 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "crawled_policy_news.csv")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "crawler_error_log.txt")

def write_log(message, level="INFO"):
    """
    지정한 로그 메시지를 logs/crawler_error_log.txt 파일에 실시간 누적 기록합니다.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}\n"
    
    # 로그 파일에 추가
    with open(LOG_FILE, mode="a", encoding="utf-8") as f:
        f.write(log_line)

# ==============================================================================
# 2. 보조 함수 (Utility Functions)
# ==============================================================================

def clean_text(text):
    """
    텍스트 내부의 불필요한 줄바꿈, 공백, 탭 문자 등을 제거하고 깨끗한 한 줄의 텍스트로 합쳐줍니다.
    """
    if not text:
        return ""
    # 여러 줄 공백 및 줄바꿈 정리
    lines = text.strip().split()
    return " ".join(lines)


def parse_date(raw_date_str):
    """
    다양한 형식의 날짜 문자열을 읽어 'YYYY-MM-DD' 표준 포맷으로 변환합니다.
    """
    if not raw_date_str:
        return None
    raw_date_str = raw_date_str.strip()
    
    # 1. RSS RFC822 포맷 (예: Thu, 20 Aug 2026 15:19:40 +0900)
    # feedparser가 알아서 파싱해주거나 직접 파싱을 시도합니다.
    try:
        # 이메일/RSS 표준 날짜 변환 라이브러리 사용
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(raw_date_str)
        return dt.strftime("%Y-%m-%d")
    except:
        pass

    # 2. 과기정통부 형식 (예: 2026.08.20)
    try:
        cleaned_date = raw_date_str.replace(".", "-")
        # 10자리 문자열만 남기기 (예: 2026-08-20)
        if len(cleaned_date) >= 10:
            return cleaned_date[:10]
    except:
        pass
        
    # 3. KISA 형식 (예: 2026-08-12)
    if len(raw_date_str) >= 10 and raw_date_str[4] == '-' and raw_date_str[7] == '-':
        return raw_date_str[:10]

    return raw_date_str


def get_body_text_from_html(url, source_name):
    """
    기사 상세 페이지 URL에 접속해 실제 본문(Content)에 해당하는 한글 텍스트만 추출합니다.
    서버 차단이나 에러 시 None을 반환하며 안전하게 Fallback 하도록 구성되었습니다.
    """
    try:
        # 대상 서버 보호를 위해 1.0 ~ 2.0초 동안 무작위로 쉬어갑니다. (Polite Crawling)
        time.sleep(random.uniform(1.0, 2.0))
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            msg = f"{url} 접속 실패 (HTTP 상태 코드: {response.status_code})"
            print(f"    [경고] {msg}")
            write_log(msg, "WARNING")
            return None
            
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 소스 언론사/공공기관별 고유의 본문 영역 셀렉터 적용
        if "ETNews" in source_name:
            # 전자신문 본문 컨테이너
            body_container = soup.find(id="articleBody") or soup.find(class_="article_body")
            if body_container:
                # 불필요한 스크립트나 스타일 제거
                for s in body_container(["script", "style", "iframe"]):
                    s.decompose()
                return clean_text(body_container.get_text())
                
        elif "MSIT" in source_name:
            # 과학기술정보통신부 본문 컨테이너
            body_container = soup.find(class_="board_notcon") or soup.find(class_="board_view")
            if body_container:
                for s in body_container(["script", "style"]):
                    s.decompose()
                return clean_text(body_container.get_text())
                
        elif "KISA" in source_name:
            # KISA 보도자료 본문 컨테이너
            body_container = soup.find(class_="board_view") or soup.find(class_="view_cont")
            if body_container:
                for s in body_container(["script", "style"]):
                    s.decompose()
                return clean_text(body_container.get_text())

        # 매칭되는 고유 셀렉터가 없거나 텍스트를 찾지 못했다면 일반적인 텍스트 추출 시도 (Fallback)
        # 본문 내용이 있을법한 대형 div 영역 중 불필요 요소 제거 후 추출
        for s in soup(["script", "style", "header", "footer", "nav", "aside"]):
            s.decompose()
        
        # 글자수가 가장 많은 컨테이너를 본문으로 휴리스틱하게 추정
        divs = soup.find_all("div")
        if divs:
            divs_sorted = sorted(divs, key=lambda x: len(x.get_text(strip=True)), reverse=True)
            for best_div in divs_sorted[:3]:
                txt = clean_text(best_div.get_text())
                if len(txt) > 200:
                    return txt
                    
        return None
    except Exception as e:
        msg = f"{url} 상세 본문 크롤링 중 오류 발생: {e}"
        print(f"    [에러] {msg}")
        write_log(msg, "ERROR")
        return None

# ==============================================================================
# 3. 메인 수집 로직 (Main Collection Engine)
# ==============================================================================

def run_crawler():
    # 실행 로그 파일 초기화 및 시작 기록
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, mode="w", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] === 크롤러 실행 시작 ===\n")

    print("==================================================")
    print("🚀 뉴스 및 정책 문서 수집 크롤러 가동 시작")
    print("==================================================")
    write_log("크롤러 작동을 개시합니다.", "INFO")
    
    # 1. 폴더 생성 확인
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"데이터 저장 경로 확인: {OUTPUT_DIR}")

    # 2. RSS 피드 파싱하여 기사 목록 메타데이터 수집
    raw_articles = []
    seen_urls = set()  # 중복 URL을 빠르게 방지하기 위한 세트
    
    print("\n--- [1단계] RSS 피드 메타데이터 파싱 ---")
    for source_name, feed_url in RSS_FEEDS.items():
        print(f"수집 중: {source_name} ({feed_url}) ...")
        try:
            # feedparser를 사용하여 XML 데이터를 쉽고 간결하게 파싱합니다.
            feed = feedparser.parse(feed_url)
            
            feed_items_count = 0
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                url = entry.get("link", "").strip()
                pub_date = entry.get("published", entry.get("pubDate", ""))
                description = entry.get("description", entry.get("summary", ""))
                
                # 수집 도중 URL이 비어있거나 이미 목록에 존재하면 중복 수집 제외
                if not url or url in seen_urls:
                    continue
                
                seen_urls.add(url)
                
                # 나중에 분류나 소스 분류용으로 사용할 이름 저장
                source_base = "ETNews" if "ETNews" in source_name else ("MSIT" if "MSIT" in source_name else "KISA")
                
                raw_articles.append({
                    "title": title,
                    "source_url": url,
                    "date": pub_date,
                    "description": description,
                    "source_name": source_base
                })
                feed_items_count += 1
            msg = f"{source_name} 완료: {feed_items_count}개의 고유 기사 링크 확보"
            print(f"  └ {msg}")
            write_log(msg, "INFO")
        except Exception as e:
            msg = f"{source_name} RSS 피드 파싱 실패: {e}"
            print(f"  └ [실패] {msg}")
            write_log(msg, "ERROR")

    total_links = len(raw_articles)
    msg = f"총 {total_links}개의 유니크한 기사 수집 링크를 확보하였습니다."
    print(f"\n{msg}")
    print("--------------------------------------------------")
    write_log(msg, "INFO")

    # 3. 상세 기사 본문 내용 수집 및 규격 변환
    print("\n--- [2단계] 상세 페이지 본문 수집 시작 ---")
    print("※ 서버를 보호하고 정상적인 요청을 위해 각 수집 간 안전 딜레이가 적용됩니다. 잠시만 기다려주세요...\n")
    
    final_dataset = []
    
    # 통계용 변수 정의
    missing_title_count = 0
    missing_content_count = 0
    source_stats = {}

    for idx, art in enumerate(raw_articles, 1):
        url = art["source_url"]
        title = art["title"]
        source_name = art["source_name"]
        
        print(f"[{idx}/{total_links}] [{source_name}] {title[:35]}...")

        # 상세 페이지 HTML에서 본문 텍스트 수집
        content = get_body_text_from_html(url, source_name)
        
        # 만약 상세 본문 크롤링 실패 시 RSS의 description을 본문 및 요약으로 활용 (Fallback 구조)
        has_null = False
        if not content:
            if art["description"]:
                # RSS description에 데이터가 존재하면 이를 본문으로 간주
                content = clean_text(art["description"])
                print("    -> 상세 본문 수집에 실패하여 RSS 요약설명으로 대체 적용하였습니다.")
            else:
                # RSS description 마저 없으면 빈값 처리 후 결측 마킹
                content = ""
                has_null = True
                print("    -> [경고] 상세 본문 및 RSS 요약설명이 모두 존재하지 않습니다.")

        # 요약(Summary) 생성: 본문의 앞부분에서 최대 150자 추출 또는 RSS 요약 사용
        summary = ""
        if content:
            summary = content[:150].strip()
            if len(content) > 150:
                summary += "..."
        elif art["description"]:
            summary = clean_text(art["description"])[:150]
        else:
            summary = ""
            has_null = True

        # 날짜 포맷 표준화 (YYYY-MM-DD)
        formatted_date = parse_date(art["date"])
        if not formatted_date:
            formatted_date = datetime.date.today().strftime("%Y-%m-%d")
            has_null = True

        # 고유 Article ID 생성 (URL 문자열의 MD5 해시값을 생성하여 고유성 보장)
        article_id = hashlib.md5(url.encode("utf-8")).hexdigest()

        # 수집 시점 타임스탬프 기록
        collected_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 결측치 통계 산출
        if not title:
            missing_title_count += 1
            has_null = True
        if not content:
            missing_content_count += 1
            has_null = True

        # 수집된 행 레코드 구축
        row = {
            "article_id": article_id,
            "title": title,
            "date": formatted_date,
            "content": content,
            "summary": summary,
            "source_url": url,
            "source_name": source_name,
            "collected_at": collected_at,
            "has_null": has_null
        }
        
        final_dataset.append(row)
        
        # 소스별 통계 가산
        source_stats[source_name] = source_stats.get(source_name, 0) + 1

        # 성능 및 서버 보호 최적화: 최소 요구 건수인 200건(안전을 위해 210건)을 달성하면 상세 수집 조기 종료
        if len(final_dataset) >= 210:
            msg = f"목표 요구치인 200건을 상회하는 {len(final_dataset)}건 수집을 달성하여 서버 부하 방지차 상세 수집을 조기 종료합니다."
            print(f"\n💡 [안내] {msg}")
            write_log(msg, "INFO")
            break

    # ==============================================================================
    # 4. CSV 저장 및 결과 출력
    # ==============================================================================
    print("\n--- [3단계] CSV 파일 저장 및 최종 평가 ---")
    
    # CSV 저장 수행
    headers_list = ["article_id", "title", "date", "content", "summary", "source_url", "source_name", "collected_at", "has_null"]
    
    try:
        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers_list)
            writer.writeheader()
            for r in final_dataset:
                writer.writerow(r)
        msg = f"데이터 저장이 완료되었습니다! 경로: {OUTPUT_FILE}"
        print(f"💾 {msg}")
        write_log(msg, "INFO")
    except Exception as e:
        msg = f"CSV 저장 중 치명적 오류 발생: {e}"
        print(f"❌ [에러] {msg}")
        write_log(msg, "ERROR")
        return

    # 화면에 최종 성적 요약 출력 (USER_REQUEST 내 Evaluate 항목 충족)
    final_count = len(final_dataset)
    print("\n==================================================")
    print("📊 [수집 결과 분석 리포트]")
    print("==================================================")
    print(f"총 수집 건수       : {final_count} 건")
    print(f"결측 제목 수       : {missing_title_count} 건")
    print(f"결측 본문 수       : {missing_content_count} 건")
    print("\n[출처(Source)별 수집 성과]")
    for src, cnt in source_stats.items():
        print(f"- {src:<12} : {cnt} 건")
    print("==================================================")

    # 로그 파일에도 최종 보고서 요약 기록
    write_log("--- [최종 통계 수집 리포트] ---", "INFO")
    write_log(f"총 수집 건수       : {final_count} 건", "INFO")
    write_log(f"결측 제목 수       : {missing_title_count} 건", "INFO")
    write_log(f"결측 본문 수       : {missing_content_count} 건", "INFO")
    for src, cnt in source_stats.items():
        write_log(f"- {src:<12} : {cnt} 건", "INFO")

    if final_count >= 200:
        success_msg = "목표한 200건 이상의 데이터 수집에 성공하였습니다!"
        print(f"🎉 [성공] {success_msg}")
        write_log(success_msg, "INFO")
    else:
        warn_msg = "수집 건수가 200건에 도달하지 못했습니다. 대체 소스 추가 검토가 필요합니다."
        print(f"⚠️ [부족] {warn_msg}")
        write_log(warn_msg, "WARNING")
        
    print("==================================================")
    write_log("=== 크롤러 가동 완료 ===", "INFO")


if __name__ == "__main__":
    run_crawler()
