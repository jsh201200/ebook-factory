import streamlit as st
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import init_session, save_project
from utils.gemini import generate_text

st.set_page_config(page_title="AI 집필 | 전자책 팩토리", page_icon="📘", layout="wide", initial_sidebar_state="collapsed")
init_session()

st.title("📘 AI 전자책 집필")
st.caption("챕터별 초안을 작성합니다. (챕터당 3개 섹션)")
st.markdown("---")

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

# 책 정보 표시
st.markdown(f"**📚 {topic}**")
if subtitle:
    st.caption(subtitle)
st.caption(f"🎯 {target}")
st.markdown("---")

toc = st.session_state.get("toc", [])
chapters = st.session_state.get("chapters", {})

# ── 목차 생성 ──
if not toc:
    st.subheader("📋 목차 생성")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📋 목차 자동 생성하기", use_container_width=True):
            with st.spinner("목차를 구성하고 있습니다..."):
                prompt = f"""전자책 목차를 만들어주세요.

주제: {topic}
{"부제: " + subtitle if subtitle else ""}
타겟 독자: {target}
핵심 노하우:
{knowhow}
톤앤매너: {tone}
목표 페이지: {page_count}페이지
챕터 수: {chapter_count}개

목차 품질 기준:
- 챕터 제목은 그 자체가 훅이 되어야 함 (읽기만 해도 "오 이거 궁금한데?" 싶게)
- 반드시 숫자 포함 (3가지, 5단계, 100일, 12가지 등)
- 구체적 결과/방법이 제목에 드러나야 함
- 마지막 챕터는 [부록] 형식으로 실전 체크리스트
- 섹션 3개는 반드시: 왜/공감 → 어떻게/방법 → 실전/체크리스트 흐름

다음 JSON 형식으로만 응답 (다른 텍스트 없이):
[
  {{
    "num": 1,
    "title": "챕터 제목",
    "sections": ["섹션1 제목", "섹션2 제목", "섹션3 제목"]
  }}
]"""
                result = generate_text(prompt, max_tokens=4096)
                try:
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
    # ── 진행 상태 ──
    chapters_done = len(chapters)
    total = len(toc)
    total_chars = sum(v.get("char_count", 0) for v in chapters.values())
    est_pages = total_chars // 400

    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    col_p1.metric("완성 챕터", f"{chapters_done}/{total}")
    col_p2.metric("총 글자 수", f"{total_chars:,}")
    col_p3.metric("예상 페이지", f"~{est_pages}p")
    col_p4.metric("목표 페이지", f"{page_count}p")

    pct = int(chapters_done / total * 100) if total else 0
    st.progress(pct / 100)

    col_r1, col_r2 = st.columns([4, 1])
    with col_r2:
        if st.button("🔄 목차 재생성"):
            st.session_state.toc = []
            st.session_state.chapters = {}
            st.rerun()

    # ── 전체 챕터 생성 버튼 ──
    if chapters_done < total:
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button(f"⚡ 전체 챕터 생성 ({total}개 × 3섹션)", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                pages_per_ch = max(5, page_count // total)

                for i, ch in enumerate(toc):
                    ch_key = str(ch["num"])
                    if ch_key in chapters:
                        progress_bar.progress((i + 1) / total)
                        continue

                    status_text.markdown(f"**챕터 {ch['num']}/{total}** 작성 중... `{ch['title']}`")

                    prompt = f"""전자책 챕터를 작성해주세요.

전자책 주제: {topic}
타겟 독자: {target}
핵심 노하우: {knowhow}
톤앤매너: {tone}
이 챕터 목표: 약 {pages_per_ch}페이지 (약 {pages_per_ch * 400}자)

챕터 {ch['num']}: {ch['title']}
섹션 구성:
- {ch['sections'][0]}
- {ch['sections'][1]}
- {ch['sections'][2]}

글쓰기 품질 기준:
- 각 섹션 첫 문장은 독자를 강하게 잡는 훅으로 시작
- 반드시 구체적 숫자/사례 포함 (추상적 표현 금지)
- 독자에게 직접 말하는 2인칭 문체 ("여러분", "당신")
- 실전에서 바로 쓸 수 있는 팁과 행동 지침
- 각 섹션 최소 500자 이상
- 어떤 장르든 동일한 구조: 공감(왜) → 방법(어떻게) → 실전(체크리스트/템플릿)
- 챕터 마지막에 "핵심 정리" 3줄 추가

형식:
## {ch['sections'][0]}

[섹션 내용]

## {ch['sections'][1]}

[섹션 내용]

## {ch['sections'][2]}

[섹션 내용]

---
**핵심 정리**
- 
- 
- """
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
                status_text.success(f"✅ 전체 {total}챕터 생성 완료! 총 {sum(v['char_count'] for v in chapters.values()):,}자")
                st.rerun()

    st.markdown("---")

    # ── 목차 리스트 ──
    st.subheader(f"📋 목차 ({total}개 챕터)")

    for ch in toc:
        ch_key = str(ch["num"])
        is_done = ch_key in chapters
        char_count = chapters[ch_key]["char_count"] if is_done else 0

        col1, col2, col3, col4 = st.columns([0.5, 6, 1.5, 1.5])
        with col1:
            st.markdown(f"**{ch['num']}**")
        with col2:
            st.markdown(f"**{ch['title']}**")
            st.caption(" · ".join(ch['sections']))
        with col3:
            if is_done:
                st.caption(f"✅ {char_count:,}자")
            else:
                st.caption("미작성")
        with col4:
            if is_done:
                if st.button("보기 ▶", key=f"view_{ch['num']}", use_container_width=True):
                    st.session_state.selected_chapter = ch_key
                    st.rerun()
            else:
                if st.button("생성 ✨", key=f"gen_{ch['num']}", use_container_width=True):
                    with st.spinner(f"챕터 {ch['num']} 작성 중..."):
                        pages_per_ch = max(5, page_count // total)
                        prompt = f"""전자책 챕터를 작성해주세요.

전자책 주제: {topic}
타겟 독자: {target}
핵심 노하우: {knowhow}
톤앤매너: {tone}

챕터 {ch['num']}: {ch['title']}
섹션:
- {ch['sections'][0]}
- {ch['sections'][1]}
- {ch['sections'][2]}

글쓰기 기준:
- 각 섹션 첫 문장은 강한 훅
- 구체적 숫자/사례 필수
- 2인칭 문체
- 실전 팁과 행동 지침
- 각 섹션 500자 이상
- 구조: 공감 → 방법 → 실전
- 챕터 마지막 핵심 정리 3줄

형식:
## {ch['sections'][0]}
[내용]
## {ch['sections'][1]}
[내용]
## {ch['sections'][2]}
[내용]
---
**핵심 정리**
- 
- 
- """
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
    selected = st.session_state.get("selected_chapter")
    if selected and selected in chapters:
        ch_data = chapters[selected]
        st.markdown("---")
        st.subheader(f"Chapter {selected}: {ch_data['title']}")
        st.caption(f"글자 수: {ch_data['char_count']:,}자 · 약 {ch_data['char_count']//400}페이지")

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
            new_tone = st.selectbox("새 톤:", ["더 친근하게", "더 전문적으로", "더 직접적으로", "더 감성적으로"], key=f"tone_sel_{selected}")
            if st.button("✅ 적용", key=f"apply_tone_{selected}"):
                with st.spinner("톤 변경 중..."):
                    result = generate_text(f"다음 텍스트의 톤을 '{new_tone}' 스타일로 바꿔주세요. 내용은 동일하게:\n\n{ch_data['content']}", max_tokens=4096)
                    if result:
                        chapters[selected]["content"] = result
                        chapters[selected]["char_count"] = len(result)
                        st.session_state.chapters = chapters
                        st.session_state[f"edit_mode_{selected}"] = None
                        st.rerun()

        elif edit_mode == "length":
            direction = st.radio("길이:", ["더 길게 (상세하게)", "더 짧게 (핵심만)"], horizontal=True, key=f"len_radio_{selected}")
            if st.button("✅ 적용", key=f"apply_len_{selected}"):
                with st.spinner("길이 조정 중..."):
                    result = generate_text(f"다음 텍스트를 {'2배 더 상세하고 길게' if '길게' in direction else '절반으로 핵심만'} 다시 써주세요:\n\n{ch_data['content']}", max_tokens=4096)
                    if result:
                        chapters[selected]["content"] = result
                        chapters[selected]["char_count"] = len(result)
                        st.session_state.chapters = chapters
                        st.session_state[f"edit_mode_{selected}"] = None
                        st.rerun()

        elif edit_mode == "hook":
            if st.button("✅ 훅 강화 적용", key=f"apply_hook_{selected}"):
                with st.spinner("훅 강화 중..."):
                    result = generate_text(f"다음 챕터의 각 섹션 첫 문단을 독자가 계속 읽고 싶게 만드는 강렬한 훅으로 바꿔주세요. 나머지는 그대로:\n\n{ch_data['content']}", max_tokens=4096)
                    if result:
                        chapters[selected]["content"] = result
                        chapters[selected]["char_count"] = len(result)
                        st.session_state.chapters = chapters
                        st.session_state[f"edit_mode_{selected}"] = None
                        st.rerun()

        elif edit_mode == "cta":
            if st.button("✅ CTA 추가", key=f"apply_cta_{selected}"):
                with st.spinner("CTA 추가 중..."):
                    result = generate_text(f"다음 챕터 끝에 독자가 바로 행동하게 만드는 강력한 CTA 문단을 추가해주세요:\n\n{ch_data['content']}", max_tokens=4096)
                    if result:
                        chapters[selected]["content"] = result
                        chapters[selected]["char_count"] = len(result)
                        st.session_state.chapters = chapters
                        st.session_state[f"edit_mode_{selected}"] = None
                        st.rerun()

        elif edit_mode == "regen":
            st.warning("⚠️ 기존 내용이 삭제됩니다.")
            if st.button("확인, 재생성", key=f"confirm_regen_{selected}"):
                del chapters[selected]
                st.session_state.chapters = chapters
                st.session_state[f"edit_mode_{selected}"] = None
                st.session_state.selected_chapter = None
                st.rerun()

        # 내용 편집
        edited = st.text_area("챕터 내용 (직접 편집 가능):", value=ch_data["content"], height=500, key=f"edit_{selected}")
        col_save1, col_save2 = st.columns(2)
        with col_save1:
            if st.button("💾 편집 내용 저장", key=f"save_{selected}"):
                chapters[selected]["content"] = edited
                chapters[selected]["char_count"] = len(edited)
                st.session_state.chapters = chapters
                if st.session_state.project_name:
                    save_project(st.session_state.project_name, dict(st.session_state))
                st.success("저장됐어요!")
        with col_save2:
            if st.button("✖ 닫기", key=f"close_{selected}"):
                st.session_state.selected_chapter = None
                st.rerun()

    # ── 다음 단계 ──
    if chapters_done > 0:
        st.markdown("---")

        # PDF/원고 다운로드
        st.subheader("📄 원고 저장")
        full_text = f"# {topic}\n"
        if subtitle:
            full_text += f"### {subtitle}\n\n"
        full_text += f"**타겟 독자:** {target}\n\n---\n\n"
        if toc:
            full_text += "## 목차\n\n"
            for ch in toc:
                full_text += f"{ch['num']}. {ch['title']}\n"
            full_text += "\n---\n\n"
        for key in sorted(chapters.keys(), key=lambda x: int(x)):
            ch_data = chapters[key]
            full_text += f"## Chapter {key}: {ch_data['title']}\n\n"
            full_text += ch_data["content"] + "\n\n---\n\n"

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.download_button("📥 바로 저장 (TXT)", data=full_text.encode("utf-8"),
                file_name=f"{topic[:20]}_원고.txt", mime="text/plain", use_container_width=True)
        with col_d2:
            st.download_button("📝 편집용 저장 (MD)", data=full_text.encode("utf-8"),
                file_name=f"{topic[:20]}_원고.md", mime="text/markdown", use_container_width=True)
        with col_d3:
            if st.button("📣 카피라이팅 단계로 →", use_container_width=True):
                if st.session_state.project_name:
                    save_project(st.session_state.project_name, dict(st.session_state))
                st.switch_page("pages/03_카피라이팅.py")
