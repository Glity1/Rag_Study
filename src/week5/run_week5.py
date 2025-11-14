from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import hydra
from dotenv import load_dotenv
from omegaconf import DictConfig, OmegaConf

# src 디렉토리를 sys.path에 추가하여 패키지 import 가능하게 함
CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent
ROOT_DIR = SRC_DIR.parent  # Rag_Study 루트 디렉토리

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from langchain_google_genai import ChatGoogleGenerativeAI  # noqa: E402
from langchain_community.embeddings import HuggingFaceEmbeddings  # noqa: E402
from prompt_tuning import PromptTuner, PromptVariant  # noqa: E402
from week4.rag_chain import DenseRetriever, load_documents_and_vectors  # noqa: E402
from langgraph_rag import build_rag_graph, preview_documents, run_rag  # noqa: E402

load_dotenv()


def ensure_google_api_key(required: bool) -> Optional[str]:
    key = os.getenv("GOOGLE_API_KEY")
    if required and not key:
        raise EnvironmentError("GOOGLE_API_KEY가 설정되지 않았습니다. 환경 변수 또는 .env 파일을 확인하세요.")
    return key


def build_variants(cfg_variants) -> List[PromptVariant]:
    variants: List[PromptVariant] = []
    for variant_cfg in cfg_variants:
        examples_cfg = variant_cfg.get("examples")
        examples: Optional[List[Tuple[str, str]]] = None
        if examples_cfg:
            examples = [(item["question"], item["answer"]) for item in examples_cfg]

        variants.append(
            PromptVariant(
                name=variant_cfg["name"],
                system=variant_cfg.get("system", ""),
                user=variant_cfg.get("user", ""),
                examples=examples,
            )
        )
    return variants


def render_results(results: dict, show_analytics: bool) -> Tuple[List[str], Optional[str]]:
    report_lines: List[str] = []
    analytics_lines: List[str] = []
    header = f"{'Variant':<15}{'Chars':>8}{'Lines':>8}{'JSON?':>8}{'Steps?':>8}"

    for name, response in results.items():
        block = f"--- Variant: {name} ---\n{response}\n"
        report_lines.append(block)

        if show_analytics:
            newline_char = '\n'
            analytics_lines.append(
                f"{name:<15}"
                f"{len(response):>8}"
                f"{(response.count(newline_char) + 1):>8}"
                f"{'Y' if response.strip().startswith('{') else 'N':>8}"
                f"{'Y' if any(token in response for token in ['1.', '①', 'Step']) else 'N':>8}"
            )

    analytics_report = None
    if show_analytics and analytics_lines:
        analytics_report = "\n".join([header, "-" * len(header), *analytics_lines])

    return report_lines, analytics_report


