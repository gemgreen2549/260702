import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="글로벌 & 한국 주식 분석 앱", layout="wide")

# 앱 제목
st.title("📈 글로벌 & 한국 주식 데이터 분석 웹앱")
st.markdown("스트림릿과 yfinance를 이용한 실시간 주식 데이터 시각화 도구입니다.")

# 사이드바: 설정 및 가이드
st.sidebar.header("🔍 주식 조회 설정")

# 주식 용어 사전 (사이드바에 배치하여 상시 확인 가능)
with st.sidebar.expander("💡 알아두면 좋은 주식 용어 사전", expanded=False):
    st.markdown("""
    * **시가 (Open):** 장이 시작할 때의 가격이에요.
    * **고가 (High):** 장 중 가장 높이 올라갔던 가격이에요.
    * **저가 (Low):** 장 중 가장 낮게 내려갔던 가격이에요.
    * **종가 (Close):** 장이 마감할 때의 최종 가격이에요. 
    * **수정종가 (Adj Close):** 주식 배당이나 분할 등을 반영한 실제 가치 기준의 종가예요. 연속된 데이터 분석 시 가장 신뢰도가 높답니다!
    * **거래량 (Volume):** 그날 하루 동안 거래된 주식의 총 개수예요. 시장의 관심도를 나타내죠.
    * **이동평균선 (MA):** 일정 기간 동안의 주가를 평균 낸 선이에요. (예: 20일선은 최근 20일간의 주가 평균). 주가의 전반적인 방향성(트렌드)을 파악할 때 유용해요.
    """)

# 한국 주식 입력 가이드
st.sidebar.subheader("📌 티커(Ticker) 입력 가이드")
st.sidebar.write("- **미국 주식:** 애플(`AAPL`), 테슬라(`TSLA`), 엔비디아(`NVDA`) 등")
st.sidebar.write("- **코스피 (KOSPI):** 삼성전자(`005930.KS`), SK하이닉스(`000660.KS`) 등")
st.sidebar.write("- **코스닥 (KOSDAQ):** 에코프로(`086520.KQ`), 알테오젠(`191170.KQ`) 등")

# 사용자 입력 받기
ticker_input = st.sidebar.text_input("주식 티커를 입력하세요", value="AAPL").strip().upper()

# 날짜 선택
end_date = datetime.today()
start_date_default = end_date - timedelta(days=365)
start_date = st.sidebar.date_input("시작일 선택", start_date_default)
end_date_input = st.sidebar.date_input("종료일 선택", end_date)

# 분석 시작
if ticker_input:
    with st.spinner('데이터를 불러오는 중입니다...'):
        try:
            # 데이터 로드
            df = yf.download(ticker_input, start=start_date, end=end_date_input)
            
            if df.empty:
                st.error("데이터를 가져오지 못했습니다. 티커 입력이 올바른지 확인해주세요! (예: 삼성전자는 005930.KS)")
            else:
                # 회사 정보 가져오기 (try-except로 예외 처리)
                try:
                    info = yf.Ticker(ticker_input).info
                    company_name = info.get('longName', ticker_input)
                    currency = info.get('currency', 'USD')
                except:
                    company_name = ticker_input
                    currency = "데이터 없음"

                # 메인 화면 레이아웃
                st.header(f"📊 {company_name} ({ticker_input}) 분석 결과")
                
                # 최신 주가 정보 요약 (Metrics)
                latest_data = df.iloc[-1]
                prev_data = df.iloc[-2] if len(df) > 1 else latest_data
                
                # 단일 값 추출을 위한 처리 (.item() 사용)
                latest_close = float(latest_data['Close'].item())
                prev_close = float(prev_data['Close'].item())
                price_delta = latest_close - prev_close
                
                col1, col2, col3 = st.columns(3)
                col1.metric("최신 종가", f"{latest_close:,.2f} {currency}", f"{price_delta:+,.2f}")
                col2.metric("당일 고가", f"{float(latest_data['High'].item()):,.2f} {currency}")
                col3.metric("최신 거래량", f"{int(latest_data['Volume'].item()):,} 주")

                # --- 이동평균선(MA) 계산 ---
                df['MA20'] = df['Close'].rolling(window=20).mean()
                df['MA60'] = df['Close'].rolling(window=60).mean()

                # --- 캔들스틱 차트 그리기 ---
                st.subheader("📈 주가 차트 (인터렉티브 캔들스틱)")
                fig = go.Figure()

                # 캔들스틱 추가
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'].squeeze(),
                    high=df['High'].squeeze(),
                    low=df['Low'].squeeze(),
                    close=df['Close'].squeeze(),
                    name="주가 (OHLC)"
                ))

                # 이동평균선 추가
                fig.add_trace(go.Scatter(x=df.index, y=df['MA20'].squeeze(), mode='lines', name='20일 이평선', line=dict(color='orange', width=1.5)))
                fig.add_trace(go.Scatter(x=df.index, y=df['MA60'].squeeze(), mode='lines', name='60일 이평선', line=dict(color='blue', width=1.5)))

                # 차트 레이아웃 설정
                fig.update_layout(
                    xaxis_rangeslider_visible=True, # 하단 범위 조절 슬라이더 활성화
                    template="plotly_white",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)

                # --- 데이터 테이블 확인 ---
                st.subheader("📋 최근 데이터 표")
                st.dataframe(df.tail(10).style.format("{:,.2f}"))

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
