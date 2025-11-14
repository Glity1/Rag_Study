# 이미지 플레이스홀더 가이드

## 개요

PDF 문서에서 추출된 이미지 정보를 텍스트 청크에 플레이스홀더로 삽입하여, RAG 시스템이 이미지 존재를 인식하고 답변에 반영할 수 있도록 합니다.

---

## 동작 원리

1. **PDF 추출 단계** (Week2):
   - `pdf_loader.py`에서 텍스트 블록과 이미지 메타데이터를 추출
   - 이미지 정보: 페이지 번호, 파일명, 크기(width x height), 위치(bbox)

2. **플레이스홀더 삽입 단계** (Week2):
   - `insert_image_placeholders()` 함수가 텍스트에 이미지 정보를 플레이스홀더로 삽입
   - 이미지가 있는 페이지의 텍스트 블록 근처에 플레이스홀더 삽입

3. **청킹 단계** (Week2):
   - 플레이스홀더가 포함된 텍스트를 청킹
   - 이미지 정보가 청크에 포함됨

4. **검색 및 생성 단계** (Week4/5):
   - 이미지 플레이스홀더가 포함된 청크가 검색되면 프롬프트에 자동 포함
   - LLM이 이미지 정보를 인식하고 답변에 반영

---

## 사용 방법

### Week2에서 이미지 플레이스홀더 활성화

#### Hydra 설정 파일 (`conf/week2.yaml`)

```yaml
pdf:
  # 이미지 플레이스홀더 삽입 여부
  insert_image_placeholders: true
  # 이미지 플레이스홀더 형식
  image_placeholder_format: "Image: [{name}] (Page {page}, {width}x{height})"
```

#### 명령줄에서 실행

```bash
# 이미지 플레이스홀더 활성화
python src/week2/run_week2.py pdf.insert_image_placeholders=true

# 커스텀 플레이스홀더 형식 사용
python src/week2/run_week2.py pdf.insert_image_placeholders=true pdf.image_placeholder_format="[이미지: {name} (페이지 {page})]"
```

---

## 플레이스홀더 형식

### 기본 형식

```
Image: [{name}] (Page {page}, {width}x{height})
```

### 사용 가능한 변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `{name}` | 이미지 파일명 | `page1_img1.png` |
| `{page}` | 페이지 번호 | `1` |
| `{width}` | 이미지 너비 (픽셀) | `800` |
| `{height}` | 이미지 높이 (픽셀) | `600` |

### 커스텀 형식 예시

```yaml
# 간단한 형식
image_placeholder_format: "[이미지: {name}]"

# 상세한 형식
image_placeholder_format: "📷 이미지 참조: {name} (페이지 {page}, 크기: {width}x{height}px)"

# JSON 형식
image_placeholder_format: '{"type": "image", "name": "{name}", "page": {page}, "size": "{width}x{height}"}'
```

---

## 예시

### 입력 PDF

- 페이지 1: 텍스트 블록 + 이미지 1개
- 페이지 2: 이미지만 (텍스트 없음)
- 페이지 3: 텍스트 블록 + 이미지 2개

### 플레이스홀더 삽입 결과

```
[텍스트 블록 내용]

Image: [page1_img1.png] (Page 1, 800x600)

[다음 텍스트 블록 내용]

[Page 2 Images]
Image: [page2_img1.jpg] (Page 2, 1200x900)

[페이지 3 텍스트 블록]

Image: [page3_img1.png] (Page 3, 600x400)

Image: [page3_img2.png] (Page 3, 500x300)
```

### 청킹 결과

이미지 플레이스홀더가 포함된 청크가 생성됩니다:

```
청크 1:
"그랜드코리아레저의 코로나 대응 전략은 다음과 같습니다.
Image: [page1_img1.png] (Page 1, 800x600)
주요 내용은..."
```

### RAG 검색 및 답변

질문: "코로나 대응 전략에 대한 이미지가 있나요?"

검색된 청크에 이미지 플레이스홀더가 포함되어 있으면:
```
답변: 네, 코로나 대응 전략과 관련된 이미지가 있습니다. 
페이지 1에 800x600 크기의 이미지(page1_img1.png)가 포함되어 있습니다.
```

---

## 장점

1. **이미지 인식**: LLM이 문서에 이미지가 있다는 것을 인식
2. **컨텍스트 제공**: 이미지 위치와 크기 정보 제공
3. **검색 가능**: 이미지 관련 질문에 대해 적절한 청크 검색
4. **유연성**: 플레이스홀더 형식을 커스터마이징 가능

---

## 제한사항

1. **이미지 내용 미포함**: 플레이스홀더는 이미지 메타데이터만 포함, 실제 이미지 내용은 포함하지 않음
2. **OCR 필요**: 이미지에서 텍스트를 추출하려면 OCR 기능 필요
3. **위치 정확도**: 이미지가 텍스트 블록 근처에 삽입되지만, 정확한 위치는 보장되지 않음

---

## 향후 개선 방향

1. **이미지 캡션 추출**: 
   - Vision-Language 모델을 사용하여 이미지 캡션 생성
   - 캡션을 플레이스홀더에 포함

2. **OCR 통합**:
   - 이미지 내 텍스트를 OCR로 추출
   - 추출된 텍스트를 플레이스홀더에 포함

3. **정확한 위치 삽입**:
   - 이미지 bbox와 텍스트 블록 bbox를 비교하여 정확한 위치에 삽입

4. **멀티모달 RAG**:
   - 이미지 자체를 임베딩하여 벡터 검색에 포함
   - Vision-Language 모델을 사용한 이미지-텍스트 통합 검색

---

## 참고 자료

- `src/week2/pdf_loader.py` - PDF 추출 로직
- `src/week2/run_week2.py` - 플레이스홀더 삽입 로직
- `conf/week2.yaml` - 설정 파일

---

**구현 위치**: `src/week2/run_week2.py` - `insert_image_placeholders()` 함수

