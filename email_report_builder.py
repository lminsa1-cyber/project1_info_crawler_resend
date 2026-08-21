import os
import csv
import sys
import datetime

# Windows 콘솔 한글 인코딩 지원 설정
sys.stdout.reconfigure(encoding='utf-8')

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "recommended_policy_news.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "reports")
HTML_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "email_preview.html")
TXT_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "email_preview.txt")

# ==============================================================================
# 1. HTML 이메일 템플릿 정의
# ==============================================================================

HTML_HEADER_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI & Tech 뉴스/정책 요약 리포트</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Malgun Gothic', '맑은 고딕', helvetica, sans-serif; background-color: #ffffff; color: #334155;-webkit-font-smoothing: antialiased;">
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 680px; margin: 0 auto; background-color: #ffffff; border-collapse: collapse; border: 1px solid #e2e8f0;">
        <!-- Header Section -->
        <tr>
            <td style="padding: 40px 30px; background-color: #0f172a; text-align: center; border-bottom: 4px solid #10b981;">
                <h1 style="margin: 0 0 10px 0; font-size: 26px; color: #ffffff; font-weight: 800; letter-spacing: -0.5px;">AI & Tech 뉴스/정책 리포트</h1>
                <p style="margin: 0; font-size: 15px; color: #94a3b8; font-weight: 400;">오늘 엄선된 정보통신 분야 핵심 뉴스 및 정책 동향 TOP 10</p>
                <div style="margin-top: 15px; display: inline-block; padding: 5px 12px; background-color: #1e293b; border-radius: 20px; font-size: 12px; color: #10b981; font-weight: 600;">
                    발송일: {report_date} | 수신대상: 수강생 전용
                </div>
            </td>
        </tr>
        <!-- Content Section -->
        <tr>
            <td style="padding: 35px 24px;">
                <p style="margin: 0 0 24px 0; font-size: 15px; line-height: 1.6; color: #334155;">
                    안녕하세요, 수강생님! 수집된 뉴스/정책 데이터 210건 중, **생성형 AI, 데이터, 보안, 클라우드, 자동화, 디지털 전환** 테마 가중치 알고리즘을 거쳐 선별된 최종 **상위 10개(TOP 10)** 핵심 뉴스를 전달해 드립니다.
                </p>
                
                <!-- Articles List Container -->
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
"""

HTML_CARD_TEMPLATE = """
                    <!-- Article Card {rank} -->
                    <tr>
                        <td style="padding: 24px; margin-bottom: 20px; border-radius: 8px; border: 1px solid #e2e8f0; background-color: #f8fafc;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td valign="top">
                                        <!-- Score & Source Badge -->
                                        <div style="margin-bottom: 12px;">
                                            <span style="display: inline-block; padding: 4px 10px; background-color: #e6f4ea; color: #059669; font-size: 12px; font-weight: bold; border-radius: 6px; border: 1px solid #a7f3d0; margin-right: 6px;">
                                                ✔ 추천 점수: {score}점
                                            </span>
                                            <span style="display: inline-block; padding: 4px 8px; background-color: #cbd5e1; color: #1e293b; font-size: 11px; font-weight: 600; border-radius: 4px;">
                                                {source}
                                            </span>
                                        </div>
                                        <!-- Title -->
                                        <h2 style="margin: 0 0 8px 0; font-size: 18px; line-height: 1.4; font-weight: 700;">
                                            <a href="{source_url}" target="_blank" style="color: #0f172a; text-decoration: none; hover: text-decoration: underline;">
                                                {rank}. {title}
                                            </a>
                                        </h2>
                                        <!-- Meta Info -->
                                        <p style="margin: 0 0 12px 0; font-size: 12px; color: #64748b;">
                                            일자: {date} | 출처: {source} | ID: {article_id}
                                        </p>
                                        <!-- Summary -->
                                        <p style="margin: 0 0 16px 0; font-size: 14px; line-height: 1.6; color: #475569; background-color: #ffffff; padding: 12px 16px; border-left: 3px solid #10b981; border-radius: 0 6px 6px 0; border-top: 1px solid #f1f5f9; border-right: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9;">
                                            {summary}
                                        </p>
                                        <!-- Button -->
                                        <table border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td align="center" style="border-radius: 6px;" bgcolor="#0f172a">
                                                    <a href="{source_url}" target="_blank" style="display: inline-block; padding: 8px 16px; font-size: 13px; color: #ffffff; font-weight: 600; text-decoration: none; border-radius: 6px; border: 1px solid #0f172a;">기사 원문 읽기 ➔</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Spacing -->
                    <tr><td style="height: 20px;"></td></tr>
"""

HTML_FOOTER_TEMPLATE = """
                </table>
            </td>
        </tr>
        <!-- Footer Section -->
        <tr>
            <td style="padding: 30px; background-color: #f8fafc; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="margin: 0 0 8px 0; font-size: 12px; color: #64748b; font-weight: bold;">본 메일은 크롤러 자동화 수집 학습 프로젝트의 미리보기 리포트입니다.</p>
                <p style="margin: 0 0 16px 0; font-size: 11px; color: #94a3b8; line-height: 1.5;">본 메일은 수강생이 설계한 필터링 및 추천 규칙 알고리즘으로 자동 생성되었으며, 실제 배포 목적으로 상업적으로 사용되지 않습니다. 수신을 원치 않으시면 아래 링크를 이용해 주세요.</p>
                <table align="center" border="0" cellpadding="0" cellspacing="0">
                    <tr>
                        <td>
                            <a href="#" style="font-size: 11px; color: #0f172a; text-decoration: underline; margin-right: 15px;">수신 거부(Unsubscribe)</a>
                            <a href="#" style="font-size: 11px; color: #0f172a; text-decoration: underline;">개인정보처리방침</a>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

