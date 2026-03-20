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

실제로 잘 팔리는 전자책 아이디어 10개를 추천해주세요.

주제 제목 규칙:
- 반드시 숫자 포함 (월 100만원, 78가지, 3개월, 12단계 등)
- 구체적인 결과/방법이 보여야 함
- 독자가 제목만 봐도 "이거 나 얘기다!" 싶어야 함
- 예시 수준: "월 100만원 부업을 위한 타로 실전 상담 매뉴얼: 질문 설계부터 클로징까지 팩트폭격 화법"

부제 규칙:
- 핵심 노하우 2~3가지를 압축해서 한 줄로
- 독자가 얻을 구체적 스킬/결과 명시
- 예시: "타로 부업을 희망하는 예비 상담사, 수익이 정체된 초보 상담사가 공개하는 내담자의 마음을 열고 재방문을 부르는 상담 연출법과 상담 화법 템플릿"

타겟독자 규칙:
- 핀셋 타겟 (나이대+상황+구체적 고민까지)
- 예시: "수익이 정체된 초보 타로 상담사", "퇴사를 앞둔 3~5년차 직장인", "자기계발에 관심 있는 2030 여성"

반드시 아래 형식으로만 10줄, 다른 텍스트 절대 금지:
1|주제|부제|타겟독자
2|주제|부제|타겟독자
3|주제|부제|타겟독자
4|주제|부제|타겟독자
5|주제|부제|타겟독자
6|주제|부제|타겟독자
7|주제|부제|타겟독자
8|주제|부제|타겟독자
9|주제|부제|타겟독자
10|주제|부제|타겟독자"""
                result = generate_text(prompt, max_tokens=800)
                if result:
                    ideas = []
                    for line in result.strip().split("\n"):
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split("|")
                        if len(parts) >= 4:
                            ideas.append({
                                "topic": parts[1].strip(),
                                "subtitle": parts[2].strip(),
                                "target": parts[3].strip()
                            })
                        elif len(parts) == 3:
                            ideas.append({
                                "topic": parts[0].strip().lstrip("12345. "),
                                "subtitle": parts[1].strip(),
                                "target": parts[2].strip()
                            })
                    if ideas:
                        st.session_state["recommend_ideas"] = ideas
                        st.rerun()
                    elif result:
                        # 파싱 실패시 원본 그대로 보여주기
                        st.session_state["recommend_raw"] = result
                        st.rerun()

        else:
            st.warning("키워드를 입력해주세요!")

# 파싱 실패시 원본 표시
if st.session_state.get("recommend_raw"):
    st.warning("AI 응답을 파싱하지 못했어요. 직접 확인하고 복사해서 입력해주세요!")
    st.text(st.session_state["recommend_raw"])
    if st.button("닫기", key="close_raw"):
        st.session_state["recommend_raw"] = None
        st.rerun()

# 추천 결과 표시
if st.session_state.get("recommend_ideas"):
    st.markdown("**👇 클릭하면 자동으로 채워져요!**")
    ideas = st.session_state["recommend_ideas"]
    # 2열 카드 형태
    for i in range(0, len(ideas), 2):
        col1, col2 = st.columns(2)
        for j, col in enumerate([col1, col2]):
            idx = i + j
            if idx < len(ideas):
                idea = ideas[idx]
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{idea['topic']}**")
                        st.caption(idea['subtitle'])
                        st.caption(f"🎯 {idea['target']}")
                        if st.button("이걸로 선택 →", key=f"idea_{idx}", use_container_width=True):
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
                prompt = f"""전자책 주제: {st.session_state.topic}
타겟 독자: {st.session_state.target or '일반 독자'}

이 전자책에 담을 핵심 노하우를 7~10개 추천해주세요.

조건:
- 각 항목은 줄바꿈으로 구분
- 번호, 기호, 마크다운 없이 순수 텍스트만
- 추상적인 말 금지 (예: "마인드셋을 바꿔라" X)
- 반드시 구체적이고 실용적으로 (예: "첫 고객 확보를 위한 오픈채팅방 3단계 전략" O)
- 독자가 "오, 이거 진짜 유용하다!" 싶은 것들만
- 실제 현장에서 바로 쓸 수 있는 팁 위주
- 각 항목은 10~30자 사내로 명확하게

