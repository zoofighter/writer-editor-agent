# 멀티 에이전트 콘텐츠 생성 시스템 - 프로젝트 요약

**작성일**: 2025-12-27
**프로젝트**: Writer-Editor 멀티 에이전트 시스템 → 범용 서적 제작 시스템

---

## 📋 프로젝트 개요

LangGraph 기반의 멀티 에이전트 협업 시스템으로, 단순한 Writer-Editor 루프에서 시작하여 **완전한 범용 서적 제작 시스템**으로 발전한 프로젝트입니다.

### 진화 과정

```
단계 1: Writer-Editor 리뷰 루프
    ↓
단계 2: 6개 에이전트 멀티 에이전트 시스템
    ↓
단계 3: Python 튜토리얼 북 확장
    ↓
단계 4: 범용 서적 제작 시스템 (계획 중)
```

---

## 🎯 현재 구현 상태

### ✅ 완료된 기능

#### 1. 기본 Writer-Editor 시스템
- **Writer Agent**: 초안 작성 및 피드백 기반 수정
- **Editor Agent**: 구조화된 피드백 제공
- **Human-in-the-Loop**: 사용자 개입 지점을 통한 품질 관리
- **SQLite Checkpointing**: 세션 영속화 및 재개 기능

#### 2. 멀티 에이전트 시스템 (6개 에이전트)
- **Business Analyst**: 사용자 의도 분석 (JSON 출력)
- **Content Strategist**: 템플릿 기반 목차 작성
- **Outline Reviewer**: Self-Review 패턴으로 목차 검토
- **Web Search Agent**: DuckDuckGo/Tavily/Serper 검색
- **Writer**: 목차 + 리서치 기반 작성
- **Editor**: 편집 및 최종 검토

#### 3. Python 튜토리얼 북 확장 (8개 에이전트)
- **Code Example Agent**: Python 코드 예제 자동 생성
- **Exercise Generator**: 3가지 유형 연습문제 생성
  - Multiple Choice Questions (4개/챕터)
  - Fill-in-the-Blank Exercises (3개/챕터)
  - Coding Challenges (3개/챕터)
- **Python Code Validator**: AST 기반 구문 검증
- **Tutorial Export Manager**: 챕터 마크다운 내보내기

#### 4. 템플릿 시스템
- `BLOG_POST_TEMPLATE`: 블로그 포스트
- `TECHNICAL_ARTICLE_TEMPLATE`: 기술 문서
- `MARKETING_COPY_TEMPLATE`: 마케팅 카피
- `PYTHON_TUTORIAL_TEMPLATE`: Python 튜토리얼

#### 5. 웹 검색 통합
- DuckDuckGo (무료, 기본)
- Tavily (AI 최적화, 선택)
- Serper (Google 결과, 선택)

---

## 📁 프로젝트 구조

```
94_agent/
├── src/
│   ├── agents/                     # 8개 에이전트
│   │   ├── business_analyst.py
│   │   ├── content_strategist.py
│   │   ├── outline_reviewer.py
│   │   ├── web_search_agent.py
│   │   ├── writer.py
│   │   ├── editor.py
│   │   ├── code_example_agent.py   # 튜토리얼 전용
│   │   └── exercise_generator.py   # 튜토리얼 전용
│   ├── graph/
│   │   ├── state.py                # 상태 스키마 (TypedDict)
│   │   └── workflow.py             # LangGraph 워크플로우
│   ├── templates/
│   │   └── outline_templates.py    # 4개 템플릿
│   ├── tools/
│   │   └── search_tools.py         # 웹 검색 통합
│   ├── utils/
│   │   └── code_validator.py       # Python 코드 검증
│   ├── export/
│   │   └── export_manager.py       # 챕터 내보내기
│   ├── llm/
│   │   └── client.py               # LM Studio 클라이언트
│   ├── config/
│   │   └── settings.py             # Pydantic 설정
│   └── ui/
│       └── cli.py                  # Rich CLI
├── docs/
│   ├── tutorial-book-extension.md      # 튜토리얼 북 문서 (영문)
│   ├── tutorial-book-extension-ko.md   # 튜토리얼 북 문서 (한글)
│   ├── general-purpose-book-system.md  # 범용 시스템 계획
│   └── project-summary.md              # 이 문서
├── output/
│   └── tutorial/                   # 챕터 마크다운 파일
├── data/
│   └── checkpoints.sqlite          # 세션 상태 저장
├── main.py                         # 진입점
├── requirements.txt
└── .env                            # 환경 변수
```

