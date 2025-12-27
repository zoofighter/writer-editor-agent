# 사용 가이드

## 목차

1. [빠른 시작](#빠른-시작)
2. [설치](#설치)
3. [기본 사용법](#기본-사용법)
4. [고급 사용법](#고급-사용법)
5. [설정 커스터마이징](#설정-커스터마이징)
6. [세션 관리](#세션-관리)
7. [웹 검색 설정](#웹-검색-설정)
8. [문제 해결](#문제-해결)

---

## 빠른 시작

### 5분 안에 시작하기

```bash
# 1. 저장소 클론
git clone https://github.com/zoofighter/writer-editor-agent.git
cd writer-editor-agent

# 2. 가상 환경 및 의존성 설치
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env

# 4. LM Studio 시작 (별도 애플리케이션)
# - LM Studio 실행
# - Qwen 모델 로드
# - 로컬 서버 시작 (포트 1234)

# 5. 연결 테스트
python main.py --test-connection

# 6. 첫 콘텐츠 생성
python main.py --topic "파이썬 비동기 프로그래밍 소개"
```

---

## 설치

### 필수 요구사항

- **Python**: 3.10 이상
- **LM Studio**: 최신 버전
- **운영체제**: macOS, Linux, Windows

### 1단계: Python 환경 준비

```bash
# Python 버전 확인
python --version
# Python 3.10.0 이상이어야 함

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# macOS/Linux:
source venv/bin/activate

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate.bat
```

### 2단계: 의존성 설치

```bash
# requirements.txt로 설치
pip install -r requirements.txt

# 또는 pyproject.toml로 설치 (개발 모드)
pip install -e ".[dev]"
```

### 3단계: LM Studio 설정

1. [LM Studio](https://lmstudio.ai/) 다운로드 및 설치
2. LM Studio 실행
3. 모델 다운로드:
   - 검색: "qwen" 또는 원하는 모델
   - 다운로드 (권장: Qwen2.5-7B-Instruct 이상)
4. 로컬 서버 시작:
   - "Local Server" 탭 이동
   - 모델 선택
   - "Start Server" 클릭
   - 포트 1234 확인

### 4단계: 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (선택사항)
# nano .env
# 또는
# code .env
```

`.env` 파일 내용:
```env
# LM Studio 설정
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=qwen

# 에이전트 Temperature
BUSINESS_ANALYST_TEMPERATURE=0.2
CONTENT_STRATEGIST_TEMPERATURE=0.5
OUTLINE_REVIEWER_TEMPERATURE=0.2
WRITER_TEMPERATURE=0.8
EDITOR_TEMPERATURE=0.3

# 워크플로우 설정
MAX_ITERATIONS=10
MAX_OUTLINE_REVISIONS=3

# 웹 검색 (선택사항)
SEARCH_PROVIDER=duckduckgo
ENABLE_WEB_SEARCH=True
```

### 5단계: 연결 테스트

```bash
python main.py --test-connection
```

성공 시:
```
Testing connection to LM Studio at http://localhost:1234/v1...
✓ Successfully connected to LM Studio
  Model: qwen
```

---

## 기본 사용법

### 1. 대화형 모드 (기본)

```bash
python main.py
```

프롬프트가 나타나면 토픽 입력:
```
What topic would you like to write about? AI in healthcare
```

### 2. 토픽 지정 모드

```bash
python main.py --topic "Python 데코레이터 완벽 가이드"
```

### 3. Simple 모드 (Writer-Editor만)

```bash
python main.py --mode simple --topic "머신러닝 기초"
```

### 워크플로우 흐름

#### Multi-Agent Mode (기본)

```
1. 토픽 입력
   ↓
2. Business Analyst가 의도 분석
   - 문서 유형, 대상 독자, 톤 파악
   ↓
3. Content Strategist가 목차 생성
   - 템플릿 기반 구조화
   ↓
4. Outline Reviewer가 목차 검토
   - 품질 평가 및 피드백
   - 승인되지 않으면 2-3회 반복
   ↓
5. 👤 사용자 목차 승인
   - proceed: 다음 단계
   - revise: 목차 수정
   ↓
6. Web Search Agent가 리서치
   - 섹션별 정보 수집
   ↓
7. Writer가 초안 작성
   - 목차 + 리서치 기반
   ↓
8. Editor가 피드백 제공
   ↓
9. 👤 사용자 초안 검토
   - continue: 수정 루프
   - stop: 완료
   ↓
10. 최종 문서 완성
```

#### Simple Mode

```
1. 토픽 입력
   ↓
2. Writer가 초안 작성
   ↓
3. Editor가 피드백
   ↓
4. 👤 사용자 결정
   - continue/stop
   ↓
5. 완료 또는 2로 돌아감
```

---

## 고급 사용법

### 반복 횟수 커스터마이징

```bash
# 목차 최대 2회, 초안 최대 5회 반복
python main.py --max-outline-revisions 2 --max-iterations 5 --topic "Django REST Framework"
```

### 세션 재개

```bash
# 첫 실행 (세션 ID 확인)
python main.py --topic "React Hooks"
# Session ID: abc-123-def (터미널 출력)

# 세션 중단 (Ctrl+C) 후 재개
python main.py --thread-id abc-123-def
```

### 모드 전환

```bash
# Multi-Agent 모드 (전체 파이프라인)
python main.py --mode multi-agent --topic "TypeScript 제네릭"

# Simple 모드 (빠른 초안)
python main.py --mode simple --topic "Quick Git Tutorial"
```

### 프로그래매틱 사용

Python 스크립트에서 직접 사용:

```python
from src.graph import compile_workflow, create_initial_state
from src.ui import CLI

# 방법 1: CLI 사용
cli = CLI(mode="multi-agent")
cli.start_session(
    topic="Kubernetes 배포 전략",
    max_iterations=3
)

# 방법 2: 직접 워크플로우 제어
app = compile_workflow("multi-agent")
initial_state = create_initial_state("Docker 컨테이너 최적화")
config = {"configurable": {"thread_id": "my-session"}}

for event in app.stream(initial_state, config):
    print(event.get("current_stage"))
```

---

## 설정 커스터마이징

### Temperature 조정

각 에이전트의 창의성 조절:

```env
# .env 파일
BUSINESS_ANALYST_TEMPERATURE=0.1  # 매우 분석적
CONTENT_STRATEGIST_TEMPERATURE=0.7  # 더 창의적
WRITER_TEMPERATURE=0.9  # 매우 창의적
EDITOR_TEMPERATURE=0.2  # 매우 엄격
```

**가이드라인**:
- **0.1-0.3**: 분석적, 사실 기반 (Analyst, Reviewer, Editor)
- **0.4-0.6**: 균형잡힌 (Strategist)
- **0.7-0.9**: 창의적 (Writer)

### 토큰 제한 조정

```env
MAX_TOKENS=3000  # 더 긴 출력
```

### 반복 제한

```env
MAX_ITERATIONS=15  # 더 많은 초안 수정
MAX_OUTLINE_REVISIONS=5  # 더 많은 목차 검토
```

---

## 세션 관리

### 세션 ID 이해

각 세션은 고유 ID를 가지며, SQLite 데이터베이스에 저장됩니다:

```
data/checkpoints.sqlite
```

### 세션 재개

```bash
# 1. 이전 세션 ID 확인 (첫 실행 시 출력됨)
Session ID: f47ac10b-58cc-4372-a567-0e02b2c3d479

# 2. 세션 재개
python main.py --thread-id f47ac10b-58cc-4372-a567-0e02b2c3d479
```

### 여러 세션 동시 관리

```bash
# 세션 1: 블로그 포스트
python main.py --thread-id blog-ai-healthcare --topic "AI in Healthcare"

# 세션 2: 기술 문서
python main.py --thread-id tech-kubernetes --topic "Kubernetes Architecture"

# 나중에 각각 재개 가능
```

### 세션 데이터 백업

```bash
# 체크포인트 데이터베이스 백업
cp data/checkpoints.sqlite data/checkpoints-backup.sqlite
```

---

## 웹 검색 설정

### DuckDuckGo (기본, 무료)

`.env` 설정:
```env
SEARCH_PROVIDER=duckduckgo
ENABLE_WEB_SEARCH=True
```

API 키 불필요. 즉시 사용 가능.

### Tavily (AI 최적화, 유료)

1. [Tavily](https://tavily.com/) 계정 생성
2. API 키 발급
3. `.env` 설정:

```env
SEARCH_PROVIDER=tavily
SEARCH_API_KEY=tvly-your-api-key-here
ENABLE_WEB_SEARCH=True
```

### Serper (Google 결과, 유료)

1. [Serper](https://serper.dev/) 계정 생성
2. API 키 발급
3. `.env` 설정:

```env
SEARCH_PROVIDER=serper
SEARCH_API_KEY=your-serper-api-key
ENABLE_WEB_SEARCH=True
```

### 검색 결과 수 조정

```env
MAX_SEARCH_RESULTS_PER_QUERY=10  # 기본값: 5
```

### 웹 검색 비활성화

테스트나 빠른 실행 시:

```env
ENABLE_WEB_SEARCH=False
```

또는 커맨드라인:
```bash
python main.py --mode simple  # Simple 모드는 웹 검색 안 함
```

---

## 문제 해결

### LM Studio 연결 실패

**증상**:
```
✗ Failed to connect to LM Studio
```

**해결 방법**:
1. LM Studio가 실행 중인지 확인
2. 로컬 서버가 시작되었는지 확인 (포트 1234)
3. 모델이 로드되었는지 확인
4. `.env`의 `LM_STUDIO_BASE_URL` 확인
5. 방화벽 설정 확인

**테스트**:
```bash
# 직접 API 호출 테스트
curl http://localhost:1234/v1/models
```

### JSON 파싱 오류

**증상**:
```
Warning: Failed to parse Business Analyst output
```

**원인**: LLM이 JSON 형식이 아닌 응답 생성

**해결 방법**:
- 자동 폴백 메커니즘이 작동하므로 일반적으로 무시 가능
- 지속되면 다른 모델 시도 (Qwen 권장)
- Temperature 낮추기 (더 구조화된 출력)

### 웹 검색 실패

**증상**:
```
DuckDuckGo search error: ...
```

**해결 방법**:
1. 인터넷 연결 확인
2. API 키 확인 (Tavily/Serper 사용 시)
3. 프록시 설정 확인
4. 일시적으로 검색 비활성화:
   ```bash
   ENABLE_WEB_SEARCH=False python main.py
   ```

### 메모리 부족

**증상**: 시스템이 느려지거나 멈춤

**해결 방법**:
1. LM Studio에서 더 작은 모델 사용
2. `MAX_TOKENS` 줄이기
3. Simple 모드 사용
4. 반복 횟수 줄이기

### 세션 재개 실패

**증상**: 이전 세션을 찾을 수 없음

**해결 방법**:
1. Thread ID 정확히 입력했는지 확인
2. `data/checkpoints.sqlite` 파일 존재 확인
3. 데이터베이스 백업에서 복원

---

## 팁과 베스트 프랙티스

### 1. 효과적인 토픽 작성

**좋은 예**:
- "React Hooks를 사용한 상태 관리 패턴"
- "Django에서 REST API 보안 구현하기"
- "AWS Lambda로 서버리스 아키텍처 구축"

**피해야 할 예**:
- "프로그래밍" (너무 광범위)
- "버그 수정" (구체성 부족)

### 2. 모드 선택 가이드

**Multi-Agent 모드 사용 시기**:
- 긴 형식 콘텐츠 (1000+ 단어)
- 리서치가 필요한 주제
- 구조화된 문서 (블로그, 기술 문서)
- 품질이 매우 중요한 경우

**Simple 모드 사용 시기**:
- 빠른 초안 필요
- 짧은 콘텐츠 (500단어 미만)
- 개인적인 글쓰기
- 리서치 불필요한 주제

### 3. 반복 횟수 설정

**목차 반복** (`max_outline_revisions`):
- 1-2회: 빠른 진행
- 3회: 기본 (권장)
- 4-5회: 매우 정밀한 구조 필요

**초안 반복** (`max_iterations`):
- 3-5회: 빠른 완성
- 10회: 기본 (권장)
- 15-20회: 최고 품질 추구

### 4. 웹 검색 최적화

- DuckDuckGo: 일반 주제, 무료
- Tavily: AI/ML 관련 주제, 최신 정보
- Serper: 정확한 통계, 뉴스

### 5. 세션 관리

정기적으로 백업:
```bash
# 매주 백업 스크립트
cp data/checkpoints.sqlite backups/checkpoints-$(date +%Y%m%d).sqlite
```

---

## 예제 시나리오

### 시나리오 1: 블로그 포스트 작성

```bash
python main.py --topic "웹 개발에서 TypeScript 도입 경험담" \
               --max-iterations 7
```

**기대 결과**:
- 문서 유형: blog_post
- 5개 섹션 목차
- 웹 검색으로 TypeScript 통계 수집
- 약 2000단어 초안
- 5-7회 반복으로 완성

### 시나리오 2: 기술 문서

```bash
python main.py --topic "Kubernetes Pod 라이프사이클 상세 가이드" \
               --max-outline-revisions 4 \
               --max-iterations 10
```

**기대 결과**:
- 문서 유형: technical_article
- 기술적 섹션 구조
- 공식 문서 및 예제 검색
- 상세하고 정확한 내용

### 시나리오 3: 빠른 초안

```bash
python main.py --mode simple --topic "Git Rebase vs Merge 차이점"
```

**기대 결과**:
- 목차 및 리서치 건너뜀
- Writer가 바로 초안 작성
- 빠른 완성 (5분 이내)

---

## 자주 묻는 질문 (FAQ)

### Q: 오프라인에서 사용 가능한가요?

**A**: 부분적으로 가능합니다.
- LM Studio는 로컬에서 실행되므로 LLM은 오프라인 가능
- 웹 검색은 인터넷 연결 필요
- 오프라인 사용 시 `ENABLE_WEB_SEARCH=False` 설정

### Q: 다른 LLM 모델 사용 가능한가요?

**A**: 네, LM Studio에서 지원하는 모든 모델 사용 가능:
1. LM Studio에서 원하는 모델 다운로드
2. 로컬 서버에서 해당 모델 선택
3. `.env`에서 `LM_STUDIO_MODEL` 변경 (선택사항)

권장 모델:
- Qwen2.5-7B-Instruct
- Mistral-7B-Instruct
- Llama-3-8B-Instruct

### Q: 생성된 문서를 저장하는 방법은?

**A**: 현재 터미널 출력만 제공됩니다. 저장 방법:
```bash
# 출력 리다이렉션
python main.py --topic "..." > output.txt

# 또는 Python 스크립트에서:
# draft = state["current_draft"]
# with open("output.txt", "w") as f:
#     f.write(draft)
```

향후 버전에서 자동 저장 기능 추가 예정.

### Q: 한국어 지원되나요?

**A**: 네, 사용하는 LLM 모델에 따라 다릅니다:
- Qwen 모델: 한국어 우수
- 한국어 전용 모델 사용 가능 (예: KoAlpaca)

### Q: API 비용은 얼마나 드나요?

**A**:
- LM Studio: 무료 (로컬 실행)
- 웹 검색:
  - DuckDuckGo: 무료
  - Tavily: 유료 (API 요금제 확인)
  - Serper: 유료 (API 요금제 확인)

---

## 다음 단계

1. **기본 사용법 숙달**: Simple 모드로 시작하여 워크플로우 이해
2. **Multi-Agent 탐험**: 전체 파이프라인 경험
3. **설정 최적화**: Temperature 및 반복 횟수 조정
4. **고급 기능**: 프로그래매틱 사용, 커스텀 템플릿

더 많은 정보:
- [멀티 에이전트 아키텍처](multi-agent-architecture.md)
- [API 레퍼런스](api-reference.md)
- [구현 가이드](implementation-guide.md)
