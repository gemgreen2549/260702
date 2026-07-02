import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="주식 분석 및 ISA 대시보드", layout="wide")

st.title("📊 글로벌 및 한국 주식 분석 & ISA 대시보드")
st.markdown("yfinance 실시간 주가 데이터와 국내 주요 증권사별 ISA 트렌드를 확인하세요.")

# 탭 구성
tab1, tab2 = st.tabs(["주식 데이터 분석", "증권사별 ISA 비교"])

# ==========================================
# TAB 1: 주식 데이터 분석
# ==========================================
with tab1:
    st.header("🔍 실시간 주식 데이터 시각화")
    
    col_input, col_chart = st.columns([1, 3])
    
    with col_input:
        st.subheader("⚙️ 조회 설정")
        ticker_input = st.text_input("주식 티커 입력 (예: AAPL, 005930.KS)", value="AAPL").strip().upper()
        
        st.write("📌 티ker 가이드:")
        st.write("- 미국: AAPL, TSLA")
        st.write("- 코스피: 005930.KS (삼성전자)")
        st.write("- 코스닥: 000660.KS (SK하이닉스)")
        
        end_date = datetime.today()
        start_date_default = end_date - timedelta(days=365)
        start_date = st.date_input("시작일 선택", start_date_default, key="sb")
        end_date_input = st.date_input("종료일 선택", end_date, key="eb")
        
    with col_chart:
        if ticker_input:
            try:
                df = yf.download(ticker_input, start=start_date, end=end_date_input)
                
                if not df.empty:
                    # 데이터 단일화 처리
                    latest_data = df.iloc[-1]
                    prev_data = df.iloc[-2] if len(df) > 1 else latest_data
                    
                    # 3.14 안전한 데이터 추출
                    latest_close = float(df['Close'].iloc[-1].item()) if hasattr(df['Close'].iloc[-1], 'item') else float(df['Close'].iloc[-1])
                    prev_close = float(df['Close'].iloc[-2].item()) if len(df) > 1 and hasattr(df['Close'].iloc[-2], 'item') else float(df['Close'].iloc[-2])
                    
                    price_delta = latest_close - prev_close
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("최신 종가", f"{latest_close:,.2f}", f"{price_delta:+,.2f}")
                    m2.metric("당일 고가", f"{float(df['High'].iloc[-1]):,.2f}")
                    m3.metric("최신 거래량", f"{int(df['Volume'].iloc[-1]):,} 주")
                    
                    # 이동평균선 계산
                    df['MA20'] = df['Close'].rolling(window=20).mean()
                    df['MA60'] = df['Close'].rolling(window=60).mean()
                    
                    # 차트 생성
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=df.index,
                        open=df['Open'].squeeze(),
                        high=df['High'].squeeze(),
                        low=df['Low'].squeeze(),
                        close=df['Close'].squeeze(),
                        name="주가"
                    ))
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'].squeeze(), mode='lines', name='20일선', line=dict(color='orange', width=1.5)))
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'].squeeze(), mode='lines', name='60일선', line=dict(color='blue', width=1.5)))
                    
                    fig.update_layout(template="plotly_white", xaxis_rangeslider_visible=True, height=450)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader("📋 최근 데이터 표")
                    st.dataframe(df.tail(10).astype(str), use_container_width=True)
            except Exception as e:
                st.error(f"데이터 로드 중 오류 발생: {e}")

# ==========================================
# TAB 2: 증권사별 ISA 비교
# ==========================================
with tab2:
    st.header("🏦 국내 주요 증권사별 투자중개형 ISA 가입 트렌드")
    st.write("최근 ISA 총 가입자 수가 800만 명을 돌파하며 투자중개형 계좌로 자금이 쏠리고 있습니다.")
    
    isa_data = {
        "증권사": ["미래에셋증권", "한국투자증권", "삼성증권", "KB증권", "NH투자증권", "키움증권"],
        "중개형 가입자 수 (추정)": [1650000, 1350000, 1300000, 1150000, 1050000, 750000],
        "국내주식 거래수수료 혜택": ["평생 우대 (조건 만족시)", "개설 우대 평생 혜택", "신규 평생 혜택", "기본 우대세율 적용", "우대 멤버십 제공", "평생 수수료 우대 제공"],
        "특징": ["해외주식 절세 마케팅 강점", "대형 채권 라인업 우수", "전용 디지털 자산관리 연계", "금융그룹 혜택 연계", "나무 전용 간편 UI", "영웅문 앱 편리성"]
    }
    df_isa = pd.DataFrame(isa_data)
    
    # 막대 그래프
    fig_isa = go.Figure(go.Bar(
        x=df_isa["증권사"],
        y=df_isa["중개형 가입자 수 (추정)"],
        text=df_isa["중개형 가입자 수 (추정)"].apply(lambda x: f"{x/10000:,.0f}만"),
        textposition='auto',
        marker_color='#4A90E2'
    ))
    fig_isa.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig_isa, use_container_width=True)
    
    st.subheader("📋 증권사별 상세 비교")
    st.dataframe(df_isa, use_container_width=True)
    
    st.divider()
    
    # 친절한 용어 설명 (컴파일 에러 안전지대 버전)
    st.subheader("💡 아주 친절한 금융 용어 사전")
    
    st.write("**시가와 종가:** 장이 시작할 때 가격이 시가, 끝날 때 가격이 종가입니다.")
    st.write("**수정종가:** 배당이나 주식분할 등 주식의 실제 가치 변화를 반영하여 조정한 최종 가격입니다.")
    st.write("**이동평균선:** 일정 기간 동안의 주가 평균을 선으로 이은 것으로, 20일선은 한 달간의 투자자 평균 심리를 보여줍니다.")
    st.write("**투자중개형 ISA:** 개인이 직접 국내 주식이나 ETF를 골라 담아 굴리면서 비과세 및 분리과세 혜택을 받는 만능 절세 통장입니다.")
