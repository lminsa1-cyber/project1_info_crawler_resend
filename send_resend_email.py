import os
import csv
import sys
import datetime
from dotenv import load_dotenv

# Windows 콘솔 한글 인코딩 지원 설정
sys.stdout.reconfigure(encoding='utf-8')

# 1. 환경설정 (.env) 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE)

# 2. 파일 및 로그 경로 설정
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
HTML_FILE = os.path.join(REPORTS_DIR, "email_preview.html")
TXT_FILE = os.path.join(REPORTS_DIR, "email_preview.txt")
SEND_LOG_FILE = os.path.join(REPORTS_DIR, "resend_send_log.csv")

# 3. 환경 변수 추출
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "").strip()
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "").strip()
ENABLE_REAL_SEND_STR = os.getenv("ENABLE_REAL_EMAIL_SEND", "false").strip().lower()

# 실제 메일 전송 작동 여부 판별
ENABLE_REAL_SEND = (ENABLE_REAL_SEND_STR == "true")


def check_duplicate(receiver, subject):
    """
    중복 발송 방지를 위해 같은 날짜(오늘), 같은 제목, 같은 수신자에게 이미 발송 성공한 기록이 있는지 검사합니다.
    """
    if not os.path.exists(SEND_LOG_FILE):
        return False
        
    try:
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        with open(SEND_LOG_FILE, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sent_at = row.get("sent_at", "")
                row_receiver = row.get("receiver_email", "")
                row_subject = row.get("subject", "")
                row_status = row.get("status", "")
                
                # 오늘 날짜로 시작하고, 수신자와 제목이 일치하고, 발송 상태가 SUCCESS인 경우 중복 처리
                if (sent_at.startswith(today_str) 
                        and row_receiver == receiver 
                        and row_subject == subject 
                        and row_status == "SUCCESS"):
                    return True
    except Exception as e:
        print(f"⚠️ [경고] 중복 발송 이력 검사 중 오류 발생 (무시하고 계속): {e}")
    return False


def log_send_history_success(receiver, subject, email_id):
    """
    발송 성공 시 reports/resend_send_log.csv 에
    sent_at, receiver_email, subject, status, resend_email_id 를 기록합니다.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    headers = ["sent_at", "receiver_email", "subject", "status", "resend_email_id"]
    file_exists = os.path.exists(SEND_LOG_FILE)
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {
        "sent_at": now_str,
        "receiver_email": receiver,
        "subject": subject,
        "status": "SUCCESS",
        "resend_email_id": email_id
    }
    
    try:
        with open(SEND_LOG_FILE, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        print(f"⚠️ [경고] 발송 이력 로그를 저장하지 못했습니다: {e}")


def log_send_error(receiver, subject, error_msg):
    """
    실패 시 logs/resend_error_log.txt 에 오류를 기록합니다.
    """
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    error_log_file = os.path.join(log_dir, "resend_error_log.txt")
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(error_log_file, mode="a", encoding="utf-8") as f:
            f.write(f"[{now_str}] [ERROR] 수신자: {receiver} | 제목: {subject} | 오류 내용: {error_msg}\n")
    except Exception as e:
        print(f"⚠️ [경고] 에러 로그 파일 저장 중 오류 발생: {e}")


def run_sender():
    print("==================================================")
    print("✉️ Resend 이메일 발송 자동화 엔진")
    print("==================================================")

    # 1. 미리보기 파일 검증 및 동적 생성 처리
    if not os.path.exists(HTML_FILE) or not os.path.exists(TXT_FILE):
        print("💡 [안내] 이메일 미리보기 파일이 존재하지 않아 자동으로 생성해 줍니다...")
        try:
            from email_report_builder import run_report_builder
            run_report_builder()
        except Exception as e:
            print(f"❌ [에러] 이메일 미리보기 파일 자동 빌드 중 에러 발생: {e}")
            return

    # 2. 내용 읽기
    try:
        with open(HTML_FILE, mode="r", encoding="utf-8") as f:
            html_content = f.read()
        with open(TXT_FILE, mode="r", encoding="utf-8") as f:
            text_content = f.read()
    except Exception as e:
        print(f"❌ [에러] 미리보기 파일 로드 중 치명적 오류 발생: {e}")
        return

    subject_title = f"[AI & Tech 리포트] {datetime.date.today().strftime('%Y-%m-%d')} 핵심 IT 뉴스 20선"

    # 3. 중복 발송 여부 검사 (Context 조건 충족)
    if check_duplicate(RECEIVER_EMAIL, subject_title):
        print("==================================================")
        print("⚠️ [발송 중단] 중복 발송 방지 가드가 작동했습니다.")
        print("==================================================")
        print(f"이미 오늘({datetime.date.today().strftime('%Y-%m-%d')}) 같은 수신자({RECEIVER_EMAIL})에게")
        print(f"동일한 제목('{subject_title}')으로 발송된 성공 이력이 존재합니다.")
        print("네트워크 자원 및 크레딧 낭비를 막기 위해 전송을 생략합니다.")
        print("==================================================")
        return

    # 4. 실발송 조건 안전성 체크 (유효성 검증)
    is_valid_api_key = (
        RESEND_API_KEY 
        and RESEND_API_KEY != "your_resend_api_key_here" 
        and RESEND_API_KEY.startswith("re_")
    )
    is_valid_emails = (
        SENDER_EMAIL 
        and "@" in SENDER_EMAIL
        and RECEIVER_EMAIL 
        and "@" in RECEIVER_EMAIL
        and RECEIVER_EMAIL != "student@example.com"
    )
    
    # 5. 시뮬레이션 모드 (Preview Mode) 작동 조건
    if not ENABLE_REAL_SEND or not is_valid_api_key or not is_valid_emails:
        print("\n🔎 [시뮬레이션 모드 - Preview Mode 작동 중]")
        print("--------------------------------------------------")
        print("※ 이 모드에서는 실제 이메일 전송이 발생하지 않습니다.")
        print("--------------------------------------------------")
        print(f"▶ 발송 예정 제목 : {subject_title}")
        print(f"▶ 발송 예정자    : {SENDER_EMAIL if SENDER_EMAIL else '(미지정)'}")
        print(f"▶ 수신 예정자    : {RECEIVER_EMAIL if RECEIVER_EMAIL else '(미지정)'}")
        print(f"▶ 본문 HTML 크기: {len(html_content)} bytes")
        print(f"▶ 본문 Text 크기: {len(text_content)} bytes")
        print("--------------------------------------------------")
        print("💡 [실제 메일 발송으로 전환하는 가이드라인]")
        print("  1. project1_info_crawler_resend/ 폴더 안에 '.env' 파일을 생성합니다.")
        print("  2. '.env.example' 파일을 열어 내용을 그대로 복사해 넣습니다.")
        print("  3. RESEND_API_KEY 란에 실제 Resend에서 발급받은 개인 API 키를 입력합니다.")
        print("  4. SENDER_EMAIL 은 'onboarding@resend.dev'를 그대로 두거나 인증된 도메인을 입력합니다.")
        print("  5. RECEIVER_EMAIL 은 반드시 수강생 본인의 '실제 이메일 주소'를 입력해야 합니다.")
        print("     (onboarding@resend.dev 발송자는 오직 본인 인증 이메일로만 전송을 허용합니다.)")
        print("  6. ENABLE_REAL_EMAIL_SEND=true 로 변경합니다.")
        print("  7. 이 스크립트(send_resend_email.py)를 다시 구동해 주세요.")
        print("--------------------------------------------------")
        return

    # 6. 실제 메일 발송 작동 (Real Dispatch)
    import resend
    
    print("\n🚀 [실제 메일 발송 모드 가동]")
    print(f"- 발송자: {SENDER_EMAIL}")
    print(f"- 수신자: {RECEIVER_EMAIL}")
    print("Resend 서버와 연결 중... 잠시만 기다려주세요...\n")
    
    try:
        # Resend SDK 설정
        resend.api_key = RESEND_API_KEY
        
        # 메일 발송 파라미터 구성
        params = {
            "from": SENDER_EMAIL,
            "to": [RECEIVER_EMAIL],
            "subject": subject_title,
            "html": html_content,
            "text": text_content
        }
        
        # 메일 발송 요청
        response = resend.Emails.send(params)
        
        email_id = response.get("id", "N/A")
        print("==================================================")
        print("🎉 [발송 성공] 메일이 정상적으로 발송되었습니다!")
        print("==================================================")
        print(f"발송 이메일 ID : {email_id}")
        print(f"발송 일시      : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("==================================================")
        
        # 발송 이력 보관 (Reference 사양 충족)
        log_send_history_success(RECEIVER_EMAIL, subject_title, email_id)
        
    except Exception as e:
        err_str = str(e)
        print("==================================================")
        print(f"❌ [발송 실패] Resend API 연동 에러 발생")
        print("==================================================")
        print(f"상세 에러 내용: {err_str}")
        print("==================================================")
        
        # 에러 로그 기록 (Evaluate 사양 충족)
        log_send_error(RECEIVER_EMAIL, subject_title, err_str)
        
        # 403 오류 처리 및 해결 방법 안내 (Iterate 사양 충족)
        if "403" in err_str or "forbidden" in err_str.lower():
            print("\n💡 [403 Forbidden 권한 오류 해결 가이드]")
            print("--------------------------------------------------")
            print("이 오류는 주로 '발신 도메인 검증 및 수신 제한'으로 발생합니다:")
            print("1. 발신 주소가 'onboarding@resend.dev'인 경우:")
            print("   - 오직 Resend 가입에 사용하신 본인의 '실제 가입/로그인용 이메일 주소'로만 메일을 보낼 수 있습니다.")
            print("   - 수신자 이메일(RECEIVER_EMAIL)에 수강생 본인의 Resend 계정 이메일을 입력했는지 꼭 확인해 주세요.")
            print("2. 개인 소유 도메인(예: tech@yourdomain.com)으로 보내는 경우:")
            print("   - Resend 웹 콘솔(https://resend.com/domains)에 해당 도메인이 등록 완료되었는지 확인해 주세요.")
            print("   - 네임서버에 TXT/MX 레코드 설정이 적용되어 'Verified(인증 완료)' 상태인지 체크해 주시기 바랍니다.")
            print("--------------------------------------------------\n")


if __name__ == "__main__":
    run_sender()
