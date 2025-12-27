# 멀티 에이전트 아키텍처 가이드

## 개요

Writer-Editor 시스템의 멀티 에이전트 확장은 6개의 전문화된 에이전트가 협업하여 고품질 콘텐츠를 생성하는 시스템입니다.

## 시스템 아키텍처

### 전체 워크플로우

```
사용자 입력 (토픽)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: 의도 분석                                           │
│ Business Analyst → 사용자 의도 파악 (문서 유형, 대상, 톤)      │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: 목차 작성 및 검토                                    │
│ Content Strategist → 템플릿 기반 목차 생성                    │
│         ↓                                                    │
│ Outline Reviewer → 목차 품질 검토                            │
│         ↓                                                    │
│    [검토 루프: 최대 3회 반복]                                 │
│         ↓                                                    │
│ 👤 User Intervention → 목차 승인/수정 요청                   │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: 웹 리서치                                           │
│ Web Search Agent → 섹션별 정보 수집 및 요약                  │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: 초안 작성 및 편집                                    │
│ Writer → 목차 + 리서치 기반 초안 작성                         │
│         ↓                                                    │
│ Editor → 피드백 제공                                          │
│         ↓                                                    │
│ 👤 User Intervention → 계속/중단 결정                        │
│         ↓                                                    │
│    [검토 루프: 최대 10회 반복]                                │
└─────────────────────────────────────────────────────────────┘
    ↓
최종 문서 완성
```

## 에이전트 상세 설명

### 1. Business Analyst Agent

**파일**: `src/agents/business_analyst.py`

**역할**: 사용자 요청 분석 및 의도 파악

**Temperature**: 0.2 (분석적)

**입력**:
- 사용자가 제공한 토픽

**출력** (JSON 형식):
```python
UserIntentAnalysis = {
    "document_type": str,        # blog_post, technical_article, marketing_copy
    "target_audience": str,      # 대상 독자
    "tone": str,                 # professional, casual, technical, friendly
    "key_messages": List[str],   # 전달할 핵심 메시지
    "constraints": List[str],    # 제약사항 (길이, 형식 등)
    "objectives": List[str]      # 콘텐츠 목표
}
```

**예시**:
```json
{
  "document_type": "blog_post",
  "target_audience": "일반 독자 및 AI 초보자",
  "tone": "professional",
  "key_messages": [
    "AI가 헬스케어를 혁신하고 있음",
    "진단 정확도 향상",
    "개인화된 치료 가능"
  ],
  "constraints": ["1500-2500단어", "비전문가도 이해 가능"],
  "objectives": ["AI 헬스케어 활용 사례 소개", "독자 관심 유도"]
}
```

**구현 포인트**:
- JSON 파싱 실패 시 폴백 메커니즘
- 구조화된 출력으로 후속 에이전트 가이드

---

### 2. Content Strategist Agent

**파일**: `src/agents/content_strategist.py`

**역할**: 구조화된 목차 작성

**Temperature**: 0.5 (균형잡힌 창의성)

**입력**:
- 토픽
- UserIntentAnalysis
- 이전 목차 (수정 시)
- 피드백 (수정 시)

**출력**:
```python
ContentOutline = {
    "version": int,
    "sections": List[OutlineSection],
    "overall_structure": str,
    "estimated_total_length": str,
    "template_used": str,
    "timestamp": str
}

OutlineSection = {
    "section_id": str,
    "title": str,
    "purpose": str,
    "key_points": List[str],
    "estimated_length": str,
    "research_needed": bool,
    "search_queries": List[str]
}
```

**템플릿 사용**:
- Blog Post Template: hook, context, main_content, practical, conclusion
- Technical Article: abstract, introduction, technical_details, results, conclusion
- Marketing Copy: headline, problem, solution, benefits, social_proof, cta

**예시**:
```python
{
  "version": 1,
  "sections": [
    {
      "section_id": "hook",
      "title": "AI가 바꾸는 의료의 미래",
      "purpose": "독자의 관심을 끌고 주제 소개",
      "key_points": [
        "AI 헬스케어 시장 급성장",
        "왜 지금 중요한가",
        "이 글에서 다룰 내용"
      ],
      "estimated_length": "200-250 words",
      "research_needed": True,
      "search_queries": [
        "AI healthcare market size 2024",
        "AI healthcare trends"
      ]
    },
    // ... 추가 섹션
  ],
  "overall_structure": "5-section structure: Introduction → Background → Main Content → Examples → Conclusion",
  "estimated_total_length": "1500-2500 words"
}
```

---

### 3. Outline Reviewer Agent

**파일**: `src/agents/outline_reviewer.py`

**역할**: 목차 품질 검토 (Self-Review 패턴)

**Temperature**: 0.2 (분석적)

**입력**:
- ContentOutline
- UserIntentAnalysis
- 토픽

