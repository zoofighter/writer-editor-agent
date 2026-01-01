# 실행 예제 가이드

본 문서는 Writer-Editor 에이전트 시스템의 다양한 실행 예제를 제공합니다.

## 목차

1. [기본 실행 예제](#1-기본-실행-예제)
2. [고급 옵션](#2-고급-옵션)
3. [간단한 워크플로우](#3-간단한-워크플로우)
4. [연결 테스트](#4-연결-테스트)
5. [실행 흐름 예제](#5-실행-흐름-예제)
6. [생성된 파일 확인](#6-생성된-파일-확인)
7. [프로그래밍 방식 사용](#7-프로그래밍-방식-사용)
8. [다양한 책 유형 예제](#8-다양한-책-유형-예제)
9. [워크플로우 모드 비교](#9-워크플로우-모드-비교)
10. [출력 파일 구조](#10-출력-파일-구조)
11. [문제 해결](#11-문제-해결)

---

## 1. 기본 실행 예제

### 역사서 생성 (구글의 역사)

```bash
python main.py --mode book --book-type history --topic "구글의 역사" --chapters 5
```

**용도**: 역사적 사실, 타임라인, 인용이 필요한 책
**특징**:
- Fact-checking 활성화
- Bibliography 자동 생성
- Timeline 구성 지원

---

### 기술 가이드 생성 (GPT 모델 이해)

```bash
python main.py --mode book --book-type technical_guide --topic "GPT 모델의 이해" --chapters 12
```

**용도**: 기술 문서, 아키텍처 가이드, 개념 설명서
**특징**:
- Math formulas (LaTeX) 지원
- Diagram 생성 (Mermaid/PlantUML)
- 용어 사전 자동 생성
- 교차 참조 관리

---

### Python 튜토리얼 생성

```bash
python main.py --mode tutorial --topic "Python 초보자를 위한 가이드" --chapters 15
```

**용도**: 프로그래밍 튜토리얼, 코드 예제가 필요한 교육 자료
**특징**:
- Code example 자동 생성
- Exercise (연습문제) 생성
- 코드 검증 (PythonCodeValidator)
- 단계별 학습 구조

---

### 일반 논픽션 생성

```bash
python main.py --mode book --book-type general --topic "인공지능과 미래 사회" --chapters 8
```

**용도**: 일반 논픽션, 에세이, 비즈니스 서적
**특징**:
- 균형잡힌 에이전트 구성
- 실용적 예제 중심
- 대중 독자 대상

---

## 2. 고급 옵션

### 반복 횟수 제한 설정

```bash
python main.py --mode book --book-type history \
  --topic "Tesla의 역사" \
  --chapters 7 \
  --max-iterations 5 \
  --max-outline-revisions 2
```

**옵션 설명**:
- `--max-iterations`: 각 챕터의 최대 수정 반복 횟수 (기본값: 10)
- `--max-outline-revisions`: 목차 수정 최대 반복 횟수 (기본값: 3)

**사용 시나리오**:
- 빠른 프로토타입 생성 시 낮은 값 사용
- 고품질 콘텐츠 필요 시 높은 값 사용

---

### 세션 재개 (중단된 작업 계속하기)

```bash
# 첫 실행 시 Session ID가 출력됨
# 예: "Session ID: 6d98d02c-c9d6-4094-917c-8bfae6e10310"

# 세션 재개
python main.py --thread-id 6d98d02c-c9d6-4094-917c-8bfae6e10310
```

**사용 시나리오**:
- 프로그램이 중단된 경우
- 인터넷 연결 끊김
- LM Studio 재시작 필요
- 작업 일시 중단 후 재개

**주의사항**:
- SQLite 체크포인트에 상태 저장됨 (`data/checkpoints.sqlite`)
- 같은 thread_id로 재개 시 정확히 중단 시점부터 계속됨

---

## 3. 간단한 워크플로우

### Writer-Editor만 사용 (간단한 글쓰기)

```bash
python main.py --mode simple --topic "AI의 미래"
```

**워크플로우**:
```
START → Writer → Editor → User Intervention → [continue/stop]
```

**사용 시나리오**:
- 빠른 블로그 포스트 작성
- 간단한 아티클
- 프로토타입 초안

**특징**:
- 2개 에이전트만 사용
- 빠른 실행
- 최소한의 Human-in-the-Loop

---

### 멀티 에이전트 (블로그 포스트)

```bash
python main.py --mode multi-agent --topic "클라우드 컴퓨팅 입문"
```

**워크플로우**:
```
START → Business Analyst → Content Strategist → Outline Reviewer
     → Web Search → Writer → Editor → END
```

**사용 시나리오**:
- 고품질 블로그 포스트
- 마케팅 카피
- 기술 아티클
- 리포트

**특징**:
- 6개 에이전트 사용
- 웹 검색 통합
- 구조화된 목차
- 목차 검토 루프

---

## 4. 연결 테스트

### LM Studio 연결 확인

```bash
python main.py --test-connection
```

**출력 예시 (성공)**:
```
Testing connection to LM Studio at http://localhost:1234/v1...
✓ Successfully connected to LM Studio
  Model: qwen
```

**출력 예시 (실패)**:
```
✗ Failed to connect to LM Studio

Troubleshooting:
1. Make sure LM Studio is running
2. Check that the local server is started (port 1234)
3. Verify the model is loaded
```

**문제 해결 단계**:
1. LM Studio 앱 실행 확인
2. 로컬 서버 시작 (포트 1234)
3. 모델 로드 확인 (Qwen 권장)
4. `.env` 파일의 `LM_STUDIO_BASE_URL` 확인

---

## 5. 실행 흐름 예제

### 구글 역사 책 생성 - 전체 과정

#### Step 1: 환경 확인

```bash
# LM Studio 연결 테스트
python main.py --test-connection
```

#### Step 2: 책 생성 시작

```bash
python main.py --mode book --book-type history --topic "구글의 역사" --chapters 3
```

#### Step 3: 예상 출력

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     Writer-Editor Review Loop System                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Mode: BOOK | LLM: qwen @ http://localhost:1234/v1

Session ID: 6d98d02c-c9d6-4094-917c-8bfae6e10310

Starting book generation: 구글의 역사
Book Type: history
Chapters: 3


=== BUSINESS ANALYST ===
Analyzing user intent...
✓ Document type: historical_book
✓ Target audience: general readers, tech enthusiasts
✓ Tone: informative, engaging


=== BOOK COORDINATOR ===
Planning book structure...
✓ Book title: "구글의 역사: 검색엔진에서 테크 제국까지"
✓ Table of contents generated (3 chapters)
✓ Chapter dependencies identified
✓ Terminology glossary initialized


Writing Chapter 1...

=== CONTENT STRATEGIST ===
Creating chapter outline...
✓ Chapter 1: "구글의 탄생과 초기 혁신"
  - 섹션 5개 계획됨

=== WEB SEARCH ===
Researching section: Background/Context
Warning: duckduckgo-search not installed. Install with: pip install duckduckgo-search
Researching section: Main Content
...

=== WRITER ===
Generating chapter draft...

╭────────────────────────── Chapter 1 Draft ──────────────────────────────╮
│ Imagine a world without instant access to information—where finding     │
│ answers required flipping through encyclopedias or asking strangers on  │
│ the street. Today, that world feels almost foreign. The search engine   │
│ that transformed how we interact with knowledge is Google, a company    │
│ born from a simple idea but built into a global powerhouse. Founded in  │
│ 1998 by Larry Page and Sergey Brin...                                   │
╰──────────────────────────────────────────────────────────────────────────╯
Full length: 7244 characters

=== FACT CHECK ===
Verifying claims...
✓ 12 claims verified
✓ Confidence score: 0.85

=== BIBLIOGRAPHY ===
Generating citations...
✓ 8 sources cited in APA format

=== EDITOR ===
Reviewing chapter...

╭────────────────────────── Editor Feedback ──────────────────────────────╮
│ **Strengths:**                                                           │
│ - Strong Hook and Engaging Tone                                          │
│ - Clear Structure                                                        │
│ - Comprehensive Historical Coverage                                      │
│                                                                          │
│ **Areas for Improvement:**                                               │
│ 1. Clarity and Flow in the Main Content Section                          │
│ 2. Depth on Key Innovations                                              │
│ ...                                                                      │
╰──────────────────────────────────────────────────────────────────────────╯

✓ Book generation completed successfully!

Final output:
  - Markdown: output/books/구글의_역사/complete_book.md
  - PDF: output/books/구글의_역사/complete_book.pdf
```

---

## 6. 생성된 파일 확인

### 디렉토리 구조 확인

```bash
# 생성된 책 목록 보기
ls -la output/books/

# 특정 책의 내용 확인
ls -la output/books/구글의_역사/
```

**출력 예시**:
```
drwxr-xr-x  구글의_역사/
├── chapter_01.md
├── chapter_02.md
├── chapter_03.md
├── complete_book.md
└── complete_book.pdf
```

### 챕터 내용 보기

```bash
# 특정 챕터 읽기
cat output/books/구글의_역사/chapter_01.md

# 완성된 책 읽기
cat output/books/구글의_역사/complete_book.md

# Less로 페이지 단위 읽기
less output/books/구글의_역사/complete_book.md
```

### PDF 열기 (macOS)

```bash
open output/books/구글의_역사/complete_book.pdf
```

### PDF 열기 (Linux)

```bash
xdg-open output/books/구글의_역사/complete_book.pdf
```

### PDF 열기 (Windows)

```bash
start output/books/구글의_역사/complete_book.pdf
```

---

## 7. 프로그래밍 방식 사용

### Python 스크립트에서 직접 사용

```python
from src.graph.workflow import compile_workflow, create_initial_state
from src.config.settings import settings

# 워크플로우 컴파일
app = compile_workflow(mode="book")

# 초기 상태 생성
initial_state = create_initial_state(
    topic="인공지능의 역사",
    mode="book",
    book_type="history",
    estimated_chapters=10,
    max_iterations=5,
    max_outline_revisions=2
)

# 설정
config = {
    "configurable": {
        "thread_id": "my-ai-history-book"
    }
}

# 실행 및 이벤트 처리
for event in app.stream(initial_state, config, stream_mode="values"):
    current_stage = event.get("current_stage", "")
    print(f"Stage: {current_stage}")

    # 챕터 완료 시
    if event.get("current_draft"):
        chapter_num = event.get('chapter_number', 0)
        draft_length = len(event.get('current_draft', ''))
        print(f"Chapter {chapter_num} completed! ({draft_length} characters)")

    # 피드백 생성 시
    if event.get("current_feedback"):
        print(f"Editor feedback received")
```

### 커스텀 에이전트 통합

```python
from src.agents import WriterAgent, EditorAgent
from src.llm.client import LMStudioClient

# LLM 클라이언트 초기화
client = LMStudioClient(
    base_url="http://localhost:1234/v1",
    model_name="qwen",
    temperature=0.7,
    max_tokens=2000
)

# Writer 에이전트 사용
writer = WriterAgent(llm_client=client, temperature=0.8)
draft = writer.create_initial_draft(topic="AI의 미래")

print(f"Draft length: {len(draft)} characters")
print(draft[:500])  # 처음 500자 출력

# Editor 에이전트 사용
editor = EditorAgent(llm_client=client, temperature=0.3)
feedback = editor.review_draft(draft, iteration=1)

print("\nEditor Feedback:")
print(feedback)
```

### 웹 검색 통합

```python
from src.agents import WebSearchAgent

# 웹 검색 에이전트 초기화
search_agent = WebSearchAgent(search_provider="duckduckgo")

# 검색 쿼리 실행
queries = [
    "Google history founding",
    "Larry Page Sergey Brin Stanford",
    "PageRank algorithm"
]

results = search_agent.search_multiple_queries(queries, max_results=5)

for query, search_results in results.items():
    print(f"\nQuery: {query}")
    for result in search_results:
        print(f"  - {result['title']}: {result['url']}")
```

---

## 8. 다양한 책 유형 예제

### 역사서

```bash
python main.py --mode book --book-type history \
  --topic "Apple의 역사" \
  --chapters 8
```

**구조 예시**:
- Chapter 1: 창업과 초기 비전
- Chapter 2: Apple II와 개인 컴퓨터 혁명
- Chapter 3: Macintosh의 탄생
- Chapter 4: Steve Jobs의 복귀
- Chapter 5: iPod과 디지털 음악 혁명
- Chapter 6: iPhone과 모바일 시대
- Chapter 7: iPad와 생태계 확장
- Chapter 8: 현재와 미래 전망

---

### 기술 가이드

```bash
python main.py --mode book --book-type technical_guide \
  --topic "Docker 완벽 가이드" \
  --chapters 15
```

**구조 예시**:
- Chapter 1: 컨테이너 기초
- Chapter 2: Docker 설치 및 설정
- Chapter 3: Docker 이미지 이해
- Chapter 4: Dockerfile 작성법
- Chapter 5: 컨테이너 네트워킹
- Chapter 6: 볼륨과 데이터 관리
- Chapter 7: Docker Compose
- Chapter 8: Multi-stage 빌드
- Chapter 9: 보안 베스트 프랙티스
- Chapter 10: 성능 최적화
- Chapter 11: Docker Swarm
- Chapter 12: Kubernetes 통합
- Chapter 13: CI/CD 파이프라인
- Chapter 14: 모니터링과 로깅
- Chapter 15: 프로덕션 배포

---

### 프로그래밍 튜토리얼

```bash
python main.py --mode tutorial \
  --topic "FastAPI 시작하기" \
  --chapters 12
```

**구조 예시** (코드 예제 + 연습문제 포함):
- Chapter 1: FastAPI 소개 및 환경 설정
- Chapter 2: 첫 번째 API 만들기
- Chapter 3: Path Parameters와 Query Parameters
- Chapter 4: Request Body와 Pydantic 모델
- Chapter 5: Response Models와 상태 코드
- Chapter 6: 의존성 주입 (Dependency Injection)
- Chapter 7: 데이터베이스 연동 (SQLAlchemy)
- Chapter 8: 인증과 권한 관리
- Chapter 9: 파일 업로드와 다운로드
- Chapter 10: WebSocket 실시간 통신
- Chapter 11: 테스팅과 문서화
- Chapter 12: 배포와 프로덕션 설정

---

### 일반 논픽션

```bash
python main.py --mode book --book-type general \
  --topic "디지털 마케팅 전략" \
  --chapters 10
```

**구조 예시**:
- Chapter 1: 디지털 마케팅 개요
- Chapter 2: 타겟 오디언스 분석
- Chapter 3: 콘텐츠 마케팅 전략
- Chapter 4: SEO와 검색 엔진 최적화
- Chapter 5: 소셜 미디어 마케팅
- Chapter 6: 이메일 마케팅 캠페인
- Chapter 7: 유료 광고 (PPC)
- Chapter 8: 데이터 분석과 KPI
- Chapter 9: 마케팅 자동화
- Chapter 10: 사례 연구 및 베스트 프랙티스

---

## 9. 워크플로우 모드 비교

| 모드 | 에이전트 수 | 실행 시간 | 품질 | 사용 시나리오 |
|------|------------|----------|------|--------------|
| `simple` | 2개<br>(Writer, Editor) | ⚡ 빠름<br>(~2분) | ⭐⭐⭐ 기본 | 빠른 초안, 블로그 포스트 |
| `multi-agent` | 6개<br>(BA, CS, OR, WS, W, E) | ⚡⚡ 보통<br>(~5분) | ⭐⭐⭐⭐ 우수 | 고품질 아티클, 리포트 |
| `book` | 12개<br>(모든 book agents) | ⚡⚡⚡ 느림<br>(~15분/챕터) | ⭐⭐⭐⭐⭐ 최상 | 역사서, 기술 가이드 |
| `tutorial` | 14개<br>(+ Code, Exercise) | ⚡⚡⚡⚡ 매우 느림<br>(~20분/챕터) | ⭐⭐⭐⭐⭐ 최상 | 프로그래밍 튜토리얼 |

### 에이전트 약어

- **BA**: Business Analyst
- **CS**: Content Strategist
- **OR**: Outline Reviewer
- **WS**: Web Search
- **W**: Writer
- **E**: Editor
- **Book agents**: Coordinator, Fact Check, Math, Diagram, Bibliography, Cross Reference
- **Tutorial agents**: Code Example Generator, Exercise Generator

---

## 10. 출력 파일 구조

### 생성된 책의 디렉토리 구조

```
output/books/구글의_역사/
├── chapter_01.md          # 챕터 1: 구글의 탄생과 초기 혁신
├── chapter_02.md          # 챕터 2: 검색 엔진의 진화
├── chapter_03.md          # 챕터 3: 글로벌 테크 기업으로의 성장
├── complete_book.md       # 전체 책 (목차 + 모든 챕터 + 용어집)
└── complete_book.pdf      # PDF 버전 (pandoc 설치 시)
```

### 챕터 파일 구조 예시

```markdown
# Chapter 1: 구글의 탄생과 초기 혁신

[본문 내용 - 7000자 이상]

## Formulas

- **F1.1**: PageRank 알고리즘
  - Description: 웹페이지 중요도 계산 공식
  - LaTeX: `PR(A) = (1-d) + d \sum_{i=1}^{n} \frac{PR(T_i)}{C(T_i)}`

## Diagrams

- **D1.1**: Google 검색 아키텍처
  - Type: mermaid
  - Caption: 초기 Google 검색 시스템의 구조

## References

### Bibliography

1. Battelle, J. (2005). *The Search: How Google and Its Rivals Rewrote the Rules of Business*. Portfolio.
2. Levy, S. (2011). *In the Plex: How Google Thinks, Works, and Shapes Our Lives*. Simon & Schuster.
3. Vise, D. A., & Malseed, M. (2005). *The Google Story*. Delacorte Press.

### Cross-References

- See Chapter 2 for details on PageRank evolution
- Related to Chapter 3: "Global Expansion Strategy"
```

### 완성된 책 파일 구조

```markdown
---
title: "구글의 역사: 검색엔진에서 테크 제국까지"
author: "AI Writer System"
date: 2025-01-15
version: 1.0.0
---

# 구글의 역사: 검색엔진에서 테크 제국까지

**Author:** AI Writer System

**Version:** 1.0.0

**Published:** 2025-01-15

## Description

이 책은 Google의 탄생부터 현재까지의 역사를 다루며...

\pagebreak

# Table of Contents

1. **구글의 탄생과 초기 혁신**
   Stanford에서 시작된 검색 엔진 프로젝트부터 회사 설립까지

2. **검색 엔진의 진화**
   PageRank 알고리즘의 발전과 검색 품질 향상

3. **글로벌 테크 기업으로의 성장**
   IPO, 제품 확장, 그리고 Alphabet 재편

\pagebreak

# Chapter 1: 구글의 탄생과 초기 혁신

[전체 챕터 내용]

\pagebreak

# Chapter 2: 검색 엔진의 진화

[전체 챕터 내용]

\pagebreak

# Chapter 3: 글로벌 테크 기업으로의 성장

[전체 챕터 내용]

\pagebreak

# Glossary

**PageRank**
: 웹페이지의 중요도를 측정하는 Google의 핵심 알고리즘
  *First introduced in Chapter 1*

**AdWords**
: Google의 광고 플랫폼 (현재는 Google Ads로 명칭 변경)
  *First introduced in Chapter 2*

\pagebreak

# Appendix: Fact-Checking Report

## Summary

- Total Claims Verified: 45
- Verified: 38
- Unverified: 5
- Disputed: 2

## Chapter 1

**Claim:** Google was founded in 1998
- **Status:** verified
- **Confidence:** 0.95
- **Sources:**
  - https://about.google/our-story/
  - Wikipedia: History of Google
```

---

## 11. 문제 해결

### LM Studio 연결 안 됨

**증상**:
```
✗ Failed to connect to LM Studio
Connection refused
```

**해결 방법**:

1. **LM Studio 실행 확인**
   ```bash
   # 프로세스 확인 (macOS/Linux)
   ps aux | grep "LM Studio"

   # 포트 확인
   lsof -i :1234
   ```

2. **로컬 서버 시작**
   - LM Studio 앱 열기
   - "Local Server" 탭 선택
   - "Start Server" 클릭
   - 포트 1234 확인

3. **모델 로드 확인**
   - Models 탭에서 모델 선택
   - Qwen 시리즈 권장 (예: Qwen2.5-7B-Instruct)
   - "Load Model" 클릭

4. **.env 파일 확인**
   ```bash
   cat .env
   ```

   확인 사항:
   ```env
   LM_STUDIO_BASE_URL=http://localhost:1234/v1
   LM_STUDIO_MODEL=qwen
   ```

5. **재시도**
   ```bash
   python main.py --test-connection
   ```

---

### 웹 검색 경고 (선택사항)

**증상**:
```
Warning: duckduckgo-search not installed.
Install with: pip install duckduckgo-search
```

**영향**:
- 웹 검색 기능 비활성화
- 리서치 데이터 없이 작성됨
- 책 품질 다소 저하 가능

**해결 방법**:

```bash
# DuckDuckGo 검색 라이브러리 설치
pip install duckduckgo-search

# 또는 requirements.txt 업데이트 후
pip install -r requirements.txt
```

**선택적 검색 제공자**:

```bash
# Tavily (AI 최적화)
pip install tavily-python
# .env에 추가: TAVILY_API_KEY=your-api-key

# Serper (Google 결과)
pip install requests
# .env에 추가: SERPER_API_KEY=your-api-key
```

---

### 세션 중단 후 재개

**증상**:
- 프로그램이 갑자기 종료됨
- 인터넷 연결 끊김
- 전원 문제

**해결 방법**:

1. **Session ID 확인**
   ```
   Session ID: 6d98d02c-c9d6-4094-917c-8bfae6e10310
   ```

   위 ID를 복사하세요.

2. **세션 재개**
   ```bash
   python main.py --thread-id 6d98d02c-c9d6-4094-917c-8bfae6e10310
   ```

3. **체크포인트 확인**
   ```bash
   ls -la data/checkpoints.sqlite
   ```

   파일이 있으면 세션 상태가 저장된 것입니다.

4. **다중 세션 관리**
   ```bash
   # 세션 A (구글 역사)
   python main.py --mode book --book-type history \
     --topic "구글의 역사" \
     --thread-id google-history-v1

   # 세션 B (AI 튜토리얼)
   python main.py --mode tutorial \
     --topic "AI 기초" \
     --thread-id ai-tutorial-v1
   ```

---

### PDF 생성 실패

**증상**:
```
Warning: pandoc not found. Skipping PDF generation.
```

**해결 방법**:

1. **Pandoc 설치 (macOS)**
   ```bash
   brew install pandoc
   brew install --cask basictex  # LaTeX 엔진
   ```

2. **Pandoc 설치 (Ubuntu/Debian)**
   ```bash
   sudo apt-get update
   sudo apt-get install pandoc texlive-xetex
   ```

3. **Pandoc 설치 (Windows)**
   - https://pandoc.org/installing.html 에서 설치
   - MiKTeX 또는 TeX Live 설치

4. **설치 확인**
   ```bash
   pandoc --version
   xelatex --version
   ```

5. **.env 설정**
   ```env
   GENERATE_PDF=true
   PANDOC_PATH=pandoc  # 또는 전체 경로
   ```

---

### 메모리 부족

**증상**:
```
MemoryError: Unable to allocate array
```

**해결 방법**:

1. **작은 모델 사용**
   - Qwen2.5-7B 대신 Qwen2.5-3B 사용
   - LM Studio에서 Quantized 모델 선택

2. **챕터 수 줄이기**
   ```bash
   # 15챕터 → 5챕터
   python main.py --mode book --book-type history \
     --topic "주제" \
     --chapters 5
   ```

3. **반복 제한**
   ```bash
   python main.py --max-iterations 3 --max-outline-revisions 1
   ```

4. **체크포인트 주기적 정리**
   ```bash
   # 오래된 세션 삭제
   rm data/checkpoints.sqlite
   ```

---

### 한글 인코딩 문제

**증상**:
- PDF에 한글이 깨짐
- 출력 파일에 � 문자 표시

**해결 방법**:

1. **UTF-8 인코딩 확인**
   ```bash
   file -I output/books/구글의_역사/complete_book.md
   # charset=utf-8 확인
   ```

2. **XeLaTeX 사용** (이미 기본 설정)
   - pandoc은 자동으로 XeLaTeX 사용
   - Unicode 완벽 지원

3. **폰트 설치** (필요 시)
   ```bash
   # macOS - 나눔 폰트
   brew tap homebrew/cask-fonts
   brew install --cask font-nanum-gothic

   # Ubuntu
   sudo apt-get install fonts-nanum
   ```

---

### 긴 실행 시간

**증상**:
- 한 챕터 생성에 20분 이상 소요

**원인**:
- LM Studio 모델 속도
- 웹 검색 지연
- 많은 에이전트 실행

**최적화 방법**:

1. **더 빠른 모델 사용**
   - Qwen2.5-7B-Instruct-Q4_K_M (Quantized)
   - 또는 더 작은 3B 모델

2. **웹 검색 비활성화** (임시)
   ```python
   # src/config/settings.py
   enable_web_search: bool = False
   ```

3. **에이전트 선택적 비활성화**
   ```python
   # src/config/settings.py
   enable_fact_checking: bool = False
   enable_diagrams: bool = False
   ```

4. **Simple 모드 사용**
   ```bash
   python main.py --mode simple --topic "주제"
   ```

---

## 추가 리소스

### 공식 문서

- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [LM Studio 가이드](https://lmstudio.ai/docs)
- [Pandoc 매뉴얼](https://pandoc.org/MANUAL.html)

### 예제 프로젝트

- `examples/` 디렉토리에 추가 예제 제공
- `tests/` 디렉토리에 테스트 케이스 참조

### 커뮤니티 지원

- GitHub Issues: 버그 리포트 및 기능 요청
- Discussions: 질문 및 아이디어 공유

---

## 다음 단계

1. **테스트 실행**: 간단한 예제로 시스템 테스트
2. **설정 조정**: `.env` 파일에서 파라미터 최적화
3. **커스텀 템플릿**: 자신만의 책 템플릿 작성
4. **에이전트 확장**: 새로운 전문 에이전트 추가

성공적인 책 생성을 기원합니다! 🎉
