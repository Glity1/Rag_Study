# GitHub 업로드 가이드

이 문서는 Rag_Study 프로젝트를 GitHub에 업로드할 때의 체크리스트와 가이드를 제공합니다.

---

## 📋 업로드 전 체크리스트

### 1. 민감한 정보 제거

#### ✅ 필수 확인 사항:
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] 코드 내에 하드코딩된 API 키가 없는지 확인
- [ ] `GOOGLE_API_KEY` 등 민감한 정보가 코드에 직접 작성되지 않았는지 확인

#### 확인 방법:
```bash
# .env 파일 검색
grep -r "GOOGLE_API_KEY" . --exclude-dir=.git

# 하드코딩된 키 검색
grep -r "AIza" . --exclude-dir=.git
```

---

### 2. 불필요한 파일 제외

#### ✅ 제외해야 할 항목:
- [ ] `__pycache__/` 디렉토리
- [ ] `.pyc`, `.pyo` 파일
- [ ] 가상환경 디렉토리 (`venv/`, `.venv/`, `env/`)
- [ ] IDE 설정 파일 (`.vscode/`, `.idea/`)
- [ ] 로그 파일 (`*.log`, `outputs/`)
- [ ] 개인 학습 기록 (`study.txt` - 선택적)
- [ ] 대용량 데이터 파일 (`data/raw/` - 선택적)

#### 포함 여부 결정:
- `data/processed/`: 샘플 데이터 포함 권장 (실행 예시용)
- `outputs/`: 제외 권장 (실행 결과물)
- `docs/`, `notebooks/`: 포함 권장 (문서화)

---

### 3. README.md 확인

#### ✅ README에 포함되어야 할 내용:
- [ ] 프로젝트 소개
- [ ] 설치 방법
- [ ] 실행 방법
- [ ] 환경 설정 (API 키 등)
- [ ] 프로젝트 구조
- [ ] 주요 기능 설명

현재 `README.md`가 잘 작성되어 있습니다.

---

### 4. 라이선스 추가 (선택적)

#### MIT License 예시:
```markdown
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted...
```

`LICENSE` 파일을 추가하는 것을 권장합니다.

---

## 🚀 GitHub 업로드 단계

### 방법 1: Git 명령어 사용 (권장)

#### 1단계: Git 저장소 초기화
```bash
cd Rag_Study
git init
```

#### 2단계: .gitignore 확인
```bash
# .gitignore 파일이 있는지 확인
ls -la .gitignore
```

#### 3단계: 파일 추가
```bash
# 모든 파일 추가 (gitignore 제외)
git add .

# 추가된 파일 확인
git status
```

#### 4단계: 첫 커밋
```bash
git commit -m "Initial commit: RAG Study 프로젝트

- 7주차 RAG 파이프라인 구현
- LangChain, LangGraph 기반 RAG 체인
- FastAPI + Dash UI 구현
- Docker Compose 지원"
```

#### 5단계: GitHub 저장소 생성
1. GitHub에서 새 저장소 생성
2. 저장소 이름: `rag-study` (또는 원하는 이름)
3. Public 또는 Private 선택
4. README, .gitignore, license 추가하지 않기 (이미 있음)

#### 6단계: 원격 저장소 연결 및 푸시
```bash
# 원격 저장소 추가 (YOUR_USERNAME을 실제 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/rag-study.git

# 기본 브랜치를 main으로 설정
git branch -M main

# 푸시
git push -u origin main
```

---

### 방법 2: GitHub Desktop 사용

1. **GitHub Desktop 설치 및 로그인**
2. **File → Add Local Repository**
   - Local path: `C:\Users\qqtta\OneDrive\Desktop\rag\Rag_Study`
3. **변경사항 확인**
   - `.gitignore`에 의해 제외된 파일 확인
4. **커밋 작성**
   - Summary: "Initial commit: RAG Study 프로젝트"
   - Description: 상세 설명 작성
5. **Publish repository**
   - Repository name: `rag-study`
   - Description: "7주차 RAG 파이프라인 학습 프로젝트"
   - Public/Private 선택

---

## ⚠️ 주의사항

### 1. API 키 보안
- ❌ **절대 하드코딩하지 마세요**
- ✅ 환경 변수 또는 `.env` 파일 사용
- ✅ `.env`는 반드시 `.gitignore`에 포함

