import streamlit as st
import random

# 1. 페이지 기본 설정 & 타이틀
st.set_page_config(
    page_title="MBTI 포켓몬 & 직업 연구소",
    page_icon="🔮",
    layout="centered"
)

# 시각적 효과를 위한 커스텀 CSS (배경 그라데이션 및 애니메이션 효과)
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem !important;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(45deg, #FF5353, #FFCC00, #4682B4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    .pokemon-card {
        background-color: #f9f9f9;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border: 2px solid #FFCC00;
    }
    .job-tag {
        display: inline-block;
        background: #e1f5fe;
        color: #0288d1;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🔮 MBTI 포켓몬 연구소</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">나의 MBTI 유형과 딱 맞는 포켓몬 파트너와 천직을 찾아보세요!</p>', unsafe_allow_html=True)

# 2. MBTI 데이터셋 구성 (포켓몬 이미지 번호, 이름, 수식어, 추천 직업 3개)
# 공식 포켓몬 셔플 이미지 번호 활용
mbti_db = {
    "INTJ": {"num": "150", "name": "뮤츠", "desc": "치밀한 전략과 압도적인 통찰력의 소유자!", "jobs": ["🤖 AI 연구원", "📈 전략 기획자", "🔒 보안 전문가"]},
    "INTP": {"num": "65", "name": "후딘", "desc": "끝없는 호기심으로 진리를 탐구하는 천재 아이디어맨!", "jobs": ["💻 소프트웨어 개발자", "🔬 데이터 과학자", "🕵️‍♂️ 시스템 분석가"]},
    "ENTJ": {"num": "6", "name": "리자몽", "desc": "강력한 카리스마로 무리를 이끄는 대담한 리더!", "jobs": ["💼 CEO / 창업가", "📊 경영 컨설턴트", "🧑‍판사 / 변호사"]},
    "ENTP": {"num": "94", "name": "팬텀", "desc": "세상의 모든 틀을 깨부수는 위트 있는 변론가!", "jobs": ["💡 벤처 투자자", "🎨 크리에이티브 디렉터", "🎤 마케팅 전문가"]},
    "INFJ": {"num": "149", "name": "망나뇽", "desc": "강인한 내면과 따뜻한 공감 능력으로 세상을 치유하는 자!", "jobs": ["🏫 교사 / 교육학자", "🧠 심리 상담사", "✍️ 작가 / 저널리스트"]},
    "INFP": {"num": "133", "name": "이브이", "desc": "무한한 가능성을 품은 다정다감한 낭만주의자!", "jobs": ["🎨 일러스트레이터", "🎵 음악가 / 작곡가", "🌱 NGO 활동가"]},
    "ENFJ": {"num": "251", "name": "세레비", "desc": "더 나은 사회를 위해 사람들을 독려하는 정의로운 이타주의자!", "jobs": ["인사관련 전문가(HR)", "📢 홍보 전문가", "🎭 비영리 단체 리더"]},
    "ENFP": {"num": "25", "name": "피카츄", "desc": "언제나 에너지가 넘치고 사람들을 행복하게 만드는 분위기 메이커!", "jobs": ["🎬 콘텐츠 크리에이터", "✈️ 여행 기획자", "🎪 이벤트 디렉터"]},
    "ISTJ": {"num": "9", "name": "거북왕", "desc": "한 번 맡은 일은 끝까지 책임지는 듬직한 현실주의자!", "jobs": ["⚖️ 회계사 / 세무사", "🏛️ 공무원", "🛠️ 품질 관리 엔지니어"]},
    "ISFJ": {"num": "35", "name": "삐삐", "desc": "소중한 사람들을 조용하고 헌신적으로 지키는 수호천사!", "jobs": ["🏥 간호사 / 의료인", "🏫 초등/유치원 교사", "🗂️ 행정 전문가"]},
    "ESTJ": {"num": "68", "name": "괴력몬", "desc": "철저한 규칙과 완벽한 계획으로 결과를 도출하는 추진력의 화신!", "jobs": ["👮 경찰 / 군 장교", "🏗️ 프로젝트 매니저", "📊 자산 관리사"]},
    "ESFJ": {"num": "39", "name": "푸린", "desc": "친절과 따뜻함으로 주변 사람들을 하나로 묶는 사교가!", "jobs": ["🏨 호텔리어 / 승무원", "🤝 고객 만족(CS) 팀장", "🎈 사회복지사"]},
    "ISTP": {"num": "123", "name": "스content라크", "desc": "상황에 적응하는 능력이 뛰어나며 도구를 자유자재로 다루는 장인!", "jobs": ["🏎️ 카레이서 / 파일럿", "🛠️ 하드웨어 엔지니어", "🕵️‍♂️ 과학 수사관"]},
    "ISFP": {"num": "143", "name": "잠만보", "desc": "삶의 여유를 즐기며 예술적 감각이 뛰어난 다정한 예술가!", "jobs": ["🧑‍🍳 파티시에 / 셰프", "📐 인테리어 디자이너", "📸 사진작가"]},
    "ESTP": {"num": "130", "name": "Gyara 갸라도스", "desc": "스릴을 즐기며 당면한 문제를 해결해 나가는 개척자!", "jobs": ["🔥 소방관", "📈 주식 트레이더", "🏋️‍♂️ 스포츠 에이전트"]},
    "ESFP": {"num": "124", "name": "루주라", "desc": "인생을 한 편의 축제처럼 즐기는 타고난 연예인!", "jobs": ["🎭 뮤지컬 배우 / 연예인", "🛍️ 패션 스타일리스트", "🎉 파티 플래너"]}
}

# 3. 사용자 입력 (MBTI 선택)
mbti_list = list(mbti_db.keys())
selected_mbti = st.selectbox(
    "🧐 당신의 MBTI 유형을 선택해 주세요:",
    mbti_list,
    index=None,
    placeholder="여기서 선택하세요..."
)

st.markdown("---")

# 4. 결과 출력
if selected_mbti:
    pokemon = mbti_db[selected_mbti]
    
    # 팡팡 터지는 시각 효과들!
    st.balloons()  # 풍선 효과
    st.toast(f"🎉 {selected_mbti} 분석 완료! 당신의 파트너를 확인하세요!", icon="✨")
    
    # 결과 레이아웃 구성
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        # 포켓몬 공식 이미지 (PokeAPI 스프라이트) 사용
        img_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon['num']}.png"
        st.image(img_url, caption=f"No.{pokemon['num']} {pokemon['name']}", use_container_width=True)
        
    with col2:
        st.subheader(f"✨ {selected_mbti}의 파트너: **{pokemon['name']}**")
        st.info(f"💡 **성향 분석:**\n\n {pokemon['desc']}")
        
        st.markdown("### 💼 추천 천직 TOP 3")
        for job in pokemon['jobs']:
            st.markdown(f"⏱️ **{job}**")
            
    # 하단 응원 메시지
    st.success(f"🍀 {pokemon['name']}(이)가 당신의 앞날을 응원합니다! 파이팅! 🔥")

else:
    # 선택 전 대기 화면 안내
    st.warning("👉 위 드롭다운 메뉴에서 MBTI를 선택하면 파트너 포켓몬이 등장합니다!")
