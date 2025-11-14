"""새로 구현된 기능들의 실제 실행 테스트 스크립트."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

# 프로젝트 루트를 sys.path에 추가
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
CURRENT_DIR = SRC_DIR / "week4"
for path in [str(SRC_DIR), str(CURRENT_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from dotenv import load_dotenv
from src.week4.rag_chain import build_rag_chain

load_dotenv()

# 테스트 결과 저장
results: Dict[str, Dict] = {}


def test_mmr_vs_similarity():
    """MMR 검색 vs 일반 유사도 검색 비교 테스트."""
    print("\n" + "=" * 60)
    print("테스트 1: MMR 검색 vs 일반 유사도 검색")
    print("=" * 60)
    
    index_dir = ROOT_DIR / "data/processed/index/20201231-34-63/recursive"
    if not (index_dir / "metadata.json").exists():
        print(f"⚠️  인덱스를 찾을 수 없습니다: {index_dir}")
        return None
    
    question = "그랜드코리아레저의 코로나 대응 전략은 무엇인가?"
    
    test_results = {
        "question": question,
        "index_dir": str(index_dir),
        "similarity_search": {},
        "mmr_search": {},
    }
    
    # 1. 일반 유사도 검색
    print("\n[1/2] 일반 유사도 검색 테스트...")
    try:
        start_time = time.time()
        chain_sim = build_rag_chain(
            index_dir=index_dir,
            use_mmr=False,
            retrieval_k=5,
        )
        build_time = time.time() - start_time
        
        start_time = time.time()
        result_sim = chain_sim.invoke({"query": question})
        answer_sim = result_sim.get("result", str(result_sim))
        query_time = time.time() - start_time
        
        test_results["similarity_search"] = {
            "build_time": round(build_time, 3),
            "query_time": round(query_time, 3),
            "answer_length": len(answer_sim),
            "answer_preview": answer_sim[:200] + "..." if len(answer_sim) > 200 else answer_sim,
        }
        print(f"✅ 완료: 응답 시간 {query_time:.2f}초")
    except Exception as e:
        print(f"❌ 실패: {e}")
        test_results["similarity_search"]["error"] = str(e)
    
    # 2. MMR 검색 (diversity=0.5)
    print("\n[2/2] MMR 검색 테스트 (diversity=0.5)...")
    try:
        start_time = time.time()
        chain_mmr = build_rag_chain(
            index_dir=index_dir,
            use_mmr=True,
            mmr_diversity=0.5,
            retrieval_k=5,
        )
        build_time = time.time() - start_time
        
        start_time = time.time()
        result_mmr = chain_mmr.invoke({"query": question})
        answer_mmr = result_mmr.get("result", str(result_mmr))
        query_time = time.time() - start_time
        
        test_results["mmr_search"] = {
            "build_time": round(build_time, 3),
            "query_time": round(query_time, 3),
            "answer_length": len(answer_mmr),
            "answer_preview": answer_mmr[:200] + "..." if len(answer_mmr) > 200 else answer_mmr,
        }
        print(f"✅ 완료: 응답 시간 {query_time:.2f}초")
    except Exception as e:
        print(f"❌ 실패: {e}")
        test_results["mmr_search"]["error"] = str(e)
    
    # 비교 결과 출력
    if "error" not in test_results["similarity_search"] and "error" not in test_results["mmr_search"]:
        print("\n--- 비교 결과 ---")
        print(f"응답 시간: 유사도 {test_results['similarity_search']['query_time']:.2f}초 vs MMR {test_results['mmr_search']['query_time']:.2f}초")
        print(f"답변 길이: 유사도 {test_results['similarity_search']['answer_length']}자 vs MMR {test_results['mmr_search']['answer_length']}자")
    
    return test_results


def test_llm_parameters():
    """LLM 파라미터 (top_p, top_k) 테스트."""
    print("\n" + "=" * 60)
    print("테스트 2: LLM 파라미터 (temperature, top_p, top_k)")
    print("=" * 60)
    
    index_dir = ROOT_DIR / "data/processed/index/20201231-34-63/recursive"
    if not (index_dir / "metadata.json").exists():
        print(f"⚠️  인덱스를 찾을 수 없습니다: {index_dir}")
        return None
    
    question = "그랜드코리아레저의 코로나 대응 전략을 간단히 요약해줘."
    
    test_results = {
        "question": question,
        "index_dir": str(index_dir),
        "parameter_tests": [],
    }
    
    # 다양한 파라미터 조합 테스트
    test_configs = [
        {"name": "기본값", "temperature": 0.0, "top_p": None, "top_k": None},
        {"name": "temperature=0.5", "temperature": 0.5, "top_p": None, "top_k": None},
        {"name": "temperature=0.5, top_p=0.9", "temperature": 0.5, "top_p": 0.9, "top_k": None},
        {"name": "temperature=0.5, top_k=40", "temperature": 0.5, "top_p": None, "top_k": 40},
        {"name": "temperature=0.5, top_p=0.9, top_k=40", "temperature": 0.5, "top_p": 0.9, "top_k": 40},
    ]
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n[{i}/{len(test_configs)}] {config['name']} 테스트...")
        try:
            start_time = time.time()
            chain = build_rag_chain(
                index_dir=index_dir,
                temperature=config["temperature"],
                top_p=config["top_p"],
                top_k=config["top_k"],
                retrieval_k=5,
            )
            
            start_time = time.time()
            result = chain.invoke({"query": question})
            answer = result.get("result", str(result))
            query_time = time.time() - start_time
            
            test_results["parameter_tests"].append({
                "config": config,
                "query_time": round(query_time, 3),
                "answer_length": len(answer),
                "answer_preview": answer[:150] + "..." if len(answer) > 150 else answer,
            })
            print(f"✅ 완료: 응답 시간 {query_time:.2f}초, 답변 길이 {len(answer)}자")
        except Exception as e:
            print(f"❌ 실패: {e}")
            test_results["parameter_tests"].append({
                "config": config,
                "error": str(e),
            })
    
    return test_results


def test_langgraph_conditional():
    """LangGraph 조건부 분기 테스트."""
    print("\n" + "=" * 60)
    print("테스트 3: LangGraph 조건부 분기")
    print("=" * 60)
    
    try:
        from src.week5.langgraph_rag import build_rag_graph, run_rag
        from src.week4.rag_chain import DenseRetriever, load_documents_and_vectors
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as e:
        print(f"⚠️  필요한 모듈을 임포트할 수 없습니다: {e}")
        return None
    
    index_dir = ROOT_DIR / "data/processed/index/20201231-34-63/recursive"
    if not (index_dir / "metadata.json").exists():
        print(f"⚠️  인덱스를 찾을 수 없습니다: {index_dir}")
        return None
    
    test_results = {
        "index_dir": str(index_dir),
        "basic_flow": {},
        "conditional_branching": {},
    }
    
    # 기본 설정
    documents, vectors = load_documents_and_vectors(index_dir)
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    retriever = DenseRetriever(
        documents=documents,
        vectors=vectors,
        embedder=embedder,
        k=5,
    )
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        convert_system_message_to_human=False,
    )
    
    question = "그랜드코리아레저의 코로나 대응 전략은 무엇인가?"
    
    # 1. 기본 플로우 (조건부 분기 없음)
    print("\n[1/2] 기본 플로우 테스트...")
    try:
        graph_basic = build_rag_graph(
            llm=llm,
            retriever=retriever,
            max_context_docs=4,
            enable_conditional_branching=False,
        )
        
        start_time = time.time()
        state_basic = run_rag(graph_basic, question)
        query_time = time.time() - start_time
        
        answer_basic = state_basic.get("answer", "")
        test_results["basic_flow"] = {
            "query_time": round(query_time, 3),
            "answer_length": len(answer_basic),
            "answer_preview": answer_basic[:200] + "..." if len(answer_basic) > 200 else answer_basic,
            "retrieval_count": state_basic.get("retrieval_count", 0),
        }
        print(f"✅ 완료: 응답 시간 {query_time:.2f}초")
    except Exception as e:
        print(f"❌ 실패: {e}")
        test_results["basic_flow"]["error"] = str(e)
    
    # 2. 조건부 분기 활성화
    print("\n[2/2] 조건부 분기 활성화 테스트...")
    try:
        graph_conditional = build_rag_graph(
            llm=llm,
            retriever=retriever,
            max_context_docs=4,
            enable_conditional_branching=True,
            reretrieve_threshold=0.3,
            max_reretrieves=1,
        )
        
        start_time = time.time()
        state_conditional = run_rag(graph_conditional, question)
        query_time = time.time() - start_time
        
        answer_conditional = state_conditional.get("answer", "")
        test_results["conditional_branching"] = {
            "query_time": round(query_time, 3),
            "answer_length": len(answer_conditional),
            "answer_preview": answer_conditional[:200] + "..." if len(answer_conditional) > 200 else answer_conditional,
            "retrieval_count": state_conditional.get("retrieval_count", 0),
            "keywords_detected": state_conditional.get("keywords_detected", []),
        }
        print(f"✅ 완료: 응답 시간 {query_time:.2f}초, 재검색 횟수: {state_conditional.get('retrieval_count', 0)}")
    except Exception as e:
        print(f"❌ 실패: {e}")
        test_results["conditional_branching"]["error"] = str(e)
    
    return test_results


def main():
    """모든 테스트 실행."""
    print("=" * 60)
    print("새로 구현된 기능들의 실제 실행 테스트")
    print("=" * 60)
    
    # API 키 확인
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("   일부 테스트가 실패할 수 있습니다.")
    
    # 테스트 실행
    results["mmr_test"] = test_mmr_vs_similarity()
    results["llm_params_test"] = test_llm_parameters()
    results["langgraph_test"] = test_langgraph_conditional()
    
    # 결과 저장
    output_dir = ROOT_DIR / "outputs" / "feature_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"test_results_{int(time.time())}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print(f"결과 저장 위치: {output_file}")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    main()

