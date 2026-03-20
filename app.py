import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.storage import init_session, save_project, load_project, list_projects
from utils.gemini import generate_text

st.set_page_config(
    page_title="전자책 팩토리",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed"
)

init_session()

st.title("📘 전자책 팩토리")
st.markdown("---")

# API 키 설정
with st.expander("⚙️ API 설정", expanded=not st.session_state.gemini_api_key):
    api_input = st.text_input(
        "Gemini API 키",
        value=st.session_state.gemini_api_key,
        type="password",
        placeholder="AIza..."
    )
    if api_input:
        st.session_state.gemini_api_key = api_input

# 프로젝트 이름
st.session_state.project_name = st.text_input(
    "📁 프로젝트 이름",
    value=st.session_state.project_name,
    placeholder="예: 타로 부업 매뉴얼"
)

st.markdown("---")
st.header("전자책 기획 정보 입력")
st.caption("당신의 경험과 노하우를 입력하세요. 나머지는 시스템이 처리합니다.")

# ── 주제 추천 ──
st.subheader("💡 주제 추천")
col1, col2 = st.columns([4, 1])
with col1:
    keyword_input = st.text_input(
        "키워드 입력",
        placeholder="예: 타로, 부업, 다이어트, 주식...",
        key="keyword_input"
    )
with col2:
    st.write("")
    if st.button("추천받기 ✨", key="btn_recommend"):
        kw = st.session_state.get("keyword_input", "")
        if kw:
            with st.spinner("AI가 추천하는 중..."):
                prompt = f"""키워드: {kw}
판매 가능한 전자책 아이디어 5개를 추천해주세요.
각각 아래 형식으로만 응답 (다른 텍스트 없이):
1|주제|부제|타겟독자
2|주제|부제|타겟독자
3|주제|부제|타겟독자
4|주제|부제|타겟독자
5|주제|부제|타겟독자"""
                result = generate_text(prompt, max_tokens=800)
                if result:
                    ideas = []
                    for line in result.strip().split("\n"):
                        parts = line.split("|")
                        if len(parts) >= 4:
                            ideas.append({
                                "topic": parts[1].strip(),
                                "subtitle": parts[2].strip(),
                                "target": parts[3].strip()
                            })
                    if ideas:
                        st.session_state["recommend_ideas"] = ideas
                        st.rerun()
        else:
            st.warning("키워드를 입력해주세요!")

# 추천 결과 표시
if st.session_state.get("recommend_ideas"):
    st.info("👇 클릭하면 주제/부제/타겟이 자동으로 채워져요! (직접 수정도 가능해요)")
    for i, idea in enumerate(st.session_state["recommend_ideas"]):
        if st.button(f"📌 {idea['topic']}", key=f"idea_{i}"):
            st.session_state.topic = idea["topic"]
            st.session_state.subtitle = idea["subtitle"]
            st.session_state.target = idea["target"]
            st.session_state["recommend_ideas"] = []
            st.rerun()

st.markdown("---")
st.subheader("📚 기본 정보")

# 입력 후 수정 가능
st.session_state.topic = st.text_input(
    "전자책 주제 *",
    value=st.session_state.topic,
    placeholder="예: 퇴사 후 프리랜서로 월 500만원 버는 법"
)

st.session_state.subtitle = st.text_input(
    "부제 (선택)",
    value=st.session_state.subtitle,
    placeholder="예: 카드 의미 나열 대신 상황을 꿰뚫는 메타포 화법"
)

st.session_state.target = st.text_input(
    "타겟 독자 *",
    value=st.session_state.target,
    placeholder="예: 타로 부업을 희망하는 예비 상담사"
)

# 핵심 노하우
col_kh1, col_kh2 = st.columns([4, 1])
with col_kh1:
    st.session_state.knowhow = st.text_area(
        "핵심 노하우 * (줄바꿈으로 구분, 최소 3개)",
        value=st.session_state.knowhow,
        placeholder="클라이언트 확보하는 3가지 채널\n단가 협상에서 절대 양보하면 안 되는 것\n프리랜서 세금 처리 꿀팁",
        height=120
    )
with col_kh2:
    st.write("")
    st.write("")
    st.write("")
    if st.button("노하우 추천 ✨", key="btn_knowhow"):
        if st.session_state.topic:
            with st.spinner("추천 중..."):
                prompt = f"전자책 주제: {st.session_state.topic}\n타겟: {st.session_state.target or '일반 독자'}\n핵심 노하우 5~7가지를 줄바꿈으로 구분해서 추천해주세요. 번호 없이."
                result = generate_text(prompt, max_tokens=400)
                if result:
                    st.session_state.knowhow = result
                    st.rerun()
        else:
            st.warning("주제를 먼저 입력해주세요!")

# 톤앤매너
tone_options = ["친근하고 실용적인", "전문적이고 신뢰감 있는", "유머러스하고 가벼운", "진지하고 깊이 있는", "직접적이고 임팩트 있는"]
st.session_state.tone = st.selectbox(
    "🎨 톤앤매너",
    tone_options,
    index=tone_options.index(st.session_state.tone) if st.session_state.tone in tone_options else 0
)

# 시리즈
col_s1, col_s2 = st.columns(2)
with col_s1:
    if st.button("📕 단권" + (" ✓" if st.session_state.series == "단권" else ""), use_container_width=True):
        st.session_state.series = "단권"
        st.rerun()
with col_s2:
    if st.button("📚 3권 시리즈" + (" ✓" if st.session_state.series == "3권" else ""), use_container_width=True):
        st.session_state.series = "3권"
        st.rerun()

# 페이지 수
st.session_state.page_count = st.slider(
    "📄 목표 페이지 수",
    min_value=80,
    max_value=250,
    value=st.session_state.page_count,
    step=10
)

st.markdown("---")
can_start = bool(st.session_state.topic and st.session_state.target and st.session_state.knowhow)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 AI 집필 시작하기 →", use_container_width=True, disabled=not can_start):
        if st.session_state.project_name:
            save_project(st.session_state.project_name, dict(st.session_state))
        st.switch_page("pages/02_집필.py")

if not can_start:
    st.caption("⚠️ 주제, 타겟 독자, 핵심 노하우를 모두 입력해야 시작할 수 있어요.")