def run_langgraph_demo(cfg: DictConfig) -> None:
    """LangGraph 기반 RAG 데모 실행."""

    langgraph_cfg = cfg.get("langgraph")
    if not langgraph_cfg or not bool(langgraph_cfg.get("enabled", False)):
        return

    index_dir_value = langgraph_cfg.get("index_dir")
    if not index_dir_value:
        print("[LangGraph] index_dir가 설정되어 있지 않습니다.")
        return

    # 상대 경로를 프로젝트 루트 기준으로 절대 경로로 변환
    index_dir_str = str(index_dir_value)
    if Path(index_dir_str).is_absolute():
        index_dir_root = Path(index_dir_str)
    else:
        # 상대 경로인 경우 프로젝트 루트를 기준으로 해석
        # ../../data/processed/index 같은 경로는 ROOT_DIR 기준으로 해석
        if index_dir_str.startswith("../"):
            # ../를 제거하고 ROOT_DIR 기준으로 해석
            parts = index_dir_str.split("/")
            # ../ 개수 세기
            up_levels = sum(1 for p in parts if p == "..")
            # ../ 제거 후 나머지 경로
            remaining = "/".join([p for p in parts if p != ".."])
            # ROOT_DIR에서 up_levels만큼 올라간 후 remaining 경로 추가
            # 하지만 우리는 ROOT_DIR 기준이므로, ../가 있으면 무시하고 ROOT_DIR 기준으로
            index_dir_root = (ROOT_DIR / remaining).resolve()
        else:
            index_dir_root = (ROOT_DIR / index_dir_str).resolve()
    
    if not index_dir_root.exists():
        print(f"[LangGraph] 인덱스 루트 경로를 찾을 수 없습니다: {index_dir_root}")
        print(f"[LangGraph] 프로젝트 루트: {ROOT_DIR}")
        return
    
    # metadata.json이 있는 하위 디렉토리를 찾기
    # 먼저 직접 경로에 metadata.json이 있는지 확인
    if (index_dir_root / "metadata.json").exists():
        index_dir = index_dir_root
    else:
        # 하위 디렉토리에서 metadata.json을 찾기
        metadata_files = list(index_dir_root.rglob("metadata.json"))
        if not metadata_files:
            print(f"[LangGraph] {index_dir_root} 아래에서 metadata.json을 찾을 수 없습니다.")
            print(f"[LangGraph] 구체적인 하위 디렉토리 경로를 지정하세요 (예: data/processed/index/20201231-34-63/fixed)")
            return
        # 첫 번째 metadata.json이 있는 디렉토리 사용
        index_dir = metadata_files[0].parent
        print(f"[LangGraph] 인덱스 디렉토리 자동 선택: {index_dir}")

    print("\n=== LangGraph 기반 RAG 데모 ===")

    documents, vectors = load_documents_and_vectors(index_dir)
    embedder = HuggingFaceEmbeddings(model_name=langgraph_cfg.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"))
    retriever = DenseRetriever(
        documents=documents,
        vectors=vectors,
        embedder=embedder,
        k=int(langgraph_cfg.get("retrieval_k", 5)),
    )

    model_name = langgraph_cfg.get("model_name") or cfg.llm.model_name
    temperature = float(langgraph_cfg.get("temperature", cfg.llm.temperature))
    
    # LLM 파라미터 추가
    llm_kwargs = {
        "model": model_name,
        "temperature": temperature,
        "convert_system_message_to_human": False,
    }
    
    # top_p, top_k 파라미터 추가 (Gemini API 지원)
    if langgraph_cfg.get("top_p") is not None:
        llm_kwargs["top_p"] = float(langgraph_cfg.get("top_p"))
    if langgraph_cfg.get("top_k") is not None:
        llm_kwargs["top_k"] = int(langgraph_cfg.get("top_k"))
    
    llm = ChatGoogleGenerativeAI(**llm_kwargs)

    # 조건부 분기 설정
    enable_branching = bool(langgraph_cfg.get("enable_conditional_branching", False))
    reretrieve_threshold = float(langgraph_cfg.get("reretrieve_threshold", 0.3))
    max_reretrieves = int(langgraph_cfg.get("max_reretrieves", 1))
    keyword_prompts = langgraph_cfg.get("keyword_prompts") or {}

    graph_app = build_rag_graph(
        llm=llm,
        retriever=retriever,
        max_context_docs=int(langgraph_cfg.get("max_context_docs", 4)),
        enable_conditional_branching=enable_branching,
        reretrieve_threshold=reretrieve_threshold,
        max_reretrieves=max_reretrieves,
        keyword_prompts=keyword_prompts,
    )
    
    if enable_branching:
        print("[LangGraph] 조건부 분기 활성화: 재검색 및 키워드 기반 프롬프트 사용")

    questions = langgraph_cfg.get("demo_questions") or []
    if not questions:
        print("[LangGraph] 데모 질문이 설정되어 있지 않습니다. config.langgraph.demo_questions를 확인하세요.")
        return

    show_context = bool(langgraph_cfg.get("show_context", True))
    preview_limit = int(langgraph_cfg.get("preview_limit", 2))

    for question in questions:
        print(f"\n[질문] {question}")
        state = run_rag(graph_app, question)
        answer = state.get("answer", "(응답 없음)")
        print(f"[답변]\n{answer}")

        if show_context:
            docs = state.get("documents", [])
            previews = preview_documents(docs, limit=preview_limit)
            if previews:
                print("\n[참고 문서 미리보기]")
                for line in previews:
                    print(f"  {line}")
            else:
                print("\n[참고 문서 미리보기] 없음")


@hydra.main(version_base=None, config_path="../../conf", config_name="week5")
def main(cfg: DictConfig) -> None:
    print("=== Week5 Hydra 설정 ===")
    print(OmegaConf.to_yaml(cfg, resolve=True))

    ensure_google_api_key(bool(cfg.llm.ensure_api_key))

    variants = build_variants(cfg.variants)
    
    # 프롬프트 튜닝에 LLM 파라미터 추가
    top_p = cfg.llm.get("top_p")
    top_k = cfg.llm.get("top_k")
    tuner = PromptTuner(
        model_name=cfg.llm.model_name, 
        temperature=cfg.llm.temperature,
        top_p=top_p,
        top_k=top_k,
    )
    results = tuner.run(variants)

    report_lines, analytics_report = render_results(results, show_analytics=bool(cfg.output.show_analytics))

    if cfg.output.print_results:
        for block in report_lines:
            print(block)
        if analytics_report:
            print("\n--- [간단 비교 지표] ---")
            print(analytics_report)

    save_path = cfg.output.save_path
    if save_path:
        save_file = Path(str(save_path))
        save_file.parent.mkdir(parents=True, exist_ok=True)

        payload = "\n".join(report_lines)
        if analytics_report:
            payload += "\n\n--- [간단 비교 지표] ---\n" + analytics_report

        save_file.write_text(payload, encoding="utf-8")
        print(f"결과를 저장했습니다: {save_file.resolve()}")

    run_langgraph_demo(cfg)


if __name__ == "__main__":
    main()