---

## 🔧 핵심 기술 스택

| 기술 | 용도 | 버전 |
|------|------|------|
| **LangGraph** | 멀티 에이전트 워크플로우 오케스트레이션 | ≥0.2.31 |
| **LM Studio** | 로컬 LLM 실행 (Qwen 모델) | - |
| **Pydantic** | 타입 안전 설정 관리 | ≥2.0.0 |
| **Rich** | 아름다운 CLI 인터페이스 | ≥13.0.0 |
| **SQLite** | 세션 영속화 (LangGraph Checkpointer) | - |
| **DuckDuckGo Search** | 무료 웹 검색 | ≥5.0.0 |

---

## 📊 상태 관리 아키텍처

### WorkflowState 스키마

```python
class WorkflowState(TypedDict):
    # ===== 기본 필드 =====
    topic: str                                          # 주제
    current_draft: str                                  # 현재 초안
    current_feedback: str                               # 현재 피드백
    iterations: Annotated[List[ReviewIteration], add]   # 반복 이력
    iteration_count: int
    user_decision: str
    max_iterations: int
    conversation_history: Annotated[List[dict], add]

    # ===== 멀티 에이전트 필드 =====
    user_intent: Optional[UserIntentAnalysis]
    outlines: Annotated[List[ContentOutline], add]
    current_outline: Optional[ContentOutline]
    outline_version: int
    outline_reviews: Annotated[List[OutlineReview], add]
    outline_revision_count: int
    max_outline_revisions: int
    research_data: Annotated[List[SectionResearch], add]
    research_by_section: Dict[str, SectionResearch]
    current_stage: str

    # ===== 튜토리얼 북 필드 =====
    code_examples_by_section: Dict[str, List[str]]
    code_validation_results: Dict[str, tuple]
    chapter_exercises: Optional[ChapterExercises]
    chapter_number: Optional[int]
    chapter_metadata: Optional[Dict[str, Any]]
    export_path: Optional[str]
```

### Reducer 패턴

```python
# 리스트 누적 (add reducer)
iterations: Annotated[List[ReviewIteration], add]
conversation_history: Annotated[List[dict], add]
outlines: Annotated[List[ContentOutline], add]
research_data: Annotated[List[SectionResearch], add]
```

---

## 🔄 워크플로우

### 1. Simple Workflow (Writer-Editor Loop)

```
START → Writer → Editor → User Intervention → [조건 분기]
                                                    ↓
                                    [계속] ─────→ Writer (루프)
                                    [중단] ─────→ END
```

### 2. Multi-Agent Workflow

```
Business Analyst (의도 분석)
    ↓
Content Strategist (목차 작성)
    ↓
Outline Reviewer (목차 검토) → [수정 루프 최대 3회]
    ↓
User Intervention 1 (목차 승인)
    ↓
Web Search Agent (섹션별 리서치)
    ↓
Writer (목차+리서치 기반 작성)
    ↓
Editor (편집 및 피드백)
    ↓
User Intervention 2 (초안 검토) → [수정 루프 최대 10회]
    ↓
END
```

### 3. Tutorial Workflow (Python 튜토리얼 챕터)

```
Multi-Agent Workflow (위와 동일)
    ↓
Code Example Agent (코드 예제 생성)
    ↓
Python Code Validator (구문 검증)
    ↓
Exercise Generator (연습문제 생성)
    ↓
Tutorial Export Manager (마크다운 내보내기)
    ↓
END
```

---

## 🎓 핵심 학습 포인트

### 1. 에이전트 간 검토 루프 (Review Loop)

