import streamlit as st

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.page-title { text-align: center; font-size: 28px; font-weight: 700; color: #1a1a1a; margin: 24px 0 8px; }
.page-subtitle { text-align: center; font-size: 14px; color: #777; margin-bottom: 28px; }
.card { background: white; border-radius: 12px; padding: 20px 24px; margin-bottom: 16px; border: 1px solid #eee; }
.progress-bar-wrap { background: #f0ede8; border-radius: 4px; height: 6px; margin: 8px 0 16px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: linear-gradient(90deg, #e05c2a, #f08050); border-radius: 4px; }
.badge-done { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; background: #e8f5e9; color: #388e3c; font-weight: 600; }
.badge-wip { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; background: #fff3e0; color: #f57c00; font-weight: 600; }
.main-wrap { max-width: 820px; margin: 0 auto; padding: 0 16px 80px; }
</style>
"""

def render_nav(project_name=""):
    st.markdown(f"""
    <div style="background:white;border-bottom:1px solid #eee;padding:12px 32px;margin-bottom:16px">
        <span style="font-size:18px;font-weight:700">📘 전자책 팩토리</span>
        {"&nbsp;&nbsp;<span style='color:#999;font-size:13px'>📁 " + project_name + "</span>" if project_name else ""}
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
    cols = st.columns(len(STEPS))
    for i, (name, sub) in enumerate(STEPS):
        step_num = i + 1
        with cols[i]:
            if step_num < current:
                st.markdown(f"<div style='text-align:center;color:#4caf50'>✓<br><small>{name}</small></div>", unsafe_allow_html=True)
            elif step_num == current:
                st.markdown(f"<div style='text-align:center;color:#e05c2a;font-weight:700'>●<br><small>{name}</small></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center;color:#ccc'>○<br><small>{name}</small></div>", unsafe_allow_html=True)
