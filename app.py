import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="청소년 인구 데이터 교실", layout="wide")

st.title("🏫 데이터로 보는 대한민국 인구 교실")
st.markdown("""
### "인구 데이터는 미래를 비추는 거울입니다"
단순한 숫자를 넘어, 우리 사회의 과거와 현재, 그리고 **내일의 가능성**을 함께 탐색해 봅시다. 
""")

# 2. 데이터 업로드 및 전처리 기능
@st.cache_data
def load_and_preprocess_data():
    # 제공된 파일명으로 로드 시도 (EUC-KR 인코딩 대응)
    try:
        df = pd.read_csv("202606_202606_연령별인구현황_월간.csv", encoding="euc-kr")
    except:
        df = pd.read_csv("202606_202606_연령별인구현황_월간.csv", encoding="cp949")
        
    # '전국' 행 추출 및 불필요한 공백 제거
    df['행정구역'] = df['행정구역'].astype(str).str.strip()
    national_df = df[df['행정구역'].str.contains('전국', na=False)]
    
    if national_df.empty:
        national_df = df.iloc[[0]] # 없을 경우 첫 행을 전국으로 가정
        
    # 연령별 인구수 컬럼 매핑 (0세부터 100세 이상까지 순서대로 추출)
    age_population = []
    ages = list(range(0, 101))
    
    for age in ages:
        # csv 컬럼명 규칙 탐색 (예: "2026년06월_계_0세" 또는 "0세")
        col_candidates = [c for c in df.columns if f"_{age}세" in c or c == f"{age}세"]
        if col_candidates:
            val = national_df[col_candidates[0]].values[0]
            # 천단위 콤마 제거 후 정수 변환
            if isinstance(val, str):
                val = int(val.replace(',', ''))
            age_population.append(int(val))
        else:
            age_population.append(0)
            
    return pd.DataFrame({"연령": ages, "인구수": age_population})

try:
    data = load_and_preprocess_data()
    data_loaded = True
except Exception as e:
    st.error(f"❌ 데이터를 로드하는 중 오류가 발생했습니다. 파일명을 확인해 주세요: {e}")
    data_loaded = False

# 데이터가 정상 로드되었을 때만 대시보드 표출
if data_loaded:
    # 3. 데이터 분석 파트
    # 최근 영유아 데이터 추출 (0세~4세)
    infants = data[data['연령'] <= 4].copy()
    
    # 💡 [교육 가이드] 인사이트 도출 및 개념 설명
    st.sidebar.header("💡 인구학 전문가의 핵심 레슨")
    
    with st.sidebar.expander("✨ 0세 인구 증가의 비밀 (출생 반등)", expanded=True):
        st.markdown("""
        **Q. 최근 0세 인구가 왜 이전 세대보다 많아졌을까요?**
        
        2020년대 초반 극심한 저출생 기저효과 이후, 최근 결혼 건수의 회복과 맞물려 **초기 영유아(0세) 구간에서 미세하지만 뚜렷한 반등 흐름**이 관찰됩니다! 
        
        이 표시는 단순히 숫자가 증가한 것을 넘어, 우리 사회의 지속 가능성에 청신호가 켜지고 있음을 의미하는 매우 귀중한 **'인구학적 터닝포인트'** 후보군입니다.
        """)

    with st.sidebar.expander("📊 인구 피라미드로 미래 예측하기", expanded=False):
        st.markdown("""
        * **종형(Bell-shaped):** 출생률과 사망률이 모두 낮아 인구가 안정적인 구조예요.
        * **역피라미드형:** 젊은 층이 줄고 노년층이 늘어나는 구조로, 현재 대한민국이 겪고 있는 고령화 문제를 직관적으로 보여줍니다.
        """)

    # 메인 화면 레이아웃 분할
    tab1, tab2 = st.tabs(["📉 영유아 트렌드 & 출생 반등", "🏺 대한민국 연령별 인구 피라미드"])
    
    # ----------------------------------------------------
    # TAB 1: 영유아 트렌드 및 출생 반등 분석
    # ----------------------------------------------------
    with tab1:
        st.subheader("👶 최근 출생 흐름과 영유아 인구 분석")
        st.write("0세부터 4세까지의 데이터를 정밀 비교하여 최근 '출생 반등'의 실체적 흐름을 추적합니다.")
        
        # Plotly 막대 그래프 (0~4세)
        fig_infants = px.bar(
            infants, 
            x="연령", 
            y="인구수",
            text="인구수",
            title="연령별 영유아 인구수 현황 (0세~4세)",
            labels={"인구수": "인구수 (명)", "연령": "연령 (세)"},
            color="인구수",
            color_continuous_scale="Purples"
        )
        fig_infants.update_traces(texttemplate='%{text}:,', textposition='outside')
        fig_infants.update_layout(template="plotly_white", height=450)
        st.plotly_chart(fig_infants, use_container_width=True)
        
        # 심층 교육 노트
        st.info("""
        🔬 **전문가 데이터 문해력 노트:**
        위 그래프에서 **0세 인구의 막대**와 **1세~2세 인구의 막대** 높이를 정밀하게 비교해 보세요. 
        만약 0세 인구가 1~2세 인구보다 높거나 균형을 이루고 있다면, 과거 지속적으로 하향 곡선을 그리던 출생 지표가 **브레이크를 밟고 반등하기 시작했다는 강력한 증거**가 됩니다!
        """)

    # ----------------------------------------------------
    # TAB 2: 전체 인구 구조 분석
    # ----------------------------------------------------
    with tab2:
        st.subheader("🏺 연령별 전체 인구 분포 차트")
        st.write("0세부터 100세 이상까지의 연속적인 흐름을 통해 우리 사회에서 가장 두터운 허리 계층이 어디인지 탐색합니다.")
        
        # Plotly 라인 및 영역 차트
        fig_all = go.Figure()
        fig_all.add_trace(go.Scatter(
            x=data["연령"], 
            y=data["인구수"], 
            mode='lines',
            name='인구수',
            line=dict(color='#2ECC71', width=3),
            fill='tozeroy',
            fillcolor='rgba(46, 204, 113, 0.2)'
        ))
        
        fig_all.update_layout(
            title="대한민국 연령별 전체 인구 분포 (전국 기준)",
            xaxis_title="연령 (세)",
            yaxis_title="인구수 (명)",
            template="plotly_white",
            height=500,
            hovermode="x unified"
        )
        st.plotly_chart(fig_all, use_container_width=True)
        
        # 청소년 토론 과제 제공
        st.markdown("""
        ### 👨‍🏫 함께 생각해 볼 워크숍 과제
        1. **가장 높은 봉우리:** 그래프에서 가장 높게 솟아오른 연령대는 몇 세 구간인가요? 이들이 바로 대한민국의 경제 활동을 지탱하는 핵심 축이자 부모 세대입니다.
        2. **인구 절벽 체감:** 연령이 낮아질수록 그래프가 급격하게 계곡처럼 깎여 내려가는 모습을 관찰할 수 있습니다. 이를 '인구 절벽' 현상이라고 부릅니다.
        """)

else:
    st.warning("⚠️ 대시보드를 구동하기 위해 사이드바 혹은 동일 디렉토리에 정확한 명칭의 인구 통계 CSV 파일이 위치해야 합니다.")