**출력**:
```python
OutlineReview = {
    "version_reviewed": int,
    "approved": bool,
    "strengths": List[str],
    "weaknesses": List[str],
    "specific_feedback": Dict[str, str],  # section_id -> 피드백
    "recommendations": List[str],
    "overall_assessment": str,
    "timestamp": str
}
```

**검토 기준**:
1. 논리적 흐름
2. 완전성
3. 대상 독자 적합성
4. 명확성
5. 일관성
6. 실행 가능성

**예시**:
```python
{
  "version_reviewed": 1,
  "approved": True,
  "strengths": [
    "명확한 5단계 구조",
    "각 섹션의 목적이 분명함",
    "리서치 쿼리가 구체적"
  ],
  "weaknesses": [
    "실용적 예시 섹션의 key_points가 다소 추상적"
  ],
  "specific_feedback": {
    "practical": "사례 연구나 구체적 수치 추가 권장"
  },
  "recommendations": [
    "practical 섹션에 실제 병원/기업 사례 추가"
  ],
  "overall_assessment": "전반적으로 우수한 구조. 작은 개선사항만 있으면 진행 가능."
}
```

**Self-Review 루프**:
- 승인되지 않으면 자동으로 Content Strategist에게 피드백 전달
- 최대 3회 반복
- 3회 도달 시 사용자에게 강제 개입

---

### 4. Web Search Agent

**파일**: `src/agents/web_search_agent.py`

**역할**: 웹 검색 및 정보 수집

**Temperature**: 0.3 (사실 정확성)

**입력**:
- ContentOutline (research_needed=True인 섹션들)
- 토픽

**출력**:
```python
SectionResearch = {
    "section_id": str,
    "search_queries": List[str],
    "results": List[SearchResult],
    "summary": str,           # LLM이 생성한 요약
    "key_facts": List[str],   # 추출된 핵심 사실
    "sources": List[str],     # URL 목록
    "timestamp": str
}
```

**검색 제공자**:
1. **DuckDuckGo** (기본, 무료)
   - API 키 불필요
   - `duckduckgo-search` 라이브러리 사용

2. **Tavily** (선택, AI 최적화)
   - API 키 필요
   - LLM 애플리케이션에 최적화된 결과

3. **Serper** (선택, Google 결과)
   - API 키 필요
   - Google 검색 결과 제공

**프로세스**:
1. 각 섹션의 search_queries 실행
2. 결과 수집 및 중복 제거
3. LLM으로 요약 생성
4. 핵심 사실 추출
5. 출처 URL 저장

**예시**:
```python
{
  "section_id": "context",
  "search_queries": [
    "AI healthcare market size 2024",
    "AI healthcare statistics"
  ],
  "results": [
    {
      "title": "Global AI in Healthcare Market Size Report 2024",
      "url": "https://example.com/report",
      "snippet": "Market expected to reach $188B by 2030...",
      "relevance_score": 0.95,
      "source": "duckduckgo"
    },
    // ... 더 많은 결과
  ],
  "summary": "AI 헬스케어 시장은 2024년 약 200억 달러에서 2030년 1,880억 달러로 급성장할 전망입니다. 주요 동인은 진단 정확도 향상(92%+), 비용 절감(30-40%), 개인화된 치료입니다.",
  "key_facts": [
    "AI 진단 정확도 92% 이상",
    "2030년까지 연평균 37.5% 성장 예상",
    "방사선 영상 분석에서 가장 큰 활용"
  ],
  "sources": [
    "https://example.com/report",
    "https://medical-ai.org/stats"
  ]
}
```

---

### 5. Writer Agent (Enhanced)

**파일**: `src/agents/writer.py`

**역할**: 초안 작성

**Temperature**: 0.8 (창의적)

**3가지 작성 모드**:

#### Mode 1: 목차 기반 작성 (Multi-Agent)
```python
create_draft_from_outline(
    topic: str,
    outline: ContentOutline,
    user_intent: UserIntentAnalysis,
    research_by_section: Dict[str, SectionResearch]
)
```

**프로세스**:
1. 목차의 각 섹션 구조 파악
2. 해당 섹션의 리서치 데이터 활용
3. UserIntentAnalysis의 톤/대상에 맞춰 작성
4. 자연스러운 흐름으로 연결

#### Mode 2: 단순 초안 (Simple)
```python
create_initial_draft(topic: str)
```

#### Mode 3: 수정 (Both)
```python
revise_draft(current_draft: str, feedback: str)
```

**입력 구조 (Mode 1)**:
```
Write a complete draft about: [토픽]

USER INTENT:
Target Audience: [대상]
Tone: [톤]
Key Messages: [메시지1, 메시지2, ...]
Objectives: [목표1, 목표2, ...]

OUTLINE TO FOLLOW:
1. [섹션1 제목]
   Purpose: [목적]
   Key points: [포인트들]

2. [섹션2 제목]
   ...

RESEARCH FINDINGS:
For section "[섹션1 제목]":
Summary: [요약]
Key Facts:
  - [사실1]
  - [사실2]
Sources: [개수] sources available
```

