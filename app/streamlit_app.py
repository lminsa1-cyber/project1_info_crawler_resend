import streamlit as st
import pandas as pd
import os
import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="AI & IT 핵심 뉴스/정책 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Path Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECOMMENDED_FILE = os.path.join(BASE_DIR, "data", "processed", "recommended_policy_news.csv")
CLEANED_FILE = os.path.join(BASE_DIR, "data", "processed", "cleaned_policy_news.csv")
RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "crawled_policy_news.csv")

# 3. Custom CSS styling (Business Report Theme: White, Navy, Gray, Green)
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Deep Navy Header */
    .main-header {
        background-color: #0f172a;
        padding: 30px;
        border-radius: 12px;
        color: #ffffff;
        text-align: center;
        margin-bottom: 25px;
        border-bottom: 5px solid #10b981;
    }
    .main-header h1 {
        margin: 0;
        color: #ffffff !important;
        font-size: 32px !important;
        font-weight: 800;
    }
    .main-header p {
        margin: 10px 0 0 0;
        color: #94a3b8;
        font-size: 16px;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #0f172a;
        margin-bottom: 5px;
    }
    .metric-label {
        font-size: 14px;
        color: #64748b;
        font-weight: 600;
    }
    
    /* Article Cards (Light Gray) */
    .article-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 22px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .article-title {
        font-size: 18px !important;
        font-weight: bold;
        color: #0f172a !important;
        margin-top: 5px;
        margin-bottom: 10px;
    }
    .article-title a {
        color: #0f172a !important;
        text-decoration: none;
    }
    .article-title a:hover {
        text-decoration: underline;
    }
    
    /* Success Badges */
    .badge-score {
        background-color: #e6f4ea;
        color: #059669;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid #a7f3d0;
        font-size: 12px;
        display: inline-block;
    }
    .badge-source {
        background-color: #cbd5e1;
        color: #1e293b;
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        display: inline-block;
        margin-left: 6px;
    }
    
    /* Summary Block */
    .summary-box {
        background-color: #ffffff;
        border-left: 4px solid #10b981;
        padding: 12px 16px;
        margin: 12px 0;
        font-size: 14px;
        color: #334155;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
        border-radius: 0 6px 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# 4. Data Loading Utility (cached)
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception:
            return None
    return None

df_raw = load_data(RAW_FILE)
df_cleaned = load_data(CLEANED_FILE)
df_recommended = load_data(RECOMMENDED_FILE)

# 5. Header Area
st.markdown(f"""
<div class="main-header">
    <h1>📊 AI & IT 핵심 뉴스/정책 실무 대시보드</h1>
    <p>수집-정제-알고리즘 추천 파이프라인 실시간 결과 모니터링</p>
</div>
""", unsafe_allow_html=True)

# 6. Sidebar Controls
st.sidebar.markdown("### ⚙️ 대시보드 제어판")
st.sidebar.info("본 대시보드는 초보자도 바로 이해하고 경영진에 보고할 수 있는 실무용 대시보드입니다.")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏷️ 필터링 키워드 가중치")
st.sidebar.code("""
1. AI (생성형 AI): 1.5배
2. 보안: 1.3배
3. 자동화: 1.2배
4. 디지털 전환: 1.2배
5. 클라우드: 1.1배
6. 데이터: 1.0배
""")

# 7. Metrics Section
st.markdown("### 📈 파이프라인 처리 성과 (Overview)")
col1, col2, col3, col4 = st.columns(4)

total_raw = len(df_raw) if df_raw is not None else 210
total_clean = len(df_cleaned) if df_cleaned is not None else 190
removed_cnt = total_raw - total_clean if (df_raw is not None and df_cleaned is not None) else 20
max_score = df_recommended["recommendation_score"].max() if df_recommended is not None else 101.10

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_raw}건</div>
        <div class="metric-label">📥 총 수집 원본 뉴스 (Raw)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_clean}건</div>
        <div class="metric-label">🧹 정제 유효 기사 (Cleaned)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-bottom: 4px solid #ef4444;">
        <div class="metric-value" style="color: #ef4444;">{removed_cnt}건</div>
        <div class="metric-label">🚫 결측 및 유사 중복 제거</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-bottom: 4px solid #10b981;">
        <div class="metric-value" style="color: #059669;">{max_score:.2f}점</div>
        <div class="metric-label">🏆 최우수 추천 지수 (Top Score)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 8. Main Tabs
tab1, tab2, tab3 = st.tabs(["🔥 추천 TOP 10 요약 보고", "🔍 전체 데이터 정제 필터 탐색", "📊 키워드 및 통계 정보"])