**구현**:
```python
workflow.add_conditional_edges(
    "user_intervention",
    should_continue,  # 라우팅 함수
    {"writer": "writer", "end": END}
)
```

**특징**:
- 조건부 엣지로 동적 워크플로우 제어
- 최대 반복 횟수 제한으로 무한 루프 방지
- 사용자 개입으로 품질 보장

### 2. 상태(State) 공유 방법

**TypedDict + Reducer**:
```python
class WorkflowState(TypedDict):
    iterations: Annotated[List[ReviewIteration], add]  # 자동 누적
```

**노드는 부분 상태만 반환**:
```python
def writer_node(state: WorkflowState) -> Dict[str, Any]:
    return {
        "current_draft": new_draft,
        "iteration_count": state["iteration_count"] + 1,
        "iterations": [new_iteration]  # add reducer가 자동 병합
    }
```

### 3. Human-in-the-Loop 패턴

**Interrupt 사용**:
```python
from langgraph.types import interrupt, Command

# 노드에서 실행 중단
user_input = interrupt("사용자에게 보여줄 메시지")

# 재개
app.stream(Command(resume=user_input), config)
```

**세션 관리**:
```python
config = {"configurable": {"thread_id": "unique-session-id"}}
checkpointer = SqliteSaver.from_conn_string("data/checkpoints.sqlite")
app = workflow.compile(checkpointer=checkpointer)
```

### 4. 템플릿 기반 프롬프팅

**구조화된 출력 보장**:
```python
PYTHON_TUTORIAL_TEMPLATE = {
    "sections": [
        {
            "section_id": "introduction",
            "requires_code": True,
            "num_code_examples": 2,
            "exercise_types": {
                "multiple_choice": 4,
                "fill_in_blank": 3,
                "coding_challenges": 3
            }
        }
    ]
}
```

### 5. Self-Review 패턴

**Outline Reviewer**:
```python
class OutlineReviewer:
    def review_outline(self, outline: dict) -> dict:
        # 에이전트 자체가 아웃라인 검토
        # 승인/수정 요청 결정
        # 구체적 피드백 제공
```

**장점**:
- 사람 개입 최소화
- 자동 품질 개선
- 최대 수정 횟수로 효율성 유지

---

## 📝 에이전트별 Temperature 설정

| 에이전트 | Temperature | 이유 |
|---------|-------------|------|
| Business Analyst | 0.2 | 분석적 정확성 |
| Content Strategist | 0.5 | 균형잡힌 창의성 |
| Outline Reviewer | 0.2 | 분석적 검토 |
| Writer | 0.8 | 창의적 작성 |
| Editor | 0.3 | 분석적 편집 |
| Code Example Agent | 0.2 | 코드 정확성 |
| Exercise Generator | 0.4 | 적절한 다양성 |

---

## 🚀 사용 예제

### 1. 단순 Writer-Editor 루프

```bash
python main.py --mode simple --topic "AI의 미래"
```

### 2. 멀티 에이전트 워크플로우

```bash
python main.py --mode multi_agent --topic "블록체인 기술 설명"
```

### 3. Python 튜토리얼 챕터 생성

```bash
python main.py --mode tutorial \
    --topic "Python 변수와 데이터 타입" \
    --chapter-number 1
```

---

## 📖 주요 문서

