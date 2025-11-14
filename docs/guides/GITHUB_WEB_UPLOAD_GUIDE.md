# GitHub 웹 인터페이스 직접 업로드 가이드

Git 명령어 없이 GitHub 웹에서 직접 파일을 업로드할 때, 다른 사람들이 보기 편하도록 정리하는 방법입니다.

---

## 📋 업로드 전 준비사항

### 1. 업로드할 파일 정리

#### ✅ 반드시 포함해야 할 파일:
```
Rag_Study/
├── README.md                    ⭐ 가장 중요!
├── README_DOCKER.md
├── requirements.txt
├── environment.yml
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── src/                         ⭐ 모든 소스 코드
│   ├── week1/
│   ├── week2/
│   ├── week3/
│   ├── week4/
│   ├── week5/
│   ├── week6/
│   └── week7/
├── conf/                        ⭐ Hydra 설정
│   ├── week2.yaml
│   ├── week3.yaml
│   ├── week4.yaml
│   ├── week5.yaml
│   ├── week6.yaml
│   └── week7.yaml
├── docs/                        ⭐ 문서
│   ├── general/
│   ├── reports/
│   └── workflows/
└── notebooks/                   ⭐ 학습 노트
    ├── week1/
    ├── week2/
    ├── week3/
    ├── week4/
    ├── week5/
    ├── week6/
    └── week7/
```

#### ❌ 제외해야 할 파일:
- `.env` (API 키)
- `__pycache__/` (Python 캐시)
- `outputs/` (실행 결과물)
- `*.log` (로그 파일)
- `study.txt` (개인 학습 기록)
- `data/raw/` (대용량 PDF - 선택적)
- `.vscode/`, `.idea/` (IDE 설정)

#### 🤔 선택적 포함:
- `data/processed/index/` (샘플 인덱스 - 실행 예시용으로 포함 권장)
- `data/processed/` 하위의 일부 샘플 데이터

---

## 🎯 다른 사람들이 보기 편하도록 하는 방법

### 1. README.md 강화 (가장 중요!)

#### 현재 README에 추가하면 좋은 내용:

```markdown
# 🚀 빠른 시작 (Quick Start)

## 1분 안에 시작하기

```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_USERNAME/rag-study.git
cd rag-study

# 2. 가상환경 생성 및 패키지 설치
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. 환경 변수 설정
# .env 파일 생성 후 GOOGLE_API_KEY 추가

# 4. 실행
python src/week2/run_week2.py
```

## 📁 프로젝트 구조 한눈에 보기

```
rag-study/
├── src/week1/     # RAG 개념 학습
├── src/week2/     # PDF 전처리 & 청킹
├── src/week3/     # 임베딩 & 벡터 인덱스
├── src/week4/     # RAG 체인 구성 ⭐ 핵심 모듈
├── src/week5/     # 프롬프트 튜닝 + LangGraph
├── src/week6/     # FastAPI 서버
└── src/week7/     # Dash UI
```

각 주차는 이전 주차의 결과물을 사용합니다.
```

---

### 2. 폴더 구조 최적화

#### 권장 구조:
```
Rag_Study/
├── 📄 README.md              (프로젝트 소개)
├── 📄 README_DOCKER.md       (Docker 가이드)
├── 📄 requirements.txt       (의존성)
├── 📄 environment.yml        (Conda 환경)
├── 📄 Dockerfile             (Docker 이미지)
├── 📄 docker-compose.yml     (Docker Compose)
├── 📄 .gitignore             (제외 파일 목록)
│
├── 📁 src/                   (소스 코드)
│   ├── week1/
│   ├── week2/
│   ├── week3/
│   ├── week4/                ⭐ 핵심 모듈
│   ├── week5/
│   ├── week6/
│   └── week7/
│
├── 📁 conf/                  (Hydra 설정)
│   └── week*.yaml
│
├── 📁 docs/                  (문서)
│   ├── general/              (아키텍처, 비교 분석)
│   ├── reports/              (주차별 보고서)
│   └── workflows/            (순서도)
│
├── 📁 notebooks/             (학습 노트)
│   └── week*/
│
└── 📁 data/                  (데이터 - 샘플만)
    └── processed/
        └── index/            (샘플 인덱스)
```

