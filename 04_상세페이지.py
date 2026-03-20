import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.storage import init_session, save_project
from utils.styles import STYLE, render_nav, render_steps
from utils.gemini import generate_text

st.set_page_config(page_title="상세페이지 | 전자책 팩토리", page_icon="📘", layout="wide", initial_sidebar_state="collapsed")
init_session()
st.markdown(STYLE, unsafe_allow_html=True)
render_nav(st.session_state.get("project_name", ""))
render_steps(4)

st.markdown('<div class="page-title">상세페이지 디자인</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">전자책 표지와 상세페이지를 완성하세요.</div>', unsafe_allow_html=True)
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

topic = st.session_state.get("topic", "")
subtitle = st.session_state.get("subtitle", "")
copy_sections = st.session_state.get("copy_sections", {})
chapters = st.session_state.get("chapters", {})

if not topic:
    st.warning("⚠️ 먼저 기획 정보를 입력해주세요!")
    if st.button("← 처음으로"):
        st.switch_page("app.py")
    st.stop()

# ── 탭 구성 ──
tab1, tab2, tab3 = st.tabs(["📄 원고 PDF", "🖼️ 표지 & 목업", "🌐 상세페이지 HTML"])

# ── 탭 1: 원고 PDF ──
with tab1:
    st.markdown("### 📄 원고 다운로드")
    if not chapters:
        st.info("아직 작성된 챕터가 없어요. AI 집필 단계로 돌아가세요.")
        if st.button("← AI 집필로"):
            st.switch_page("pages/02_집필.py")
    else:
        chapter_count = len(chapters)
        total_chars = sum(v.get("char_count", 0) for v in chapters.values())
        st.markdown(f"""
        <div class="card">
            <div style="display:flex;gap:24px">
                <div><div style="font-size:24px;font-weight:700;color:#e05c2a">{chapter_count}</div><div style="font-size:12px;color:#888">챕터</div></div>
                <div><div style="font-size:24px;font-weight:700;color:#e05c2a">{total_chars:,}</div><div style="font-size:12px;color:#888">총 글자 수</div></div>
                <div><div style="font-size:24px;font-weight:700;color:#e05c2a">~{total_chars // 400}</div><div style="font-size:12px;color:#888">예상 페이지</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_pdf1, col_pdf2 = st.columns(2)

        with col_pdf1:
            # 텍스트로 다운로드 (Markdown)
            full_text = f"# {topic}\n"
            if subtitle:
                full_text += f"### {subtitle}\n\n"
            full_text += "---\n\n"

            toc = st.session_state.get("toc", [])
            if toc:
                full_text += "## 목차\n\n"
                for ch in toc:
                    full_text += f"{ch['num']}. {ch['title']}\n"
                full_text += "\n---\n\n"

            for i, (key, ch_data) in enumerate(sorted(chapters.items(), key=lambda x: int(x[0]))):
                full_text += f"## Chapter {key}: {ch_data['title']}\n\n"
                full_text += ch_data["content"] + "\n\n---\n\n"

            st.download_button(
                "📥 원고 저장 (Markdown)",
                data=full_text.encode("utf-8"),
                file_name=f"{topic[:20]}_원고.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col_pdf2:
            # 텍스트 파일
            st.download_button(
                "📥 원고 저장 (TXT)",
                data=full_text.encode("utf-8"),
                file_name=f"{topic[:20]}_원고.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.info("💡 Markdown 파일은 Notion, Obsidian, Word에서 열 수 있어요. PDF 변환은 각 앱에서 가능합니다.")

# ── 탭 2: 표지 & 목업 ──
with tab2:
    st.markdown("### 🖼️ 표지 디자인")

    # 표지 컬러 선택
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cover_color = st.color_picker("표지 배경색", value="#d63384")
    with col_c2:
        text_color = st.color_picker("텍스트 색상", value="#ffffff")

    # 표지 미리보기 (HTML/CSS)
    short_title = topic[:30] if len(topic) > 30 else topic
    short_subtitle = subtitle[:50] if subtitle and len(subtitle) > 50 else (subtitle or "")

    cover_html = f"""
    <div style="
        width: 260px;
        height: 370px;
        background: linear-gradient(135deg, {cover_color}, {cover_color}dd);
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 24px;
        box-shadow: 8px 8px 24px rgba(0,0,0,0.2);
        margin: 16px auto;
        text-align: center;
    ">
        <div style="font-size:40px;margin-bottom:12px">📘</div>
        <div style="color:{text_color};font-size:16px;font-weight:700;font-family:'Noto Serif KR',serif;line-height:1.4;margin-bottom:12px">{short_title}</div>
        <div style="width:40px;height:2px;background:{text_color};opacity:0.5;margin:8px 0"></div>
        <div style="color:{text_color};font-size:11px;opacity:0.85;line-height:1.5">{short_subtitle}</div>
    </div>
    """
    st.markdown(cover_html, unsafe_allow_html=True)

    # 목업 스타일 선택
    st.markdown("**📱 목업 스타일 선택:**")
    mockup_styles = [
        ("태블릿 3D", "아이패드에 표지가 표시된 3D 목업", "📱"),
        ("하드커버 책", "실물 하드커버 책 형태", "📗"),
        ("손에 든 책", "사람 손이 책을 잡고 있는 목업", "🤝"),
        ("비스듬히 세운", "약간 기울어져 세워진 책 표현", "📐"),
        ("플로팅", "공중에 떠 있는 느낌의 목업", "✨"),
        ("밀친 책", "책이 펼쳐지는 느낌의 목업", "📖"),
        ("프리미엄 다크", "어두운 배경에 고급스러운 표현", "🌑"),
    ]

    selected_mockup = st.session_state.get("selected_mockup", "태블릿 3D")
    cols = st.columns(4)
    for i, (style, desc, icon) in enumerate(mockup_styles):
        with cols[i % 4]:
            is_sel = selected_mockup == style
            border = "2px solid #e05c2a" if is_sel else "1px solid #eee"
            bg = "#fff0eb" if is_sel else "white"
            if st.button(f"{icon} {style}", key=f"mockup_{i}", use_container_width=True,
                        help=desc):
                st.session_state.selected_mockup = style
                st.rerun()

    if st.button("🎨 목업 생성하기", use_container_width=False):
        st.info(f"'{selected_mockup}' 스타일로 생성! (실제 이미지 생성은 Canva/Midjourney 프롬프트를 참고하세요)")
        with st.expander("🎨 Midjourney 프롬프트"):
            prompt = f"ebook mockup, {selected_mockup.lower()} style, book cover with gradient background {cover_color}, title '{short_title}', professional product photo, white background, 4k"
            st.code(prompt)

# ── 탭 3: 상세페이지 HTML ──
with tab3:
    st.markdown("### 🌐 상세페이지 HTML 생성")

    if not copy_sections:
        st.info("카피라이팅 단계를 먼저 완성해주세요.")
        if st.button("← 카피라이팅으로"):
            st.switch_page("pages/03_카피라이팅.py")
    else:
        if st.button("🚀 상세페이지 HTML 생성", use_container_width=False):
            with st.spinner("HTML 상세페이지 생성 중..."):
                sections_text = "\n\n".join([f"[{k}]\n{v}" for k, v in copy_sections.items()])
                prompt = f"""
다음 카피를 사용해서 전자책 판매 상세페이지 HTML을 만들어주세요.

전자책: {topic}
표지 색상: {st.session_state.get('cover_color', '#d63384') if 'cover_color' in st.session_state else '#d63384'}

카피 내용:
{sections_text[:3000]}

요구사항:
- 완전한 HTML 파일 (<!DOCTYPE html> 포함)
- 모바일 반응형
- 전문적인 디자인 (CSS 인라인 또는 <style> 태그)
- 섹션별로 잘 구분
- 구매 버튼 포함 (링크는 #으로)
- 한국어
"""
                html_result = generate_text(prompt, max_tokens=6000)

                # HTML 정제
                import re
                clean_html = re.sub(r'```html|```', '', html_result).strip()

                st.download_button(
                    "📥 상세페이지 HTML 다운로드",
                    data=clean_html.encode("utf-8"),
                    file_name=f"{topic[:20]}_상세페이지.html",
                    mime="text/html",
                    use_container_width=True
                )

                with st.expander("👀 미리보기"):
                    st.components.v1.html(clean_html, height=600, scrolling=True)

# ── 배포 가이드 링크 ──
st.markdown("---")
col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
with col_nav2:
    if st.button("🚀 배포 가이드 →", use_container_width=True):
        if st.session_state.project_name:
            save_project(st.session_state.project_name, dict(st.session_state))
        st.switch_page("pages/05_배포가이드.py")

st.markdown('</div>', unsafe_allow_html=True)
