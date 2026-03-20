import json
import os
import streamlit as st
from datetime import datetime

SAVE_DIR = "saved_projects"

def ensure_save_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)

def save_project(project_name: str, data: dict):
    ensure_save_dir()
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    path = os.path.join(SAVE_DIR, f"{project_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_project(project_name: str) -> dict:
    path = os.path.join(SAVE_DIR, f"{project_name}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_projects() -> list:
    ensure_save_dir()
    files = [f.replace(".json", "") for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
    return sorted(files)

def delete_project(project_name: str):
    path = os.path.join(SAVE_DIR, f"{project_name}.json")
    if os.path.exists(path):
        os.remove(path)

def init_session():
    defaults = {
        "step": 1,
        "project_name": "",
        "topic": "",
        "subtitle": "",
        "target": "",
        "knowhow": "",
        "tone": "친근하고 실용적인",
        "series": "단권",
        "page_count": 150,
        "toc": [],
        "chapters": {},
        "copy_sections": {},
        "gemini_api_key": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