---

### 3. README.md에 추가할 섹션

#### A. 프로젝트 미리보기 이미지 (선택적)
```markdown
![RAG Pipeline](docs/images/pipeline.png)
```

#### B. 기능 요약
```markdown
## ✨ 주요 기능

- 📄 **PDF 전처리**: 다양한 청킹 전략 지원
- 🔍 **벡터 검색**: FAISS 기반 고속 검색
- 🤖 **RAG 체인**: LangChain & LangGraph 지원
- 🎨 **프롬프트 튜닝**: 다양한 프롬프트 실험
- 🌐 **API 서버**: FastAPI 기반 REST API
- 💻 **웹 UI**: Dash 기반 인터랙티브 UI
```

#### C. 기술 스택 배지 (선택적)
```markdown
![Python](https://img.shields.io/badge/Python-3.11-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.2.16-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.112.1-teal)
![Docker](https://img.shields.io/badge/Docker-Supported-blue)
```

#### D. 사용 예시
```markdown
## 💡 사용 예시

### Week2: PDF 청킹
```python
python src/week2/run_week2.py
```

### Week6 + Week7: API + UI 동시 실행
```bash
docker-compose --profile full up
```
```

---

### 4. 파일명 및 폴더명 정리

#### ✅ 명확한 이름 사용:
- `run_week2.py` ✅ (명확)
- `main.py` ❌ (모호함)

#### ✅ 일관된 네이밍:
- 모든 주차: `run_weekX.py`
- 설정 파일: `conf/weekX.yaml`
- 문서: `docs/reports/weekX/weekX_report.md`

---

### 5. 샘플 데이터 포함 전략

#### 권장 방법:
```
data/
├── raw/                    (제외 또는 샘플 1개만)
│   └── sample.pdf
│
└── processed/              (샘플 인덱스 포함)
    └── index/
        └── sample/         (작은 샘플 인덱스)
            └── fixed/
                ├── metadata.json
                ├── index.faiss
                └── chunks_with_ids.json
```

**이유:**
- 사용자가 바로 실행해볼 수 있음
- 전체 데이터 없이도 동작 확인 가능
- 저장소 크기 최소화

---

### 6. 문서화 강화

#### 각 주차 폴더에 간단한 설명 추가:

**예시: `src/week4/README.md`** (선택적)
```markdown
# Week4: RAG 체인 구성

이 폴더는 RAG 체인의 핵심 모듈을 포함합니다.

## 주요 파일
- `rag_chain.py`: RAG 체인 구성 (다른 주차에서 재사용)
- `retrieval_eval.py`: 검색 평가
- `run_week4.py`: 실행 스크립트

## 사용법
```bash
python src/week4/run_week4.py
```
```

---

## 📤 GitHub 웹에서 업로드하는 방법

### 단계별 가이드:

#### 1단계: GitHub 저장소 생성
1. GitHub 로그인
2. 우측 상단 `+` → `New repository`
3. Repository name: `rag-study`
4. Description: "7주차 RAG 파이프라인 학습 프로젝트"
5. Public/Private 선택
6. **README, .gitignore, license 추가하지 않기** (이미 있음)
7. `Create repository` 클릭

#### 2단계: 파일 업로드
1. 저장소 페이지에서 `uploading an existing file` 클릭
2. 또는 `Add file` → `Upload files` 클릭

#### 3단계: 파일 드래그 앤 드롭
- 준비한 파일들을 드래그 앤 드롭
- **폴더 단위로 업로드 가능**

#### 4단계: 커밋
- Commit message: "Initial commit: RAG Study 프로젝트"
- `Commit changes` 클릭

---

## 🎨 다른 사람들이 보기 편하게 하는 팁

### 1. README 첫 화면 강화

