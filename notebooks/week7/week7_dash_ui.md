# 📗 7주차: Dash UI를 통한 RAG 인터랙션

## 학습 목표
- Week6 FastAPI 서버를 소비하는 Dash 기반 웹 UI 구축  
- 사용자 질문 입력 → RAG 응답 출력 흐름 검증  
- API 연결 상태 및 오류 핸들링을 이해

---

## 1. 시스템 구성
```mermaid
flowchart LR
    user((사용자 브라우저)) --> Dash[Dash UI (Week7)]
    Dash --> FastAPI[FastAPI RAG API (Week6)]
    FastAPI --> Gemini
    FastAPI --> FAISS[Index + metadata]
```

---

## 2. 주요 파일

| 파일 | 역할 | 비고 |
|------|------|------|
| `dash_app.py` | Dash 레이아웃/콜백 정의 (`POST /query` 호출) | `API_ENDPOINT` 변수 |
| `run_week7.py` | Hydra 설정 → Dash 서버 실행 | `conf/week7.yaml` |

---

## 3. Hydra 실행 예시
```powershell
# 기본값 (포트 8050, API 8000)
python src/week7/run_week7.py

# API 엔드포인트 변경
python src/week7/run_week7.py ui.api_endpoint=http://localhost:9000/query

# 다른 포트/디버그 모드
python src/week7/run_week7.py ui.port=9001 ui.debug=true

# Docker Compose (Week6+Week7 동시)
docker-compose --profile full up
```

실행 후 브라우저에서 `http://localhost:8050` 접속 → 질문 입력 → "질문하기" 클릭

**중요**: Week6 API 서버가 먼저 실행되어 있어야 합니다!

---

## 4. Dash 콜백 로직
```python
@app.callback(Output("answer", "children"),
              Input("submit", "n_clicks"),
              State("question", "value"))
def ask_rag(n_clicks, question):
    if not n_clicks:
        return ""
    if not question or not question.strip():
        return "질문을 입력해주세요."
    try:
        response = httpx.post(API_ENDPOINT, json={"question": question.strip()})
        response.raise_for_status()
        data = response.json()
        return data.get("answer", "응답을 읽을 수 없습니다.")
    except httpx.HTTPError as exc:
        return f"요청에 실패했습니다: {exc}"
```
- FastAPI 서버와의 연결 상태가 좋지 않으면 에러 메시지를 그대로 표시  
- `API_ENDPOINT`는 `run_week7.py`에서 Hydra 설정을 통해 주입

---

## 5. 체크리스트
- [ ] FastAPI 서버(Week6)가 먼저 기동 중인지 확인 (`python src/week6/run_week6.py`)  
- [ ] Dash 실행 후 터미널에 “Dash is running on http://0.0.0.0:8050” 로그 확인  
- [ ] 브라우저 404는 `/` 라우트가 없어서 발생할 수 있음 → `/` 대신 기본 페이지가 뜨므로 무시 가능  
- [ ] “연결 거부” → FastAPI 포트/주소 불일치  
- [ ] “timed out” → FastAPI 서버 미응답 또는 LLM 응답 지연  
- [ ] `httpx.ConnectError` 발생 시 사용자에게 “API 서버가 실행 중인지 확인하세요” 메시지 표시 (코드 반영)

---

## 6. Docker 실행

```bash
# Week7만 실행 (Week6가 별도로 실행 중이어야 함)
docker-compose --profile week7 up

# Week6와 Week7 동시 실행 (권장)
docker-compose --profile full up
```

Docker 환경에서는 `ui.api_endpoint`가 자동으로 `http://week6:8000/query`로 설정됩니다.

---

## 7. 확장 아이디어
- **대화 로그 추가**: 이전 질문/답변을 리스트로 누적  
- **문서 하이라이트**: FastAPI에서 반환한 근거 텍스트를 함께 표시  
- **입력 검증 강화**: 질문 길이 제한, 금지어 필터 등  
- **연결 상태 표시**: API 서버 연결 상태를 실시간으로 표시

---

## 8. 실제 실행 결과 요약
- 테스트 스크립트: `python scripts/test_new_features.py` (Dash는 FastAPI와 함께 수동 확인)
- Docker Compose: `docker-compose --profile full up` 한 번으로 FastAPI/Dash 동시 실행
- 관찰 메모
  | 시나리오 | 결과 |
  |----------|------|
  | FastAPI 실행 후 Dash 실행 | 정상 동작, 응답 ≈ 2~3초 |
  | FastAPI 미실행 상태 | “요청에 실패했습니다: API 서버가 실행 중인지 확인하세요” 출력 |
  | Docker 환경 | `ui.api_endpoint` 자동으로 `http://week6:8000/query` 로 설정 |
- 상세 리포트: `docs/results/ACTUAL_EXECUTION_RESULTS.md`

---

## 9. 마무리
Week1~7 전체 파이프라인을 통해 다음을 달성했습니다.

1. PDF 전처리 → 청킹 → 임베딩 → 인덱스  
2. RAG 체인 구성 및 평가  
3. 프롬프트 튜닝  
4. FastAPI 서버화  
5. Dash UI 제공  

