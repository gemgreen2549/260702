import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="주식 분석 & ISA 가입 정보 대시보드", layout="wide")

# 앱 대시보드 대제목
st.title("📊 글로벌·한국 주식 분석 및 ISA 가입 비교 대시보드")
st.markdown("yfinance 실시간 주가 데이터와 국내 주요 증권사별 ISA 트렌드를 한눈에 확인하세요.")

# 탭 구성 (1. 주식 분석, 2. ISA 비교 및 용어사전)
tab1, tab2 = st.tabs(["📈 글로벌 & 한국 주식 데이터 분석", "🏦 증권사별 ISA 비교 및 용어사전"])

# ==========================================
# TAB 1: 주식 데이터 분석 (yfinance + Plotly)
# ==========================================
with tab1:
    st.header("🔍 실시간 주식 데이터 시각화")
    
    # 3구역 레이아웃 (설정창 / 차트 / 요약)
    col_input, col_chart = st.columns([1, 3])
    
    with col_input:
        st.subheader("⚙️ 조회 설정")
        ticker_input = st.text_input("주식 티커를 입력하세요", value="AAPL").strip().upper()
        
        st.markdown("""
        **📌 티커 입력 가이드:**
        - **미국 주식:** `AAPL`(애플), `TSLA`(테슬라)
        - **코스피:** `005930.KS`(삼성전자)
        - **코스닥:** `000660.KS`(SK하이닉스)
        """)
        
        # 날짜 범위 설정
        end_date = datetime.today()
        start_date_default = end_date - timedelta(days=365)
        start_date = st.date_input("시작일 선택", start_date_default, key="start")
        end_date_input = st.date_input("종료일 선택", end_date, key="end")
        
    with col_chart:
        if ticker_input:
            with st.spinner('실시간 데이터를 불러오는 중...'):
                try:
                    # 데이터 로드
                    df = yf.download(ticker_input, start=start_date, end=end_date_input)
                    
                    if df.empty:
                        st.error("데이터를 불러오지 못했습니다. 티커와 날짜를 다시 확인해 주세요.")
                    else:
                        # 주식 기본 데이터 추출을 위한 단순화 처리
                        latest_data = df.iloc[-1]
                        prev_data = df.iloc[-2] if len(df) > 1 else latest_data
                        
                        latest_close = float(latest_data['Close'].item())
                        prev_close = float(prev_data['Close'].item())
                        price_delta = latest_close - prev_close
                        price_delta_percent = (price_delta / prev_close) * 100
                        
                        # 지표 요약 (Metrics)
                        m1, m2, m3 = st.columns(3)
                        m1.metric("최신 종가", f"{latest_close:,.2f}", f"{price_delta:+,.2f} ({price_delta_percent:+.2f}%)")
                        m2.metric("당일 고가", f"{float(latest_data['High'].item()):,.2f}")
                        m3.metric("최신 거래량", f"{int(latest_data['Volume'].item()):,} 주")
                        
                        # 이동평균선(MA) 계산
                        df['MA20'] = df['Close'].rolling(window=20).mean()
                        df['MA60'] = df['Close'].rolling(window=60).mean()
                        
                        # 인터렉티브 캔들스틱 차트 생성
                        fig = go.Figure()
                        fig.add_trace(go.Candlestick(
                            x=df.index,
                            open=df['Open'].squeeze(),
                            high=df['High'].squeeze(),
                            low=df['Low'].squeeze(),
                            close=df['Close'].squeeze(),
                            name="주가 변동"
                        ))
                        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'].squeeze(), mode='lines', name='20일 이평선', line=dict(color='orange', width=1.5)))
                        fig.add_trace(go.Scatter(x=df.index, y=df['MA60'].squeeze(), mode='lines', name='60일 이평선', line=dict(color='blue', width=1.5)))
                        
                        fig.update_layout(
                            template="plotly_white",
                            xaxis_rangeslider_visible=True,
                            margin=dict(l=10, r=10, t=10, b=10),
                            height=500
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 데이터 표 출력
                        st.subheader("📋 최근 10거래일 데이터 표")
                        st.dataframe(df.tail(10).style.format("{:,.2f}"))
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

# ==========================================
# TAB 2: 증권사별 ISA 비교 및 주식 용어 사전
# ==========================================
with tab2:
    st.header("🏦 국내 주요 증권사별 투자중개형 ISA 가입 트렌드")
    st.markdown("""
    최근 ISA 총 가입자 수가 **800만 명**을 돌파하였으며, 자금의 대부분이 개인이 직접 운용하는 **투자중개형 계좌(약 700만 명 돌파)**로 몰리고 있습니다.  
    아래는 시장 점유율 상위를 달리고 있는 주요 증권사별 가입자 규모 추정치와 핵심 특징을 비교한 자료입니다.
    """)
    
    # 가상의 최신 추정 통계 데이터 구성 (실제 금투협 공시 경향 반영)
    isa_data = {
        "증권사": ["미래에셋증권", "한국투자증권", "삼성증권", "KB증권", "NH투자증권", "키움증권"],
        "중개형 가입자 수 (추정)": [1650000, 1350000, 1300000, 1150000, 1050000, 750000],
        "국내주식 거래수수료 혜택": ["평생 우대 (조건 만족시)", "개설 우대 평생 혜택", "신규 평생 혜택", "기본 우대세율 적용", "우대 멤버십 제공", "평생 수수료 우대 제공"],
        "이벤트 및 플랫폼 특징": ["해외주식 절세 마케팅 강점", "대형 채권 라인업 우수", "전용 디지털 자산관리 연계", "KB Pay/금융그룹 혜택 연계", "나무(NAMUH) 전용 간편 UI", "영웅문 앱을 통한 편리한 국내주식 투자"]
    }
    df_isa = pd.DataFrame(isa_data)
    
    # 2-1. 가입자 수 시각화 (Plotly 막대 그래프)
    fig_isa = go.Figure(go.Bar(
        x=df_isa["증권사"],
        y=df_isa["중개형 가입자 수 (추정)"],
        text=df_isa["중개형 가입자 수 (추정)"].apply(lambda x: f"{x/10000:,.0f}만 명"),
        textposition='auto',
        marker_color='#4A90E2'
    ))
    fig_isa.update_layout(
        title="주요 증권사별 투자중개형 ISA 가입자 규모 비교 (추정)",
        template="plotly_white",
        height=400,
        yaxis_title="가입자 수 (명)"
    )
    st.plotly_chart(fig_isa, use_container_width=True)
    
    # 2-2. 상세 비교 표
    st.subheader("📋 증권사별 수수료 및 핵심 특징 상세")
    st.dataframe(df_isa, use_container_width=True)
    
    # 2-3. 친절한 주식 및 ISA 용어 사전
    st.divider()
    st.subheader("💡 초보자를 위한 아주 친절한 금융/주식 용어 사전")
    
    col_word1, col_word2 = st.columns(2)
    with col_word1:
        st.markdown("""
        #### 💰 주식 기본 용어
        * **시가 (Open) & 종가 (Close):** 장이 켜질 때 처음 기록된 주가를 **시가**, 장이 끝날 때 확정된 최종 주가를 **종가**라고 해요.
        * **수정종가 (Adj Close):** 주식 분할이나 배당금을 주주에게 지급하는 등 주식 가치에 변화가 생겼을 때, 이를 반영해 과거 주가까지 다듬어 놓은 실제 가치 중심의 종가예요!
        * **거래량 (Volume):** 하루 동안 사고판 주식의 개수예요. 반도체 신기술 발표 등 큰 이슈가 생기면 거래량이 폭발한답니다.
        * **이동평균선 (MA):** 매일 널뛰는 주가를 일정한 기간(예: 최근 20일) 동안 묶어서 평균 내 연결한 선이에요. 주가가 20일 이동평균선보다 위에 있다면 최근 상승 기류를 타고 있다고 생각하면 쉬워요.
        """)
        
    with col_word2:
        st.markdown("""
        #### 🏦 ISA (개인종합자산관리계좌) 관련 용어
        * **ISA란 무엇인가요?:** 하나의 계좌 안에 주식, ETF, 예적금, 채권 등을 담아 굴리면서 세금을 대폭 아낄 수 있는 **대박 절세 통장**이에요.
        * **투자중개형 ISA:** 과거에는 은행에 맡기거나 정해진 예금만 굴려야 했는데, 투자중개형은 **증권사 계좌**를 통해 투자자가 직접 국내 주식이나 ETF를 사고팔 수 있어서 요즘 인기가 가장 뜨거워요!
        * **비과세 혜택:** 투자해서 얻은 순이익 중에서 법정 한도(일반형 기준 최대 200만 원)까지는 **세금을 1원도 내지 않아도 돼요.** 한도를 넘어선 수익도 일반 세율(15.4%)보다 훨씬 낮은 9.9% 분리과세
