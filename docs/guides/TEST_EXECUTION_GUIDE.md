# 실제 실행 테스트 가이드

## 개요

새로 구현된 기능들(MMR 검색, LangGraph 조건부 분기, LLM 파라미터, 이미지 플레이스홀더)을 실제로 실행하고 결과를 문서에 반영하는 방법입니다.

---

## 사전 준비

### 1. 가상환경 활성화

```bash
# Windows
conda activate rag-study
# 또는
.\rag-study\Scripts\activate

# Linux/Mac
conda activate rag-study
# 또는
source rag-study/bin/activate
```

### 2. 환경 변수 확인

`.env` 파일에 `GOOGLE_API_KEY`가 설정되어 있는지 확인:

```bash
# .env 파일 확인
cat .env
# 또는
type .env  # Windows
```

### 3. 인덱스 확인

Week3에서 생성한 인덱스가 있는지 확인:

```bash
# 인덱스 확인
ls data/processed/index/*/recursive/metadata.json
# 또는 Windows
dir data\processed\index\*\recursive\metadata.json
```

---

## 테스트 실행 방법

### 방법 1: 자동 테스트 스크립트 사용

```bash
# 프로젝트 루트에서 실행
cd Rag_Study
python scripts/test_new_features.py
```

이 스크립트는 다음을 테스트합니다:
1. MMR 검색 vs 일반 유사도 검색 비교
2. LLM 파라미터 (temperature, top_p, top_k) 조합 테스트
3. LangGraph 조건부 분기 테스트

결과는 `outputs/feature_tests/test_results_*.json`에 저장됩니다.

### 방법 2: 수동 테스트

#### 1. MMR 검색 테스트

```bash
# 일반 유사도 검색
python src/week4/run_week4.py \
  rag.question="그랜드코리아레저의 코로나 대응 전략은 무엇인가?" \
  rag.use_mmr=false \
  rag.top_k=5

# MMR 검색 (diversity=0.5)
python src/week4/run_week4.py \
  rag.question="그랜드코리아레저의 코로나 대응 전략은 무엇인가?" \
  rag.use_mmr=true \
  rag.mmr_diversity=0.5 \
  rag.top_k=5

# MMR 검색 (diversity=0.8, 다양성 우선)
python src/week4/run_week4.py \
  rag.question="그랜드코리아레저의 코로나 대응 전략은 무엇인가?" \
  rag.use_mmr=true \
  rag.mmr_diversity=0.8 \
  rag.top_k=5
```

**비교 포인트**:
- 응답 시간
- 답변 내용의 다양성
- 검색된 문서의 중복도

#### 2. LLM 파라미터 테스트

```bash
# 기본값 (temperature=0.0)
python src/week4/run_week4.py \
  rag.temperature=0.0 \
  rag.top_p=null \
  rag.top_k_llm=null

# temperature만 조정
python src/week4/run_week4.py \
  rag.temperature=0.5

# top_p 추가
python src/week4/run_week4.py \
  rag.temperature=0.5 \
  rag.top_p=0.9

# top_k 추가
python src/week4/run_week4.py \
  rag.temperature=0.5 \
  rag.top_k_llm=40

# 모든 파라미터 조합
python src/week4/run_week4.py \
  rag.temperature=0.5 \
  rag.top_p=0.9 \
  rag.top_k_llm=40
```

**비교 포인트**:
- 답변의 창의성/일관성
- 응답 시간
- 답변 길이

#### 3. LangGraph 조건부 분기 테스트

```bash
# 기본 플로우 (조건부 분기 없음)
python src/week5/run_week5.py \
  langgraph.enable_conditional_branching=false \
  langgraph.demo_questions='["그랜드코리아레저의 코로나 대응 전략은 무엇인가?"]'

# 조건부 분기 활성화
python src/week5/run_week5.py \
  langgraph.enable_conditional_branching=true \
  langgraph.reretrieve_threshold=0.3 \
  langgraph.max_reretrieves=1 \
  langgraph.demo_questions='["그랜드코리아레저의 코로나 대응 전략은 무엇인가?"]'

# 키워드 기반 프롬프트 테스트
python src/week5/run_week5.py \
  langgraph.enable_conditional_branching=true \
  langgraph.keyword_prompts='{"긴급": "긴급 상황에 대한 답변입니다. 빠르고 정확한 정보를 제공하세요."}' \
  langgraph.demo_questions='["긴급 상황에서의 대응 방법은?"]'
```