---

### 6. Editor Agent

**파일**: `src/agents/editor.py`

**역할**: 편집 및 피드백

**Temperature**: 0.3 (분석적)

**입력**:
- 초안
- ContentOutline (있는 경우)
- UserIntentAnalysis (있는 경우)
- 토픽
- 반복 횟수

**출력** (구조화된 피드백):
```
**강점:**
- [잘된 부분들]

**개선 영역:**
- [구체적 제안들]

**목차 준수:**
- [목차 대비 평가]

**권장사항:**
- [우선순위별 제안]

**전체 평가:**
[1-2문장 요약]
```

**검토 항목**:
1. 구조 및 조직
2. 명확성
3. 완전성
4. 품질
5. 대상 독자 적합성
6. 의도 부합성

---

## 상태 관리

### WorkflowState 확장

```python
class WorkflowState(TypedDict):
    # 기존 Writer-Editor 필드
    topic: str
    current_draft: str
    current_feedback: str
    iterations: Annotated[List[ReviewIteration], add]
    iteration_count: int
    user_decision: str
    max_iterations: int
    conversation_history: Annotated[List[dict], add]

    # 멀티 에이전트 확장 필드
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

### Reducer 패턴

`Annotated[List[T], add]` 사용:
```python
from operator import add
from typing import Annotated

iterations: Annotated[List[ReviewIteration], add]
```

- 각 노드가 리스트에 항목 추가 시 자동 병합
- 전체 이력 누적
- 상태 일관성 보장

---

## 워크플로우 라우팅

### 1. 목차 검토 라우팅

```python
def should_approve_outline(state: WorkflowState) -> Literal["approved", "revise", "max_revisions"]:
    review = state["current_outline_review"]

    # 최대 반복 도달
    if state["outline_revision_count"] >= state["max_outline_revisions"]:
        return "max_revisions"

    # 승인됨
    if review["approved"]:
        return "approved"

    # 수정 필요
    return "revise"
```

### 2. 사용자 목차 결정

```python
def route_outline_decision(state: WorkflowState) -> Literal["proceed", "revise"]:
    decision = state.get("user_decision", "proceed")

    if decision == "revise":
        return "revise"  # Content Strategist로 돌아감
    else:
        return "proceed"  # Web Search로 진행
```

### 3. 초안 검토 라우팅

```python
def should_continue_draft(state: WorkflowState) -> Literal["writer", "end"]:
    # 최대 반복 도달
    if state["iteration_count"] >= state["max_iterations"]:
        return "end"

    # 사용자 결정
    decision = state.get("user_decision", "stop")
    if decision == "continue":
        return "writer"  # 수정 루프
    else:
        return "end"  # 종료
```

---

## Human-in-the-Loop 구현

### Interrupt 메커니즘

```python
from langgraph.types import interrupt, Command

# 노드에서 실행 중단
def outline_intervention_node(state: WorkflowState) -> Dict[str, Any]:
    # 사용자에게 정보 표시
    prompt = "목차를 승인하시겠습니까? (proceed/revise)"

    # 중단 및 대기
    user_decision = interrupt(prompt)

    return {"user_decision": user_decision}

# 재개
app.stream(Command(resume=user_input), config)
```

### 2개 개입 포인트

1. **Outline Intervention**
   - 목차 승인/수정 결정
   - 자동 검토 후 사용자 확인

2. **Draft Intervention**
   - 초안 계속/중단 결정
   - 매 반복마다 사용자 확인

---

## 템플릿 시스템

### 템플릿 구조

**파일**: `src/templates/outline_templates.py`

```python
TEMPLATE = {
    "name": str,
    "description": str,
    "sections": List[{
        "section_id": str,
        "title": str,
        "purpose": str,
        "key_points": List[str],
        "estimated_length": str,
        "research_needed": bool,
        "search_queries": List[str]  # {topic} 플레이스홀더 사용
    }]
}
```

### 3가지 템플릿

1. **Blog Post**: 5 섹션
   - hook, context, main_content, practical, conclusion

2. **Technical Article**: 5 섹션
   - abstract, introduction, technical_details, results, conclusion

3. **Marketing Copy**: 6 섹션
   - headline, problem, solution, benefits, social_proof, cta

### 커스터마이징

```python
from src.templates import get_outline_template, customize_template

template = get_outline_template("blog_post")
customized = customize_template(template, topic="AI in healthcare")