```markdown
# 🎓 RAG Study - 7주차 RAG 파이프라인 학습 프로젝트

> LangChain, LangGraph, FastAPI, Dash를 활용한 완전한 RAG 시스템 구현

[![Python](https://img.shields.io/badge/Python-3.11-blue)]()
[![LangChain](https://img.shields.io/badge/LangChain-0.2.16-green)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

## 🚀 빠른 시작

```bash
git clone https://github.com/YOUR_USERNAME/rag-study.git
cd rag-study
pip install -r requirements.txt
python src/week2/run_week2.py
```

## 📚 학습 커리큘럼

| 주차 | 내용 | 실행 명령 |
|------|------|----------|
| Week1 | RAG 개념 학습 | `python src/week1/week1_hands_on.py` |
| Week2 | PDF 전처리 & 청킹 | `python src/week2/run_week2.py` |
| Week3 | 임베딩 & 벡터 인덱스 | `python src/week3/run_week3.py` |
| Week4 | RAG 체인 구성 | `python src/week4/run_week4.py` |
| Week5 | 프롬프트 튜닝 | `python src/week5/run_week5.py` |
| Week6 | FastAPI 서버 | `python src/week6/run_week6.py` |
| Week7 | Dash UI | `python src/week7/run_week7.py` |

## 🏗️ 프로젝트 구조

```
rag-study/
├── src/          # 주차별 소스 코드
├── conf/         # Hydra 설정 파일
├── docs/         # 문서 및 보고서
├── notebooks/    # 학습 노트
└── data/         # 데이터 (샘플 포함)
```

## 📖 상세 문서

- [프로젝트 아키텍처](docs/guides/ARCHITECTURE.md)
- [LangChain vs LangGraph](docs/guides/LANGCHAIN_VS_LANGGRAPH.md)
- [Docker 사용 가이드](README_DOCKER.md)
- [GitHub 업로드 가이드](docs/GITHUB_WEB_UPLOAD_GUIDE.md)

## ⚙️ 환경 설정

1. Python 3.11 설치
2. 패키지 설치: `pip install -r requirements.txt`
3. `.env` 파일 생성:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## 🤝 기여하기

이슈나 PR을 환영합니다!

## 📄 라이선스

MIT License
```

### 2. Topics 추가

GitHub 저장소 설정에서 Topics 추가:
- `rag`
- `langchain`
- `langgraph`
- `fastapi`
- `dash`
- `nlp`
- `vector-search`
- `retrieval-augmented-generation`
- `python`
- `docker`

### 3. 저장소 설명

**Repository description:**
```
7주차 RAG 파이프라인 학습 프로젝트 | LangChain, LangGraph, FastAPI, Dash | PDF 전처리 → 벡터 검색 → RAG 체인 → API → UI
```

---

## 📦 업로드할 파일 우선순위

### 1순위 (필수):
- ✅ `README.md` (강화된 버전)
- ✅ `src/` (모든 소스 코드)
- ✅ `conf/` (Hydra 설정)
- ✅ `requirements.txt`
- ✅ `environment.yml`
- ✅ `.gitignore`

### 2순위 (권장):
- ✅ `docs/` (문서)
- ✅ `notebooks/` (학습 노트)
- ✅ `Dockerfile`, `docker-compose.yml`
- ✅ `README_DOCKER.md`

### 3순위 (선택):
- ⚠️ `data/processed/index/` (샘플만)
- ❌ `data/raw/` (제외 또는 샘플 1개)
- ❌ `outputs/` (제외)

---

## 🎯 최종 체크리스트

### 업로드 전:
- [ ] README.md가 명확하고 완성도 높은지 확인
- [ ] .gitignore에 민감한 정보 제외 확인
- [ ] 불필요한 파일 제거 (__pycache__, outputs, logs)
- [ ] 샘플 데이터만 포함 (전체 데이터는 제외)
- [ ] 폴더 구조가 명확한지 확인
- [ ] 각 주차별 실행 방법이 README에 있는지 확인

### 업로드 후:
- [ ] README가 GitHub에서 잘 표시되는지 확인
- [ ] Topics 추가
- [ ] Description 작성
- [ ] 저장소를 클론해서 실행 테스트

---

## 💡 추가 팁

### 1. README에 스크린샷 추가 (선택적)
- Dash UI 스크린샷
- 실행 결과 스크린샷
- 아키텍처 다이어그램

### 2. 예제 코드 추가
README에 간단한 사용 예시를 포함하면 좋습니다.

### 3. 문제 해결 섹션
자주 발생하는 문제와 해결 방법을 README에 추가.

---

이 가이드를 따라하면 다른 사람들이 프로젝트를 쉽게 이해하고 사용할 수 있습니다! 🚀

