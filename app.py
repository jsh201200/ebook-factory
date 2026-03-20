from google import genai
from google.genai import types
import streamlit as st
import os

def get_api_key():
    api_key = ""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.session_state.get("gemini_api_key", "")
    return api_key

def generate_text(prompt: str, max_tokens: int = 8192) -> str:
    api_key = get_api_key()
    if not api_key:
        st.error("⚠️ Gemini API 키를 설정해주세요!")
        return ""
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_tokens)
        )
        return response.text
    except Exception as e:
        st.error(f"API 오류: {e}")
        return ""

def stream_text(prompt: str):
    api_key = get_api_key()
    if not api_key:
        st.error("⚠️ Gemini API 키를 설정해주세요!")
        return
    try:
        client = genai.Client(api_key=api_key)
        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=prompt
        ):
            if chunk.text:
                yield chunk.text
    except Exception as e:
        st.error(f"API 오류: {e}")
