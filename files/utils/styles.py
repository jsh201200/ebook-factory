STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Noto+Serif+KR:wght@400;700&display=swap');

/* ── 전체 기본 ── */
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* ── 배경 ── */
.stApp {
    background: #faf9f7;
}

/* ── 사이드바 숨기기 ── */
section[data-testid="stSidebar"] { display: none; }

/* ── 헤더 숨기기 ── */
header[data-testid="stHeader"] { display: none; }

/* ── 상단 네비게이션 ── */
.top-nav {
    background: white;
    border-bottom: 1px solid #eee;
    padding: 12px 32px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0;
    position: sticky;
    top: 0;
    z-index: 100;
}
.logo {
    font-size: 18px;
    font-weight: 700;
    color: #1a1a1a;
}

/* ── 스텝 인디케이터 ── */
.step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    padding: 20px 0 8px;
    flex-wrap: wrap;
}
.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
}
.step-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 600;
    border: 2px solid #ddd;
    background: white;
    color: #999;
    position: relative;
    z-index: 1;
}
.step-circle.done {
    background: #e8f5e9;
    border-color: #4caf50;
    color: #4caf50;
}
.step-circle.active {
    background: #e05c2a;
    border-color: #e05c2a;
    color: white;
}
.step-label {
    font-size: 11px;
    color: #999;
    margin-top: 4px;
    text-align: center;
    white-space: nowrap;
}
.step-label.active { color: #e05c2a; font-weight: 600; }
.step-line {
    width: 40px;
    height: 2px;
    background: #ddd;
    margin-top: -20px;
    margin-bottom: 20px;
}
.step-line.done { background: #4caf50; }

/* ── 페이지 타이틀 ── */
.page-title {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    color: #1a1a1a;
    margin: 24px 0 8px;
    font-family: 'Noto Serif KR', serif;
}
.page-subtitle {
    text-align: center;
    font-size: 14px;
    color: #777;
    margin-bottom: 28px;
}

/* ── 진행 바 ── */
.progress-bar-wrap {
    background: #f0ede8;
    border-radius: 4px;
    height: 6px;
    margin: 8px 0 16px;
    overflow: hidden;
}
.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #e05c2a, #f08050);
    border-radius: 4px;
    transition: width 0.4s ease;
}

/* ── 카드 ── */
.card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    border: 1px solid #eee;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.card-title {
    font-size: 16px;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 4px;
}
.card-subtitle {
    font-size: 13px;
    color: #666;
    margin-bottom: 16px;
}

/* ── 버튼 ── */
.stButton > button {
    border-radius: 8px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.btn-primary > button {
    background: #e05c2a !important;
    color: white !important;
    border: none !important;
    padding: 10px 24px !important;
}
.btn-primary > button:hover {
    background: #c94e22 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(224,92,42,0.3) !important;
}
.btn-secondary > button {
    background: white !important;
    color: #e05c2a !important;
    border: 1px solid #e05c2a !important;
}

/* ── 챕터 카드 ── */
.chapter-card {
    background: white;
    border: 1px solid #eee;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s;
}
.chapter-card:hover {
    border-color: #e05c2a;
    box-shadow: 0 2px 8px rgba(224,92,42,0.1);
}
.chapter-num {
    font-size: 12px;
    color: #e05c2a;
    font-weight: 600;
}
.chapter-title {
    font-size: 15px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 2px 0;
}

/* ── 섹션 탭 ── */
.section-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}
.section-tab {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    background: #f5f5f5;
    color: #666;
    cursor: pointer;
    border: 1px solid transparent;
}
.section-tab.active {
    background: #fff0eb;
    color: #e05c2a;
    border-color: #e05c2a;
}

/* ── 입력 필드 ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    border-radius: 8px !important;
    border-color: #ddd !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #e05c2a !important;
    box-shadow: 0 0 0 2px rgba(224,92,42,0.15) !important;
}

/* ── 태그 ── */
.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    background: #fff0eb;
    color: #e05c2a;
    margin: 2px;
}

/* ── 완료 뱃지 ── */
.badge-done {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    background: #e8f5e9;
    color: #388e3c;
    font-weight: 600;
}
.badge-wip {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    background: #fff3e0;
    color: #f57c00;
    font-weight: 600;
}

/* ── 변경 옵션 버튼 그룹 ── */
.option-group {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 12px 0;
}
.option-btn {
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid #ddd;
    background: white;
    font-size: 13px;
    color: #555;
    cursor: pointer;
    font-family: 'Noto Sans KR', sans-serif;
    transition: all 0.15s;
}
.option-btn:hover {
    border-color: #e05c2a;
    color: #e05c2a;
}

/* ── 구분선 ── */
hr { border-color: #eee; }

/* ── 숨김 ── */
.hide { display: none !important; }

/* 메인 컨텐츠 최대 너비 */
.main-wrap {
    max-width: 820px;
    margin: 0 auto;
    padding: 0 16px 80px;
}
</style>
"""

def render_nav(project_name=""):
    from streamlit.components.v1 import html as st_html
    import streamlit as st
    st.markdown(f"""
    <div class="top-nav">
        <span class="logo">📘 전자책 팩토리</span>
        {"<span style='color:#999;font-size:13px;'>📁 " + project_name + "</span>" if project_name else ""}
    </div>
    """, unsafe_allow_html=True)

STEPS = [
    ("기획 입력", "주제, 타겟, 핵심 노하우"),
    ("AI 집필", "목차 생성 → 챕터 초안"),
    ("카피라이팅", "판매 카피 + 이미지"),
    ("상세페이지", "템플릿 디자인 생성"),
    ("배포 가이드", "업로드 대시보드"),
]

def render_steps(current: int):
    html = '<div class="step-indicator">'
    for i, (name, sub) in enumerate(STEPS):
        step_num = i + 1
        if step_num < current:
            cls = "done"
            icon = "✓"
        elif step_num == current:
            cls = "active"
            icon = str(step_num)
        else:
            cls = ""
            icon = str(step_num)

        label_cls = "active" if step_num == current else ""
        html += f'<div class="step-item"><div class="step-circle {cls}">{icon}</div><div class="step-label {label_cls}">{name}</div></div>'
        if i < len(STEPS) - 1:
            line_cls = "done" if step_num < current else ""
            html += f'<div class="step-line {line_cls}"></div>'
    html += '</div>'
    import streamlit as st
    st.markdown(html, unsafe_allow_html=True)
