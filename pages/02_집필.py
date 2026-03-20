import streamlit as st
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import init_session, save_project
from utils.styles import STYLE, render_nav, render_steps
from utils.gemini import generate_text, stream_text

st.set_page_config(page_title="AI 집필 | 전자책 팩토리", page_icon="📘", layout="wide", initial_sidebar_state="collapsed")
init_session()
st.markdown(STYLE, unsafe_allow_html=True)
render_nav(st.session_state.get("project_name", ""))
render_steps(2)

st.markdown('<div class="page-title">AI 전자책 집필</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">챕터별 초안을 작성합니다. (챕터당 3개 섹션)</div>', unsafe_allow_html=True)
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

topic = st.session_state.get("topic", "")
subtitle = st.session_state.get("subtitle", "")
target = st.session_state.get("target", "")
knowhow = st.session_state.get("knowhow", "")
tone = st.session_state.get("tone", "친근하고 실용적인")
page_count = st.session_state.get("page_count", 150)

if not topic:
    st.warning("⚠️ 먼저 기획 정보를 입력해주세요!")
    if st.button("← 기획 입력으로"):
        st.switch_page("app.py")
    st.stop()

# 챕터 수 계산
chapter_count = max(10, min(25, page_count // 7))

# ── 목차 생성 섹션 ──
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown(f"**📚 {topic}**")
if subtitle:
    st.markdown(f"<small style='color:#888'>{subtitle}</small>", unsafe_allow_html=True)
st.markdown(f"<small>🎯 {target}</small>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 목차 생성
toc = st.session_state.get("toc", [])

if not toc:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📋 목차 자동 생성하기", use_container_width=True):
            with st.spinner("목차를 구성하고 있습니다..."):
                prompt = f"""
전자책 목차를 만들어주세요.

주제: {topic}
{'부제: ' + subtitle if subtitle else ''}
타겟 독자: {target}
핵심 노하우:
{knowhow}
톤앤매너: {tone}
목표 페이지: {page_count}페이지
챕터 수: {chapter_count}개

규칙:
- 정확히 {chapter_count}개 챕터
- 각 챕터는 JSON 형식으로
- 챕터 제목은 독자가 끌릴 만한 매력적인 제목으로
- 각 챕터에 섹션 3개 포함

다음 JSON 형식으로만 응답 (다른 텍스트 없이):
[
  {{
    "num": 1,
    "title": "챕터 제목",
    "sections": ["섹션1 제목", "섹션2 제목", "섹션3 제목"]
  }},
  ...
]
"""
                result = generate_text(prompt, max_tokens=4096)
                # JSON 파싱
                try:
                    # 코드블록 제거
                    clean = re.sub(r'```json|```', '', result).strip()
                    toc_data = json.loads(clean)
                    st.session_state.toc = toc_data
                    if st.session_state.project_name:
                        save_project(st.session_state.project_name, dict(st.session_state))
                    st.rerun()
                except Exception as e:
                    st.error(f"목차 파싱 오류. 다시 시도해주세요. ({e})")
                    st.code(result)
else:
    # 목차 표시
    chapters_done = len(st.session_state.get("chapters", {}))
    total = len(toc)
    pct = int(chapters_done / total * 100) if total else 0

    # 진행 상태
    col_prog1, col_prog2 = st.columns([3, 1])
    with col_prog1:
        st.markdown(f"""
        <div style="font-size:13px;color:#888;margin-bottom:4px">
            챕터 {chapters_done}/{total} 완성 · 약 {chapters_done * (page_count // total)}페이지
        </div>
        <div class="progress-bar-wrap">
            <div class="progress-bar-fill" style="width:{pct}%"></div>
        </div>
        """, unsafe_allow_html=True)
    with col_prog2:
        if st.button("🔄 목차 재생성", use_container_width=True):
            st.session_state.toc = []
            st.session_state.chapters = {}
            st.rerun()

    # ── 전체 챕터 생성 버튼 ──
    if chapters_done < total:
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button(f"⚡ 전체 챕터 생성하기 ({total}개 × 3섹션)", use_container_width=True):
                chapters = st.session_state.get("chapters", {})
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, ch in enumerate(toc):
                    ch_key = str(ch["num"])
                    if ch_key in chapters:
                        progress_bar.progress((i + 1) / total)
                        continue

                    status_text.markdown(f"챕터 {ch['num']}/{total} 작성 중... `{ch['title']}`")
                    pages_per_ch = page_count // total

                    prompt = f"""
전자책의 챕터를 작성해주세요.

전자책 주제: {topic}
타겟 독자: {target}
핵심 노하우: {knowhow}
톤앤매너: {tone}
목표 페이지: 이 챕터 약 {pages_per_ch}페이지 (A4 기준 약 {pages_per_ch * 400}자)

챕터 {ch['num']}: {ch['title']}
섹션 구성:
- {ch['sections'][0]}
- {ch['sections'][1]}
- {ch['sections'][2]}

각 섹션을 풍부하게 작성해주세요:
- 실제 사례/예시 포함
- 독자에게 직접 말하는 2인칭 문체
- 실용적인 팁과 행동 지침
- 각 섹션 최소 400자 이상

형식:
## {ch['sections'][0]}

[섹션 내용]

## {ch['sections'][1]}

[섹션 내용]

## {ch['sections'][2]}

[섹션 내용]
"""
                    content = generate_text(prompt, max_tokens=4096)
                    chapters[ch_key] = {
                        "title": ch["title"],
                        "sections": ch["sections"],
                        "content": content,
                        "char_count": len(content)
                    }
                    st.session_state.chapters = chapters
                    progress_bar.progress((i + 1) / total)

                if st.session_state.project_name:
                    save_project(st.session_state.project_name, dict(st.session_state))
                status_text.success("✅ 전체 챕터 생성 완료!")
                st.rerun()

    # ── 목차 리스트 + 개별 챕터 보기 ──
    chapters = st.session_state.get("chapters", {})

    # 선택된 챕터
    if "selected_chapter" not in st.session_state:
        st.session_state.selected_chapter = None

    st.markdown("---")
    st.markdown(f"**📋 목차 ({total}개 챕터)**")

    for ch in toc:
        ch_key = str(ch["num"])
        is_done = ch_key in chapters
        badge = '<span class="badge-done">완성</span>' if is_done else '<span class="badge-wip">미작성</span>'

        col_ch1, col_ch2, col_ch3 = st.columns([1, 7, 2])
        with col_ch1:
            st.markdown(f"<span style='color:#e05c2a;font-weight:600'>{ch['num']}</span>", unsafe_allow_html=True)
        with col_ch2:
            st.markdown(f"**{ch['title']}**")
            st.markdown(f"<small style='color:#aaa'>{' · '.join(ch['sections'])}</small>", unsafe_allow_html=True)
        with col_ch3:
            st.markdown(badge, unsafe_allow_html=True)
            btn_label = "보기 ▶" if is_done else "생성 ✨"
            if st.button(btn_label, key=f"ch_btn_{ch['num']}", use_container_width=True):
                if not is_done:
                    # 단일 챕터 생성
                    with st.spinner(f"챕터 {ch['num']} 작성 중..."):
                        pages_per_ch = page_count // total
                        prompt = f"""
전자책의 챕터를 작성해주세요.

전자책 주제: {topic}
타겟 독자: {target}
핵심 노하우: {knowhow}
톤앤매너: {tone}

챕터 {ch['num']}: {ch['title']}
섹션 구성:
- {ch['sections'][0]}
- {ch['sections'][1]}
- {ch['sections'][2]}

각 섹션을 풍부하게 작성해주세요:
- 실제 사례/예시 포함
- 독자에게 직접 말하는 2인칭 문체
- 실용적인 팁과 행동 지침
- 각 섹션 최소 400자 이상

형식:
## {ch['sections'][0]}

[섹션 내용]

## {ch['sections'][1]}

[섹션 내용]

## {ch['sections'][2]}

[섹션 내용]
"""
                        content = generate_text(prompt, max_tokens=4096)
                        chapters[ch_key] = {
                            "title": ch["title"],
                            "sections": ch["sections"],
                            "content": content,
                            "char_count": len(content)
                        }
                        st.session_state.chapters = chapters
                        if st.session_state.project_name:
                            save_project(st.session_state.project_name, dict(st.session_state))
                st.session_state.selected_chapter = ch_key
                st.rerun()

    # ── 챕터 뷰어 ──
    selected = st.session_state.selected_chapter
    if selected and selected in chapters:
        ch_data = chapters[selected]
        st.markdown("---")
        st.markdown(f"### Chapter {selected}: {ch_data['title']}")
        st.markdown(f"<small style='color:#888'>글자 수: {ch_data['char_count']:,}자</small>", unsafe_allow_html=True)

        # 변경 옵션
        st.markdown("**✏️ 변경 옵션:**")
        col_o1, col_o2, col_o3, col_o4, col_o5 = st.columns(5)

        with col_o1:
            if st.button("🎨 톤 변경", key=f"tone_{selected}"):
                st.session_state[f"edit_mode_{selected}"] = "tone"
        with col_o2:
            if st.button("📏 길이 조정", key=f"len_{selected}"):
                st.session_state[f"edit_mode_{selected}"] = "length"
        with col_o3:
            if st.button("🔄 재생성", key=f"regen_{selected}"):
                st.session_state[f"edit_mode_{selected}"] = "regen"
        with col_o4:
            if st.button("🪝 훅 강화", key=f"hook_{selected}"):
                st.session_state[f"edit_mode_{selected}"] = "hook"
        with col_o5:
            if st.button("📣 CTA 추가", key=f"cta_{selected}"):
                st.session_state[f"edit_mode_{selected}"] = "cta"

        edit_mode = st.session_state.get(f"edit_mode_{selected}")

        if edit_mode == "tone":
            new_tone = st.selectbox("새 톤 선택:", ["더 친근하게", "더 전문적으로", "더 직접적으로", "더 감성적으로"])
            if st.button("✅ 적용"):
                with st.spinner("톤 변경 중..."):
                    prompt = f"다음 텍스트의 톤을 '{new_tone}' 스타일로 바꿔주세요. 내용은 동일하게:\n\n{ch_data['content']}"
                    new_content = generate_text(prompt, max_tokens=4096)
                    chapters[selected]["content"] = new_content
                    chapters[selected]["char_count"] = len(new_content)
                    st.session_state.chapters = chapters
                    st.session_state[f"edit_mode_{selected}"] = None
                    st.rerun()

        elif edit_mode == "length":
            direction = st.radio("길이:", ["더 길게 (상세하게)", "더 짧게 (핵심만)"], horizontal=True)
            if st.button("✅ 적용"):
                with st.spinner("길이 조정 중..."):
                    prompt = f"다음 텍스트를 {'2배 더 상세하고 길게' if '길게' in direction else '절반으로 핵심만'} 다시 써주세요:\n\n{ch_data['content']}"
                    new_content = generate_text(prompt, max_tokens=4096)
                    chapters[selected]["content"] = new_content
                    chapters[selected]["char_count"] = len(new_content)
                    st.session_state.chapters = chapters
                    st.session_state[f"edit_mode_{selected}"] = None
                    st.rerun()

        elif edit_mode == "hook":
            if st.button("✅ 훅 강화 적용"):
                with st.spinner("훅 강화 중..."):
                    prompt = f"다음 챕터의 첫 문단(훅)을 독자가 계속 읽고 싶게 만드는 강렬한 도입부로 바꿔주세요. 나머지 내용은 그대로:\n\n{ch_data['content']}"
                    new_content = generate_text(prompt, max_tokens=4096)
                    chapters[selected]["content"] = new_content
                    chapters[selected]["char_count"] = len(new_content)
                    st.session_state.chapters = chapters
                    st.session_state[f"edit_mode_{selected}"] = None
                    st.rerun()

        elif edit_mode == "cta":
            if st.button("✅ CTA 추가"):
                with st.spinner("CTA 추가 중..."):
                    prompt = f"다음 챕터 끝에 독자가 행동하게 만드는 강력한 CTA(Call to Action) 문단을 추가해주세요:\n\n{ch_data['content']}"
                    new_content = generate_text(prompt, max_tokens=4096)
                    chapters[selected]["content"] = new_content
                    chapters[selected]["char_count"] = len(new_content)
                    st.session_state.chapters = chapters
                    st.session_state[f"edit_mode_{selected}"] = None
                    st.rerun()

        elif edit_mode == "regen":
            if st.button("⚠️ 전체 재생성 (기존 내용 삭제됨)"):
                del chapters[selected]
                st.session_state.chapters = chapters
                st.session_state[f"edit_mode_{selected}"] = None
                st.rerun()

        # 내용 표시 + 편집
        edited = st.text_area("챕터 내용 (직접 편집 가능):", value=ch_data["content"], height=500, key=f"edit_{selected}")
        if edited != ch_data["content"]:
            if st.button("💾 편집 내용 저장"):
                chapters[selected]["content"] = edited
                chapters[selected]["char_count"] = len(edited)
                st.session_state.chapters = chapters
                if st.session_state.project_name:
                    save_project(st.session_state.project_name, dict(st.session_state))
                st.success("저장됐어요!")

    # ── 다음 단계 버튼 ──
    if chapters_done > 0:
        st.markdown("---")
        col_next1, col_next2, col_next3 = st.columns([1, 2, 1])
        with col_next2:
            if st.button("📣 카피라이팅 단계로 →", use_container_width=True):
                if st.session_state.project_name:
                    save_project(st.session_state.project_name, dict(st.session_state))
                st.switch_page("pages/03_카피라이팅.py")

st.markdown('</div>', unsafe_allow_html=True)
