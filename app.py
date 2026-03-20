import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.storage import init_session, save_project, load_project, list_projects
from utils.styles import STYLE, render_nav, render_steps
from utils.gemini import generate_text

st.set_page_config(
    page_title="전자책 팩토리",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed"
)

init_session()
st.markdown(STYLE, unsafe_allow_html=True)
render_nav(st.session_state.get("project_name", ""))

# ── API 키 설정 (사이드바 대신 상단 expander) ──
with st.expander("⚙️ API 설정", expanded=not st.session_state.gemini_api_key):
    api_input = st.text_input(
        "Gemini API 키",
        value=st.session_state.gemini_api_key,
        type="password",
        placeholder="AIza...",
        help="Google AI Studio에서 발급 (무료)"
    )
    if api_input:
        st.session_state.gemini_api_key = api_input

# ── 프로젝트 관리 ──
projects = list_projects()
col_proj1, col_proj2 = st.columns([3, 1])
with col_proj1:
    project_name_input = st.text_input(
        "📁 프로젝트 이름",
        value=st.session_state.project_name,
        placeholder="예: 타로 부업 매뉴얼"
    )
    st.session_state.project_name = project_name_input
with col_proj2:
    if projects:
        selected_load = st.selectbox("기존 프로젝트 불러오기", ["선택..."] + projects)
        if selected_load != "선택..." and st.button("불러오기"):
            data = load_project(selected_load)
            for k, v in data.items():
                st.session_state[k] = v
            st.rerun()

st.markdown("---")

# ── 스텝 인디케이터 ──
render_steps(1)

# ── 페이지 타이틀 ──
st.markdown('<div class="page-title">전자책 기획 정보 입력</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">당신의 경험과 노하우를 입력하세요. 나머지는 시스템이 처리합니다.</div>', unsafe_allow_html=True)

st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

# ── 주제 추천 ──
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("💡 **어떤 주제로 쓸지 모르겠다면?**")
st.markdown("<small style='color:#888'>관심 키워드만 입력하면 AI가 구체적인 전자책 주제를 추천해드려요.</small>", unsafe_allow_html=True)
col_kw1, col_kw2 = st.columns([4, 1])
with col_kw1:
    keyword_input = st.text_input("", placeholder="예: 타로, 부업, 다이어트, 주식...", label_visibility="collapsed")
with col_kw2:
    if st.button("추천받기 ✨", use_container_width=True):
        if keyword_input:
            with st.spinner("AI가 주제를 추천하는 중..."):
                prompt = f"""
키워드: {keyword_input}
이 키워드 기반으로 판매 가능한 전자책 주제 5개를 추천해주세요.
각각 한 줄로: [주제 제목] - [타겟 독자 한 줄 설명]
번호 없이, 마크다운 없이 순수 텍스트로만.
"""
                result = generate_text(prompt, max_tokens=500)
                if result:
                    st.success(result)
st.markdown('</div>', unsafe_allow_html=True)

# ── 기본 정보 입력 ──
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown("📚 **전자책 주제**")
topic = st.text_input("", value=st.session_state.topic,
    placeholder="예: 퇴사 후 프리랜서로 월 500만원 버는 법",
    label_visibility="collapsed", key="topic_input")
st.session_state.topic = topic

st.markdown("✏️ **부제 (선택)**")
subtitle = st.text_input("", value=st.session_state.subtitle,
    placeholder="예: 카드 의미 나열 대신 상황을 꿰뚫는 메타포 화법과 재방문을 부르는 질문 설계의 기술",
    label_visibility="collapsed", key="subtitle_input")
st.session_state.subtitle = subtitle

st.markdown("🎯 **타겟 독자**")
target = st.text_input("", value=st.session_state.target,
    placeholder="예: 타로 부업을 희망하는 예비 상담사, 수익이 정체된 초보 상담사",
    label_visibility="collapsed", key="target_input")
st.session_state.target = target

st.markdown("💡 **핵심 노하우** (줄바꿈으로 구분, 최소 3개)")
col_kh1, col_kh2 = st.columns([4, 1])
with col_kh1:
    knowhow = st.text_area("", value=st.session_state.knowhow,
        placeholder="클라이언트 확보하는 3가지 채널\n단가 협상에서 절대 양보하면 안 되는 것\n프리랜서 세금 처리 꿀팁",
        label_visibility="collapsed", height=120, key="knowhow_input")
    st.session_state.knowhow = knowhow
with col_kh2:
    if st.button("추천 중...\n✨", use_container_width=True, help="AI가 노하우를 추천해줍니다"):
        if topic:
            with st.spinner("추천 중..."):
                prompt = f"""
전자책 주제: {topic}
타겟: {target or "일반 독자"}
이 전자책에 담을 수 있는 핵심 노하우 5~7가지를 추천해주세요.
각 항목을 줄바꿈으로 구분, 번호 없이, 마크다운 없이.
"""
                result = generate_text(prompt, max_tokens=400)
                if result:
                    st.session_state.knowhow = result
                    st.rerun()

st.markdown("🎨 **톤앤매너**")
tone_options = ["친근하고 실용적인", "전문적이고 신뢰감 있는", "유머러스하고 가벼운", "진지하고 깊이 있는", "직접적이고 임팩트 있는"]
tone = st.selectbox("톤앤매너 선택", tone_options,
    index=tone_options.index(st.session_state.tone) if st.session_state.tone in tone_options else 0,
    label_visibility="collapsed")
st.session_state.tone = tone

st.markdown("📖 **시리즈 구성**")
col_s1, col_s2 = st.columns(2)
with col_s1:
    if st.button("📕 단권 (1권)" + (" ✓" if st.session_state.series == "단권" else ""), use_container_width=True):
        st.session_state.series = "단권"
        st.rerun()
with col_s2:
    if st.button("📚 3권 시리즈" + (" ✓" if st.session_state.series == "3권" else ""), use_container_width=True):
        st.session_state.series = "3권"
        st.rerun()

if st.session_state.series == "단권":
    st.caption("1권 완결 전자책 (약 100~150페이지)")
else:
    st.caption("3권 시리즈 — 각 권을 순차적으로 집필합니다")

st.markdown("📄 **목표 페이지 수**")
page_count = st.slider("페이지 수 선택", min_value=80, max_value=250, value=st.session_state.page_count,
    step=10, label_visibility="collapsed",
    help="80~250장 선택 가능")
st.session_state.page_count = page_count
st.caption(f"선택: {page_count}페이지 → 약 {page_count // 10}~{page_count // 8}개 챕터 자동 계산")

st.markdown('</div>', unsafe_allow_html=True)

# ── AI 집필 시작 버튼 ──
st.markdown("")
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    can_start = bool(st.session_state.topic and st.session_state.target and st.session_state.knowhow)
    if st.button("🚀 AI 집필 시작하기 →", use_container_width=True, disabled=not can_start,
                 help="주제, 타겟 독자, 핵심 노하우를 입력해야 시작할 수 있어요"):
        # 프로젝트 저장
        if st.session_state.project_name:
            save_project(st.session_state.project_name, dict(st.session_state))
        st.session_state.step = 2
        st.switch_page("pages/02_집필.py")

if not can_start:
    st.caption("⚠️ 주제, 타겟 독자, 핵심 노하우를 모두 입력해야 시작할 수 있어요.")

st.markdown('</div>', unsafe_allow_html=True)
