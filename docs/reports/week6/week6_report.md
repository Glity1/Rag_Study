# Week 6 Report — FastAPI RAG 서비스

## 1. 학습 목표
- Week4 RAG 체인을 FastAPI 엔드포인트로 노출  
- `POST /query` 스펙 확정 및 스모크 테스트  
- Docker 환경에서 실행 가능하도록 준비

---

## 2. 실행 요약

| 항목 | 내용 |
|------|------|
| 실행 명령 | `python src/week6/run_week6.py` |
| Hydra 설정 | `conf/week6.yaml` |
| 기본 포트 | 8000 (`server.port`) |
| 엔드포인트 | `POST /query` (request: `{question, top_k}`) |
| 의존 인덱스 | `data/processed/index/<slug>/<strategy>/` |

추가 명령 예:
```powershell
# 포트 9000, 특정 인덱스 사용
python src/week6/run_week6.py server.port=9000 paths.index_root=data/processed/index/20201231-34-63

# 모델 변경
python src/week6/run_week6.py rag.model_name=gemini-2.5-flash

# MMR 검색 및 LLM 파라미터 조정
python src/week6/run_week6.py rag.use_mmr=true rag.mmr_diversity=0.5 rag.temperature=0.7 rag.top_p=0.9 rag.top_k=40

# Docker Compose로 실행
docker-compose --profile week6 up

# Docker 내에서 Hydra override
docker run --rm -it -p 8000:8000 rag-study src/week6/run_week6.py server.host=0.0.0.0
```

**참고**: 인덱스 경로는 자동으로 탐색됩니다. `index.faiss` 파일이 있는 디렉토리를 재귀적으로 찾아 사용합니다.

**주요 기능**:
- ✅ **MMR 검색 지원**: `use_mmr=true`로 다양성 있는 검색 결과 제공
- ✅ **LLM 파라미터 조율**: `temperature`, `top_p`, `top_k` 파라미터 지원

---

## 3. 테스트 결과

### 스모크 테스트
```powershell
python src/week6/smoke_test.py --url http://localhost:8000/query --question "Dash UI는 어떻게 연결되나요?"
```
응답: 약 1.8초, 정상 동작.

### Swagger
- `http://localhost:8000/docs` → `POST /query`  
- 요청 바디:
  ```json
  {
    "question": "LangChain RAG 파이프라인을 요약해줘",
    "top_k": 5
  }
  ```
- 응답 예시:
  ```json
  {
    "answer": "1) Week2에서 PDF를 전처리하고 ... 3) Week6 FastAPI가 이를 서비스합니다."
  }
  ```

---

## 4. 주요 이슈 & 해결
| 이슈 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError: week4` | 패키지 경로 인식 실패 | `sys.path`에 `src` 추가 |
| `metadata.json not found` | 기본 경로가 최상위 인덱스 가리킴 | `determine_index_dir`에서 포인터 기반 탐색 보완 |
| `Connection refused` | FastAPI 미실행 상태에서 Dash 호출 | Dash 가이드에 서버 실행 선행 명시 |
| `timed out` | LLM 호출 지연 | httpx 기본 timeout(5초) → 15초로 확장 검토 |

---

## 5. 운영 체크포인트
- ✅ `GOOGLE_API_KEY` 환경변수 주입 (Docker run 시 `-e` 옵션)  
- ✅ 404 로그는 루트(`/`) 요청이므로 무시 가능, `/query`만 사용  
- ✅ FastAPI 실행 로그는 `outputs/week6/<timestamp>/run_week6.log`에 저장  
- ✅ Dockerfile을 통해 `CMD ["src/week6/run_week6.py"]` 기본 실행 확인

---

## 6. 다음 단계
- Week7 Dash UI에서 `ui.api_endpoint`를 FastAPI 주소와 일치시키기  
- 8000/8050 포트 충돌 방지 위해 Hydra override 예시 문서화  
- 추후 확장:  
  - 응답에 근거 문단을 포함시키기 (`metadata` 활용)  
  - 로깅/모니터링(예: 구조화 로그, 타임스탬프) 추가  
  - Docker Compose로 FastAPI + Dash 연동
