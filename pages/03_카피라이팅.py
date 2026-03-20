import streamlit as st
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import init_session, save_project
from utils.gemini import generate_text

st.set_page_config(page_title="카피라이팅 | 전자책 팩토리", page_icon="📘", layout="wide", initial_sidebar_state="collapsed")
init_session()

st.title("📣 카피라이팅")
st.caption("11개 섹션의 고전환율 카피를 AI가 작성합니다. 생성 후 순서 변경, 삭제, 추가가 자유롭게 가능합니다.")
st.markdown("---")

topic = st.session_state.get("topic", "")
subtitle = st.session_state.get("subtitle", "")
target = st.session_state.get("target", "")
knowhow = st.session_state.get("knowhow", "")
tone = st.session_state.get("tone", "")
toc = st.session_state.get("toc", [])
chapters = st.session_state.get("chapters", {})

if not topic:
    st.warning("⚠️ 먼저 기획 정보를 입력해주세요!")
    if st.button("← 처음으로"):
        st.switch_page("app.py")
    st.stop()

copy_sections = st.session_state.get("copy_sections", {})

SECTION_ORDER = [
    "🎯 헤드라인",
    "😱 문제 제기",
    "🤔 공감 & 실패 이유",
    "✨ 해결책 소개",
    "📚 목차 요약",
    "💎 이 책의 차별점",
    "👤 저자 소개",
    "🌟 추천사",
    "❓ FAQ",
    "🎁 구성 & 보너스",
    "📣 최종 CTA"
]

if not copy_sections:
    # 심플하게 버튼 하나
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center;padding:40px 0 20px'>
            <div style='font-size:48px'>💬</div>
            <div style='font-size:20px;font-weight:700;margin:12px 0 8px'>상세페이지 카피를 생성합니다</div>
            <div style='color:#888;font-size:14px'>11개 섹션의 고전환율 카피를 AI가 작성합니다.<br>생성 후 순서 변경, 삭제, 추가가 자유롭게 가능합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✨ 카피 생성하기", use_container_width=True):
            toc_str = "\n".join([f"{c['num']}. {c['title']}" for c in toc[:10]]) if toc else "목차 없음"
            with st.spinner("카피 생성 중... (약 30~60초)"):
                prompt = f"""전자책 판매 상세페이지 카피를 작성해주세요.

전자책 정보:
- 주제: {topic}
- 부제: {subtitle or "없음"}
- 타겟 독자: {target}
- 핵심 노하우: {knowhow}
- 톤앤매너: {tone}
- 목차 일부: {toc_str}

각 섹션을 아래 구분자로 나눠서 작성해주세요:

=== 헤드라인 ===
메인 제목 + 서브 제목. 숫자와 구체적 결과 포함. 독자가 "이거 나 얘기다!" 싶게.

=== 문제 제기 ===
타겟 독자가 겪는 핵심 고통 3가지. 현실적이고 구체적으로. 공감 극대화.

=== 공감 & 실패 이유 ===
왜 지금까지 안 됐는지. 독자 편에서 깊이 공감. "저도 그랬어요" 느낌.

=== 해결책 소개 ===
이 전자책이 제시하는 해결책. 기대감 형성. 구체적 변화 약속.

=== 목차 요약 ===
주요 챕터 소개. 각 챕터에서 얻을 것 명시. 볼륨감 강조.

=== 차별점 ===
다른 책/정보와 다른 점 3가지. 구체적 수치와 근거 포함.

=== 저자 소개 ===
신뢰감 주는 소개. 1인칭. 실제 경험과 결과 중심.

=== 추천사 ===
실제 같은 추천사 3개. 이름+직업+구체적 변화 포함.

=== FAQ ===
자주 묻는 질문 5개 + 솔직하고 명확한 답변.

=== 구성 & 보너스 ===
책의 구성 + 보너스 자료. 가치를 숫자로 표현.

=== 최종 CTA ===
지금 구매해야 하는 이유. 긴박감과 가치 강조. 강력한 마무리.
절대 금지사항 (모든 텍스트에 적용):
- 첫 줄에 "네", "알겠습니다", "작성해 드리겠습니다" 같은 AI 응답 멘트 금지 (바로 본문 시작)
- ** 같은 마크다운 볼드 표시 금지
- # ## 같은 마크다운 헤더 금지
- "물론이죠!", "좋은 질문이에요!", "~해드립니다", "~드리겠습니다" 같은 AI 말투 금지
- 같은 말 반복 금지
- "~할 수도 있습니다", "아마도", "~인 것 같습니다", "~라고 할 수 있죠" 두리뭉실한 표현 금지
- "지금까지 알아봤습니다", "어떠셨나요?" 불필요한 마무리 멘트 금지
- 추상적이고 뻔한 표현 금지 ("긍정적인 마인드", "열심히 노력" 등)"""

                result = generate_text(prompt, max_tokens=6000)
                sections = {}
                parts = re.split(r'===\s*(.+?)\s*===', result)
                section_map = {
                    "헤드라인": "🎯 헤드라인",
                    "문제": "😱 문제 제기",
                    "공감": "🤔 공감 & 실패 이유",
                    "해결책": "✨ 해결책 소개",
                    "목차": "📚 목차 요약",
                    "차별점": "💎 이 책의 차별점",
                    "저자": "👤 저자 소개",
                    "추천사": "🌟 추천사",
                    "FAQ": "❓ FAQ",
                    "구성": "🎁 구성 & 보너스",
                    "CTA": "📣 최종 CTA"
                }
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        key = parts[i].strip()
                        content = parts[i+1].strip()
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
                    st.error("파싱 실패. 다시 시도해주세요.")
                    st.text(result[:500])
else:
    st.success(f"✅ {len(copy_sections)}개 섹션 완성!")
    col_r1, col_r2 = st.columns([4, 1])
    with col_r2:
        if st.button("🔄 전체 재생성"):
            st.session_state.copy_sections = {}
            st.rerun()

    for section_name in SECTION_ORDER:
        if section_name in copy_sections:
            with st.expander(section_name, expanded=False):
                content = copy_sections[section_name]
                edited = st.text_area("내용", value=content, height=200,
                    key=f"copy_{section_name}", label_visibility="collapsed")
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    if st.button("💾 저장", key=f"save_{section_name}"):
                        copy_sections[section_name] = edited
                        st.session_state.copy_sections = copy_sections
                        if st.session_state.project_name:
                            save_project(st.session_state.project_name, dict(st.session_state))
                        st.success("저장!")
                with col_s2:
                    if st.button("🔄 재생성", key=f"regen_{section_name}"):
                        with st.spinner("재생성 중..."):
                            result = generate_text(
                                f"전자책: {topic}\n타겟: {target}\n톤: {tone}\n다음 섹션을 다시 써주세요: {section_name}\n고전환율 판매 카피로.\n** 마크다운 금지, AI 응답 멘트 금지, 바로 카피 본문 시작.",
                                max_tokens=1000)
                            if result:
                                copy_sections[section_name] = result
                                st.session_state.copy_sections = copy_sections
                                st.rerun()
                with col_s3:
                    if st.button("🗑️ 삭제", key=f"del_{section_name}"):
                        del copy_sections[section_name]
                        st.session_state.copy_sections = copy_sections
                        st.rerun()

    st.markdown("---")
    col_n1, col_n2, col_n3 = st.columns([1, 2, 1])
    with col_n2:
        if st.button("🎨 상세페이지 디자인하기 →", use_container_width=True):
            if st.session_state.project_name:
                save_project(st.session_state.project_name, dict(st.session_state))
            st.switch_page("pages/04_상세페이지.py")
