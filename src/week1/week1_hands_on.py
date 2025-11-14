"""
1주차 실습: 임베딩과 벡터 검색 기초
RAG의 핵심 개념을 간단한 예제로 이해하기
"""

import sys
import io
import numpy as np
from typing import List, Tuple

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("🎯 1주차 실습: RAG 핵심 개념 체험하기")
print("=" * 80)

# ============================================================================
# Part 1: 임베딩의 기본 개념
# ============================================================================
print("\n\n📚 Part 1: 임베딩이란 무엇인가?")
print("-" * 80)

# 간단한 예시: 단어를 2차원 벡터로 표현
# 실제로는 수백~수천 차원이지만, 이해를 위해 2차원으로 단순화

word_embeddings = {
    "강아지": np.array([0.8, 0.9]),  # 동물, 귀여움
    "고양이": np.array([0.9, 0.85]), # 동물, 귀여움
    "펫": np.array([0.85, 0.8]),     # 동물, 반려동물
    "자동차": np.array([0.1, 0.2]),  # 탈것, 기계
    "비행기": np.array([0.15, 0.1]), # 탈것, 기계
}

print("\n단어들의 벡터 표현:")
for word, vec in word_embeddings.items():
    print(f"  {word:6s} → {vec}")

# 코사인 유사도 계산 함수
def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """두 벡터 간의 코사인 유사도를 계산"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

print("\n\n코사인 유사도 계산:")
print("  (1.0에 가까울수록 유사, 0에 가까울수록 다름)")

# 강아지와 다른 단어들의 유사도
dog_vec = word_embeddings["강아지"]
print(f"\n  '강아지'와의 유사도:")
for word, vec in word_embeddings.items():
    if word != "강아지":
        similarity = cosine_similarity(dog_vec, vec)
        print(f"    강아지 ↔ {word:6s}: {similarity:.4f}")

print("\n  💡 해석:")
print("     - '고양이', '펫'은 0.99로 매우 유사 (같은 카테고리)")
print("     - '자동차', '비행기'는 0.3~0.4로 매우 다름 (다른 카테고리)")


# ============================================================================
# Part 2: 벡터 검색 (Retrieval) 시뮬레이션
# ============================================================================
print("\n\n" + "=" * 80)
print("🔍 Part 2: 벡터 검색 시뮬레이션")
print("-" * 80)

# 간단한 문서 데이터베이스 (실제로는 수천~수만 개)
documents = {
    "doc1": "강아지는 충성스러운 반려동물입니다",
    "doc2": "고양이는 독립적인 성격을 가진 동물입니다",
    "doc3": "자동차는 편리한 교통수단입니다",
    "doc4": "비행기는 빠른 장거리 이동에 적합합니다",
    "doc5": "반려동물을 키우려면 책임감이 필요합니다",
}

# 간단한 임베딩 생성 (실제로는 임베딩 모델 사용)
# 여기서는 키워드 기반으로 단순화
def simple_embed(text: str) -> np.ndarray:
    """단순화된 임베딩: 키워드 기반"""
    vec = np.array([0.0, 0.0])
    
    # 동물 관련 키워드
    animal_keywords = ["강아지", "고양이", "동물", "반려", "펫"]
    for keyword in animal_keywords:
        if keyword in text:
            vec[0] += 0.3
    
    # 탈것 관련 키워드
    vehicle_keywords = ["자동차", "비행기", "교통", "이동"]
    for keyword in vehicle_keywords:
        if keyword in text:
            vec[1] += 0.3
    
    # 정규화
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    
    return vec

# 모든 문서를 벡터로 변환
doc_embeddings = {}
print("\n문서들의 벡터 표현:")
for doc_id, text in documents.items():
    vec = simple_embed(text)
    doc_embeddings[doc_id] = vec
    print(f"  {doc_id}: {text[:30]:30s} → {vec}")

# 검색 함수
def search(query: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
    """쿼리와 가장 유사한 문서 검색"""
    query_vec = simple_embed(query)
    
    # 모든 문서와의 유사도 계산
    similarities = []
    for doc_id, doc_vec in doc_embeddings.items():
        sim = cosine_similarity(query_vec, doc_vec)
        similarities.append((doc_id, documents[doc_id], sim))
    
    # 유사도 기준으로 정렬
    similarities.sort(key=lambda x: x[2], reverse=True)
    
    return similarities[:top_k]

# 검색 테스트
print("\n\n🔎 검색 테스트:")
queries = [
    "반려동물에 대해 알려줘",
    "교통수단은 어떤 것이 있나요?",
]

for query in queries:
    print(f"\n질문: '{query}'")
    print("-" * 60)
    results = search(query, top_k=3)
    
    for i, (doc_id, text, score) in enumerate(results, 1):
        print(f"  {i}위 [{doc_id}] (유사도: {score:.4f})")
        print(f"       → {text}")


# ============================================================================
# Part 3: RAG 전체 과정 시뮬레이션
# ============================================================================
print("\n\n" + "=" * 80)
print("🤖 Part 3: 간단한 RAG 시뮬레이션")
print("-" * 80)

def simple_rag(query: str) -> str:
    """간단한 RAG 시스템 시뮬레이션"""
    
    print(f"\n[단계 1] 질문: {query}")
    
    # 검색 (Retrieval)
    print(f"[단계 2] 벡터 검색 수행...")
    results = search(query, top_k=2)
    
    print(f"[단계 3] 검색된 관련 문서:")
    retrieved_docs = []
    for doc_id, text, score in results:
        print(f"         - {text} (유사도: {score:.4f})")
        retrieved_docs.append(text)
    
    # 생성 (Generation) - 실제로는 LLM 사용
    print(f"[단계 4] LLM으로 답변 생성 중...")
    
    # 여기서는 간단히 검색된 문서를 조합 (실제로는 LLM이 자연스럽게 생성)
    context = " ".join(retrieved_docs)
    answer = f"검색된 문서에 따르면: {context}"
    
    return answer

# RAG 실행
print("\n" + "=" * 60)
test_query = "반려동물은 어떤 특징이 있나요?"
answer = simple_rag(test_query)

print(f"\n[최종 답변]")
print(f"  {answer}")

print("\n" + "=" * 60)
print("💡 실제 RAG 시스템에서는:")
print("   1. 임베딩: 사전 학습된 모델 사용 (예: BGE, OpenAI)")
print("   2. 벡터 DB: FAISS, ChromaDB 등 전문 DB 사용")
print("   3. LLM: GPT, Claude 등으로 자연스러운 답변 생성")
print("   4. 수천~수백만 개의 문서에서 빠르게 검색")


# ============================================================================
# Part 4: 실전 준비 - 필요한 라이브러리 설치 안내
# ============================================================================
print("\n\n" + "=" * 80)
print("🛠️ Part 4: 실전 RAG 구축을 위한 환경 설정")
print("-" * 80)

print("""
다음 주부터는 실제 라이브러리를 사용합니다!

