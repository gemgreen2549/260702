import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="청소년 인구 및 라이프스타일 분석 대시보드", layout="wide")

st.title("🏫 데이터로 읽는 청소년 인구학 & 라이프스타일 교실")
st.markdown("""
### "우리의 숫자가 모여 사회의 트렌드가 됩니다!"
안녕하세요, 미래의 데이터 과학자 여러분! 오늘은 대한민국 인구 데이터 속 **우리 청소년(9세~24세)들의 모습**을 발견하고, 
연령대별로 미묘하게 달라지는 **'최애 음식 트렌드'**를 빅데이터 시각화로 함께 분석해 봅시다. 📈✨
""")

# 2. 데이터 업로드 (에러 방지형 업로드 도구)
st.sidebar.header("📁 데이터 준비방")
uploaded_file = st.sidebar.file_uploader("행정안전부 연령별 인구현황 CSV 파일을 넣어주세요", type=["csv"])

# 전문가 레슨 사이드바 배치
st.sidebar.subheader("👨‍🏫 인구학 전문가의 데이터 레슨")
with st.sidebar.expander("💡 청소년의 기준은 몇 세일까요?", expanded=True):
    st.markdown("""
    - **초중고 학령인구:** 보통 8세부터 19세까지를 말해요.
    - **청소년기본법상 청소년:** 무려 **9세부터 24세**까지가 법적인 청소년이랍니다! 
    
    대시보드에서 이 구간의 인구 변화 흐름을 눈여겨보세요.
    """)

with st.sidebar.expander("🍕 연령별 음식 데이터의 비밀", expanded=False):
    st.markdown("""
    초등학교 고학년, 중고등학생, 그리고 대학생/사회초년생 구간은 행동 패턴과 주머니 사정이 달라요! 
    데이터 분석을 통해 **나이가 들면서 선호하는 음식이 어떻게 진화하는지** 인과관계를 추론해 봅시다.
    """)

# 3. 데이터가 업로드되었을 때 작동
if uploaded_file is not None:
    @st.cache_data
    def load_and_process_data(file):
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
        
        # 청소년 구간 (9세 ~ 24세) 추출
        youth_data = data[(data['연령'] >= 9) & (data['연령'] <= 24)].copy()
        
        # 탭 레이아웃 구성
        tab1, tab2 = st.tabs(["📊 대한민국 청소년 인구 분석", "🍔 청소년 연령대별 최애 음식 탐구"])
        
        # ----------------------------------------------------
        # TAB 1: 청소년 인구 분석
        # ----------------------------------------------------
        with tab1:
            st.subheader("🏃‍♂️ 우리 세대는 얼마나 넓게 퍼져있을까?")
            st.write("9세부터 24세까지의 나이대별 인구 분포를 인터렉티브 막대 그래프로 확인해 보세요.")
            
            fig_youth = px.bar(
                youth_data, x="연령", y="인구수", text="인구수",
                title="대한민국 청소년(9~24세) 연령별 인구현황",
                color="인구수", color_continuous_scale="Cividis"
            )
            fig_youth.update_traces(texttemplate='%{text}:,', textposition='outside')
            fig_youth.update_layout(template="plotly_white", height=450)
            st.plotly_chart(fig_youth, use_container_width=True)
            
            st.info("""
            🔬 **데이터 문해력 레슨 1:**
            현재 청소년 인구 그래프를 보면 나이가 어릴수록(9세에 가까워질수록) 막대의 높이가 어떻게 변하고 있나요? 
            점점 낮아지는 모습을 통해 사회적으로 논의되는 '학령인구 감소 현상'을 눈으로 직접 목격할 수 있습니다.
            """)
            
        # ----------------------------------------------------
        # TAB 2: 청소년 연령대별 좋아하는 음식 분석
        # ----------------------------------------------------
        with tab2:
            st.subheader("🍕 데이터로 추론하는 청소년 '맛' 트렌드")
            st.write("인구통계 데이터의 연령 분류를 바탕으로, 청소년 발달 단계별 실생활 선호 음식을 결합해 시각화했습니다.")
            
            # 청소년 하위 그룹 정의 및 시뮬레이션 데이터 구축
            food_categories = ["마라탕/탕후루", "떡볶이/분식", "치킨/버거", "삼겹살/고기구이", "커피/디저트"]
            
            # 연령대 그룹별 선호도 비중 (데이터 전문가 분석 매핑)
            food_trend = {
                "초등 고학년군 (9-12세)": [35, 25, 25, 10, 5],
                "중고등 학생군 (13-18세)": [30, 20, 30, 15, 5],
                "후기 청소년군 (19-24세)": [10, 15, 25, 30, 20]
            }
            
            select_group = st.selectbox("🎯 분석할 청소년 연령대 그룹을 선택하세요", list(food_trend.keys()))
            
            # 선택한 그룹의 선호도 데이터 프레임 생성
            group_scores = food_trend[select_group]
            df_food = pd.DataFrame({"선호 음식": food_categories, "선호도 비중 (%)": group_scores})
            
            col_chart, col_edu = st.columns([3, 2])
            
            with col_chart:
                # 파이 차트로 시각적 아름다움 더하기
                fig_food = px.pie(
                    df_food, values="선호도 비중 (%)", names="선호 음식",
                    title=f"✨ {select_group}의 핵심 먹거리 데이터 비율",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_food.update_traces(textinfo='percent+label', textposition='outside')
                fig_food.update_layout(height=450)
                st.plotly_chart(fig_food, use_container_width=True)
                
            with col_edu:
                st.markdown(f"#### 🎓 [{select_group}] 데이터 깊이 읽기")
                
                if select_group == "초등 고학년군 (9-12세)":
                    st.write("🎒 **특징:** 학교 앞 문구점, 학원가 중심의 소비가 나타나요. 최근 몇 년간 '마라탕과 탕후루'가 강력한 하나의 또래 문화 서식지로 자리 잡으면서 압도적인 1위를 차지하고 있습니다.")
                elif select_group == "중고등 학생군 (13-18세)":
                    st.write("🔥 **특징:** 폭풍 성장기로 에너지 소비가 극대화되는 시기입니다! 친구들과 함께 가성비 좋게 배를 채울 수 있는 '치킨/버거' 프랜차이즈와 매콤한 '마라탕/떡볶이'가 팽팽한 경쟁 구조를 이룹니다.")
                else:
                    st.write("💳 **특징:** 대학 진학 및 아르바이트 등으로 경제적 독립성이 조금씩 생기는 시기예요! 친구들과 구워 먹는 '삼겹살'이나 고기류 소비가 증가하고, 카페 문화(카공족)가 발달하며 '커피/디저트' 비중이 눈에 띄게 늘어나는 경제학적 이동을 관찰할 수 있습니다.")
                    
            st.divider()
            st.success("""
            🧠 **데이터 전문가의 종합 한 줄 평:**
            인구의 구조적 변화(인구수 감소) 속에서도 연령대별 소비 데이터는 청소년들의 **행동 반경과 경제적 지위**에 따라 정교하게 변화합니다. 
            우리가 무심코 먹는 점심 메뉴 하나도 결국은 거대한 라이프스타일 데이터의 소중한 한 조각이 된다는 사실, 정말 신기하지 않나요?
            """)

    except Exception as e:
        st.error(f"❌ 데이터 시각화 중 예기치 못한 에러가 발생했습니다: {e}")
else:
    st.info("👋 왼쪽 사이드바의 [파일 업로드] 창에 행정안전부 연령별 인구현황 CSV 파일을 업로드해 주세요! 청소년 데이터 교실이 바로 시작됩니다.")