# ==============================================================================
# 2. 텍스트 이메일 템플릿 정의
# ==============================================================================

TXT_HEADER_TEMPLATE = """============================================================
[AI & Tech 뉴스/정책 요약 리포트]
오늘 엄선된 정보통신 분야 핵심 뉴스 및 정책 동향 10선
============================================================
발송일: {report_date} | 수신대상: 수강생 전용

안녕하세요, 수강생님!
수집된 뉴스/정책 데이터 중 엄격한 정제와 추천 가중치 알고리즘을 거친 
오늘의 최우수 정보 상위 10선을 전달해 드립니다.

------------------------------------------------------------
"""

TXT_CARD_TEMPLATE = """
[{rank}등] [추천 점수: {score}점]
▶ 제목: {title}
▶ 출처: {source} (일자: {date})
▶ 요약: {summary}
▶ 원문 링크: {source_url}
------------------------------------------------------------
"""

TXT_FOOTER_TEMPLATE = """
============================================================
본 메일은 크롤러 자동화 수집 학습 프로젝트의 미리보기 리포트입니다.
수강생이 설계한 알고리즘으로 자동 분석되었으며 상업적으로 활용하지 않습니다.
수신을 원하지 않으시면 메일 수신거부 설정을 눌러주시기 바랍니다.
============================================================
"""

# ==============================================================================
# 3. 리포트 동적 생성 엔진
# ==============================================================================

def run_report_builder():
    print("==================================================")
    print("✉️ 이메일 리포트 빌더(Report Builder) 프로세스 시작")
    print("==================================================")
    
    # 1. 파일 검증
    if not os.path.exists(INPUT_FILE):
        print(f"❌ [에러] 추천 결과 파일이 존재하지 않습니다: {INPUT_FILE}")
        print("     추천 가중치 계산(recommender.py)을 먼저 실행해 주세요.")
        return

    # 2. 폴더 구성
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 3. 추천 데이터 로드
    articles = []
    try:
        with open(INPUT_FILE, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            articles = list(reader)
        print(f"로드 완료: 최우수 추천 기사 {len(articles)}건 확보")
    except Exception as e:
        print(f"❌ [에러] 추천 파일 로드 중 오류 발생: {e}")
        return

    # 기사 수량 유연하게 제어 (최대 10건 제한)
    articles_to_render = articles[:10]
    
    # 날짜 세팅 (Windows 로케일 인코딩 우회를 위한 f-string 포맷팅)
    now = datetime.datetime.now()
    current_date_str = f"{now.year}년 {now.month:02d}월 {now.day:02d}일"

    # 4. HTML 미리보기 템플릿 동적 조립
    html_content = HTML_HEADER_TEMPLATE.format(report_date=current_date_str)
    
    for idx, art in enumerate(articles_to_render, 1):
        score_val = float(art.get("recommendation_score", 0.0))
        formatted_score = f"{score_val:.2f}"
        
        card_html = HTML_CARD_TEMPLATE.format(
            rank=idx,
            score=formatted_score,
            source=art.get("source_name", "N/A"),
            title=art.get("title", "No Title"),
            date=art.get("date", "N/A"),
            article_id=art.get("article_id", "N/A"),
            summary=art.get("summary", "No Summary available."),
            source_url=art.get("source_url", "#")
        )
        html_content += card_html
        
    html_content += HTML_FOOTER_TEMPLATE

    # 5. TXT 미리보기 템플릿 동적 조립
    txt_content = TXT_HEADER_TEMPLATE.format(report_date=current_date_str)
    
    for idx, art in enumerate(articles_to_render, 1):
        score_val = float(art.get("recommendation_score", 0.0))
        formatted_score = f"{score_val:.2f}"
        
        card_txt = TXT_CARD_TEMPLATE.format(
            rank=idx,
            score=formatted_score,
            title=art.get("title", "No Title"),
            source=art.get("source_name", "N/A"),
            date=art.get("date", "N/A"),
            summary=art.get("summary", "No Summary available."),
            source_url=art.get("source_url", "#")
        )
        txt_content += card_txt
        
    txt_content += TXT_FOOTER_TEMPLATE

    # 6. HTML 및 TXT 파일 디스크 저장
    try:
        with open(HTML_OUTPUT_FILE, mode="w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"💾 [성공] HTML 이메일 미리보기 파일 생성 완료!")
        print(f"     경로: {HTML_OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ [에러] HTML 파일 저장 실패: {e}")
        return

    try:
        with open(TXT_OUTPUT_FILE, mode="w", encoding="utf-8") as f:
            f.write(txt_content)
        print(f"💾 [성공] 텍스트 이메일 미리보기 파일 생성 완료!")
        print(f"     경로: {TXT_OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ [에러] 텍스트 파일 저장 실패: {e}")
        return

    print("\n==================================================")
    print("🎉 이메일 리포트 미리보기 파일 저장 및 검증 성공!")
    print("==================================================")
    print("아래 링크를 통해 생성된 내용을 즉시 검토하실 수 있습니다:")
    print(f"- [HTML 미리보기](file:///{HTML_OUTPUT_FILE.replace(chr(92), '/')})")
    print(f"- [텍스트 미리보기](file:///{TXT_OUTPUT_FILE.replace(chr(92), '/')})")
    print("==================================================")


if __name__ == "__main__":
    run_report_builder()
