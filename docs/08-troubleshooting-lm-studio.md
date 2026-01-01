# LM Studio 문제 해결 가이드

## 🔴 발생한 에러 분석

### 에러 유형

#### 1. Model Crash (Exit Code 11)
```
Error code: 400 - {'error': 'The model has crashed without additional information. (Exit code: 11)'}
```

**원인**:
- 메모리 부족 (RAM/VRAM)
- 컨텍스트 길이 초과
- 세그멘테이션 폴트 (메모리 접근 오류)

**발생 위치**: Cross Reference Agent (책 생성 후반부)

**해결 방법**:
1. 더 작은 양자화 모델 사용 (Q4 → Q3)
2. 컨텍스트 길이 줄이기 (8192 → 4096)
3. 챕터 수 줄이기 (3 → 1)
4. 반복 횟수 줄이기 (10 → 2)

---

#### 2. No Models Loaded
```
Error code: 400 - {'error': {'message': "No models loaded. Please load a model..."}}
```

**원인**:
- LM Studio에서 모델이 언로드됨
- 이전 크래시 후 모델 재로드 안 됨
- LM Studio 서버가 중지됨

**해결 방법**:
1. LM Studio 앱에서 모델 재로드
2. Local Server 재시작
3. 연결 테스트 실행

---

## ✅ LM Studio 올바른 설정 방법

### 1단계: 모델 선택 및 로드

**권장 모델**:
- **Qwen2.5-7B-Instruct** (Q4_K_M 양자화)
- **최소 요구사항**: 8GB RAM
- **권장 사양**: 16GB RAM, GPU 지원

**로드 방법**:
```
1. LM Studio 앱 실행
2. Models 탭 클릭
3. "Search for models" 검색창에 "qwen" 입력
4. Qwen2.5-7B-Instruct 찾기
5. Q4_K_M 버전 선택 (균형잡힌 성능/메모리)
6. Download 클릭 (첫 실행시)
7. Load Model 클릭
8. 로딩 완료 대기 (진행률 표시)
```

---

### 2단계: Server 설정

**설정 항목**:

1. **Context Length**:
   - **권장**: 4096 (안정적)
   - **최대**: 8192 (고성능 시스템)
   - **최소**: 2048 (메모리 부족 시)

2. **GPU Offload**:
   - **GPU 있음**: "Auto" 또는 전체 레이어
   - **GPU 없음**: "None" (CPU만 사용)

3. **Temperature**:
   - 시스템이 자동으로 설정하므로 기본값 유지

4. **Port**:
   - 기본값 1234 유지

**서버 시작**:
```
1. Local Server 탭 클릭
2. 위 설정 확인
3. "Start Server" 클릭
4. 상태 확인: "Server running on port 1234" 표시되어야 함
5. 모델이 로드된 상태로 유지되는지 확인
```

---

### 3단계: 연결 테스트

**터미널에서 실행**:
```bash
cd /Users/boon/Dropbox/02_works/94_agent
python main.py --test-connection
```

**예상 출력** (성공):
```
Testing connection to LM Studio at http://localhost:1234/v1...
✓ Successfully connected to LM Studio
  Model: qwen
```

**예상 출력** (실패):
```
✗ Failed to connect to LM Studio

Troubleshooting:
1. Make sure LM Studio is running
2. Check that the local server is started (port 1234)
3. Verify the model is loaded
```

---

## 🛠 문제별 해결 방법

### 문제 1: 모델이 자꾸 크래시됨

**증상**:
- 책 생성 중간에 "Exit code: 11" 오류
- Cross Reference Agent에서 주로 발생

**원인**:
- 누적 컨텍스트가 모델 한계 초과
- 메모리 부족

**해결책**:

#### A. 더 가벼운 설정 사용
```bash
# 1챕터만 생성
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 1 --max-iterations 1

# 반복 줄이기
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 3 --max-iterations 2
```

#### B. 더 작은 모델 사용
- Qwen2.5-7B Q4_K_M → Q3_K_M
- 또는 Qwen2.5-3B 모델 사용

#### C. Context Length 줄이기
LM Studio Server 설정:
- 8192 → 4096
- 또는 4096 → 2048

#### D. LM Studio 재시작
```
1. LM Studio에서 "Stop Server" 클릭
2. 모델 Unload
3. LM Studio 앱 완전 종료
4. 앱 재시작
5. 모델 재로드
6. 서버 재시작
```

---

### 문제 2: 연결 테스트는 성공하는데 실행 시 실패

**증상**:
- `python main.py --test-connection` 성공
- 실제 생성 시작하면 "No models loaded" 오류

**원인**:
- 테스트 후 모델이 자동 언로드됨
- LM Studio 설정 문제

**해결책**:

#### A. 모델 상태 유지 확인
```
1. LM Studio 앱 열기
2. Models 탭에서 모델 상태 확인
3. "Loaded" 상태여야 함
4. Local Server 탭에서 "Running" 확인
5. 서버를 중지하지 말고 그대로 유지
```

#### B. Auto-unload 설정 비활성화
LM Studio 설정 (Settings):
- "Auto-unload models" 옵션 끄기 (있다면)

#### C. 연결 테스트 직후 즉시 실행
```bash
# 테스트와 실행을 연속으로
python main.py --test-connection && python main.py --mode simple --topic "테스트"
```

---

### 문제 3: 생성 속도가 너무 느림

**증상**:
- 토큰 생성이 초당 1-2개
- 챕터 하나 생성에 30분 이상 소요

**원인**:
- CPU만 사용 (GPU 미사용)
- 모델 크기가 시스템에 비해 큼

**해결책**:

#### A. GPU 가속 확인
LM Studio Server 설정:
- GPU Offload: "Auto" 또는 최대값

시스템에 GPU가 있는지 확인:
- Mac: M1/M2/M3 칩 (Metal 가속)
- Windows/Linux: NVIDIA GPU (CUDA)

#### B. 더 작은 모델 사용
- Qwen2.5-7B → Qwen2.5-3B
- Q4_K_M → Q4_K_S (더 빠름, 품질 약간 낮음)

#### C. Batch Size 조정
LM Studio Advanced 설정:
- Batch Size 증가 (메모리가 충분하면)

---

### 문제 4: DuckDuckGo Search 경고

**증상**:
```
Warning: duckduckgo-search not installed. Install with: pip install duckduckgo-search
```

**해결책**:
```bash
pip install duckduckgo-search
```

설치 후 확인:
```bash
python -c "import duckduckgo_search; print('✓ Installed')"
```

---

## 📋 권장 워크플로우

### 안정적인 책 생성 프로세스

#### 1. LM Studio 준비
```
1. LM Studio 실행
2. Qwen2.5-7B-Instruct (Q4_K_M) 로드
3. Server 설정:
   - Context Length: 4096
   - GPU: Auto
4. Start Server
5. 상태 확인: "Running"
```

#### 2. 연결 테스트
```bash
python main.py --test-connection
```

#### 3. 간단한 테스트 실행
```bash
# 짧은 글부터 테스트
python main.py --mode simple --topic "인공지능의 역사" --max-iterations 1
```

#### 4. 책 생성 (단계적)
```bash
# 1챕터만 먼저
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 1 --max-iterations 2

# 성공하면 3챕터로
python main.py --mode book --book-type history --topic "애플의 역사" --chapters 3 --max-iterations 2
```

---

## 🎯 최적 설정 조합

### 고성능 시스템 (16GB+ RAM, GPU)
```bash
# LM Studio 설정
- Model: Qwen2.5-7B-Instruct (Q4_K_M)
- Context: 8192
- GPU: Full offload

# 실행 명령
python main.py --mode book --book-type history --topic "주제" --chapters 5 --max-iterations 3
```

### 중간 시스템 (8-16GB RAM)
```bash
# LM Studio 설정
- Model: Qwen2.5-7B-Instruct (Q4_K_M)
- Context: 4096
- GPU: Auto

# 실행 명령
python main.py --mode book --book-type history --topic "주제" --chapters 3 --max-iterations 2
```

### 저사양 시스템 (8GB RAM)
```bash
# LM Studio 설정
- Model: Qwen2.5-3B-Instruct (Q4_K_M)
- Context: 2048
- GPU: Auto

# 실행 명령
python main.py --mode simple --topic "주제" --max-iterations 1
```

---

## 🔍 디버깅 팁

### 로그 확인
에러 발생 시 전체 스택 트레이스 저장:
```bash
python main.py --mode book --book-type history --topic "주제" --chapters 3 2>&1 | tee error.log
```

### 상태 저장 위치
세션 데이터 확인:
```bash
# Checkpoint DB
ls -lh data/checkpoints.sqlite

# 생성된 책
ls -R output/books/
```

### Thread ID로 재개
크래시 후 재개:
```bash
# 에러 메시지에서 Session ID 확인
# 예: Session ID: e8d52f69-c279-4579-a6bf-0cdb75ebb89b

python main.py --mode book --thread-id e8d52f69-c279-4579-a6bf-0cdb75ebb89b
```

---

## 📞 추가 도움말

### LM Studio 공식 문서
- https://lmstudio.ai/docs

### 모델 다운로드
- Hugging Face: https://huggingface.co/Qwen

### 시스템 요구사항 확인
```bash
# 메모리 확인 (Mac)
sysctl hw.memsize

# 메모리 확인 (Linux)
free -h

# Python 환경
python --version
pip list | grep -E "(langgraph|openai|duckduckgo)"
```

---

**작성일**: 2025-12-28
**버전**: 1.0
**시스템**: Writer-Editor Multi-Agent Book System