**비교 포인트**:
- 재검색 발생 여부
- 응답 시간 (재검색 시 증가)
- 키워드 감지 및 프롬프트 분기

#### 4. 이미지 플레이스홀더 테스트

```bash
# 이미지 플레이스홀더 비활성화 (기본)
python src/week2/run_week2.py \
  pdf.insert_image_placeholders=false

# 이미지 플레이스홀더 활성화
python src/week2/run_week2.py \
  pdf.insert_image_placeholders=true \
  pdf.image_placeholder_format="Image: [{name}] (Page {page}, {width}x{height})"

# 결과 확인
cat data/processed/*/full_text.txt | grep -i "image"
# 또는 Windows
findstr /i "image" data\processed\*\full_text.txt
```

**확인 포인트**:
- `full_text.txt`에 이미지 플레이스홀더가 포함되어 있는지
- 청크 파일에 이미지 정보가 포함되어 있는지

---

## 결과 수집 및 문서 반영

### 1. 테스트 결과 수집

각 테스트 실행 후 다음 정보를 수집:

- **MMR 검색**:
  - 응답 시간 (유사도 vs MMR)
  - 답변 내용 비교
  - 검색된 문서 수

- **LLM 파라미터**:
  - 각 파라미터 조합별 응답 시간
  - 답변 길이 및 품질
  - 파라미터별 차이점

- **LangGraph 조건부 분기**:
  - 재검색 발생 여부 및 횟수
  - 키워드 감지 여부
  - 응답 시간 비교

- **이미지 플레이스홀더**:
  - 플레이스홀더 삽입 여부
  - 청크에 포함 여부
  - RAG 답변에서 이미지 인식 여부

### 2. 문서 업데이트

수집한 결과를 다음 문서에 반영:

1. **`docs/guides/MMR_SEARCH_GUIDE.md`**:
   - 실제 실행 결과 섹션 추가
   - 성능 비교 데이터 추가

2. **`docs/guides/LLM_PARAMETERS_GUIDE.md`**:
   - 실제 테스트 결과 섹션 추가
   - 파라미터별 성능 데이터 추가

3. **`docs/guides/LANGGRAPH_CONDITIONAL_BRANCHING.md`**:
   - 실제 실행 예시 추가
   - 재검색 발생 케이스 추가

4. **`docs/IMAGE_PLACEHOLDER_GUIDE.md`**:
   - 실제 삽입 결과 예시 추가
   - RAG 답변에서의 활용 예시 추가

### 3. 결과 예시 형식

```markdown
## 실제 실행 결과

### 테스트 환경
- 날짜: 2024-11-14
- 인덱스: `data/processed/index/20201231-34-63/recursive`
- 질문: "그랜드코리아레저의 코로나 대응 전략은 무엇인가?"

### MMR 검색 비교

| 항목 | 일반 유사도 | MMR (diversity=0.5) | MMR (diversity=0.8) |
|------|------------|-------------------|-------------------|
| 응답 시간 | 1.2초 | 1.4초 | 1.5초 |
| 답변 길이 | 245자 | 280자 | 310자 |
| 검색 문서 중복도 | 높음 | 중간 | 낮음 |

**관찰 사항**:
- MMR 검색은 약간 느리지만 더 다양한 문서를 검색
- diversity=0.8일 때 답변이 더 포괄적
```

---

## 문제 해결

### 모듈을 찾을 수 없는 경우

```bash
# 가상환경 확인
conda env list
# 또는
conda info --envs

# 가상환경 활성화
conda activate rag-study

# 필요한 패키지 재설치
pip install -r requirements.txt
```

### API 키 오류

```bash
# .env 파일 확인
cat .env

# 환경 변수 직접 설정 (임시)
export GOOGLE_API_KEY="your-api-key"  # Linux/Mac
set GOOGLE_API_KEY=your-api-key  # Windows
```

### 인덱스를 찾을 수 없는 경우

```bash
# Week3 실행하여 인덱스 생성
python src/week3/run_week3.py
```

---

## 다음 단계

1. 테스트 실행 및 결과 수집
2. 결과를 문서에 반영
3. 커리큘럼 준수 체크리스트 업데이트

---

**작성일**: 2024-11-14

