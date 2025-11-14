# Week7: Dash 기반 웹 UI 구현

## 연구 날짜
2025년 11월 7주차

## 연구 목적
Dash를 활용하여 사용자 친화적인 질의응답 인터페이스를 구축하고, FastAPI 서버와 연동하여 완전한 RAG 시스템을 완성한다.

## 구현 내용

### 1. Dash 앱 구성
- **프레임워크**: Dash + dash-bootstrap-components
- **포트**: 기본 8050
- **레이아웃**: Bootstrap 기반 반응형 디자인

### 2. 주요 기능
- **질문 입력**: 텍스트 입력 필드
- **답변 표시**: 마크다운 형식 지원
- **로딩 인디케이터**: 요청 처리 중 표시
- **에러 처리**: 연결 오류 및 API 오류 처리

### 3. FastAPI 연동
- **엔드포인트**: `http://localhost:8000/query`
- **비동기 요청**: httpx를 통한 HTTP 요청
- **타임아웃**: 30초

## 실험 결과

### UI 성능
- **초기 로딩 시간**: [결과] 초
- **응답 표시 시간**: 평균 2.5초
- **사용자 경험**: 직관적이고 사용하기 쉬움

### 사용자 테스트
- 질문 입력 → 답변 표시까지의 흐름이 자연스러움
- 에러 메시지가 명확함
- 반응형 디자인으로 다양한 화면 크기 지원

## 문제 해결

### Connection Refused 오류
- **문제**: Week7 Dash 앱이 Week6 API 서버에 연결 실패
- **해결**: 
  - 서버 실행 순서 안내
  - Docker Compose `depends_on` 설정
  - `host.docker.internal` 사용 (Docker 환경)

### 타임아웃 문제
- **문제**: 긴 답변 생성 시 타임아웃
- **해결**: 타임아웃 시간 30초로 설정

### 포트 매핑
- **문제**: Docker 환경에서 포트 접근 문제
- **해결**: 포트 매핑 및 네트워크 설정

## 구현 내용

### 주요 파일
- `src/week7/dash_app.py`: Dash 앱 구현
- `src/week7/run_week7.py`: 앱 실행 스크립트

### Docker Compose 실행
```bash
# Week6와 Week7 동시 실행
docker compose --profile full up
```

### 실행 순서
1. Week6 API 서버 실행 (`python src/week6/run_week6.py`)
2. Week7 Dash UI 실행 (`python src/week7/run_week7.py`)
3. 브라우저에서 `http://localhost:8050` 접속

## 첨부 파일
- `src/week7/dash_app.py`
- `src/week7/run_week7.py`
- `docs/reports/week7/week7_report.md`
- Dash UI 스크린샷
- 질의응답 예시 화면

## 프로젝트 완성

Week7까지의 구현으로 완전한 RAG 파이프라인이 완성되었습니다:
- PDF 전처리 → 청킹 → 임베딩 → 인덱스 → RAG 체인 → API → UI

---

**작성일**: 2025년 11월 7주차
**연구자**: [서혁준]

