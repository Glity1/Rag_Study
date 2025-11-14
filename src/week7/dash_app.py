"""7주차 Dash UI."""

from __future__ import annotations

import httpx  # 백엔드 REST API 호출을 위한 HTTP 클라이언트
import dash  # Dash 애플리케이션 객체 생성을 위한 기본 패키지
import dash_bootstrap_components as dbc  # Bootstrap 스타일 컴포넌트를 제공
from dash import Input, Output, State, dcc, html  # Dash 코어/HTML 컴포넌트와 콜백 유틸리티

API_ENDPOINT = "http://localhost:8000/query"  # RAG 백엔드 질의 엔드포인트
BOOTSTRAP_ICONS = (
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css"
)  # Bootstrap 아이콘 CDN

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, BOOTSTRAP_ICONS],  # Bootstrap 테마 및 아이콘 적용
)

alerts = html.Div(  # 다양한 Alert 컴포넌트를 모아둔 블록
    [
        dbc.Alert(
            [
                html.I(className="bi bi-info-circle-fill me-2"),
                "정보성 알림 예시입니다.",
            ],
            color="info",
            className="d-flex align-items-center",
        ),
        dbc.Alert(
            [
                html.I(className="bi bi-check-circle-fill me-2"),
                "성공 알림 예시입니다.",
            ],
            color="success",
            className="d-flex align-items-center",
        ),
        dbc.Alert(
            [
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                "주의 알림 예시입니다.",
            ],
            color="warning",
            className="d-flex align-items-center",
        ),
        dbc.Alert(
            [
                html.I(className="bi bi-x-octagon-fill me-2"),
                "위험 알림 예시입니다.",
            ],
            color="danger",
            className="d-flex align-items-center",
        ),
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    [
                        dbc.CardHeader(html.H2("RAG Q&A 데모", className="mb-0")),
                        dbc.CardBody(
                            [
                                dbc.FormFloating(
                                    [
                                        dbc.Textarea(
                                            id="question",
                                            placeholder="질문을 입력하세요",
                                            style={"height": 160},
                                        ),
                                        dbc.Label("질문"),  # 부트스트랩 form-floating 스타일용 라벨
                                    ]
                                ),
                                dbc.Button(
                                    "질문하기",
                                    id="submit",
                                    color="primary",
                                    className="mt-3",
                                    n_clicks=0,
                                ),
                                dbc.Spinner(
                                    html.Div(
                                        id="answer",
                                        className="mt-4",
                                        style={"whiteSpace": "pre-wrap"},
                                    ),
                                    color="primary",
                                    delay_show=200,
                                ),
                            ]
                        ),
                    ],
                    className="shadow-sm",
                ),
                lg=6,
                md=8,
                sm=12,
            ),
            justify="center",
        ),
        dbc.Row(
            dbc.Col(
                dbc.Alert(
                    [
                        html.Strong("TIP: "),
                        "예) '회사 X의 주요 전략은 무엇인가요?'",
                    ],
                    color="info",
                    className="mt-4",
                ),
                lg=6,
                md=8,
                sm=12,
            ),
            justify="center",
        ),
        dbc.Row(
            dbc.Col(alerts, lg=6, md=8, sm=12),
            justify="center",
            className="mt-2",
        ),
        dcc.Store(id="answer-store"),
    ],
    fluid=True,
    className="py-5",
)




@app.callback(  # Dash 콜백: 버튼 클릭 시 백엔드에 질문을 보내고 결과를 렌더링
    Output("answer", "children"),  # 답변 영역 업데이트
    Input("submit", "n_clicks"),  # 버튼 클릭 횟수 입력
    State("question", "value"),  # 사용자 질문 텍스트 상태값
    prevent_initial_call=True,  # 초기 로딩 시 콜백 실행 방지
)
def ask_rag(n_clicks: int, question: str | None) -> dbc.Alert | str:
    """질문을 백엔드 RAG 서비스로 전달하고, 응답에 따라 알림 컴포넌트를 반환한다."""

    if not question or not question.strip():
        # 빈 입력일 경우 경고 메시지를 출력
        return dbc.Alert("질문을 입력해주세요.", color="warning", className="mb-0")
    try:
        # 백엔드 API에 POST 요청으로 질문 전달
        response = httpx.post(
            API_ENDPOINT,
            json={"question": question.strip()},
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as exc:
        # HTTP 오류 발생 시 사용자에게 에러 알림 제공
        return dbc.Alert(
            f"요청에 실패했습니다: {exc}",
            color="danger",
            className="mb-0",
        )

    answer = data.get("answer")
    if not answer:
        # 백엔드 응답에 answer 키가 없을 때 처리
        return dbc.Alert(
            "응답을 읽을 수 없습니다.",
            color="secondary",
            className="mb-0",
        )
    # 성공적으로 답변을 받으면 녹색 알림으로 표시
    return dbc.Alert(answer, color="success", className="mb-0")


if __name__ == "__main__":
    # 개발 편의를 위해 디버그 모드로 서버 실행
    app.run_server(host="0.0.0.0", port=8050, debug=True)
