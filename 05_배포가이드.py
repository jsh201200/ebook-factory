import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.storage import init_session
from utils.styles import STYLE, render_nav, render_steps

st.set_page_config(page_title="배포 가이드 | 전자책 팩토리", page_icon="📘", layout="wide", initial_sidebar_state="collapsed")
init_session()
st.markdown(STYLE, unsafe_allow_html=True)
render_nav(st.session_state.get("project_name", ""))
render_steps(5)

st.markdown('<div class="page-title">🚀 배포 가이드</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">완성된 전자책을 판매 플랫폼에 업로드하세요.</div>', unsafe_allow_html=True)
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

topic = st.session_state.get("topic", "")

# ── 완성 요약 ──
chapters = st.session_state.get("chapters", {})
copy_sections = st.session_state.get("copy_sections", {})
toc = st.session_state.get("toc", [])

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📊 완성 현황")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("챕터", f"{len(chapters)}/{len(toc)}")
with col2:
    total_chars = sum(v.get("char_count", 0) for v in chapters.values())
    st.metric("총 글자 수", f"{total_chars:,}")
with col3:
    st.metric("카피 섹션", f"{len(copy_sections)}/11")
with col4:
    st.metric("예상 페이지", f"~{total_chars // 400}")
st.markdown('</div>', unsafe_allow_html=True)

# ── 플랫폼별 가이드 ──
platforms = {
    "크몽": {
        "icon": "🟠",
        "desc": "국내 1위 프리랜서 마켓. 전자책 카테고리 활성화.",
        "steps": [
            "크몽 판매자 등록 (사업자 or 개인)",
            "디지털 상품 → 전자책 카테고리 선택",
            "상세페이지 HTML 내용을 에디터에 붙여넣기",
            "PDF 파일 업로드 (최대 500MB)",
            "가격 설정: 9,900원 ~ 39,000원 권장",
            "썸네일 이미지 등록 (800x600px)"
        ],
        "tip": "💡 첫 달은 9,900원으로 시작해서 리뷰 쌓기 추천"
    },
    "오픈채팅": {
        "icon": "💬",
        "desc": "카카오 오픈채팅으로 직접 판매. 수수료 0%.",
        "steps": [
            "오픈채팅방 개설 (주제 관련 커뮤니티)",
            "스마트스토어 or 텀블벅에 상품 등록",
            "링크를 오픈채팅에 공유",
            "구글 폼으로 구매 확인 후 PDF 발송",
        ],
        "tip": "💡 초반엔 오픈채팅이 가장 빠른 판매 채널"
    },
    "유료 앱": {
        "icon": "📱",
        "desc": "프립, 클래스101 등 콘텐츠 플랫폼.",
        "steps": [
            "클래스101: 전자책 단독 상품으로 등록 가능",
            "탈잉: PDF 강의 자료로 등록",
            "브런치스토어: 카카오 브런치에서 판매"
        ],
        "tip": "💡 플랫폼 자체 트래픽 활용 가능"
    }
}

for platform, info in platforms.items():
    with st.expander(f"{info['icon']} {platform}", expanded=platform == "크몽"):
        st.markdown(f"<small style='color:#888'>{info['desc']}</small>", unsafe_allow_html=True)
        for i, step in enumerate(info["steps"], 1):
            st.markdown(f"{i}. {step}")
        st.info(info["tip"])

# ── 체크리스트 ──
st.markdown("---")
st.markdown("### ✅ 출시 전 체크리스트")

checklist_items = [
    "목차 최종 확인",
    "모든 챕터 탈고 완료",
    "오탈자 검토",
    "PDF 변환 완료",
    "표지 이미지 준비",
    "판매 카피 완성",
    "상세페이지 등록",
    "가격 설정",
    "홍보 채널 준비",
]

for item in checklist_items:
    key = f"check_{item}"
    if key not in st.session_state:
        st.session_state[key] = False
    st.session_state[key] = st.checkbox(item, value=st.session_state[key], key=f"cb_{item}")

done_count = sum(1 for item in checklist_items if st.session_state.get(f"check_{item}", False))
st.markdown(f"""
<div class="progress-bar-wrap">
    <div class="progress-bar-fill" style="width:{int(done_count/len(checklist_items)*100)}%"></div>
</div>
<small style='color:#888'>{done_count}/{len(checklist_items)} 완료</small>
""", unsafe_allow_html=True)

if done_count == len(checklist_items):
    st.success("🎉 모든 준비 완료! 이제 판매를 시작하세요!")

# ── 처음으로 ──
st.markdown("---")
col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
with col_h2:
    if st.button("📘 새 전자책 시작하기", use_container_width=True):
        # 세션 초기화
        for key in list(st.session_state.keys()):
            if key not in ["gemini_api_key"]:
                del st.session_state[key]
        st.switch_page("app.py")

st.markdown('</div>', unsafe_allow_html=True)
