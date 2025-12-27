# API Reference

## 개요

이 문서는 Writer-Editor 멀티 에이전트 시스템의 주요 클래스, 함수, 타입에 대한 API 레퍼런스를 제공합니다.

---

## 목차

1. [State Schema](#state-schema)
2. [Agents](#agents)
3. [Workflow](#workflow)
4. [Templates](#templates)
5. [Tools](#tools)
6. [Configuration](#configuration)
7. [CLI](#cli)

---

## State Schema

### WorkflowState

**모듈**: `src.graph.state`

메인 워크플로우 상태 스키마.

```python
class WorkflowState(TypedDict):
    # 기본 필드
    topic: str
    current_draft: str
    current_feedback: str
    iterations: Annotated[List[ReviewIteration], add]
    iteration_count: int
    user_decision: str
    max_iterations: int
    conversation_history: Annotated[List[dict], add]

    # 멀티 에이전트 필드
    user_intent: Optional[UserIntentAnalysis]
    outlines: Annotated[List[ContentOutline], add]
    current_outline: Optional[ContentOutline]
    outline_version: int
    outline_reviews: Annotated[List[OutlineReview], add]
    current_outline_review: Optional[OutlineReview]
    outline_revision_count: int
    max_outline_revisions: int
    research_data: Annotated[List[SectionResearch], add]
    research_by_section: Dict[str, SectionResearch]
    current_stage: str
```

### UserIntentAnalysis

사용자 의도 분석 결과.

```python
class UserIntentAnalysis(TypedDict):
    document_type: str           # 문서 유형
    target_audience: str         # 대상 독자
    tone: str                    # 톤/스타일
    key_messages: List[str]      # 핵심 메시지
    constraints: List[str]       # 제약사항
    objectives: List[str]        # 목표
```

### ContentOutline

콘텐츠 목차.

```python
class ContentOutline(TypedDict):
    version: int                      # 버전 번호
    sections: List[OutlineSection]    # 섹션 목록
    overall_structure: str            # 전체 구조 설명
    estimated_total_length: str       # 예상 총 길이
    template_used: Optional[str]      # 사용된 템플릿
    timestamp: str                    # 생성 시간
```

### OutlineSection

목차의 단일 섹션.

```python
class OutlineSection(TypedDict):
    section_id: str              # 섹션 ID
    title: str                   # 제목
    purpose: str                 # 목적
    key_points: List[str]        # 핵심 포인트
    estimated_length: str        # 예상 길이
    research_needed: bool        # 리서치 필요 여부
    search_queries: List[str]    # 검색 쿼리
```

### OutlineReview

목차 검토 결과.

```python
class OutlineReview(TypedDict):
    version_reviewed: int                # 검토된 버전
    approved: bool                       # 승인 여부
    strengths: List[str]                 # 강점
    weaknesses: List[str]                # 약점
    specific_feedback: Dict[str, str]    # 섹션별 피드백
    recommendations: List[str]           # 권장사항
    overall_assessment: str              # 전체 평가
    timestamp: str                       # 검토 시간
```

### SearchResult

웹 검색 결과 항목.

```python
class SearchResult(TypedDict):
    title: str                        # 제목
    url: str                          # URL
    snippet: str                      # 요약
    relevance_score: Optional[float]  # 관련성 점수
    source: str                       # 검색 제공자
```

### SectionResearch

섹션별 리서치 데이터.

```python
class SectionResearch(TypedDict):
    section_id: str              # 섹션 ID
    search_queries: List[str]    # 사용된 쿼리
    results: List[SearchResult]  # 검색 결과
    summary: str                 # LLM 요약
    key_facts: List[str]         # 핵심 사실
    sources: List[str]           # 출처 URL
    timestamp: str               # 리서치 시간
```

---

## Agents

### BusinessAnalystAgent

**모듈**: `src.agents.business_analyst`

사용자 의도 분석 에이전트.

#### `__init__(llm_client: LMStudioClient)`

초기화.

**Parameters**:
- `llm_client`: LM Studio 클라이언트 인스턴스

#### `analyze_intent(topic: str) -> UserIntentAnalysis`

토픽에서 사용자 의도 분석.

**Parameters**:
- `topic`: 콘텐츠 토픽

**Returns**: `UserIntentAnalysis` - 분석 결과

#### Node Function: `business_analyst_node(state: WorkflowState) -> Dict[str, Any]`

LangGraph 노드 함수.

**Returns**: 부분 상태 업데이트
- `user_intent`
- `conversation_history`
- `current_stage`

---

### ContentStrategistAgent

**모듈**: `src.agents.content_strategist`

목차 작성 에이전트.

#### `__init__(llm_client: LMStudioClient)`

초기화.

#### `create_outline(topic: str, user_intent: UserIntentAnalysis, outline_version: int = 1, feedback: Optional[str] = None) -> ContentOutline`

콘텐츠 목차 생성.

**Parameters**:
- `topic`: 콘텐츠 토픽
- `user_intent`: 사용자 의도 분석
- `outline_version`: 목차 버전 번호
- `feedback`: 이전 검토 피드백 (수정 시)

**Returns**: `ContentOutline` - 생성된 목차

#### Node Function: `content_strategist_node(state: WorkflowState) -> Dict[str, Any]`

---

### OutlineReviewerAgent

**모듈**: `src.agents.outline_reviewer`

목차 검토 에이전트.

#### `__init__(llm_client: LMStudioClient)`

#### `review_outline(outline: ContentOutline, user_intent: UserIntentAnalysis, topic: str) -> OutlineReview`

목차 검토 및 피드백 제공.

**Parameters**:
- `outline`: 검토할 목차
- `user_intent`: 사용자 의도
- `topic`: 토픽

**Returns**: `OutlineReview` - 검토 결과

#### Node Function: `outline_reviewer_node(state: WorkflowState) -> Dict[str, Any]`

---

### WebSearchAgent

**모듈**: `src.agents.web_search_agent`

웹 검색 에이전트.

#### `__init__(llm_client: LMStudioClient, search_provider: SearchProvider)`

**Parameters**:
- `llm_client`: LLM 클라이언트
- `search_provider`: 검색 제공자 인스턴스

#### `research_sections(outline: ContentOutline, topic: str) -> Dict[str, SectionResearch]`

목차의 모든 섹션 리서치.

**Parameters**:
- `outline`: 콘텐츠 목차
- `topic`: 토픽

**Returns**: `Dict[section_id, SectionResearch]` - 섹션별 리서치 데이터

#### `research_section(section_id: str, section_title: str, search_queries: List[str], topic: str) -> SectionResearch`

단일 섹션 리서치.

#### Node Function: `web_search_node(state: WorkflowState) -> Dict[str, Any]`

---

### WriterAgent

**모듈**: `src.agents.writer`

초안 작성 에이전트.

#### `__init__(llm_client: LMStudioClient)`

#### `create_initial_draft(topic: str) -> str`

단순 초안 작성 (Simple 모드).

**Parameters**:
- `topic`: 토픽

**Returns**: 초안 텍스트

#### `revise_draft(current_draft: str, feedback: str) -> str`

피드백 기반 수정.

**Parameters**:
- `current_draft`: 현재 초안
- `feedback`: 편집자 피드백

**Returns**: 수정된 초안

#### `create_draft_from_outline(topic: str, outline: ContentOutline, user_intent: UserIntentAnalysis, research_by_section: Optional[Dict[str, SectionResearch]] = None) -> str`

목차 및 리서치 기반 초안 작성 (Multi-Agent 모드).

**Parameters**:
- `topic`: 토픽
- `outline`: 콘텐츠 목차
- `user_intent`: 사용자 의도
- `research_by_section`: 섹션별 리서치 데이터

**Returns**: 완전한 초안

#### Node Function: `writer_node(state: WorkflowState) -> Dict[str, Any]`

3가지 모드 자동 선택:
1. 목차 기반 작성 (첫 반복 + 목차 있음)
2. 단순 초안 (첫 반복 + 목차 없음)
3. 수정 (이후 반복)

---

### EditorAgent

**모듈**: `src.agents.editor`

편집 및 피드백 에이전트.

#### `__init__(llm_client: LMStudioClient)`

#### `review_draft(draft: str, outline: Optional[ContentOutline], user_intent: Optional[UserIntentAnalysis], topic: str, iteration: int) -> str`

초안 검토 및 피드백 생성.

**Parameters**:
- `draft`: 초안 텍스트
- `outline`: 목차 (있는 경우)
- `user_intent`: 사용자 의도 (있는 경우)
- `topic`: 토픽
- `iteration`: 현재 반복 횟수

**Returns**: 구조화된 피드백 텍스트

#### Node Function: `editor_node(state: WorkflowState) -> Dict[str, Any]`

---

## Workflow

### 워크플로우 생성

**모듈**: `src.graph.workflow`

#### `create_simple_workflow() -> StateGraph`

Simple 모드 워크플로우 생성 (Writer-Editor만).

**Returns**: `StateGraph` - 컴파일되지 않은 그래프

#### `create_multi_agent_workflow() -> StateGraph`

Multi-Agent 모드 워크플로우 생성 (6개 에이전트).

**Returns**: `StateGraph` - 컴파일되지 않은 그래프

#### `compile_workflow(mode: str = "multi-agent") -> CompiledGraph`

워크플로우 컴파일 (체크포인터 포함).

**Parameters**:
- `mode`: `"simple"` 또는 `"multi-agent"`

**Returns**: 컴파일된 실행 가능 그래프

**Example**:
```python
from src.graph import compile_workflow

app = compile_workflow("multi-agent")
```

#### `create_initial_state(topic: str, mode: str = "multi-agent", max_iterations: int = None, max_outline_revisions: int = None) -> WorkflowState`

초기 상태 생성.

**Parameters**:
- `topic`: 콘텐츠 토픽
- `mode`: 워크플로우 모드
- `max_iterations`: 최대 초안 반복 (기본값: settings)
- `max_outline_revisions`: 최대 목차 반복 (기본값: settings)

**Returns**: `WorkflowState` - 초기 상태 딕셔너리

**Example**:
```python
from src.graph import compile_workflow, create_initial_state

app = compile_workflow("multi-agent")
initial_state = create_initial_state("AI in healthcare")
config = {"configurable": {"thread_id": "session-123"}}

for event in app.stream(initial_state, config):
    print(event)
```

### 라우팅 함수

#### `should_approve_outline(state: WorkflowState) -> Literal["approved", "revise", "max_revisions"]`

목차 승인 여부 결정.

#### `route_outline_decision(state: WorkflowState) -> Literal["proceed", "revise"]`

사용자 목차 결정 라우팅.

#### `should_continue_draft(state: WorkflowState) -> Literal["writer", "end"]`

초안 계속/종료 결정.

---

## Templates

**모듈**: `src.templates.outline_templates`

### `get_outline_template(document_type: str) -> Optional[Dict[str, Any]]`

문서 유형별 템플릿 가져오기.

**Parameters**:
- `document_type`: `"blog_post"`, `"technical_article"`, `"marketing_copy"` 등

**Returns**: 템플릿 딕셔너리 또는 `None`

**Example**:
```python
from src.templates import get_outline_template

template = get_outline_template("blog_post")
print(template["description"])
# "Standard blog post structure with engaging hook and practical content"
```

### `list_available_templates() -> List[str]`

사용 가능한 템플릿 목록.

**Returns**: 템플릿 이름 리스트

### `customize_template(template: Dict[str, Any], topic: str, customizations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

템플릿 커스터마이징.

**Parameters**:
- `template`: 기본 템플릿
- `topic`: 토픽 (플레이스홀더 치환용)
- `customizations`: 추가 커스터마이징

**Returns**: 커스터마이즈된 템플릿

**Example**:
```python
from src.templates import get_outline_template, customize_template

template = get_outline_template("blog_post")
custom = customize_template(template, "AI in healthcare")
# search_queries의 {topic}이 "AI in healthcare"로 치환됨
```

### 템플릿 상수

- `BLOG_POST_TEMPLATE`
- `TECHNICAL_ARTICLE_TEMPLATE`
- `MARKETING_COPY_TEMPLATE`

---

## Tools

### SearchProvider

**모듈**: `src.tools.search_tools`

통합 웹 검색 인터페이스.

#### `__init__(provider_type: Optional[str] = None, api_key: Optional[str] = None, max_results: int = 5)`

**Parameters**:
- `provider_type`: `"duckduckgo"`, `"tavily"`, `"serper"` (기본값: settings)
- `api_key`: API 키 (tavily, serper용)
- `max_results`: 최대 결과 수

**Raises**:
- `ValueError`: tavily/serper에 API 키 없을 때

#### `search(query: str, max_results: Optional[int] = None) -> List[SearchResult]`

검색 실행.

**Parameters**:
- `query`: 검색 쿼리
- `max_results`: 이번 검색의 최대 결과 (오버라이드)

**Returns**: `List[SearchResult]` - 검색 결과 리스트

**Example**:
```python
from src.tools import SearchProvider

provider = SearchProvider("duckduckgo")
results = provider.search("AI healthcare trends", max_results=5)

for result in results:
    print(f"{result['title']}: {result['url']}")
```

#### `test_connection() -> bool`

검색 제공자 연결 테스트.

**Returns**: 연결 성공 여부

### Helper Functions

#### `search_multiple_queries(queries: List[str], provider: Optional[SearchProvider] = None, max_results_per_query: int = 5) -> Dict[str, List[SearchResult]]`

여러 쿼리 동시 검색.

**Parameters**:
- `queries`: 쿼리 리스트
- `provider`: SearchProvider 인스턴스 (기본값: 새로 생성)
- `max_results_per_query`: 쿼리당 최대 결과

**Returns**: `{query: [results]}` 딕셔너리

#### `deduplicate_results(results: List[SearchResult], by: str = "url") -> List[SearchResult]`

중복 제거.

**Parameters**:
- `results`: 결과 리스트
- `by`: 중복 기준 필드 (`"url"` 또는 `"title"`)

**Returns**: 중복 제거된 결과

---

## Configuration

### Settings

**모듈**: `src.config.settings`

Pydantic 기반 설정 클래스.

```python
class Settings(BaseSettings):
    # LM Studio
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_model: str = "qwen"

    # 에이전트 Temperature
    business_analyst_temperature: float = 0.2
    content_strategist_temperature: float = 0.5
    outline_reviewer_temperature: float = 0.2
    writer_temperature: float = 0.8
    editor_temperature: float = 0.3
    max_tokens: int = 2000

    # 워크플로우
    max_iterations: int = 10
    max_outline_revisions: int = 3

    # 웹 검색
    search_provider: str = "duckduckgo"
    search_api_key: Optional[str] = None
    max_search_results_per_query: int = 5
    enable_web_search: bool = True

    # 데이터베이스
    checkpoint_db_path: str = "data/checkpoints.sqlite"
```

#### 싱글톤 인스턴스

```python
from src.config import settings

print(settings.lm_studio_base_url)
# "http://localhost:1234/v1"
```

#### 환경 변수

`.env` 파일이나 환경 변수로 설정 오버라이드:

```bash
LM_STUDIO_BASE_URL=http://localhost:1234/v1
WRITER_TEMPERATURE=0.8
SEARCH_PROVIDER=duckduckgo
```

---

## CLI

### CLI Class

**모듈**: `src.ui.cli`

Rich 기반 CLI 인터페이스.

#### `__init__(mode: str = "multi-agent")`

**Parameters**:
- `mode`: `"simple"` 또는 `"multi-agent"`

#### `start_session(topic: Optional[str] = None, thread_id: Optional[str] = None, max_iterations: Optional[int] = None, max_outline_revisions: Optional[int] = None)`

세션 시작 또는 재개.

**Parameters**:
- `topic`: 토픽 (None이면 프롬프트)
- `thread_id`: 세션 ID (None이면 새로 생성)
- `max_iterations`: 최대 초안 반복
- `max_outline_revisions`: 최대 목차 반복

**Example**:
```python
from src.ui import CLI

cli = CLI(mode="multi-agent")
cli.start_session(
    topic="AI in healthcare",
    max_iterations=5
)
```

#### `print_banner()`

환영 배너 출력.

#### `display_session_history(thread_id: str)`

세션 이력 표시 (미구현).

#### `list_sessions()`

모든 세션 목록 (미구현).

---

## LLM Client

### LMStudioClient

**모듈**: `src.llm.client`

LM Studio OpenAI 호환 API 래퍼.

#### `__init__(base_url: str = "http://localhost:1234/v1", model_name: str = "qwen", temperature: float = 0.7, max_tokens: int = 2000)`

**Parameters**:
- `base_url`: LM Studio 서버 URL
- `model_name`: 모델 이름
- `temperature`: 기본 temperature
- `max_tokens`: 최대 토큰 수

#### `generate(messages: List[dict], temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str`

텍스트 생성.

**Parameters**:
- `messages`: OpenAI 형식 메시지 리스트
- `temperature`: 이번 생성의 temperature (오버라이드)
- `max_tokens`: 이번 생성의 최대 토큰 (오버라이드)

**Returns**: 생성된 텍스트

**Example**:
```python
from src.llm import LMStudioClient

client = LMStudioClient(temperature=0.7)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Write a haiku about AI."}
]
response = client.generate(messages)
print(response)
```

#### `test_connection() -> bool`

LM Studio 연결 테스트.

**Returns**: 연결 성공 여부

---

## 사용 예제

### 프로그래매틱 사용

```python
from src.graph import compile_workflow, create_initial_state

# 워크플로우 컴파일
app = compile_workflow("multi-agent")

# 초기 상태 생성
initial_state = create_initial_state(
    topic="AI in healthcare",
    max_iterations=5,
    max_outline_revisions=2
)

# 설정 (세션 ID 포함)
config = {"configurable": {"thread_id": "my-session"}}

# 스트리밍 실행
for event in app.stream(initial_state, config, stream_mode="values"):
    stage = event.get("current_stage")
    print(f"Stage: {stage}")

    if stage == "draft_created":
        print(f"Draft: {event['current_draft'][:200]}...")
```

### CLI 사용

```python
from src.ui import CLI

# CLI 생성
cli = CLI(mode="multi-agent")

# 세션 시작
cli.start_session(
    topic="Python async programming",
    max_iterations=3
)
```

### 커스텀 에이전트 사용

```python
from src.agents import WriterAgent
from src.llm import LMStudioClient

# LLM 클라이언트 생성
client = LMStudioClient(temperature=0.8)

# 에이전트 생성
writer = WriterAgent(client)

# 초안 작성
draft = writer.create_initial_draft("Machine learning basics")
print(draft)
```

---

## 타입 힌트

모든 공개 API는 완전한 타입 힌트를 제공합니다:

```python
from typing import Optional, List, Dict, Any
from src.graph.state import WorkflowState, UserIntentAnalysis

def my_function(
    state: WorkflowState,
    topic: str,
    iterations: Optional[int] = None
) -> Dict[str, Any]:
    ...
```

타입 체커 (mypy, pyright) 사용 권장.

---

## 에러 및 예외

### 일반 예외

- `ValueError`: 잘못된 파라미터 (예: 알 수 없는 워크플로우 모드)
- `json.JSONDecodeError`: LLM 출력 파싱 실패 (에이전트 내부에서 처리)
- `GraphInterrupt`: Human-in-the-Loop 개입 (예상된 동작)

### 연결 예외

- `ConnectionError`: LM Studio 연결 실패
- `requests.exceptions.*`: 웹 검색 API 오류

### 권장 에러 처리

```python
try:
    for event in app.stream(initial_state, config):
        handle_event(event)
except GraphInterrupt as gi:
    # 사용자 개입 처리
    handle_interrupt(gi)
except Exception as e:
    # 일반 에러
    logger.error(f"Workflow error: {e}")
    raise
```

---

## 버전 정보

현재 버전: **1.0.0**

```python
import src
print(src.__version__)
# "1.0.0"
```

---

이 API 레퍼런스는 시스템의 모든 공개 인터페이스를 다룹니다. 내부 구현 세부사항은 소스 코드의 docstring을 참조하세요.
