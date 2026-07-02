import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="청소년 인구 및 라이프스타일 분석 대시보드", layout="wide")

st.title("🏫 데이터로 읽는 청소년 인구학 & 라이프스타일 교실")
st.markdown("""
### "우리의 숫자가 모여 사회의 트렌드가 됩니다!"
안녕하세요, 미래의 데이터 과학자 여러분! 오늘은 대한민국 인구 데이터 속 **우리 청소년(9세~24세)들의 모습**을 발견하고, 
연령대별로 미묘하게 달라지는 **'최애 음식 트렌드'**를 빅데이터 시각화로 함께 분석해 봅시다. 📈✨
""")

# 2. 데이터 전처리 함수를 최상단에 안전하게 정의 (NameError 원천 차단!)
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

# 3. 사이드바 레이아웃 구성
st.sidebar.header("📁 데이터 준비방")
uploaded_file = st.sidebar.file_uploader("행정안전부 연령별 인구현황 CSV 파일을 넣어주세요", type=["csv"])

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

# 4. 파일 업로드 상태에 따른 화면 제어
if uploaded_file is not None:
    try:
        # 안전하게 정의된 함수 호출
        data = load_and_preprocess_data(uploaded_file)
        
        # 청소년 구간 (9세 ~ 24세) 추출
        youth_data = data[(data['연령'] >= 9) & (data['연령'] <= 24)].copy()
        
        # 탭 레이아웃 구성
        tab1, tab2 = st.tabs(
