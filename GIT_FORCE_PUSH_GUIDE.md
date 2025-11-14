# Git 레포지토리 덮어쓰기 가이드

현재 Rag_Study 폴더의 내용으로 원격 레포지토리를 완전히 덮어쓰는 방법입니다.

---

## ⚠️ 주의사항

**강제 푸시(Force Push)는 위험합니다!**
- 원격 레포지토리의 모든 히스토리가 덮어쓰여집니다
- 다른 사람과 협업 중이라면 반드시 팀원과 상의하세요
- 백업을 먼저 받아두는 것을 권장합니다

---

## 방법 1: 기존 레포지토리 덮어쓰기 (강제 푸시)

### 1단계: Git 저장소 확인

```bash
cd C:\Users\qqtta\OneDrive\Desktop\rag\Rag_Study

# Git 저장소인지 확인
git status

# 원격 저장소 확인
git remote -v
```

### 2단계: 모든 변경사항 추가

```bash
# 모든 파일 추가 (.gitignore 제외)
git add .

# 변경사항 확인
git status
```

### 3단계: 커밋

```bash
# 커밋 메시지 작성
git commit -m "프로젝트 전체 업데이트: 폴더 구조 재정리 및 문서 업데이트

- docs 폴더 구조 재정리 (guides, results, notes, reports)
- notebooks 업데이트 (최신 기능 반영)
- Docker 관련 파일 업데이트
- 모든 문서 링크 경로 수정
- 불필요한 빈 폴더 정리"
```

### 4단계: 강제 푸시 (⚠️ 주의!)

```bash
# 현재 브랜치 확인
git branch

# 강제 푸시 (main 브랜치인 경우)
git push --force origin main

# 또는 master 브랜치인 경우
git push --force origin master
```

---

## 방법 2: 새 레포지토리로 시작

기존 레포지토리를 완전히 무시하고 새로 시작하려면:

### 1단계: Git 초기화

```bash
cd C:\Users\qqtta\OneDrive\Desktop\rag\Rag_Study

# 기존 .git 폴더 삭제 (주의!)
# rm -rf .git  # Linux/Mac
# Remove-Item -Recurse -Force .git  # Windows PowerShell

# 새로 초기화
git init
```

### 2단계: 원격 저장소 연결

```bash
# 원격 저장소 추가 (YOUR_USERNAME과 REPO_NAME을 실제 값으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 또는 SSH 사용
git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git
```

### 3단계: 파일 추가 및 커밋

```bash
# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: RAG Study 프로젝트 전체"

# 브랜치 이름 설정
git branch -M main
```

### 4단계: 강제 푸시

```bash
# 원격 저장소를 완전히 덮어쓰기
git push --force origin main
```

---

## 방법 3: GitHub 웹 인터페이스 사용

Git 명령어 없이 웹에서 직접 업로드:

### 1단계: GitHub에서 저장소 생성/선택

1. GitHub에 로그인
2. 새 저장소 생성 또는 기존 저장소 선택
3. 저장소 페이지로 이동

### 2단계: 파일 업로드

1. **"Upload files"** 또는 **"Add file" → "Upload files"** 클릭
2. Rag_Study 폴더의 모든 파일 드래그 앤 드롭
3. **"Commit changes"** 클릭

### 3단계: 기존 파일 덮어쓰기

- 기존 파일이 있다면 자동으로 덮어쓰기 제안
- **"Replace existing files"** 선택 후 커밋

---

## .gitignore 확인

업로드 전에 `.gitignore` 파일이 올바르게 설정되어 있는지 확인:

```bash
# .gitignore 내용 확인
cat .gitignore

# 제외되어야 할 항목:
# - .env (API 키)
# - __pycache__/
# - outputs/ (실행 로그)
# - *.log
# - venv/, .venv/
```

---

## 업로드 전 체크리스트

### 필수 확인 사항

- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] API 키가 코드에 하드코딩되지 않았는지 확인
- [ ] `outputs/` 폴더가 제외되는지 확인
- [ ] `__pycache__/` 폴더가 제외되는지 확인
- [ ] 불필요한 파일이 제외되는지 확인

### 확인 명령어

```bash
# .env 파일이 제외되는지 확인
git status | grep .env

# 민감한 정보 검색
grep -r "AIza" . --exclude-dir=.git
grep -r "sk-" . --exclude-dir=.git
```

---

## 안전한 대안: 새 브랜치로 푸시

강제 푸시 대신 새 브랜치를 만들어서 푸시하는 방법:

```bash
# 새 브랜치 생성
git checkout -b update-project-structure

# 변경사항 추가 및 커밋
git add .
git commit -m "프로젝트 구조 업데이트"

# 새 브랜치로 푸시
git push origin update-project-structure

# GitHub에서 Pull Request 생성하여 main 브랜치에 병합
```

이 방법이 더 안전하고 협업에 적합합니다.

---

## 문제 해결

### "remote: Permission denied" 오류

```bash
# SSH 키 확인
ssh -T git@github.com

# 또는 HTTPS 인증 사용
git remote set-url origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

### "Updates were rejected" 오류

```bash
# 원격 변경사항 먼저 가져오기
git fetch origin

# 강제 푸시 (주의!)
git push --force origin main
```

### 파일이 너무 큰 경우

```bash
# Git LFS 사용
git lfs install
git lfs track "*.faiss"
git lfs track "*.pdf"
git add .gitattributes
```

---

## 요약

### 빠른 덮어쓰기 (기존 레포지토리)

```bash
cd C:\Users\qqtta\OneDrive\Desktop\rag\Rag_Study
git add .
git commit -m "프로젝트 전체 업데이트"
git push --force origin main
```

### 새로 시작 (새 레포지토리)

```bash
cd C:\Users\qqtta\OneDrive\Desktop\rag\Rag_Study
git init
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git add .
git commit -m "Initial commit"
git branch -M main
git push --force origin main
```

---

**⚠️ 중요**: 강제 푸시는 원격 저장소의 히스토리를 완전히 덮어씁니다. 신중하게 진행하세요!

