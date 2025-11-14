"""5주차 프롬프트 튜닝 유틸리티 (Google Gemini 수정본)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


@dataclass
class PromptVariant:
    name: str
    system: str
    user: str
    examples: Optional[List[Tuple[str, str]]] = None  # (질문, 답변) 형태의 few-shot 예시


class PromptTuner:
    """여러 프롬프트 조합을 LLM에 적용해 결과를 비교하는 클래스."""

    def __init__(
        self, 
        model_name: str = "gemini-2.5-flash", 
        temperature: float = 0.2,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
    ) -> None:
        llm_kwargs = {
            "model": model_name,
            "temperature": temperature,
            "convert_system_message_to_human": False,
        }
        
        # top_p, top_k 파라미터 추가
        if top_p is not None:
            llm_kwargs["top_p"] = float(top_p)
        if top_k is not None:
            llm_kwargs["top_k"] = int(top_k)
        
        self.llm = ChatGoogleGenerativeAI(**llm_kwargs)

    def run(self, variants: Iterable[PromptVariant]) -> Dict[str, str]:
        outputs: Dict[str, str] = {}
        for variant in variants:
            messages = []

            if variant.system:
                messages.append(SystemMessage(content=variant.system))

            if variant.examples:
                for question, answer in variant.examples:
                    messages.append(HumanMessage(content=question))
                    messages.append(AIMessage(content=answer))

            messages.append(HumanMessage(content=variant.user))
            
            # .invoke()는 AIMessage 객체를 반환합니다.
            response = self.llm.invoke(messages)
            
            # .content 속성에서 실제 텍스트 응답을 추출합니다.
            outputs[variant.name] = response.content
            
        return outputs


if __name__ == "__main__":
    print("환경변수(.env) 로드 중...")
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        print("--- [경고] ---")
        print("GOOGLE_API_KEY 환경변수가 설정되지 않았습니다.")
        print(".env 파일을 생성하고 'GOOGLE_API_KEY=\"...\"'를 입력하세요.")
        print("---------------")
        
    print("프롬프트 튜닝 시작...")
    tuner = PromptTuner()
    variants = [
        PromptVariant(
            name="baseline",
            system="당신은 도움이 되는 분석가입니다.",
            user="LangChain의 RAG 파이프라인에 대해 50자로 요약해 주세요."
        ),
        PromptVariant(
            name="cot",
            system="당신은 체계적으로 추론하는 AI 컨설턴트입니다. 답변을 내기 전 반드시 단계별로 사고 과정을 작성하세요.",
            user="LangChain의 RAG 파이프라인 구성 요소와 흐름을 설명해 주세요. 생각을 단계적으로 작성한 뒤 결론을 요약해 주세요."
        ),
        PromptVariant(
            name="structured",
            system=(
                "당신은 기술 문서를 작성하는 전문가입니다. "
                "답변은 반드시 JSON 형식으로 반환하세요. "
                "키는 'pipeline_overview', 'key_components', 'tips' 세 가지로 하고, "
                "각 값은 문자열 또는 문자열 리스트로 구성하세요."
            ),
            user="LangChain의 RAG 파이프라인을 요약하고, 핵심 구성 요소와 활용 팁을 알려주세요."
        ),
        PromptVariant(
            name="few_shot",
            system="당신은 시니어 AI 엔지니어입니다. 간결하면서도 실제 프로젝트 인사이트를 담아 답변하세요.",
            user="LangChain의 RAG 파이프라인을 요약하고, 성공적인 프로젝트 수행을 위한 조언을 제시해 주세요.",
            examples=[
                (
                    "Gemini API를 활용한 고객지원 챗봇 구축 단계를 요약해 줘.",
                    "1) 범위 정의 및 데이터 정리 -> 2) 프롬프트 설계와 테스트 -> 3) 배포 및 모니터링으로 정리할 수 있습니다."
                ),
                (
                    "LangChain 에이전트를 사용할 때 주의할 점은?",
                    "외부 도구 호출 오류 처리, 프롬프트 가드레일, 사용자 피드백 루프를 설계하는 것이 좋습니다."
                ),
            ],
        ),
    ]
    
    # user="요약해 주세요."는 LLM이 무엇을 요약할지 모르므로 
    # 데모를 위해 질문을 조금 더 구체화했습니다.
    
    results = tuner.run(variants)
    
    print("\n--- [튜닝 결과] ---")
    analytics: Dict[str, Dict[str, float]] = {}
    for name, response in results.items():
        print(f"--- Variant: [{name}] ---")
        print(response)
        print("-" * (17 + len(name)))

        analytics[name] = {
            "length_chars": len(response),
            "line_count": response.count("\n") + 1,
            "has_json": 1.0 if response.strip().startswith("{") else 0.0,
            "mentions_step": 1.0 if "1." in response or "①" in response else 0.0,
        }

    print("\n--- [간단 비교 지표] ---")
    header = f"{'Variant':<15}{'Chars':>8}{'Lines':>8}{'JSON?':>8}{'Steps?':>8}"
    print(header)
    print("-" * len(header))
    for name, stats in analytics.items():
        print(
            f"{name:<15}"
            f"{int(stats['length_chars']):>8}"
            f"{int(stats['line_count']):>8}"
            f"{'Y' if stats['has_json'] else 'N':>8}"
            f"{'Y' if stats['mentions_step'] else 'N':>8}"
        )