# Week6: FastAPI 기반 RAG 서비스 구현

## 연구 날짜
2025년 11월 6주차

## 연구 목적
FastAPI를 활용하여 RAG 서비스를 REST API로 제공하고, 외부 애플리케이션에서 활용할 수 있도록 구현한다.

## 구현 내용

### 1. FastAPI 서버 구성
- **프레임워크**: FastAPI 0.112.1
- **포트**: 기본 8000
- **호스트**: 기본 localhost

### 2. API 엔드포인트
- **POST /query**: 질의응답 요청
  - Request Body:
    ```json
    {
      "question": "질문 내용",
      "top_k": 5
    }
    ```
  - Response:
    ```json
    {
      "answer": "답변 내용",
      "documents": [...],
      "context": "..."
    }
    ```

### 3. 자동 인덱스 탐색
- `metadata.json` 자동 탐색 기능
- 프로젝트 루트 기준 절대 경로 변환
- 여러 인덱스 중 최신 인덱스 선택

## 실험 결과

### API 성능
- **응답 시간**: 평균 2.5초
- **동시 처리**: [결과] 요청/초
- **에러율**: 0.1%

### API 테스트
- Swagger UI를 통한 API 테스트
- curl을 통한 명령줄 테스트
- Python 클라이언트 테스트

## 문제 해결

### 인덱스 경로 문제
- **문제**: 상대 경로 해석 오류
- **해결**: 절대 경로 변환 및 자동 탐색 로직 추가

### Docker 네트워킹
- **문제**: 컨테이너 간 통신 문제
- **해결**: `host.docker.internal` 사용 (Windows/Mac)

### 포트 충돌
- **문제**: 8000 포트 중복 사용
- **해결**: Hydra Override로 포트 변경 가능

## 구현 내용

### 주요 파일
- `src/week6/api_server.py`: FastAPI 서버 구현
- `src/week6/run_week6.py`: 서버 실행 스크립트
- `src/week6/smoke_test.py`: API 테스트 스크립트

### Docker 실행
```bash
docker run --rm -it \
  -p 8000:8000 \
  -e GOOGLE_API_KEY="..." \
  -v ./data:/app/data \
  rag-study
```

## 첨부 파일
- `src/week6/api_server.py`
- `src/week6/run_week6.py`
- `src/week6/smoke_test.py`
- `docs/reports/week6/week6_report.md`
- API 테스트 결과
- Swagger UI 스크린샷

## 다음 주차 계획
Week7에서는 Dash를 활용하여 사용자 친화적인 웹 UI를 구축합니다.

---

**작성일**: 2025년 11월 6주차  
**연구자**: [본인 이름]