예시 수준:
클라이언트 확보하는 3가지 채널과 채널별 접근법
단가 협상에서 절대 양보하면 안 되는 3가지 이유
프리랜서 종합소득세 절세를 위한 경비 처리 꿀팁
첫 상담에서 계약까지 이어지는 질문 설계법
재방문율을 높이는 사후 관리 루틴"""
                result = generate_text(prompt, max_tokens=400)
                if result:
                    st.session_state.knowhow = result
                    st.rerun()
        else:
            st.warning("주제를 먼저 입력해주세요!")

# 톤앤매너
st.subheader("🎨 톤앤매너")

TONE_PRESETS = {
    "친한 언니/오빠 스타일": "친한 언니나 오빠가 카페에서 알려주는 느낌. 편하고 솔직한 문체, 사례 중심, 중간중간 '솔직히 말하면~', '이거 진짜 중요해요' 같은 표현 사용. 독자가 혼자 읽어도 옆에서 누가 설명해주는 느낌.",
    "전문가 멘토 스타일": "현장 경험이 풍부한 전문가가 후배에게 전수하는 느낌. 신뢰감 있고 근거 중심. 데이터와 수치로 증명. '제 경험상~', '실제로 해보면~' 같은 표현으로 권위 있게.",
    "직설적 코치 스타일": "돌려 말하지 않고 핵심만 팍팍. '이렇게 해라', '이건 하지 마라' 명확하게. 독자가 바로 행동하게 만드는 임팩트 있는 문체. 짧고 강한 문장 위주.",
    "공감형 스토리텔러": "독자의 고민에 깊이 공감하며 시작. 저자 본인의 실패와 성공 스토리를 녹여서 감성적으로. '저도 처음엔~', '그때 정말 막막했어요' 같은 공감 표현으로 독자와 연결.",
    "유머러스한 친구 스타일": "가볍고 재미있게. 중간중간 유머와 비유로 어려운 내용도 쉽게. 독자가 웃으면서 읽다 보면 어느새 내용이 머릿속에 쏙 들어오는 스타일.",
}

# 프리셋 버튼
cols = st.columns(3)
for i, (preset_name, _) in enumerate(TONE_PRESETS.items()):
    with cols[i % 3]:
        is_selected = st.session_state.get("tone_preset") == preset_name
        if st.button(
            ("✅ " if is_selected else "") + preset_name,
            key=f"tone_{i}",
            use_container_width=True
        ):
            st.session_state["tone_preset"] = preset_name
            # AI로 세부 설정 자동 생성
            with st.spinner("AI가 세부 톤 설정 중..."):
                from utils.gemini import generate_text as _gen
                auto_prompt = f"""전자책 톤앤매너 스타일: {preset_name}
전자책 주제: {st.session_state.get("topic", "미정")}

이 스타일로 전자책을 쓸 때의 세부 가이드를 3~5줄로 작성해주세요.
- 문체 특징
- 자주 쓸 표현/어투
- 피해야 할 것
- 독자와의 거리감
마크다운 없이 줄바꿈으로 구분."""
                result = _gen(auto_prompt, max_tokens=300)
                if result:
                    st.session_state.tone = preset_name + "\n\n[세부 설정]\n" + result
                else:
                    st.session_state.tone = TONE_PRESETS[preset_name]
            st.rerun()

# 세부 설정 편집창 (자동생성 후 수정 가능)
if st.session_state.get("tone_preset"):
    st.caption(f"선택됨: **{st.session_state.tone_preset}** — 아래에서 자유롭게 수정하세요!")

st.session_state.tone = st.text_area(
    "톤앤매너 세부 설정 (자동생성 후 직접 수정 가능)",
    value=st.session_state.tone,
    height=120,
    placeholder="프리셋을 선택하면 AI가 자동으로 채워드려요. 직접 입력도 가능해요.",
    label_visibility="collapsed"
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