### 2. 대용량 파일
- `data/raw/` 폴더의 PDF 파일은 용량이 클 수 있음
- GitHub는 100MB 이상 파일에 경고 표시
- 필요시 Git LFS 사용 또는 샘플만 포함

### 3. 개인 정보
- `study.txt`에 개인 정보가 있다면 제외 고려
- 현재 `.gitignore`에 포함되어 있음

### 4. 실행 결과물
- `outputs/` 폴더는 제외 권장
- 실행 로그는 불필요

---

## 📝 추천 커밋 메시지

### 첫 커밋
```
Initial commit: RAG Study 프로젝트

- 7주차 RAG 파이프라인 구현
- LangChain, LangGraph 기반 RAG 체인
- FastAPI + Dash UI 구현
- Docker Compose 지원
- Hydra 기반 설정 관리
```

### 기능별 커밋 예시
```
feat: Week5 LangGraph 데모 추가

- langgraph_rag.py 모듈 구현
- 프롬프트 튜닝 후 자동 실행
- 인덱스 경로 자동 탐색 기능
```

```
fix: 의존성 충돌 해결

- langchain-huggingface 제거
- langchain_community.embeddings로 통합
- langchain-core 버전 호환성 수정
```

```
docs: 프로젝트 구조 문서화

- ARCHITECTURE.md 추가
- LANGCHAIN_VS_LANGGRAPH.md 추가
- workflows 순서도 문서 추가
```

---

## 🔍 업로드 전 최종 확인

### 필수 확인 명령어
```bash
# 1. .env 파일이 제외되는지 확인
git status | grep .env

# 2. 민감한 정보 검색
grep -r "AIza" . --exclude-dir=.git
grep -r "sk-" . --exclude-dir=.git

# 3. 대용량 파일 확인
find . -type f -size +10M -not -path "./.git/*"

# 4. 추가될 파일 목록 확인
git status
```

---

## 📦 저장소 설정 권장사항

### GitHub 저장소 설정:
1. **Description**: "7주차 RAG 파이프라인 학습 프로젝트 - LangChain, LangGraph, FastAPI, Dash"
2. **Topics**: `rag`, `langchain`, `langgraph`, `fastapi`, `dash`, `nlp`, `vector-search`
3. **README**: 자동으로 표시됨
4. **License**: MIT 또는 Apache 2.0 권장

### .github 폴더 추가 (선택적)
```
.github/
  └── ISSUE_TEMPLATE/
      └── bug_report.md
  └── PULL_REQUEST_TEMPLATE.md
```

---

## 🎯 업로드 후 확인사항

1. **파일 확인**
   - 모든 소스 코드가 올라갔는지 확인
   - `.env` 파일이 올라가지 않았는지 확인

2. **README 확인**
   - GitHub에서 README가 잘 표시되는지 확인
   - 이미지나 링크가 깨지지 않았는지 확인

3. **클론 테스트**
   ```bash
   # 다른 디렉토리에서 클론 테스트
   cd ..
   git clone https://github.com/YOUR_USERNAME/rag-study.git rag-study-test
   cd rag-study-test
   # 실행 가능한지 확인
   ```

---

## 💡 추가 팁

### 1. .gitignore 예외 처리
특정 파일을 강제로 포함하려면:
```bash
git add -f data/processed/index/sample/metadata.json
```

### 2. Git LFS 사용 (대용량 파일)
```bash
# Git LFS 설치 후
git lfs install
git lfs track "*.faiss"
git lfs track "*.pdf"
git add .gitattributes
```

### 3. 브랜치 전략
```bash
# main: 안정 버전
# develop: 개발 버전
# feature/weekX: 주차별 기능 브랜치
```

---

## ✅ 최종 체크리스트

업로드 전:
- [ ] `.gitignore` 파일 확인
- [ ] `.env` 파일 제외 확인
- [ ] API 키 하드코딩 없음 확인
- [ ] README.md 완성도 확인
- [ ] 불필요한 파일 제외 확인
- [ ] 커밋 메시지 작성
- [ ] 저장소 설명 및 Topics 설정

업로드 후:
- [ ] 파일 목록 확인
- [ ] README 표시 확인
- [ ] 클론 테스트
- [ ] 실행 가능 여부 확인

---

이 가이드를 따라 안전하고 체계적으로 GitHub에 업로드할 수 있습니다! 🚀

