# Writer-Editor 리뷰 루프 에이전트 시스템 - 구현 가이드

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [프로젝트 구조](#프로젝트-구조)
4. [구현된 컴포넌트](#구현된-컴포넌트)
5. [남은 구현 작업](#남은-구현-작업)
6. [사용 방법](#사용-방법)
7. [핵심 학습 포인트](#핵심-학습-포인트)

---

## 프로젝트 개요

### 🎯 목표
Writer 에이전트가 초안을 작성하면 Editor 에이전트가 피드백을 제공하고, Writer가 수정하는 **리뷰 루프 시스템** 구축

### 🔑 핵심 학습 포인트
- ✅ **에이전트 간 검토 루프(Review Loop)** 패턴
- ✅ **상태(State) 공유** 및 관리 방법
- ✅ **Human-in-the-Loop** 패턴 구현

### 🛠 기술 스택
- **언어**: Python 3.10+
- **프레임워크**: LangGraph
- **LLM**: 로컬 LM Studio (Qwen 모델)
- **상태 저장**: SQLite Checkpointer
- **UI**: Rich 기반 CLI

---

## 시스템 아키텍처

### 워크플로우 흐름

```
START → Writer → Editor → User Intervention → [조건 분기]
                                                    ↓
                                    [계속] ─────→ Writer (루프)
                                    [중단] ─────→ END
```

### 상태 관리 전략

- **TypedDict** 기반 상태 스키마
- **Reducer** 패턴으로 반복 이력 및 대화 누적
- **SQLite Checkpointer**로 세션 영속화
- **Thread ID**로 세션 격리 및 재개 지원

---

## 프로젝트 구조

```
writer-editor-agent/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py           ✅ 완료
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── writer.py              ✅ 완료
│   │   └── editor.py              ⏳ 작업 중
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py               ✅ 완료
│   │   └── workflow.py            ❌ 미완료
│   ├── llm/
│   │   ├── __init__.py
│   │   └── client.py              ✅ 완료
│   └── ui/
│       ├── __init__.py
│       └── cli.py                 ❌ 미완료
├── tests/                         ❌ 미완료
├── examples/                      ❌ 미완료
├── data/
├── docs/                          ✅ 작성 중
├── requirements.txt               ✅ 완료
├── pyproject.toml                 ✅ 완료
├── .env                           ✅ 완료
├── README.md                      ❌ 미완료
└── main.py                        ❌ 미완료
```

---

## 구현된 컴포넌트

### 1. 프로젝트 설정 파일

#### `requirements.txt`
```txt
langgraph>=0.2.31
langgraph-checkpoint-sqlite>=1.0.0
openai>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
rich>=13.0.0
python-dotenv>=1.0.0
```

#### `pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "writer-editor-agent"
version = "0.1.0"
description = "Writer-Editor Review Loop Agent System with LangGraph"
requires-python = ">=3.10"
dependencies = [
    "langgraph>=0.2.31",
    "langgraph-checkpoint-sqlite>=1.0.0",
    "openai>=1.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "rich>=13.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

#### `.env`
```env
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=qwen
WRITER_TEMPERATURE=0.8
EDITOR_TEMPERATURE=0.3
MAX_TOKENS=2000
MAX_ITERATIONS=10
CHECKPOINT_DB_PATH=data/checkpoints.sqlite
```

---

### 2. 상태 스키마 (`src/graph/state.py`)

```python
from typing import TypedDict, List, Optional, Annotated
from operator import add

class ReviewIteration(TypedDict):
    """단일 리뷰 반복 기록"""
    iteration_number: int
    draft: str
    feedback: Optional[str]
    timestamp: str

class WorkflowState(TypedDict):
    """메인 워크플로우 상태"""
    topic: str                                          # 작성 주제
    current_draft: str                                  # 현재 초안
    current_feedback: str                               # 현재 피드백
    iterations: Annotated[List[ReviewIteration], add]   # 반복 이력 (누적)
    iteration_count: int                                # 현재 반복 횟수
    user_decision: str                                  # 사용자 결정
    max_iterations: int                                 # 최대 반복 횟수
    conversation_history: Annotated[List[dict], add]    # 대화 이력 (누적)
```

**핵심 설계 포인트**:
- `Annotated[List[T], add]`: 리스트 누적을 위한 **리듀서 패턴**
- 노드는 부분 상태만 반환, LangGraph가 자동 병합
- TypedDict로 타입 안전성 확보

---

### 3. 설정 관리 (`src/config/settings.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LM Studio 설정
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_model: str = "qwen"

    # 생성 파라미터
    writer_temperature: float = 0.8   # 창의적 글쓰기
    editor_temperature: float = 0.3   # 분석적 피드백
    max_tokens: int = 2000

    # 워크플로우 설정
    max_iterations: int = 10
    checkpoint_db_path: str = "data/checkpoints.sqlite"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

**핵심 설계 포인트**:
- Pydantic Settings로 환경 변수 자동 로드
- Writer(0.8)와 Editor(0.3)에 **다른 temperature** 적용
- `.env` 파일로 중앙 집중식 설정 관리

---

### 4. LLM 클라이언트 (`src/llm/client.py`)

```python
from openai import OpenAI
from typing import List, Dict, Optional

class LMStudioClient:
    """LM Studio OpenAI 호환 클라이언트"""

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model_name: str = "qwen",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        self.client = OpenAI(
            base_url=base_url,
            api_key="not-needed"  # LM Studio는 인증 불필요
        )
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """LLM 생성 요청"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LM Studio API call failed: {e}")

    def test_connection(self) -> bool:
        """연결 테스트"""
        try:
            self.client.models.list()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
```

**핵심 설계 포인트**:
- OpenAI SDK를 사용한 LM Studio 통신
- 연결 테스트 기능 제공
- Temperature 및 max_tokens 오버라이드 지원

---

### 5. Writer 에이전트 (`src/agents/writer.py`)

```python
from typing import Dict, Any
from datetime import datetime
from ..llm.client import LMStudioClient
from ..graph.state import WorkflowState
from ..config.settings import settings

class WriterAgent:
    """초안 작성 및 수정 에이전트"""

    SYSTEM_PROMPT = """You are a professional writer. Your role is to create well-structured,
engaging content based on the given topic and any feedback provided.

When writing:
- Be clear and concise
- Use proper structure (introduction, body, conclusion)
- Maintain a professional tone
- Address all feedback points if provided
- Make your content informative and engaging

Output only the draft content, no meta-commentary or explanations."""

    def __init__(self, llm_client: LMStudioClient):
        self.llm_client = llm_client

    def create_initial_draft(self, topic: str) -> str:
        """초안 작성"""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Write a draft article about: {topic}"}
        ]
        return self.llm_client.generate(messages)

    def revise_draft(self, current_draft: str, feedback: str) -> str:
        """피드백 기반 수정"""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"""Here is the current draft:

{current_draft}

Here is the editor's feedback:

{feedback}

Please revise the draft to address all the feedback points."""}
        ]
        return self.llm_client.generate(messages)


def writer_node(state: WorkflowState) -> Dict[str, Any]:
    """LangGraph Writer 노드 함수"""
    llm_client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model,
        temperature=settings.writer_temperature,
        max_tokens=settings.max_tokens
    )

    writer = WriterAgent(llm_client)

    # 첫 반복: 초안 작성
    if state["iteration_count"] == 0:
        draft = writer.create_initial_draft(state["topic"])
    else:
        # 이후 반복: 피드백 반영 수정
        draft = writer.revise_draft(
            state["current_draft"],
            state["current_feedback"]
        )

    # 반복 기록 생성
    iteration = {
        "iteration_number": state["iteration_count"],
        "draft": draft,
        "feedback": None,
        "timestamp": datetime.now().isoformat()
    }

    # 대화 히스토리 추가
    message = {
        "role": "writer",
        "content": draft,
        "iteration": state["iteration_count"]
    }

    # 부분 상태 업데이트 반환
    return {
        "current_draft": draft,
        "iterations": [iteration],
        "conversation_history": [message]
    }
```

**핵심 설계 포인트**:
- 에이전트 클래스와 노드 함수 분리
- 초안 작성과 수정 로직 분리
- 높은 temperature(0.8)로 창의적 글쓰기

---

## 남은 구현 작업

### 1. Editor 에이전트 (`src/agents/editor.py`)

```python
from typing import Dict, Any
from ..llm.client import LMStudioClient
from ..graph.state import WorkflowState
from ..config.settings import settings

class EditorAgent:
    """초안 검토 및 피드백 에이전트"""

    SYSTEM_PROMPT = """You are a professional editor. Your role is to review written content
and provide constructive, actionable feedback.

When reviewing:
- Evaluate clarity, structure, and flow
- Check for grammatical issues
- Suggest improvements for engagement and readability
- Be specific and actionable in your feedback
- Acknowledge what works well

Provide your feedback in a structured format:

**Strengths:**
- [List what works well]

**Areas for Improvement:**
- [Specific, actionable suggestions]

**Overall Assessment:**
[Brief summary]"""

    def __init__(self, llm_client: LMStudioClient):
        self.llm_client = llm_client

    def review_draft(self, draft: str, iteration: int) -> str:
        """초안 검토"""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"""Please review this draft (Iteration {iteration + 1}):

{draft}

Provide your editorial feedback."""}
        ]
        return self.llm_client.generate(messages)


def editor_node(state: WorkflowState) -> Dict[str, Any]:
    """LangGraph Editor 노드 함수"""
    llm_client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model,
        temperature=settings.editor_temperature,
        max_tokens=settings.max_tokens
    )

    editor = EditorAgent(llm_client)

    feedback = editor.review_draft(
        state["current_draft"],
        state["iteration_count"]
    )

    latest_iteration = state["iterations"][-1]
    timestamp = latest_iteration["timestamp"]

    updated_iteration = {
        "iteration_number": state["iteration_count"],
        "draft": state["current_draft"],
        "feedback": feedback,
        "timestamp": timestamp
    }

    message = {
        "role": "editor",
        "content": feedback,
        "iteration": state["iteration_count"]
    }

    return {
        "current_feedback": feedback,
        "iterations": [updated_iteration],
        "conversation_history": [message]
    }
```

---

### 2. 워크플로우 그래프 (`src/graph/workflow.py`)

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt
from typing import Literal
from .state import WorkflowState
from ..agents.writer import writer_node
from ..agents.editor import editor_node
from ..config.settings import settings


def user_intervention_node(state: WorkflowState) -> dict:
    """사용자 개입 노드 - Human-in-the-Loop"""
    prompt = f"""
========================================
ITERATION {state['iteration_count'] + 1}
========================================

DRAFT:
{state['current_draft']}

{'='*40}

FEEDBACK:
{state['current_feedback'] if state['current_feedback'] else 'Not yet provided'}

{'='*40}

What would you like to do?
1. Continue to next iteration
2. Stop and accept current draft
3. Provide additional guidance

Enter your choice (continue/stop/revise):
"""

    # interrupt()로 실행 중단 및 사용자 입력 대기
    user_decision = interrupt(prompt)

    return {
        "user_decision": user_decision,
        "iteration_count": state["iteration_count"] + 1
    }


def should_continue(state: WorkflowState) -> Literal["writer", "end"]:
    """조건부 라우팅 함수"""
    if state["iteration_count"] >= state["max_iterations"]:
        print(f"Maximum iterations ({state['max_iterations']}) reached.")
        return "end"

    decision = state.get("user_decision", "").lower().strip()

    if decision == "stop":
        return "end"
    elif decision in ["continue", "revise"]:
        return "writer"
    else:
        return "writer"


def create_workflow() -> StateGraph:
    """워크플로우 그래프 생성"""
    workflow = StateGraph(WorkflowState)

    # 노드 추가
    workflow.add_node("writer", writer_node)
    workflow.add_node("editor", editor_node)
    workflow.add_node("user_intervention", user_intervention_node)

    # 엣지 정의
    workflow.add_edge("writer", "editor")
    workflow.add_edge("editor", "user_intervention")

    # 조건부 엣지
    workflow.add_conditional_edges(
        "user_intervention",
        should_continue,
        {
            "writer": "writer",
            "end": END
        }
    )

    # 시작점 설정
    workflow.set_entry_point("writer")

    return workflow


def compile_workflow():
    """워크플로우 컴파일"""
    workflow = create_workflow()

    # SQLite 체크포인터 초기화
    checkpointer = SqliteSaver.from_conn_string(settings.checkpoint_db_path)

    # 컴파일
    app = workflow.compile(checkpointer=checkpointer)

    return app
```

---

### 3. CLI 인터페이스 (`src/ui/cli.py`)

```python
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from ..graph.workflow import compile_workflow
from ..config.settings import settings

console = Console()

class CLI:
    """CLI 인터페이스"""

    def __init__(self):
        self.app = compile_workflow()
        self.thread_id = None

    def start_session(self, topic: str, thread_id: Optional[str] = None):
        """세션 시작"""
        import uuid

        self.thread_id = thread_id or str(uuid.uuid4())

        config = {
            "configurable": {
                "thread_id": self.thread_id
            }
        }

        initial_state = {
            "topic": topic,
            "current_draft": "",
            "current_feedback": "",
            "iterations": [],
            "iteration_count": 0,
            "user_decision": "",
            "max_iterations": settings.max_iterations,
            "conversation_history": []
        }

        console.print(Panel(
            f"[bold green]Starting Writer-Editor Review Loop[/bold green]\\n"
            f"Topic: {topic}\\n"
            f"Thread ID: {self.thread_id}",
            title="Session Info"
        ))

        try:
            for event in self.app.stream(initial_state, config, stream_mode="values"):
                self._handle_event(event)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

    def _handle_event(self, event):
        """이벤트 처리"""
        if "current_draft" in event and event["current_draft"]:
            console.print(Panel(
                Markdown(event["current_draft"]),
                title=f"Draft - Iteration {event['iteration_count']}",
                border_style="blue"
            ))

        if "current_feedback" in event and event["current_feedback"]:
            console.print(Panel(
                Markdown(event["current_feedback"]),
                title=f"Feedback - Iteration {event['iteration_count']}",
                border_style="yellow"
            ))


def run_cli():
    """CLI 실행"""
    cli = CLI()

    console.print("[bold blue]Writer-Editor Review Loop Agent[/bold blue]\\n")

    topic = Prompt.ask("Enter the writing topic")

    cli.start_session(topic)
```

---

### 4. 메인 진입점 (`main.py`)

```python
#!/usr/bin/env python3
import argparse
from src.ui.cli import run_cli
from src.llm.client import LMStudioClient
from src.config.settings import settings


def test_lm_studio_connection():
    """LM Studio 연결 테스트"""
    print("Testing LM Studio connection...")
    client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model
    )

    if client.test_connection():
        print("✓ LM Studio is accessible")
        return True
    else:
        print("✗ Cannot connect to LM Studio")
        print(f"  Make sure LM Studio is running at {settings.lm_studio_base_url}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Writer-Editor Review Loop Agent System"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test LM Studio connection and exit"
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="Writing topic (skips interactive prompt)"
    )
    parser.add_argument(
        "--thread-id",
        type=str,
        help="Resume previous session with thread ID"
    )

    args = parser.parse_args()

    if args.test_connection:
        test_lm_studio_connection()
        return

    if not test_lm_studio_connection():
        return

    run_cli()


if __name__ == "__main__":
    main()
```

---

## 사용 방법

### 1. 환경 설정

```bash
# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 패키지 설치
pip install -e ".[dev]"
```

### 2. LM Studio 설정

1. LM Studio 실행
2. Qwen 모델 로드
3. 포트 1234에서 서버 실행 확인

### 3. 연결 테스트

```bash
python main.py --test-connection
```

### 4. 애플리케이션 실행

```bash
# 기본 실행
python main.py

# 주제 지정
python main.py --topic "AI의 미래"

# 세션 재개
python main.py --thread-id "previous-session-id"
```

---

## 핵심 학습 포인트

### 1. 에이전트 간 검토 루프 (Review Loop)

**구현 방법**:
```python
workflow.add_conditional_edges(
    "user_intervention",
    should_continue,  # 라우팅 함수
    {"writer": "writer", "end": END}  # 분기 맵
)
```

**학습 포인트**:
- 조건부 엣지로 루프 제어
- 상태를 통한 정보 공유
- Writer → Editor → User → Writer 순환

---

### 2. 상태(State) 공유 방법

**리듀서 패턴**:
```python
iterations: Annotated[List[ReviewIteration], add]
```

**동작 원리**:
- 각 노드가 새 항목을 반환하면 `add` 함수로 누적
- LangGraph가 자동으로 기존 리스트에 병합
- 전체 이력을 유지하면서 각 노드는 새 항목만 생성

---

### 3. Human-in-the-Loop 패턴

**Interrupt 사용**:
```python
# 노드에서 실행 중단
user_input = interrupt("사용자에게 보여줄 메시지")

# CLI에서 재개
app.stream(Command(resume=user_input), config)
```

**세션 관리**:
```python
config = {"configurable": {"thread_id": "unique-session-id"}}
```

**학습 포인트**:
- `interrupt()`로 워크플로우 일시 정지
- `Command(resume=...)`로 사용자 입력 전달
- thread_id로 세션 격리 및 재개

---

## 다음 단계

### 즉시 구현 필요
1. ✅ Editor 에이전트 완성
2. ✅ 워크플로우 그래프 구현
3. ✅ CLI 인터페이스 구현
4. ✅ 메인 진입점 작성
5. ✅ `__init__.py` 파일 작성

### 선택적 개선
- 테스트 코드 작성
- README.md 작성
- 예제 스크립트 작성
- 웹 UI 추가
- 분석 기능 추가

---

## 참고 자료

- [LangGraph 공식 문서](https://langchain-ai.github.io/langgraph/)
- [LangGraph Human-in-the-Loop](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/wait-user-input/)
- [LM Studio 개발자 문서](https://lmstudio.ai/docs/developer)
- [LangGraph 상태 관리 가이드](https://deepwiki.com/langchain-ai/langgraph-101/3.1-state-management)

---

**작성일**: 2025-12-27
**버전**: 0.1.0
**상태**: 구현 진행 중 (약 60% 완료)
