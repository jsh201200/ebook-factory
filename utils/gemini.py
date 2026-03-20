import google.generativeai as genai
import streamlit as st
import os

def get_gemini_client():
    # Streamlit Secrets → 환경변수 → 세션 순서로 키 찾기
    api_key = ""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.session_state.get("gemini_api_key", "")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

def generate_text(prompt: str, max_tokens: int = 8192) -> str:
    model = get_gemini_client()
    if not model:
        st.error("⚠️ Gemini API 키를 설정해주세요!")
        return ""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(max_output_tokens=max_tokens)
        )
        return response.text
    except Exception as e:
        st.error(f"API 오류: {e}")
        return ""

def stream_text(prompt: str):
    model = get_gemini_client()
    if not model:
        st.error("⚠️ Gemini API 키를 설정해주세요!")
        return
    try:
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        st.error(f"API 오류: {e}")