| 문서 | 설명 | 경로 |
|------|------|------|
| **Tutorial Book Extension (영문)** | Python 튜토리얼 북 확장 상세 가이드 | [docs/tutorial-book-extension.md](file:///Users/boon/Dropbox/02_works/94_agent/docs/tutorial-book-extension.md) |
| **Tutorial Book Extension (한글)** | 위 문서의 한글 번역 | [docs/tutorial-book-extension-ko.md](file:///Users/boon/Dropbox/02_works/94_agent/docs/tutorial-book-extension-ko.md) |
| **General-Purpose Book System** | 범용 서적 제작 시스템 계획 | [docs/general-purpose-book-system.md](file:///Users/boon/Dropbox/02_works/94_agent/docs/general-purpose-book-system.md) |
| **Project Summary** | 프로젝트 전체 요약 (이 문서) | [docs/project-summary.md](file:///Users/boon/Dropbox/02_works/94_agent/docs/project-summary.md) |

---

## 🔮 향후 계획: 범용 서적 제작 시스템

### 목표

Python 튜토리얼뿐 아니라 **모든 유형의 책**을 생성할 수 있는 시스템 구축:

1. **Python 튜토리얼** (✅ 이미 구현)
2. **구글의 역사** (서술형/내러티브)
3. **GPT 모형 이해 지침서** (기술 가이드)
4. **일반 논픽션**

### 신규 기능

| 기능 | 설명 | 상태 |
|------|------|------|
| 📚 **책 레벨 관리** | TOC, 챕터 의존성, 크로스 참조 | 🔜 계획됨 |
| 🧮 **수식 지원** | LaTeX 수식 생성 및 검증 | 🔜 계획됨 |
| 📊 **다이어그램** | Mermaid, PlantUML 다이어그램 | 🔜 계획됨 |
| ✓ **팩트 체크** | 역사/기술 내용 사실 확인 | 🔜 계획됨 |
| 📖 **참고문헌** | 자동 인용 및 참고문헌 생성 | 🔜 계획됨 |
| 📄 **PDF 내보내기** | Pandoc을 통한 PDF 변환 | 🔜 계획됨 |

### 6개 신규 에이전트

1. **BookCoordinatorAgent** - 책 전체 구조 계획 및 TOC 생성
2. **BibliographyAgent** - 인용 관리 및 참고문헌 컴파일
3. **FactCheckAgent** - 웹 검색 기반 사실 확인
4. **MathFormulaAgent** - LaTeX 수식 생성 및 검증
5. **DiagramAgent** - Mermaid/PlantUML 다이어그램 생성
6. **CrossReferenceAgent** - 챕터 간 참조 검증

### 신규 템플릿

- `HISTORICAL_BOOK_TEMPLATE`: 역사책 (팩트 체크, 타임라인)
- `TECHNICAL_GUIDE_TEMPLATE`: 기술 가이드 (수식, 다이어그램, 용어집)
- `GENERAL_NONFICTION_TEMPLATE`: 범용 논픽션

### 책 생성 워크플로우

```
BookCoordinator (책 구조 계획)
    ├─ TOC 생성 (15-20 챕터)
    ├─ 챕터 의존성 정의
    └─ 용어 사전 초기화
    ↓
User Intervention (책 계획 승인)
    ↓
For each chapter (의존성 순서대로):
    ├─ 챕터 워크플로우 실행
    ├─ 특수 콘텐츠 추가 (수식, 다이어그램)
    ├─ FactCheck (필요시)
    └─ Export Chapter
    ↓
CrossReferenceAgent (참조 검증)
    ↓
BibliographyAgent (참고문헌 컴파일)
    ↓
Assemble Book
    ├─ Title Page
    ├─ TOC
    ├─ All Chapters
    ├─ Glossary
    └─ Bibliography
    ↓
Export (Markdown + PDF)
```

### 사용 예제

```bash
# Python 튜토리얼 북
python main.py --mode book \
    --book-title "Python for Complete Beginners" \
    --book-type tutorial \
    --chapters 20 \
    --export-pdf

# 구글의 역사
python main.py --mode book \
    --book-title "구글의 역사" \
    --book-type history \
    --chapters 15 \
    --export-pdf

# GPT 가이드
python main.py --mode book \
    --book-title "GPT 모형을 이해하기 위한 지침서" \
    --book-type technical_guide \
    --chapters 12 \
    --export-pdf
```

---

## 🎯 구현 진행 상황

### 완료 ✅

- [x] Phase 1: 프로젝트 초기 설정
- [x] Phase 2: 상태 스키마 정의
- [x] Phase 3: 설정 관리
- [x] Phase 4: LLM 클라이언트
- [x] Phase 5: Writer 에이전트
- [x] Phase 6: Editor 에이전트
- [x] Phase 7: 워크플로우 그래프
- [x] Business Analyst
- [x] Content Strategist
- [x] Outline Reviewer
- [x] Web Search Agent
- [x] 템플릿 시스템
- [x] 웹 검색 통합
- [x] Code Example Agent
- [x] Exercise Generator
- [x] Python Code Validator
- [x] Tutorial Export Manager

### 계획 중 🔜

- [ ] Book System Phase 1: 상태 스키마 확장 (BookMetadata, ChapterDependency 등)
- [ ] Book System Phase 2: 신규 템플릿 (HISTORICAL_BOOK, TECHNICAL_GUIDE)
- [ ] Book System Phase 3: 6개 신규 에이전트
- [ ] Book System Phase 4: 책 워크플로우 (create_book_workflow)
- [ ] Book System Phase 5: Export 시스템 확장 (export_book, export_pdf)
- [ ] Book System Phase 6: CLI 업데이트 (--mode book)
- [ ] Book System Phase 7: 테스트 및 문서화

---

## 📊 프로젝트 통계

### 파일 수
- **Python 파일**: 25개
- **문서 파일**: 4개
- **설정 파일**: 2개

### 에이전트
- **구현 완료**: 8개
- **계획 중**: 6개
- **총**: 14개

### 템플릿
- **구현 완료**: 4개
- **계획 중**: 3개
- **총**: 7개

### 코드 라인 수 (추정)
- **src/**: ~3,000 줄
- **docs/**: ~2,500 줄
- **총**: ~5,500 줄

---

## 🔑 핵심 성공 요소

1. **TypedDict 기반 상태 관리** - 타입 안전성 및 명확한 계약
2. **Reducer 패턴** - 에이전트 간 정보 누적 및 공유
3. **Human-in-the-Loop** - 품질 보장 및 사용자 통제
4. **템플릿 기반 프롬프팅** - 일관성 및 구조화된 출력
5. **Self-Review 패턴** - 자동 품질 개선
6. **SQLite Checkpointing** - 세션 영속화 및 재개
7. **모듈화 설계** - 에이전트별 독립성 및 재사용성

---

## 📚 참고 자료

### LangGraph
- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [Human-in-the-Loop 가이드](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/wait-user-input/)
- [상태 관리 가이드](https://deepwiki.com/langchain-ai/langgraph-101/3.1-state-management)

### 기타
- [LM Studio 개발자 문서](https://lmstudio.ai/docs/developer)
- [Pydantic 문서](https://docs.pydantic.dev/)
- [Rich 문서](https://rich.readthedocs.io/)
- [Pandoc 사용자 가이드](https://pandoc.org/MANUAL.html)
- [Mermaid 문서](https://mermaid.js.org/)

---

## 🎓 학습 및 응용 가능성

### 학습 포인트
- 멀티 에이전트 시스템 설계
- LangGraph 워크플로우 오케스트레이션
- 상태 관리 패턴 (Reducer, TypedDict)
- Human-in-the-Loop 패턴
- 템플릿 기반 프롬프트 엔지니어링
- Self-Review 패턴

### 응용 가능 분야
- 교육 콘텐츠 생성
- 기술 문서 작성
- 마케팅 자료 제작
- 연구 보고서 작성
- 블로그 포스트 생성
- 서적 집필 지원

---

## 🚀 시작하기

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. LM Studio 설정

1. [LM Studio](https://lmstudio.ai/) 다운로드 및 설치
2. Qwen 모델 다운로드
3. 로컬 서버 시작 (포트 1234)

### 3. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일 편집
```

### 4. 실행

```bash
# 연결 테스트
python main.py --test-connection

# Writer-Editor 루프
python main.py --mode simple --topic "AI의 미래"

# 멀티 에이전트
python main.py --mode multi_agent --topic "블록체인 기술"

# 튜토리얼 챕터
python main.py --mode tutorial --topic "Python 변수" --chapter-number 1
```

---

## 📧 문의 및 기여

이 프로젝트에 대한 질문이나 제안이 있으시면 이슈를 등록해주세요.

---

**마지막 업데이트**: 2025-12-27
**버전**: 1.0 (Tutorial Book Extension 완료, General-Purpose Book System 계획)
