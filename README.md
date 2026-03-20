# 📘 전자책 팩토리

AI가 전자책 기획부터 집필, 카피, 상세페이지까지 자동으로 만들어주는 도구.

## 🚀 빠른 시작

### 1. 설치

```bash
git clone https://github.com/jsh201200/ebook-factory
cd ebook-factory
pip install -r requirements.txt
```

### 2. API 키 설정 (선택)

`.env` 파일 생성:
```
GEMINI_API_KEY=AIza여기에입력
```

또는 앱 실행 후 UI에서 직접 입력 가능.

### 3. 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 열기.

---

## 📋 기능

| 단계 | 기능 |
|------|------|
| ① 기획 입력 | 주제 추천, 타겟/노하우/톤 입력, 페이지 수 설정 |
| ② AI 집필 | 목차 자동 생성, 전체/개별 챕터 집필, 변경 옵션 |
| ③ 카피라이팅 | 11개 섹션 판매 카피 자동 생성 |
| ④ 상세페이지 | 원고 다운로드, 표지 디자인, HTML 상세페이지 |
| ⑤ 배포 가이드 | 플랫폼별 업로드 가이드, 체크리스트 |

## ✏️ 변경 옵션 (챕터별)
- 🎨 톤 변경 (친근/전문/직접/감성)
- 📏 길이 조정 (더 길게/짧게)
- 🔄 섹션 재생성
- 🪝 훅 강화
- 📣 CTA 추가

## 🔑 Gemini API 키 발급
1. [Google AI Studio](https://aistudio.google.com) 접속
2. "Get API key" 클릭
3. 무료 플랜으로 충분 (Gemini 2.5 Flash)

## 📁 프로젝트 저장
- `saved_projects/` 폴더에 JSON으로 저장
- 여러 프로젝트 관리 가능
- 언제든 불러오기 가능
