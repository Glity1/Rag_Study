# Week 2 Report — PDF 전처리 & 청킹

## 1. 학습 목표
- PDF에서 텍스트/이미지 메타데이터를 추출하고 구조화
- 다섯 가지 청킹 전략(고정, 재귀, 문장, 단락, 의미) 비교
- Week3 임베딩 단계에 전달할 표준 산출물(`chunks/*.json`, `summary.json`) 정리

---

## 2. 실행 요약

| 항목 | 내용 |
|------|------|
| 실행 명령 | `python src/week2/run_week2.py` |
| Hydra 설정 | `conf/week2.yaml` (OCR 활성화, 모든 전략 실행) |
| 처리 문서 | 3건 (그랜드코리아레저 보고서, 무민카드 리플렛, BLISS 리플렛) |
| 산출 위치 | `data/processed/<slug>/` |
| 보조 산출 | `data/processed/latest_week2.json` (포인터) |

추가 실험  
```powershell
# 의미 전략만 빠르게 확인
python src/week2/run_week2.py chunking.strategies='["semantic"]'

# OCR 비활성화 후 텍스트 블록 최소 길이 강화
python src/week2/run_week2.py pdf.enable_ocr=false pdf.min_text_length=30
```

---

## 3. 추출 결과 요약

| 문서 | 페이지 | 텍스트 블록 | 이미지 | 전체 텍스트 길이 |
|------|-------:|------------:|-------:|-----------------:|
| 그랜드코리아레저 보고서 | 52 | 1,104 | 36 | 112,660 |
| 무민카드 리플렛 | 46 | 798 | 24 | 27,903 |
| BLISS 5 리플렛 | 28 | 512 | 18 | 19,874 |

**메모**  
- 스캔본 리플렛의 경우 OCR 활성화 시 텍스트 블록이 약 20% 증가  
- 이미지 메타데이터(좌표, 확장자)를 함께 저장하여 후속 OCR/요약에 활용 가능

---

## 4. 청킹 전략 비교 (대표 문서)

### 그랜드코리아레저 보고서
| 전략 | 청크 수 | 평균 크기 | 최소 | 최대 | 특이사항 |
|------|--------:|----------:|-----:|-----:|----------|
| fixed | 23 | 585.5 | 266 | 600 | 일정한 길이 유지 |
| recursive | 23 | 565.6 | 250 | 598 | 줄바꿈, 문장 경계 우선 |
| sentence | 12 | 937.9 | 91 | 1,410 | 긴 문장으로 길이 편차 큼 |
| paragraph | 1 | 11,266 | 11,266 | 11,266 | 사실상 미사용 |
| semantic | 19 | 648.2 | 210 | 910 | 유사도 기반 분리 |

### 무민카드 / BLISS 리플렛
- `fixed` vs `recursive`: 청크 수 동일(56)이나 재귀 전략이 의미 경계 보존  
- `sentence`: 문의 응답 시 문단 조합이 필요, 평균 500자 미만  
- `semantic`: 문장간 의미 차이가 적어 상대적으로 길이 편차가 작음

---

## 5. 산출물 구조 검증
```
data/processed/<slug>/
 ├─ extraction.json          # 텍스트/이미지 블록 리스트
 ├─ full_text.txt            # 전체 텍스트 통합본
 ├─ summary.json             # 전략별 통계
 └─ chunks/
     ├─ recursive.json/.txt
     ├─ fixed.json/.txt
     ├─ ...
```

`summary.json` 발췌:
```json
{
  "recursive": {
    "count": 23,
    "avg_size": 565.6,
    "min_size": 250,
    "max_size": 598
  },
  "semantic": {
    "count": 19,
    "avg_size": 648.2,
    "min_size": 210,
    "max_size": 910
  }
}
```

---

## 6. 주요 인사이트
1. **재귀 전략**이 문맥 보존 측면에서 기본값으로 적합  
2. **문장/단락 전략**은 문서 구조가 잘 정리된 보고서에서 유효  
3. **의미 기반 청킹**은 SentenceTransformer 로드 비용이 있지만, 향후 QA 품질 향상을 위해 유지  
4. OCR 결과는 후속 사용을 위해 별도 폴더(`/data/processed/<slug>/images/`)에 저장 가능하도록 개선 여지

---

## 7. 다음 단계
- Week3 임베딩 스크립트가 `latest_week2.json`을 읽어 자동으로 청크를 처리하는지 확인  
- 의미 기반 청킹의 임계값(`semantic.similarity_threshold`)을 0.75 → 0.8로 조정해 재실험 예정  
- PDF 파일명과 slug 매핑 표를 문서화하여 협업 시 혼선을 줄일 것