# {topic} 플레이스홀더가 실제 토픽으로 치환됨
# "AI in healthcare current trends"
```

---

## 설정 관리

### Agent-Specific Temperatures

```python
# src/config/settings.py
business_analyst_temperature: float = 0.2    # 분석적
content_strategist_temperature: float = 0.5  # 균형
outline_reviewer_temperature: float = 0.2    # 분석적
writer_temperature: float = 0.8              # 창의적
editor_temperature: float = 0.3              # 분석적
```

### 워크플로우 설정

```python
max_iterations: int = 10              # 초안 최대 반복
max_outline_revisions: int = 3        # 목차 최대 반복
```

### 웹 검색 설정

```python
search_provider: str = "duckduckgo"   # duckduckgo, tavily, serper
search_api_key: Optional[str] = None  # tavily, serper용
max_search_results_per_query: int = 5
enable_web_search: bool = True
```

---

## 세션 영속화

### SQLite Checkpointer

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("data/checkpoints.sqlite")
app = workflow.compile(checkpointer=checkpointer)
```

### Thread ID로 세션 관리

```python
config = {"configurable": {"thread_id": "unique-session-id"}}

# 새 세션
app.stream(initial_state, config)

# 세션 재개
app.stream(None, config)  # 저장된 상태에서 재개
```

---

## 성능 최적화 고려사항

### 1. 토큰 사용

- Business Analyst: JSON 출력으로 최소화
- Content Strategist: 템플릿 사용으로 구조화
- Web Search: LLM 요약으로 압축
- Writer: 가장 많은 토큰 사용 (창의적 작성)

### 2. 병렬 처리 가능성

현재는 순차 실행이지만, 향후 개선 가능:
- 여러 섹션 동시 리서치
- 여러 리뷰어의 병렬 검토

### 3. 캐싱

- 웹 검색 결과 캐싱
- 템플릿 캐싱
- LLM 응답 캐싱 (동일 프롬프트)

---

## 에러 처리

### 1. LLM 출력 파싱 실패

모든 에이전트에 폴백 메커니즘:
```python
try:
    result = json.loads(llm_response)
except json.JSONDecodeError:
    # 기본값 또는 휴리스틱 사용
    result = create_fallback_result()
```

### 2. 웹 검색 실패

```python
try:
    results = search_provider.search(query)
except Exception as e:
    print(f"Search failed: {e}")
    results = []  # 빈 결과로 계속
```

### 3. 무한 루프 방지

- `max_outline_revisions`: 3회
- `max_iterations`: 10회
- 강제 종료 후 사용자 개입

---

## 확장 가능성

### 새 에이전트 추가

1. 에이전트 클래스 생성
2. 노드 함수 작성
3. WorkflowState에 필드 추가 (필요시)
4. 워크플로우 그래프에 노드 추가
5. 라우팅 함수 업데이트

### 새 템플릿 추가

```python
# src/templates/outline_templates.py
NEW_TEMPLATE = {
    "name": "new_template",
    "description": "설명",
    "sections": [...]
}

TEMPLATE_REGISTRY["new_template"] = NEW_TEMPLATE
```

### 새 검색 제공자 추가

```python
# src/tools/search_tools.py
def _search_new_provider(self, query: str, max_results: int):
    # 구현
    pass
```

---

## 모범 사례

### 1. 에이전트 설계
- 단일 책임 원칙
- 명확한 입출력 계약
- 구조화된 출력 (JSON, TypedDict)

### 2. 프롬프트 엔지니어링
- 역할 명확히 정의
- 출력 형식 명시
- 예시 제공 (Few-shot)

### 3. 상태 관리
- Reducer 패턴 활용
- 부분 업데이트만 반환
- 불변성 유지

### 4. 에러 처리
- 모든 외부 호출에 try-except
- 의미있는 에러 메시지
- 폴백 메커니즘

---

## 디버깅 팁

### 1. 대화 이력 확인

```python
for msg in state["conversation_history"]:
    print(f"[{msg['role']}]: {msg['content'][:100]}...")
```

### 2. 상태 스냅샷

```python
import json
print(json.dumps(state, indent=2, default=str))
```

### 3. 체크포인트 조회

```python
# SQLite 데이터베이스 직접 조회
import sqlite3
conn = sqlite3.connect("data/checkpoints.sqlite")
cursor = conn.cursor()
cursor.execute("SELECT * FROM checkpoints")
```

---

## 결론

멀티 에이전트 시스템은:
- ✅ 6개 전문 에이전트로 역할 분담
- ✅ 2개 Human-in-the-Loop 개입 포인트
- ✅ 템플릿 기반 구조화된 출력
- ✅ 웹 검색 통합으로 사실 기반 작성
- ✅ Self-Review 패턴으로 품질 보장
- ✅ 완전한 세션 영속화

이 아키텍처는 확장 가능하며, 새로운 에이전트와 기능을 쉽게 추가할 수 있습니다.