필수 라이브러리 설치:
```bash
# 가상환경 생성 (권장)
python -m venv rag_env
source rag_env/bin/activate  # Windows: rag_env\\Scripts\\activate

# 라이브러리 설치
pip install langchain
pip install langchain-community
pip install sentence-transformers
pip install faiss-cpu
pip install pypdf2
pip install numpy pandas
```

주요 라이브러리 역할:
  - langchain: RAG 파이프라인 구축 프레임워크
  - sentence-transformers: 고품질 임베딩 모델
  - faiss-cpu: 빠른 벡터 검색
  - pypdf2: PDF 문서 처리
""")


# ============================================================================
# 1주차 정리
# ============================================================================
print("\n" + "=" * 80)
print("✅ 1주차 학습 완료!")
print("=" * 80)

print("""
오늘 배운 내용:
  1. RAG의 3단계: Indexing → Retrieval → Generation
  2. 임베딩: 텍스트를 벡터로 변환하여 의미를 숫자로 표현
  3. 벡터 검색: 코사인 유사도로 가장 관련 있는 문서 찾기
  4. RAG 전체 흐름: 질문 → 검색 → 문서 기반 답변

다음 주 예고:
  📄 2주차: PDF 문서 처리와 청킹(Chunking)
  - 실제 PDF 파일에서 텍스트 추출
  - 문서를 의미 있는 단위로 분할
  - 이미지와 텍스트 혼합 처리
""")

print("\n💪 계속 화이팅하세요!")

