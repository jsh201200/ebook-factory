import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import init_session, save_project
from utils.styles import STYLE, render_nav, render_steps
from utils.gemini import generate_text

st.set_page_config(page_title="카피라이팅 | 전자책 팩토리", page_icon="📘", layout="wide", initial_sidebar_state="collapsed")
init_session()
st.markdown(STYLE, unsafe_allow_html=True)
render_nav(st.session_state.get("project_name", ""))
render_steps(3)

st.markdown('<div class="page-title">카피라이팅</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">판매 카피를 생성합니다. 11개 섹션의 고전환율 카피를 AI가 작성합니다.</div>', unsafe_allow_html=True)
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

topic = st.session_state.get("topic", "")
subtitle = st.session_state.get("subtitle", "")
target = st.session_state.get("target", "")
knowhow = st.session_state.get("knowhow", "")
tone = st.session_state.get("tone", "친근하고 실용적인")
toc = st.session_state.get("toc", [])
chapters = st.session_state.get("chapters", {})

if not topic:
    st.warning("⚠️ 먼저 기획 정보를 입력해주세요!")
    if st.button("← 처음으로"):
        st.switch_page("app.py")
    st.stop()

copy_sections = st.session_state.get("copy_sections", {})

COPY_SECTION_NAMES = [
    "🎯 헤드라인 (제목)",
    "😱 문제 제기",
    "🤔 공감 & 왜 실패했나",
    "✨ 해결책 소개",
    "📚 목차 요약",
    "💎 이 책의 차별점",
    "👤 저자 소개",
    "🌟 추천사 (가상)",
    "❓ FAQ",
    "🎁 보너스 & 구성",
    "📣 최종 CTA"
]

# 카피 생성 버튼
if not copy_sections:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**💬 상세페이지 카피를 생성합니다**")
    st.markdown("<small style='color:#888'>11개 섹션의 고전환율 카피를 AI가 작성합니다.<br>생성 후 순서 변경, 삭제, 추가가 자유롭게 가능합니다.</small>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ 카피 생성하기", use_container_width=True):
            toc_str = "\n".join([f"{c['num']}. {c['title']}" for c in toc[:10]]) if toc else "목차 없음"
            ch_sample = ""
            if chapters:
                first_key = list(chapters.keys())[0]
                ch_sample = chapters[first_key]["content"][:500] if chapters else ""

            with st.spinner("카피 생성 중... (약 30초)"):
                prompt = f"""
전자책 판매 상세페이지 카피를 작성해주세요.

전자책 정보:
- 주제: {topic}
- 부제: {subtitle or '없음'}
- 타겟 독자: {target}
- 핵심 노하우: {knowhow}
- 톤앤매너: {tone}
- 목차 샘플: {toc_str}

다음 11개 섹션을 각각 작성해주세요.
각 섹션은 === 섹션명 === 으로 구분:

=== 헤드라인 ===
[메인 제목 + 서브 제목. 강력하고 구체적으로]

=== 문제 제기 ===
[타겟 독자가 겪는 핵심 고통 3가지. 공감 유도]

=== 공감 & 실패 이유 ===
[왜 지금까지 안 됐는지. 독자 편에서 공감]

=== 해결책 소개 ===
[이 전자책이 제시하는 해결책. 기대감 형성]

=== 목차 요약 ===
[목차 주요 챕터 소개. 독자에게 얻을 것 명시]

=== 차별점 ===
[다른 책/정보와 다른 점 3가지. 구체적으로]

=== 저자 소개 ===
[신뢰감 주는 저자 소개. 1인칭으로]

=== 추천사 ===
[실제 같은 추천사 3개. 이름, 직업 포함]

=== FAQ ===
[자주 묻는 질문 5개 + 답변]

=== 구성 및 보너스 ===
[책의 구성 + 보너스 자료 설명]

=== 최종 CTA ===
[구매 유도 마지막 멘트. 긴박감과 가치 강조]
"""
                result = generate_text(prompt, max_tokens=6000)

                # 파싱
                import re
                sections = {}
                parts = re.split(r'===\s*(.+?)\s*===', result)
                section_map = {
                    "헤드라인": "🎯 헤드라인 (제목)",
                    "문제 제기": "😱 문제 제기",
                    "공감": "🤔 공감 & 왜 실패했나",
                    "해결책": "✨ 해결책 소개",
                    "목차": "📚 목차 요약",
                    "차별점": "💎 이 책의 차별점",
                    "저자": "👤 저자 소개",
                    "추천사": "🌟 추천사 (가상)",
                    "FAQ": "❓ FAQ",
                    "구성": "🎁 보너스 & 구성",
                    "CTA": "📣 최종 CTA"
                }
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        key = parts[i].strip()
                        content = parts[i + 1].strip()
                        # 매칭
                        for k, v in section_map.items():
                            if k in key:
                                sections[v] = content
                                break

                if sections:
                    st.session_state.copy_sections = sections
                    if st.session_state.project_name:
                        save_project(st.session_state.project_name, dict(st.session_state))
                    st.rerun()
                else:
                    st.error("카피 파싱 실패. 원본 결과:")
                    st.text(result)
else:
    # 카피 표시 및 편집
    st.markdown(f"✅ **{len(copy_sections)}개 섹션 완성**")

    col_r1, col_r2 = st.columns([4, 1])
    with col_r2:
        if st.button("🔄 전체 재생성"):
            st.session_state.copy_sections = {}
            st.rerun()

    for section_name in COPY_SECTION_NAMES:
        if section_name in copy_sections:
            with st.expander(section_name, expanded=False):
                content = copy_sections[section_name]
                edited = st.text_area("입력", value=content, height=200, key=f"copy_{section_name}", label_visibility="collapsed")
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    if st.button("💾 저장", key=f"save_{section_name}"):
                        copy_sections[section_name] = edited
                        st.session_state.copy_sections = copy_sections
                        if st.session_state.project_name:
                            save_project(st.session_state.project_name, dict(st.session_state))
                        st.success("저장!")
                with col_s2:
                    if st.button("🔄 이 섹션 재생성", key=f"regen_{section_name}"):
                        with st.spinner(f"{section_name} 재생성 중..."):
                            prompt = f"""
전자책: {topic}
타겟: {target}
다음 섹션을 다시 써주세요: {section_name}
{tone} 톤으로, 판매 카피 형식으로.
"""
                            new_content = generate_text(prompt, max_tokens=1000)
                            copy_sections[section_name] = new_content
                            st.session_state.copy_sections = copy_sections
                            st.rerun()
                with col_s3:
                    if st.button("🗑️ 삭제", key=f"del_{section_name}"):
                        del copy_sections[section_name]
                        st.session_state.copy_sections = copy_sections
                        st.rerun()

    # 다음 단계
    st.markdown("---")
    col_next1, col_next2, col_next3 = st.columns([1, 2, 1])
    with col_next2:
        if st.button("🎨 상세페이지 디자인하기 →", use_container_width=True):
            if st.session_state.project_name:
                save_project(st.session_state.project_name, dict(st.session_state))
            st.switch_page("pages/04_상세페이지.py")

st.markdown('</div>', unsafe_allow_html=True)
