# app.py
import streamlit as st
import random

st.set_page_config(page_title="MBTI 해장 추천기 🎬📚", layout="centered")

st.title("MBTI 해장 추천기 🎉")
st.markdown(
    "하루 피곤했지? 네 MBTI 골라봐 — 딱 맞는 **영화 + 책** 한 조합 추천해줄게. \n\n"
    "친근하고 편하게, 오늘 기분 풀리는 콘텐츠로 골라봤어 😊"
)

MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

# 각 MBTI에 맞춘 (영화, 책, 짧은 설명) 튜플
RECOMMENDATIONS = {
    "INTJ": ("인셉션 (Inception)", "사피엔스 (유발 하라리) — 큰 그림 다시보기", "복잡한 생각 정리하고 싶을 때 🧠"),
    "INTP": ("마션 (The Martian)", "호모 데우스 (유발 하라리) — 호기심 충전", "골똘히 생각하다 웃게 해줄 거야 🚀"),
    "ENTJ": ("머니볼 (Moneyball)", "원칙 (레이 달리오) — 전략/결단 응원", "리더십 기운 팡팡 ⚡"),
    "ENTP": ("그랜드 부다페스트 호텔", "생각의 탄생 (다양한 아이디어 모음) — 창의성 충전", "톡톡 튀는 아이디어 원할 때 💡"),
    "INFJ": ("이터널 선샤인 (Eternal Sunshine)", "밤의 여행자 (감성 에세이) — 마음 공감", "따스한 위로가 필요할 때 🌙"),
    "INFP": ("어바웃 타임 (About Time)", "연금술사 (파울로 코엘료) — 소소한 인생철학", "감성 풀코스, 마음 힐링해줘요 💖"),
    "ENFJ": ("굿 윌 헌팅 (Good Will Hunting)", "사람을 얻는 기술 (대인관계 실용서) — 공감&리드", "주변 사람들을 돌본 너에게도 위로를 🌱"),
    "ENFP": ("월플라워 (The Perks of Being a Wallflower)", "작은 아씨들 (루이자 메이 올콧) — 따뜻한 연대", "에너지 충전 + 공감 가득 ✨"),
    "ISTJ": ("셰이프 오브 워터 (The Shape of Water)", "청소의 기술 (정리/루틴서) — 안정감", "편안하게 루틴 회복하고 싶을 때 🛠️"),
    "ISFJ": ("리틀 미스 선샤인 (Little Miss Sunshine)", "온 가족 소설/에세이 — 따뜻한 휴식", "포근한 위로, 안전한 기분 원할 때 ☕"),
    "ESTJ": ("소셜 네트워크 (The Social Network)", "성과의 기술 (실무형 자기계발서) — 실용적 자극", "실행력 불태우고 싶을 때 🔥"),
    "ESFJ": ("프렌즈: 더 무비(친근한 코미디류)", "감성 에세이 모음 — 따뜻한 공감", "함께 웃고 싶은 날에 딱! 😂"),
    "ISTP": ("존 윅 (John Wick)", "장르소설(스릴러/액션) — 단순 스트레스 해소", "직접 행동하고 싶은 날에 액션충전 ⚔️"),
    "ISFP": ("어댑테이션 (Adaptation)", "시 그림책/비주얼 에세이 — 감성적 시선", "감성적으로 충전하고 싶을 때 🎨"),
    "ESTP": ("쇼생크 탈출 (The Shawshank Redemption)", "스릴러/서스펜스 장르소설 — 몰입감", "한 번 보면 빠져드는 액션+드라마 🎯"),
    "ESFP": ("라라랜드 (La La Land)", "뮤지컬/감성 소설 — 활기차고 밝은 위로", "신나게 기분 전환하고 싶을 때 💃")
}

def get_recommendation(mbti: str):
    return RECOMMENDATIONS.get(mbti, ("영화 추천 없음", "책 추천 없음", "추천 정보가 없어요."))

# 사이드바로 선택 & 랜덤
with st.sidebar:
    st.header("설정")
    chosen = st.selectbox("네 MBTI 골라줘 👇", ["선택하세요"] + MBTI_LIST)
    if st.button("랜덤 추천해줘 🎲"):
        chosen = random.choice(MBTI_LIST)
        st.success(f"랜덤으로 골랐어: {chosen}")

# 메인 영역: 선택 안내
if chosen == "선택하세요":
    st.info("왼쪽에서 MBTI를 골라줘. 선택하면 바로 추천 보여줄게! ✨")
else:
    movie, book, reason = get_recommendation(chosen)
    st.subheader(f"너는 {chosen}구나! — 맞춤 해장 콘텐츠 🍿📖")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 🎬 영화")
        st.write(f"**{movie}**")
        # 짧은 한 줄 코멘트
        st.caption("추천 포인트: 영화로 감정 풀기 👍")
    with col2:
        st.markdown("### 📚 책")
        st.write(f"**{book}**")
        st.caption("추천 포인트: 글로 천천히 위로받기 ☕")
    st.markdown("---")
    st.write(f"**왜 이걸 골랐냐면:** {reason}")
    st.markdown("")
    st.write("마음에 든다면 ‘좋아요’ 버튼 한 번 눌러줘(마음속으로라도 OK) 😆")
    if st.button("다른 추천 보여줘"):
        # 같은 MBTI에서 변형 추천(랜덤으로 짧은 코멘트 바꿔서 재제시)
        alt_movies_books = [
            ("팜프(다른 감성 영화)", "따뜻한 소설 한 권"),
            ("가벼운 로맨틱 코미디", "짧은 감성 에세이"),
            ("몰입형 스릴러", "영감을 주는 논픽션")
        ]
        alt = random.choice(alt_movies_books)
        st.info(f"다른 대안: 영화 **{alt[0]}**, 책 **{alt[1]}** — 한번 살펴봐! 👀")

st.markdown("---")
st.markdown("Made with ❤️ — MBTI 해장 추천기 · 친근한 톤으로 준비했어.")
st.caption("Note: 추천은 기분 전환 목적이에요. 진짜 ‘해장’이 필요하면 따뜻한 음식과 휴식도 잊지 마!")
