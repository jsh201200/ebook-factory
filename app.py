import streamlit as st
import sys
import os
import json
import re
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

실제로 잘 팔리는 전자책 아이디어 10개 추천.

규칙:
- 주제: 숫자 포함, 구체적 결과/방법 명시, "이거 나 얘기다!" 싶게
- 부제: 핵심 노하우 2~3가지 압축, 한 줄
- 타겟: 핀셋 (나이대+상황+고민, 예: "수익 정체된 초보 타로 상담사")

반드시 아래 JSON 형식으로만 응답. 코드블록 없이 순수 JSON만:
[
  {{"topic": "주제", "subtitle": "부제", "target": "타겟"}},
  {{"topic": "주제", "subtitle": "부제", "target": "타겟"}},
  {{"topic": "주제", "subtitle": "부제", "target": "타겟"}},
  {{"topic": "주제", "subtitle": "부제", "target": "타겟"}},
  {{"topic": "주제", "subtitle": "부제", "target": "타겟"}},
  {{"topic": "주제", "subtitle": "부제", "target": "타겟"}},
  {{"topic": "주제", "subtitle": "부제", "target": "타겟"}},
  {{"topic": "주제", "subtitle": "부제", "target": "타겟"}},
  {{"topic": "주제", "subtitle": "부제", "target": "타겟"}},
  {{"topic": "주제", "subtitle": "부제", "target": "타겟"}}
]"""
                result = generate_text(prompt, max_tokens=4000)
                if result:
                    ideas = []
                    # 코드블록 제거 후 JSON 파싱
                    clean = result.strip()
                    for marker in ["```json", "```"]:
                        clean = clean.replace(marker, "")
                    clean = clean.strip()
                    start = clean.find("[")
                    end = clean.rfind("]") + 1
                    if start != -1 and end > start:
                        try:
                            ideas = json.loads(clean[start:end])
                        except Exception:
                            ideas = []
                    if ideas:
                        st.session_state["recommend_ideas"] = ideas
                        st.rerun()
                    else:
                        st.session_state["recommend_raw"] = result
                        st.rerun()
        else:
            st.warning("키워드를 입력해주세요!")

# 파싱 실패시 원본 표시
if st.session_state.get("recommend_raw"):
    st.warning("파싱 실패! AI 원본 응답:")
    st.text(st.session_state["recommend_raw"])
    if st.button("닫기", key="close_raw"):
        st.session_state["recommend_raw"] = None
        st.rerun()

# 추천 결과 카드 표시
if st.session_state.get("recommend_ideas"):
    st.markdown("**👇 클릭하면 자동으로 채워져요!**")
    ideas = st.session_state["recommend_ideas"]
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

이 전자책에 담을 핵심 노하우 8~10개를 추천해주세요.

조건:
- 줄바꿈으로 구분, 번호/기호/마크다운 절대 없이 순수 텍스트만
- 추상적 표현 완전 금지 (예: "마인드셋을 바꿔라", "자신감을 가져라" X)
- 반드시 구체적이고 현장에서 바로 쓸 수 있는 것만
- 각 항목은 실제로 독자가 "오, 이거 진짜 유용하다!" 싶은 수준
- 예시 수준 참고:
  부담 없이 시작하는 채널별 수익화 단가표: 오픈채팅, 유료 앱, 크몽 각 플랫폼별 특성에 따른 상담 가격 책정법과 초기 노출 전략
  멘탈 소모 없는 철벽 방어 상담 매뉴얼: 무례하거나 답변을 강요하는 진상 내담자로부터 상담사를 보호하고 페이스를 유지하며 단호하게 리드하는 압도적 대화법
  이 꿰뚫한 이유를 명확히 제시하여 고정 고객으로 만드는 기술"""
                result = generate_text(prompt, max_tokens=1500)
                if result:
                    st.session_state.knowhow = result
                    st.rerun()
        else:
            st.warning("주제를 먼저 입력해주세요!")

# 톤앤매너
st.subheader("🎨 톤앤매너")

TONE_PRESETS = {
    "친한 언니/오빠 스타일": "친한 언니나 오빠가 카페에서 알려주는 느낌. 편하고 솔직한 문체, 사례 중심.",
    "전문가 멘토 스타일": "현장 경험이 풍부한 전문가가 후배에게 전수하는 느낌. 신뢰감 있고 근거 중심.",
    "직설적 코치 스타일": "돌려 말하지 않고 핵심만 팍팍. 독자가 바로 행동하게 만드는 임팩트 있는 문체.",
    "공감형 스토리텔러": "독자의 고민에 깊이 공감하며 시작. 저자 본인의 실패와 성공 스토리를 녹여서 감성적으로.",
    "유머러스한 친구 스타일": "가볍고 재미있게. 유머와 비유로 어려운 내용도 쉽게.",
}

cols = st.columns(3)
for i, (preset_name, preset_desc) in enumerate(TONE_PRESETS.items()):
    with cols[i % 3]:
        is_selected = st.session_state.get("tone_preset") == preset_name
        if st.button(
            ("✅ " if is_selected else "") + preset_name,
            key=f"tone_{i}",
            use_container_width=True
        ):
            st.session_state["tone_preset"] = preset_name
            with st.spinner("AI가 세부 톤 설정 중..."):
                auto_prompt = f"""전자책 톤앤매너: {preset_name}
전자책 주제: {st.session_state.get("topic", "미정")}

이 스타일로 쓸 때의 세부 가이드 3~5줄:
- 문체 특징
- 자주 쓸 표현/어투
- 피해야 할 것
마크다운 없이 줄바꿈으로.
"네", "알겠습니다" 같은 AI 응답 멘트 없이 바로 내용 시작."""
                result = generate_text(auto_prompt, max_tokens=300)
                st.session_state.tone = preset_name + "\n\n[세부 설정]\n" + (result or preset_desc)
            st.rerun()

if st.session_state.get("tone_preset"):
    st.caption(f"선택됨: **{st.session_state.tone_preset}** — 아래에서 수정 가능해요!")

st.session_state.tone = st.text_area(
    "톤앤매너",
    value=st.session_state.tone,
    height=120,
    placeholder="프리셋 선택하면 AI가 자동으로 채워드려요. 직접 입력도 가능해요.",
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
