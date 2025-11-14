# Week 7 Report — Dash UI 통합

## 1. 학습 목표
- Week6 FastAPI RAG API를 소비하는 Dash UI 구축  
- 사용자가 질문을 입력하고 응답을 시각적으로 확인할 수 있는 인터페이스 구현  
- Docker를 활용한 UI 배포 가능성 검토

---

## 2. 실행 요약

| 항목 | 내용 |
|------|------|
| 실행 명령 | `python src/week7/run_week7.py` |
| Hydra 설정 | `conf/week7.yaml` (`ui.host`, `ui.port`, `ui.api_endpoint`) |
| 기본 포트 | 8050 |
| 의존 서비스 | FastAPI RAG API (Week6, 포트 8000) |

추가 명령 예  
```powershell
# API 엔드포인트 변경 및 디버그 모드
python src/week7/run_week7.py ui.api_endpoint=http://localhost:9000/query ui.debug=true

# Docker Compose로 Week6와 Week7 동시 실행 (권장)
docker-compose --profile full up

# Docker 환경에서 실행
docker run --rm -it -p 8050:8050 rag-study \
  src/week7/run_week7.py ui.api_endpoint=http://host.docker.internal:8000/query
```

**Docker Compose 사용**: `docker-compose --profile full up`으로 Week6와 Week7을 동시에 실행할 수 있습니다. 자동으로 `http://week6:8000/query`로 연결됩니다.

---

## 3. UI 기능 요약
- 텍스트 입력 영역 + “질문하기” 버튼
- API 호출 성공 시 LLM 응답 표시 (줄바꿈 유지)
- 입력이 비었거나 실패 시 안내 메시지 노출  
  - 예: `요청에 실패했습니다: [WinError 10061] ...`
- Swagger(`http://localhost:8000/docs`)와 함께 사용해 백엔드 상태 확인

---

## 4. 테스트 결과

| 시나리오 | 결과 |
|----------|------|
| FastAPI 실행 후 Dash 실행 | 정상 작동, 응답 2~3초 |
| FastAPI 미실행 상태 | `Connection refused` → 오류 메시지 표시 |
| API 타임아웃 | `timed out` → 사용자에게 안내 메시지 출력 |
| 404 로그 | `/` 요청 시 404지만, 이는 루트 라우트가 없어서 발생 → 기능 영향 없음 |

UI 로그:
```
Dash is running on http://0.0.0.0:8050/
 * Running on http://127.0.0.1:8050
 * Running on http://192.168.100.65:8050
```

## 5. 배포 메모
- FastAPI(8000)와 Dash(8050) 포트 모두 Docker에서 expose 필요  
- 로컬 연동 시 `ui.api_endpoint` → `http://localhost:8000/query`  
- Docker Compose 사용 시 `ui.api_endpoint` → `http://week6:8000/query` (서비스 이름 사용)
- `docker-compose --profile full up`으로 두 서비스를 동시에 실행 가능
- 자세한 내용은 `README_DOCKER.md` 참조

---
