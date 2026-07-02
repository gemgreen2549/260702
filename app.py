import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 기본 설정 및 스타일
st.set_page_config(page_title="청소년 인구 데이터 교실", layout="wide")

st.title("🏫 데이터로 보는 대한민국 인구 교실")
st.markdown("""
### "인구 데이터는 미래를 비추는 거울입니다"
단순한 숫자를 넘어, 우리 사회의 과거와 현재, 그리고 **내일의 가능성**을 함께 탐색해 봅시다. 
""")

# 사이드바에서 파일 직접 업로드 받기
st.sidebar.header("📁 데이터 파일 업로드")
uploaded_file = st.sidebar.file_uploader("행정안전부 연령별 인구현황 CSV 파일을 올려주세요", type=["csv"])

# 💡 [교육 가이드] 인사이트 도출 및 개념 설명
st.sidebar.subheader("💡 인구학 전문가의 핵심 레슨")

with st.sidebar.expander("✨ 0세 인구 증가의 비밀 (출생 반등)", expanded=True):
    st.markdown("""
    **Q. 최근 0세 인구가 왜 이전 세대보다 많아졌을까요?**
    
    2020년대 초반 극심한 저출생 기저효과 이후, 최근 결혼 건수의 회복과 맞물려 **초기 영유아(0세) 구간에서 미세하지만 뚜렷한 반등 흐름**이 관찰됩니다! 
    
    이 표시는 단순히 숫자가 증가한 것을 넘어, 우리 사회의 지속 가능성에 청신호가 켜지고 있음을 의미하는 매우 귀중한 **'인구학적 터닝포인트'** 후보군입니다.
    """)

# 데이터 처리 로직
if uploaded_file is not None:
    @st.cache_data
    def load_and_preprocess_data(file):
        try:
            df = pd.read_csv(file, encoding="euc-kr")
        except:
            df = pd.read_csv(file, encoding="cp949")
            
        df['행정구역'] = df['행정구역'].astype(str).str.strip()
        national_df = df[df['행정구역'].str.contains('전국', na=False)]
        
        if national_df.empty:
            national_df = df.iloc[[0]]
            
        age_population = []
        ages = list(range(0, 101))
        
        for age in ages:
            col_candidates = [c for c in df.columns if f"_{age}세" in c or c == f"{age}세"]
            if col_candidates:
                val = national_df[col_candidates[0]].values[0]
                if isinstance(val, str):
                    val = int(val.replace(',', ''))
                age_population.append(int(val))
            else:
                age_population.append(0)
                
        return pd.DataFrame({"연령": ages, "인구수": age_population})

    try:
        data = load_and_preprocess_data(uploaded_file)
        
        infants = data[data['연령'] <= 4].copy()
        
        tab1, tab2 = st.tabs(["📉 영유아 트렌드 & 출생 반등", "🏺 대한민국 연령별 인구 피라미드"])
        
        # TAB 1: 영유아
        with tab1:
            st.subheader("👶 최근 출생 흐름과 영유아 인구 분석")
            fig_infants = px.bar(
                infants, x="연령", y="인구수", text="인구수",
                title="연령별 영유아 인구수 현황 (0세~4세)",
                color="인구수", color_continuous_scale="Purples"
            )
            fig_infants.update_traces(texttemplate='%{text}:,', textposition='outside')
            fig_infants.update_layout(template="plotly_white", height=450)
            st.plotly_chart(fig_infants, use_container_width=True)
            
            st.info("""
            🔬 **전문가 데이터 문해력 노트:**
            위 그래프에서 **0세 인구의 막대**와 **1세~2세 인구의 막대** 높이를 정밀하게 비교해 보세요. 
            만약 0세 인구가 1~2세 인구보다 높거나 균형을 이루고 있다면, 과거 지속적으로 하향 곡선을 그리던 출생 지표가 **브레이크를 밟고 반등하기 시작했다는 강력한 증거**가 됩니다!
            """)

        # TAB 2: 전체 인구
        with tab2:
            st.subheader("🏺 연령별 전체 인구 분포 차트")
            fig_all = go.Figure()
            fig_all.add_trace(go.Scatter(
                x=data["연령"], y=data["인구수"], mode='lines', name='인구수',
                line=dict(color='#2ECC71', width=3), fill='tozeroy', fillcolor='rgba(46, 204, 113, 0.2)'
            ))
            fig_all.update_layout(
                title="대한민국 연령별 전체 인구 분포 (전국 기준)",
                xaxis_title="연령 (세)", yaxis_title="인구수 (명)",
                template="plotly_white", height=500, hovermode="x unified"
            )
            st.plotly_chart(fig_all, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ 데이터를 처리하는 중 오류가 발생했습니다: {e}")
else:
    st.info("👋 왼쪽 사이드바에서 인구 데이터 CSV 파일을 업로드해 주시면 대시보드가 멋지게 시각화됩니다!")
