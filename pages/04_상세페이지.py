import streamlit as st
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import init_session, save_project
from utils.gemini import generate_text

st.set_page_config(page_title="상세페이지 | 전자책 팩토리", page_icon="📘", layout="wide", initial_sidebar_state="collapsed")
init_session()

st.title("🎨 상세페이지 디자인")
st.markdown("---")

topic = st.session_state.get("topic", "")
subtitle = st.session_state.get("subtitle", "")
chapters = st.session_state.get("chapters", {})
toc = st.session_state.get("toc", [])
copy_sections = st.session_state.get("copy_sections", {})

if not topic:
    st.warning("⚠️ 먼저 기획 정보를 입력해주세요!")
    if st.button("← 처음으로"):
        st.switch_page("app.py")
    st.stop()

tab1, tab2, tab3 = st.tabs(["📄 원고 & 표지", "🖼️ 목업", "🌐 상세페이지 HTML"])

# ── 탭1: 원고 & 표지 ──
with tab1:
    if not chapters:
        st.info("아직 작성된 챕터가 없어요.")
        if st.button("← AI 집필로"):
            st.switch_page("pages/02_집필.py")
    else:
        total_chars = sum(v.get("char_count", 0) for v in chapters.values())
        est_pages = total_chars // 400

        col1, col2, col3 = st.columns(3)
        col1.metric("완성 챕터", len(chapters))
        col2.metric("총 글자 수", f"{total_chars:,}")
        col3.metric("예상 페이지", f"~{est_pages}p")

        # 표지 디자인
        st.subheader("🎨 표지 디자인")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            cover_color = st.color_picker("배경색", value="#d63384", key="cover_color")
        with col_c2:
            text_color = st.color_picker("텍스트 색상", value="#ffffff", key="text_color")

        short_title = topic[:25] if len(topic) > 25 else topic
        short_sub = subtitle[:45] if subtitle and len(subtitle) > 45 else (subtitle or "")

        # 표지 미리보기
        st.markdown(f"""
        <div style="width:220px;height:310px;background:linear-gradient(135deg,{cover_color},{cover_color}cc);
        border-radius:8px;display:flex;flex-direction:column;justify-content:center;align-items:center;
        padding:20px;box-shadow:8px 8px 24px rgba(0,0,0,0.25);margin:16px auto;text-align:center;">
            <div style="font-size:32px;margin-bottom:10px">📘</div>
            <div style="color:{text_color};font-size:14px;font-weight:700;line-height:1.4;margin-bottom:10px">{short_title}</div>
            <div style="width:30px;height:2px;background:{text_color};opacity:0.5;margin:6px 0"></div>
            <div style="color:{text_color};font-size:10px;opacity:0.85;line-height:1.5">{short_sub}</div>
        </div>
        """, unsafe_allow_html=True)

        # 원고 다운로드 3버튼
        st.subheader("📥 원고 저장")
        full_text = f"# {topic}\n"
        if subtitle:
            full_text += f"### {subtitle}\n\n"
        full_text += "---\n\n"
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
            st.download_button(
                "📄 바로 PDF (TXT)",
                data=full_text.encode("utf-8"),
                file_name=f"{topic[:20]}_원고.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_d2:
            st.download_button(
                "✏️ 편집 후 PDF (MD)",
                data=full_text.encode("utf-8"),
                file_name=f"{topic[:20]}_원고.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_d3:
            if st.button("📣 상세페이지 디자인하기 →", use_container_width=True):
                st.session_state["active_tab"] = 2
                st.rerun()

        st.info("💡 MD 파일은 Notion, Obsidian에서 열 수 있어요. 폰트/이미지 편집 후 PDF 변환 가능!")

# ── 탭2: 목업 ──
with tab2:
    st.subheader("📱 목업 스타일 선택")

    MOCKUP_STYLES = [
        ("태블릿 3D", "아이패드에 표지가 표시된 3D 목업", "📱"),
        ("하드커버 책", "실물 하드커버 책 형태", "📗"),
        ("손에 든 책", "사람 손이 책을 잡고 있는 목업", "🤝"),
        ("비스듬히 세운", "약간 기울어져 세워진 표현", "📐"),
        ("플로팅", "공중에 떠 있는 느낌", "✨"),
        ("밀친 책", "책이 펼쳐지는 느낌", "📖"),
        ("프리미엄 다크", "어두운 배경 고급스러운 표현", "🌑"),
    ]

    selected_mockup = st.session_state.get("selected_mockup", "태블릿 3D")
    cols = st.columns(4)
    for i, (style, desc, icon) in enumerate(MOCKUP_STYLES):
        with cols[i % 4]:
            is_sel = selected_mockup == style
            label = ("✅ " if is_sel else "") + f"{icon} {style}"
            if st.button(label, key=f"mockup_{i}", use_container_width=True, help=desc):
                st.session_state.selected_mockup = style
                st.rerun()

    st.markdown(f"**선택됨: {selected_mockup}**")

    if st.button("🎨 목업 Midjourney 프롬프트 생성", use_container_width=False):
        cover_color = st.session_state.get("cover_color", "#d63384")
        short_title = topic[:20]
        prompts = {
            "태블릿 3D": f"iPad mockup 3D, ebook cover displayed on screen, gradient background {cover_color}, title '{short_title}', product photo, white background, 4k",
            "하드커버 책": f"hardcover book mockup, ebook cover '{short_title}', gradient {cover_color}, professional product shot, white background, 4k",
            "손에 든 책": f"hand holding book mockup, ebook '{short_title}', gradient cover {cover_color}, lifestyle photo, clean background, 4k",
            "비스듬히 세운": f"book standing at angle mockup, ebook cover '{short_title}', gradient {cover_color}, minimal product photo, 4k",
            "플로팅": f"floating book mockup, ebook '{short_title}', gradient {cover_color}, levitating, dramatic shadows, 4k",
            "밀친 책": f"book open spread mockup, ebook '{short_title}', gradient cover {cover_color}, flat lay, 4k",
            "프리미엄 다크": f"premium dark background book mockup, ebook '{short_title}', gradient {cover_color}, luxury product photo, dark studio, 4k",
        }
        st.code(prompts.get(selected_mockup, ""))

    # 추가 이미지 업로드
    st.markdown("---")
    st.subheader("🖼️ 추가 이미지 갤러리")
    st.caption("상세페이지에 배치할 이미지를 업로드하세요. (제품 사진, 목업 등)")
    uploaded_files = st.file_uploader(
        "이미지 업로드",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
    if uploaded_files:
        cols = st.columns(3)
        for i, f in enumerate(uploaded_files):
            with cols[i % 3]:
                st.image(f, use_container_width=True)

# ── 탭3: 상세페이지 HTML ──
with tab3:
    st.subheader("🌐 상세페이지 HTML 생성")
    if not copy_sections:
        st.info("카피라이팅 단계를 먼저 완성해주세요.")
        if st.button("← 카피라이팅으로"):
            st.switch_page("pages/03_카피라이팅.py")
    else:
        if st.button("🚀 상세페이지 HTML 생성", use_container_width=False):
            with st.spinner("HTML 생성 중..."):
                sections_text = "\n\n".join([f"[{k}]\n{v}" for k, v in list(copy_sections.items())[:6]])
                cover_color = st.session_state.get("cover_color", "#d63384")
                prompt = f"""전자책 판매 상세페이지 HTML을 만들어주세요.

전자책: {topic}
주색상: {cover_color}

카피:
{sections_text}

요구사항:
- 완전한 HTML (DOCTYPE 포함)
- 모바일 반응형
- 전문적 디자인
- 구매 버튼 포함 (#링크)
- 한국어
절대 금지사항:
- 첫 줄에 "네", "알겠습니다", "작성해 드리겠습니다" AI 응답 멘트 금지
- ** ## 같은 마크다운 금지
- "물론이죠!", "~해드립니다" AI 말투 금지
- 같은 말 반복 금지
- 두리뭉실한 표현 금지
- 뻔한 추상적 표현 금지"""
                result = generate_text(prompt, max_tokens=6000)
                clean_html = re.sub(r'```html|```', '', result).strip()

                st.download_button(
                    "📥 HTML 다운로드",
                    data=clean_html.encode("utf-8"),
                    file_name=f"{topic[:20]}_상세페이지.html",
                    mime="text/html",
                    use_container_width=False
                )
                with st.expander("👀 미리보기"):
                    st.components.v1.html(clean_html, height=600, scrolling=True)

# 배포 가이드
st.markdown("---")
col_n1, col_n2, col_n3 = st.columns([1, 2, 1])
with col_n2:
    if st.button("🚀 배포 가이드 →", use_container_width=True):
        if st.session_state.project_name:
            save_project(st.session_state.project_name, dict(st.session_state))
        st.switch_page("pages/05_배포가이드.py")