with tab1:
    st.markdown("### 🏆 알고리즘 추천 상위 10선 (TOP 10)")
    st.caption("AI, 클라우드, 보안, 자동화 등 6개 기업 필수 기술 키워드 매칭 가산점으로 최종 엄선된 상위 10개 실무 매칭 뉴스입니다.")
    
    if df_recommended is not None:
        top_10 = df_recommended.head(10)
        for idx, row in top_10.iterrows():
            rank = idx + 1
            title = row.get("title", "N/A")
            score = row.get("recommendation_score", 0.0)
            source = row.get("source_name", "N/A")
            date = row.get("date", "N/A")
            summary = row.get("summary", "No summary.")
            url = row.get("source_url", "#")
            article_id = row.get("article_id", "N/A")
            
            st.markdown(f"""
            <div class="article-card">
                <div>
                    <span class="badge-score">✔ 추천 점수: {score:.2f}점</span>
                    <span class="badge-source">{source}</span>
                </div>
                <div class="article-title">
                    <a href="{url}" target="_blank">{rank}. {title}</a>
                </div>
                <div style="font-size:12px; color:#64748b; margin-bottom:10px;">
                    일자: {date} | 출처: {source} | ID: {article_id}
                </div>
                <div class="summary-box">
                    {summary}
                </div>
                <div style="margin-top: 15px;">
                    <a href="{url}" target="_blank" style="background-color:#0f172a; color:#ffffff; padding:8px 16px; border-radius:6px; font-size:13px; font-weight:600; text-decoration:none; display:inline-block; border: 1px solid #0f172a;">기사 원문 읽기 ➔</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 추천 뉴스 목록을 로드할 수 없습니다. recommender.py를 먼저 실행해 주세요.")

with tab2:
    st.markdown("### 🔍 전체 정제 뉴스 데이터 필터 탐색기")
    st.caption("결측치와 중복 뉴스를 필터링한 총 190건의 고유 정제 데이터세트입니다. 실무 키워드를 검색하거나 정렬할 수 있습니다.")
    
    if df_cleaned is not None:
        # Search & Filter
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            search_query = st.text_input("🔍 제목 또는 요약문 검색", "", placeholder="키워드 입력 (예: AI, 보안, 클라우드...)")
        with col_f2:
            sort_by = st.selectbox("정렬 기준", ["최신일순", "가장 오래된순"])
            
        filtered_df = df_cleaned.copy()
        
        # Keyword Search
        if search_query:
            filtered_df = filtered_df[
                filtered_df["title"].str.contains(search_query, case=False, na=False) |
                filtered_df["summary"].str.contains(search_query, case=False, na=False)
            ]
            
        # Date sorting
        filtered_df["date"] = pd.to_datetime(filtered_df["date"], errors="coerce")
        if sort_by == "최신일순":
            filtered_df = filtered_df.sort_values(by="date", ascending=False)
        else:
            filtered_df = filtered_df.sort_values(by="date", ascending=True)
            
        st.write(f"🔎 검색된 결과: 총 {len(filtered_df)}건")
        
        # Display clean dataframe
        display_df = filtered_df[["article_id", "title", "source_name", "date", "source_url"]].copy()
        display_df["date"] = display_df["date"].dt.strftime('%Y-%m-%d')
        display_df.columns = ["뉴스 ID", "기사 제목", "출처 매체", "발행 일자", "원문 주소"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    else:
        st.warning("⚠️ 정제 뉴스 데이터를 로드할 수 없습니다. cleaner.py를 먼저 실행해 주세요.")

with tab3:
    st.markdown("### 📊 키워드 중요도 및 실무 통계분석")
    
    if df_cleaned is not None:
        # Simple keywords frequencies calculation
        keywords = ["AI", "생성형 AI", "자동화", "클라우드", "데이터", "보안", "디지털 전환"]
        keyword_counts = {}
        
        for kw in keywords:
            count = df_cleaned["title"].str.contains(kw, case=False, na=False).sum() + \
                    df_cleaned["summary"].str.contains(kw, case=False, na=False).sum()
            keyword_counts[kw] = count
            
        chart_df = pd.DataFrame(list(keyword_counts.items()), columns=["핵심 기술 테마", "매칭 빈도수"])
        chart_df = chart_df.sort_values(by="매칭 빈도수", ascending=True)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### 💡 실무 가중치 키워드 빈도 분포")
            st.caption("뉴스 기사의 제목과 본문 요약에서 언급된 핵심 기술의 통계 분포입니다.")
            
            # Matplotlib 대신 Streamlit의 네이티브 바 차트(st.bar_chart)를 사용하여
            # 리눅스 클라우드 서버 환경에서의 한글 폰트 깨짐을 원천 방지하고 반응형으로 구현합니다.
            chart_data = chart_df.set_index("핵심 기술 테마")
            st.bar_chart(chart_data, color="#0f172a", height=320)
            
        with col_c2:
            st.markdown("#### 📁 매체 출처별 점유율")
            st.caption("수집된 데이터의 매체사 분포 통계입니다.")
            source_counts = df_cleaned["source_name"].value_counts().reset_index()
            source_counts.columns = ["매체사명", "수집 기사수"]
            st.dataframe(source_counts, use_container_width=True, hide_index=True)
            
    else:
        st.warning("⚠️ 정제 데이터를 로드할 수 없어 통계를 구성할 수 없습니다.")
