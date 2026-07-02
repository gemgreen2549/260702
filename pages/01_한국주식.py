import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="반도체 주식 데이터 분석기", layout="wide", initial_sidebar_state="expanded")

# 2. 앱 타이틀 및 설명
st.title("🎛️ 글로벌 & 한국 반도체 주식 분석 웹앱")
st.markdown("yfinance와 Plotly를 이용한 반도체 핵심 기업들의 실시간 주가 분석 및 인터렉티브 시각화 도구입니다.")

# 3. 사이드바 - 주요 반도체 기업 프리셋 설정
st.sidebar.header("⚙️ 주식 선택 및 설정")

# 대표적인 반도체 기업 리스트 (이름: 티커)
semiconductor_presets = {
    "엔비디아 (NVIDIA - NVDA)": "NVDA",
    "삼성전자 (Samsung - 005930.KS)": "005930.KS",
    "SK하이닉스 (SK hynix - 000660.KS)": "000660.KS",
    "TSMC (TSM)": "TSM",
    "AMD (Advanced Micro Devices)": "AMD",
    "인텔 (Intel - INTC)": "INTC",
    "ASML (ASML Holding)": "ASML",
    "브로드컴 (Broadcom - AVGO)": "AVGO"
}

# 사용자 선택 방식 (프리셋 선택 또는 직접 입력)
search_mode = st.sidebar.radio("검색 방식 선택", ["주요 반도체 기업 선택", "티커 직접 입력"])

if search_mode == "주요 반도체 기업 선택":
    selected_name = st.sidebar.selectbox("기업을 선택하세요", list(semiconductor_presets.keys()))
    ticker = semiconductor_presets[selected_name]
else:
    ticker = st.sidebar.text_input("티커(Ticker)를 직접 입력하세요", value="NVDA").strip().upper()
    st.sidebar.markdown("""
    **💡 한국 주식 입력 팁:**
    * 코스피: 종목코드 뒤에 `.KS` (예: `005930.KS`)
    * 코스닥: 종목코드 뒤에 `.KQ` (예: `247540.KQ`)
    """)

# 4. 날짜 및 조회 기간 설정
st.sidebar.subheader("📅 조회 기간 설정")
period_mode = st.sidebar.selectbox("기간 설정 방식", ["최근 기간 선택", "날짜 직접 지정"])

end_date = datetime.today()
if period_mode == "최근 기간 선택":
    duration = st.sidebar.selectbox("조회 기간", ["1개월", "3개월", "6개월", "1년", "3년", "5년"], index=3)
    days_dict = {"1개월": 30, "3개월": 90, "6개월": 180, "1년": 365, "3년": 365*3, "5년": 365*5}
    start_date = end_date - timedelta(days=days_dict[duration])
else:
    start_date = st.sidebar.date_input("시작일", end_date - timedelta(days=365))
    end_date = st.sidebar.date_input("종료일", end_date)

# 5. 사이드바 - 용어 사전 정리
with st.sidebar.expander("💡 반도체 주식 투자 필수 용어 사전", expanded=False):
    st.markdown("""
    * **시가 (Open):** 오늘의 주식 거래가 시작될 때의 가격이에요.
    * **종가 (Close):** 오늘 거래가 마감될 때의 최종 가격이에요.
    * **수정종가 (Adj Close):** 주식 분할이나 배당 등이 반영된 주가로, 장기 추세를 볼 때 가장 정확한 데이터예요.
    * **거래량 (Volume):** 오늘 하루 동안 사고판 주식의 총 개수예요. 반도체 사이클이나 이슈가 터졌을 때 급증하곤 해요.
    * **이동평균선 (MA):** 일정 기간 동안의 주가를 평균 내어 선으로 연결한 것입니다. 20일선(한 달 흐름)과 60일선(분기 흐름)은 주가의 방향성을 판단하는 중요한 기준선이 됩니다.
    """)

# 6. 메인 화면 데이터 분석 및 시각화 구동
if ticker:
    with st.spinner('실시간 반도체 주가 데이터를 가져오는 중...'):
        try:
            # 데이터 로드
            df = yf.download(ticker, start=start_date, end=end_date)
            
            if df.empty:
                st.error("📉 데이터를 불러오지 못했습니다. 티커가 올바른지 다시 확인해주세요.")
            else:
                # 기업 기본 정보 로드 시도
                try:
                    ticker_obj = yf.Ticker(ticker)
                    info = ticker_obj.info
                    company_name = info.get('longName', ticker)
                    currency = info.get('currency', 'USD')
                except:
                    company_name = ticker
                    currency = "USD" if not ticker.endswith(('.KS', '.KQ')) else "KRW"

                # 메인 대시보드 헤더
                st.header(f"📊 {company_name} ({ticker}) 주가 데이터 분석")
                
                # 지표 요약 (Metrics)
                latest_data = df.iloc[-1]
                prev_data = df.iloc[-2] if len(df) > 1 else latest_data
                
                latest_close = float(latest_data['Close'].item())
                prev_close = float(prev_data['Close'].item())
                delta_price = latest_close - prev_close
                delta_percent = (delta_price / prev_close) * 100
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("최신 종가", f"{latest_close:,.2f} {currency}", f"{delta_price:+,.2f} ({delta_percent:+.2f}%)")
                col2.metric("당일 고가", f"{float(latest_data['High'].item()):,.2f} {currency}")
                col3.metric("당일 저가", f"{float(latest_data['Low'].item()):,.2f} {currency}")
                col4.metric("당일 거래량", f"{int(latest_data['Volume'].item()):,} 주")

                # 기술적 지표 계산 (이동평균선)
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['MA60'] = df['Close'].rolling(window=60).mean()

                # 7. 인터렉티브 차트 생성 (Plotly)
                st.subheader("📈 인터렉티브 캔들스틱 및 이동평균선 차트")
                fig = go.Figure()

                # 캔들스틱 차트 추가 (주가 변동성 시각화)
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'].squeeze(),
                    high=df['High'].squeeze(),
                    low=df['Low'].squeeze(),
                    close=df['Close'].squeeze(),
                    name="주가 변동(OHLC)",
                    increasing_line_color='#FF4136',  # 상승 시 빨간색
                    decreasing_line_color='#0074D9'   # 하락 시 파란색
                ))

                # 이동평균선 추가
                fig.add_trace(go.Scatter(x=df.index, y=df['MA20'].squeeze(), mode='lines', name='20일 이동평균선(단기)', line=dict(color='#FFDC00', width=1.5)))
                fig.add_trace(go.Scatter(x=df.index, y=df['MA60'].squeeze(), mode='lines', name='60일 이동평균선(중기)', line=dict(color='#2ECC40', width=1.5)))

                # 레이아웃 디테일 설정
                fig.update_layout(
                    template="plotly_white",
                    xaxis_rangeslider_visible=True,  # 하단 줌 컨트롤 슬라이더 활성화
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=600,
                    hovermode='x unified'
                )
                
                # 차트 출력
                st.plotly_chart(fig, use_container_width=True)

                # 8. 데이터 테이블 출력
                st.subheader("📋 최근 10거래일 데이터 표")
                st.dataframe(df.tail(10).style.format("{:,.2f}"))

        except Exception as e:
            st.error(f"⚠️ 데이터를 처리하는 중 오류가 발생했습니다: {e}")
