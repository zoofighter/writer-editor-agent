# Python 튜토리얼 북 확장 - 구현 가이드

## 📋 개요

이 문서는 Writer-Editor 멀티 에이전트 시스템을 위한 **Python 튜토리얼 북 확장** 구현에 대해 상세히 설명합니다. 이 확장 기능은 Python 초보자를 위해 특별히 설계된 코드 예제, 연습문제, 교육 콘텐츠가 포함된 완전한 튜토리얼 북 챕터를 생성할 수 있게 합니다.

**구현 날짜**: 2025-12-27
**상태**: ✅ 핵심 구현 완료 (Phase 1-4)
**남은 작업**: 워크플로우 통합, CLI 업데이트, 엔드투엔드 테스트

---

## 🎯 프로젝트 목표

### 주요 목적
1. 완전 초보자를 위한 Python 튜토리얼 챕터 생성
2. 문법적으로 올바른 코드 예제 자동 생성
3. 교육용 연습문제 생성 (객관식, 빈칸 채우기, 코딩 챌린지)
4. 잘 포맷된 마크다운 파일로 챕터 내보내기
5. 기존 Writer-Editor 시스템과의 하위 호환성 유지

### 대상 독자
- **주요 대상**: 완전 프로그래밍 초보자 (사전 경험 없음)
- **부차 대상**: 독학자, 부트캠프 학생, 교육자

---

## 🏗️ 아키텍처 개요

### 시스템 확장 전략
이 확장은 **모듈식 확장** 접근 방식을 따릅니다:
- ✅ **비침습적**: 기존 워크플로우는 변경되지 않음
- ✅ **부가적**: 새로운 에이전트와 템플릿이 기존 것과 함께 추가됨
- ✅ **상태 기반**: 선택적 튜토리얼 필드로 확장된 상태 스키마
- ✅ **템플릿 주도**: 구조화된 콘텐츠를 위한 새로운 `PYTHON_TUTORIAL_TEMPLATE`

### 컴포넌트 계층 구조
```
멀티 에이전트 시스템 (기존)
├── 템플릿 (확장됨)
│   ├── 블로그 포스트
│   ├── 기술 문서
│   ├── 마케팅 카피
│   └── 🆕 Python 튜토리얼 ← 신규
│
├── 에이전트 (확장됨)
│   ├── Business Analyst
│   ├── Content Strategist
│   ├── Outline Reviewer
│   ├── Web Search Agent
│   ├── Writer (강화됨)
│   ├── Editor
│   ├── 🆕 Code Example Agent ← 신규
│   └── 🆕 Exercise Generator ← 신규
│
├── 유틸리티 (신규 모듈)
│   └── 🆕 Code Validator ← 신규
│
└── Export (신규 모듈)
    └── 🆕 Tutorial Export Manager ← 신규
```

---

## 📦 구현 상세

### Phase 1: 템플릿 시스템 ✅

**파일**: `src/templates/outline_templates.py`

#### PYTHON_TUTORIAL_TEMPLATE 구조
```python
{
    "name": "python_tutorial",
    "description": "완전 초보자를 위한 단계별 Python 튜토리얼 챕터",
    "sections": [
        {
            "section_id": "introduction",
            "title": "챕터 소개",
            "requires_code": False,
            "estimated_length": "150-250 단어"
        },
        {
            "section_id": "concept_explanation",
            "title": "개념 설명",
            "requires_code": False,
            "research_needed": True,
            "search_queries": [
                "{topic} Python 초보자 설명",
                "{topic} Python 간단한 비유",
                "{topic} Python 튜토리얼"
            ]
        },
        {
            "section_id": "basic_examples",
            "title": "기본 예제",
            "requires_code": True,
            "code_complexity": "basic",
            "num_code_examples": 2
        },
        {
            "section_id": "progressive_examples",
            "title": "점진적 예제",
            "requires_code": True,
            "code_complexity": "intermediate",
            "num_code_examples": 3
        },
        {
            "section_id": "common_mistakes",
            "title": "흔한 실수와 해결 방법",
            "requires_code": True,
            "code_complexity": "basic",
            "num_code_examples": 2
        },
        {
            "section_id": "practical_application",
            "title": "실전 활용",
            "requires_code": True,
            "code_complexity": "intermediate",
            "num_code_examples": 1
        },
        {
            "section_id": "key_takeaways",
            "title": "핵심 요약",
            "requires_code": False
        },
        {
            "section_id": "exercises",
            "title": "연습 문제",
            "requires_code": False,
            "exercise_types": {
                "multiple_choice": 4,
                "fill_in_blank": 3,
                "coding_challenges": 3
            }
        }
    ]
}
```

#### 템플릿 레지스트리 통합
```python
TEMPLATE_REGISTRY: Dict[str, Dict[str, Any]] = {
    # 기존 템플릿들...
    "python_tutorial": PYTHON_TUTORIAL_TEMPLATE,
    "tutorial": PYTHON_TUTORIAL_TEMPLATE,  # 별칭
}
```

**핵심 설계 결정**:
- **8개 섹션**: 점진적 학습을 위한 구조 (소개 → 이론 → 실습 → 연습문제)
- **`requires_code` 플래그**: 코드 생성이 필요한 섹션 표시
- **`code_complexity`**: 예제 난이도 제어 (basic/intermediate)
- **`exercise_types`**: 유형별 연습문제 수 지정

---

### Phase 2A: 코드 검증 유틸리티 ✅

**파일**: `src/utils/code_validator.py`

#### PythonCodeValidator 클래스

**목적**: 생성된 모든 코드가 문법적으로 올바르고 Python 모범 사례를 따르도록 보장

**주요 메서드**:

1. **`validate_syntax(code: str) -> Tuple[bool, Optional[str]]`**
   - Python의 `ast.parse()`를 사용한 문법 검사
   - 줄 번호가 포함된 상세한 오류 메시지 반환
   - 코드 실행 없음 (보안상 안전)

2. **`check_line_length(code: str, max_length: int = 79) -> List[str]`**
   - PEP 8 준수 확인
   - 긴 줄에 대한 경고 반환

3. **`check_indentation_consistency(code: str) -> Tuple[bool, Optional[str]]`**
   - 스페이스/탭 혼용 감지
   - Python 코드 정확성에 중요

4. **`validate_tutorial_code(code: str) -> Dict[str, Any]`**
   - 모든 검사를 결합한 종합 검증
   - 상세한 검증 보고서 반환

**사용 예시**:
```python
from src.utils.code_validator import PythonCodeValidator

validator = PythonCodeValidator()
code = """
def greet(name):
    print(f"안녕하세요, {name}님!")
"""

is_valid, error = validator.validate_syntax(code)
# 반환: (True, None)

result = validator.validate_tutorial_code(code)
# 반환: {
#     "is_valid": True,
#     "syntax_valid": True,
#     "syntax_error": None,
#     "line_length_warnings": [],
#     "indentation_warning": None,
#     "summary": "코드가 유효합니다"
# }
```

**설계 근거**:
- **AST 전용 검증**: 실행하지 않아 무한 루프, 파일 작업, 악성 코드 방지
- **초보자 친화적 오류**: 줄 번호와 시각적 마커가 있는 명확한 오류 메시지
- **비차단 경고**: 줄 길이 경고는 검증 실패로 이어지지 않음 (교육적 유연성)

---

### Phase 2B: 코드 예제 에이전트 ✅

**파일**: `src/agents/code_example_agent.py`

#### CodeExampleAgent 클래스

**목적**: 포괄적인 주석이 있는 초보자 친화적 Python 코드 예제 생성

**설정**:
- **Temperature**: 0.2 (창의성보다 정확성)
- **모델**: 설정에 구성된 것과 동일 (LM Studio를 통한 Qwen)

**핵심 메서드**:

1. **`generate_basic_example(concept: str, context: str) -> Tuple[str, Dict]`**
   - 간단하고 잘 주석 처리된 코드 생성
   - 최대 10-15줄
   - 문법 오류 시 자동 검증 및 재시도 (최대 3회)

   ```python
   code, validation = agent.generate_basic_example(
       concept="for 루프",
       context="숫자 리스트 반복"
   )
   # 인라인 주석이 있는 검증된 코드 반환
   ```

2. **`generate_progressive_examples(concept: str, num_examples: int = 3) -> List[Tuple[str, Dict]]`**
   - 점진적으로 복잡한 예제 생성
   - 각 예제는 이전 예제를 기반으로 함
   - basic/intermediate/advanced 복잡도 지원

   ```python
   examples = agent.generate_progressive_examples(
       concept="리스트 컴프리헨션",
       complexity="intermediate",
       num_examples=3
   )
   # 복잡도가 증가하는 3개 예제 반환
   ```

3. **`generate_error_example(concept: str) -> Tuple[str, Dict]`**
   - 흔한 실수와 수정 방법 표시
   - 실제 오류 메시지 포함
   - 잘못된/올바른 패턴 따름

   ```python
   code, validation = agent.generate_error_example("리스트 인덱싱")
   # IndexError와 수정 방법을 보여주는 코드 반환
   ```

**시스템 프롬프트** (발췌):
```
당신은 완전 초보자를 가르치는 전문 Python 교육자입니다.

코드 예제 작성 시:
1. 명확성 우선: 즉시 이해할 수 있는 코드 작성
2. 포괄적 주석: 모든 줄에 설명 주석 포함
3. 의미 있는 이름: 설명적인 변수와 함수 이름 사용
4. 출력 표시: 코드가 생성하는 출력을 보여주는 print 문 포함
5. 모범 사례: PEP 8과 Python 모범 사례 준수
6. 완전한 예제: 있는 그대로 실행 가능한 코드

주석이 있는 유효한 Python 코드만 출력. 마크다운 포맷 없음.
```

**LangGraph 통합**:
```python
def code_example_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    requires_code=True로 표시된 섹션에 대한 코드 예제 생성.
    code_examples_by_section이 채워진 업데이트된 상태 반환.
    """
    # 낮은 temperature로 에이전트 초기화
    # 목차 섹션 반복
    # 필요한 섹션에 코드 생성
    # 코드 예제 딕셔너리 반환
```

---

### Phase 2C: 연습문제 생성 에이전트 ✅

**파일**: `src/agents/exercise_generator.py`

#### ExerciseGeneratorAgent 클래스

**목적**: 학습을 강화하는 교육 평가 생성

**설정**:
- **Temperature**: 0.4 (창의성/일관성 균형)
- **출력 형식**: 구조화된 JSON

**연습문제 유형**:

1. **객관식 문제** (챕터당 4개)
   ```python
   questions = agent.generate_multiple_choice(
       concept="for 루프",
       chapter_content="...",
       code_examples=["for i in range(5): print(i)"],
       num_questions=4
   )
   # 반환: List[MultipleChoiceQuestion]
   # 각 문제: question, options (4개), correct_answer (인덱스), explanation
   ```

2. **빈칸 채우기 연습** (챕터당 3개)
   ```python
   exercises = agent.generate_fill_in_blank(
       concept="변수",
       chapter_content="...",
       code_examples=["x = 5"],
       num_exercises=3
   )
   # 반환: List[FillInBlankExercise]
   # 각각: description, code_template (_____ 또는 [BLANK] 포함), correct_answer, hint
   ```

3. **코딩 챌린지** (챕터당 3개)
   ```python
   challenges = agent.generate_coding_challenges(
       concept="함수",
       chapter_content="...",
       code_examples=["def greet(): print('안녕')"],
       difficulty="easy",
       num_challenges=3
   )
   # 반환: List[CodingChallenge]
   # 각각: title, description, difficulty, starter_code, solution, test_cases, hints
   ```

**폴백 메커니즘**:
- 재시도 후에도 LLM이 유효한 연습문제 생성 실패 시
- 유용한 메시지가 있는 플레이스홀더 연습문제 생성
- 워크플로우가 완전히 실패하지 않도록 보장

---

### Phase 3: 내보내기 시스템 ✅

**파일**: `src/export/export_manager.py`

#### TutorialExportManager 클래스

**목적**: 완전한 챕터를 전문적인 마크다운 파일로 내보내기

**주요 기능**:

1. **YAML Frontmatter**
   ```yaml
   ---
   chapter: 1
   title: "변수와 데이터 타입"
   date: 2025-12-27
   learning_objectives:
     - Python 변수 이해하기
     - 기본 데이터 타입 배우기
     - 변수 할당 연습하기
   estimated_time: "45분"
   ---
   ```

2. **코드 블록 포맷팅**
   - 모든 코드를 적절한 마크다운 펜스로 감쌈
   - Python 구문 강조 활성화
   - 인라인 주석 보존

3. **접을 수 있는 연습문제 답안**
   ```markdown
   **문제 1:** `print(2 + 2)`의 출력은 무엇인가요?
   A. 3
   B. 4
   C. 5
   D. "4"

   <details>
   <summary>답안 보기</summary>

   **답:** B

   **설명:** Python에서 2 + 2는 정수 덧셈을 수행하여 4가 됩니다.
   </details>
   ```

4. **파일 이름 규칙**
   - 패턴: `chapter-{num:02d}-{slug}.md`
   - 예시: `chapter-01-variables-and-data-types.md`
   - 출력 디렉토리: `output/tutorial/`

**주요 메서드**:
```python
filepath = manager.export_chapter(
    chapter_number=1,
    chapter_title="변수와 데이터 타입",
    content="# 변수\n\n내용...",
    exercises={
        "multiple_choice": [...],
        "fill_in_blank": [...],
        "coding_challenges": [...]
    },
    code_examples={
        "basic_examples": ["x = 5\nprint(x)"],
        "progressive_examples": [...]
    },
    metadata={
        "learning_objectives": ["변수 이해하기", ...],
        "estimated_time": "45분"
    }
)
# 반환: Path('output/tutorial/chapter-01-variables-and-data-types.md')
```

---

### Phase 4: 상태 스키마 확장 ✅

**파일**: `src/graph/state.py`

#### 새로운 TypedDict 클래스들

1. **MultipleChoiceQuestion** (객관식 문제)
   ```python
   class MultipleChoiceQuestion(TypedDict):
       question: str
       options: List[str]
       correct_answer: int  # 인덱스 (0부터 시작)
       explanation: str
   ```

2. **FillInBlankExercise** (빈칸 채우기 연습)
   ```python
   class FillInBlankExercise(TypedDict):
       description: str
       code_template: str  # _____ 또는 [BLANK] 포함
       correct_answer: str
       hint: Optional[str]
   ```

3. **CodingChallenge** (코딩 챌린지)
   ```python
   class CodingChallenge(TypedDict):
       title: str
       description: str
       difficulty: str  # easy/medium/hard
       starter_code: Optional[str]
       solution: str
       test_cases: List[Dict[str, str]]
       hints: Optional[List[str]]
   ```

4. **ChapterExercises** (챕터 연습문제)
   ```python
   class ChapterExercises(TypedDict):
       chapter_number: int
       multiple_choice: List[MultipleChoiceQuestion]
       fill_in_blank: List[FillInBlankExercise]
       coding_challenges: List[CodingChallenge]
       timestamp: str
   ```

#### WorkflowState 확장

**새로운 필드들** (하위 호환성을 위해 모두 선택적):
```python
class WorkflowState(TypedDict):
    # ... 기존 필드들 ...

    # 튜토리얼 북 확장 필드들
    code_examples_by_section: Dict[str, List[str]]
    code_validation_results: Dict[str, tuple]  # section_id -> (is_valid, error)
    chapter_exercises: Optional[ChapterExercises]
    chapter_number: Optional[int]
    chapter_metadata: Optional[Dict[str, Any]]
    export_path: Optional[str]
```

**설계 원칙**: 모든 새 필드는 **선택적**이므로 기존 워크플로우(블로그, 기술 문서, 마케팅)가 수정 없이 계속 작동합니다.

---

### Phase 5: 설정 구성 ✅

**파일**: `src/config/settings.py`

**새로운 설정들**:
```python
class Settings(BaseSettings):
    # ... 기존 설정들 ...

    # 튜토리얼 북 확장 설정
    code_example_temperature: float = 0.2
    exercise_generator_temperature: float = 0.4
    tutorial_output_dir: str = "output/tutorial"
    auto_export_chapters: bool = True
    validate_code_examples: bool = True
    max_code_line_length: int = 79
    mc_questions_per_chapter: int = 4
    fill_in_blank_per_chapter: int = 3
    coding_challenges_per_chapter: int = 3
```

**환경 변수 지원**:
모든 설정은 `.env` 파일을 통해 재정의 가능:
```env
CODE_EXAMPLE_TEMPERATURE=0.2
EXERCISE_GENERATOR_TEMPERATURE=0.4
TUTORIAL_OUTPUT_DIR=output/tutorial
AUTO_EXPORT_CHAPTERS=true
VALIDATE_CODE_EXAMPLES=true
MC_QUESTIONS_PER_CHAPTER=5
FILL_IN_BLANK_PER_CHAPTER=4
CODING_CHALLENGES_PER_CHAPTER=4
```

---

### Phase 6: Writer 에이전트 강화 ✅

**파일**: `src/agents/writer.py`

**새 메서드**: `_integrate_code_examples()`

**목적**: 생성된 코드를 작성된 콘텐츠에 원활하게 통합

**통합 전략**:

1. **마커 기반 교체**
   ```python
   # Writer가 콘텐츠에 마커를 포함할 수 있음:
   content = """
   예제를 살펴봅시다:

   [CODE_EXAMPLE:basic_examples:0]

   이것은 개념을 명확하게 보여줍니다.
   """

   # 통합 후:
   content = """
   예제를 살펴봅시다:

   ```python
   # 이것은 변수입니다
   x = 5  # x에 5를 할당
   print(x)  # 출력: 5
   ```

   이것은 개념을 명확하게 보여줍니다.
   ```

2. **자동 추가**
   - 마커가 없으면 콘텐츠 끝에 코드 추가
   - 적절한 제목으로 섹션별 그룹화
   - 코드 예제가 절대 손실되지 않도록 보장

---

## 🔧 기술 사양

### 의존성

**새로운 요구사항**:
```txt
# 코드 검증 (내장, 새 의존성 없음)
# 모든 검증은 Python 표준 라이브러리 ast 모듈 사용

# 연습문제 생성을 위한 JSON 파싱 (내장)
```

**새로운 외부 의존성 없음**: 이 확장은 Python 표준 라이브러리와 기존 프로젝트 의존성(LangGraph, OpenAI 클라이언트, Pydantic, Rich)을 활용합니다.

### 성능 고려사항

1. **코드 생성**: Temperature 0.2는 일관된 출력을 생성하지만 느릴 수 있음
2. **검증**: AST 파싱은 빠름 (코드 블록당 <1ms)
3. **연습문제 생성**: 재시도 로직이 있는 JSON 파싱은 5-10초 추가 가능
4. **내보내기**: 파일 I/O는 무시할 만함 (<100ms)

**챕터당 예상 총 시간**: 3-5분 (LLM 속도 및 웹 검색에 따라 다름)

---

## 📊 테스트 전략

### 단위 테스트 (권장)

1. **코드 검증기**
   ```python
   def test_validate_syntax_valid_code():
       validator = PythonCodeValidator()
       code = "print('안녕하세요')"
       is_valid, error = validator.validate_syntax(code)
       assert is_valid is True
       assert error is None
   ```

2. **코드 예제 에이전트**
   ```python
   def test_generate_basic_example():
       agent = CodeExampleAgent(mock_llm_client)
       code, validation = agent.generate_basic_example("변수")
       assert validation["is_valid"] is True
       assert "print" in code.lower()
   ```

---

## 🚀 사용 예시

### 예시 1: Python 변수 챕터 생성

```python
from src.graph.workflow import compile_workflow

# 워크플로우 초기화
app = compile_workflow(mode="tutorial")

# 초기 상태 준비
initial_state = {
    "topic": "Python 변수와 데이터 타입",
    "chapter_number": 1,
    "iteration_count": 0,
    "max_iterations": 10,
    # 튜토리얼 전용
    "code_examples_by_section": {},
    "chapter_exercises": None,
    "chapter_metadata": {
        "learning_objectives": [
            "변수가 무엇인지 이해하기",
            "기본 Python 데이터 타입 배우기",
            "변수 할당 연습하기"
        ],
        "estimated_time": "45분"
    }
}

# 워크플로우 실행
config = {"configurable": {"thread_id": "chapter-01"}}
for event in app.stream(initial_state, config):
    print(event)

# 결과: output/tutorial/에 chapter-01-python-variables-and-data-types.md 생성
```

---

## 📁 파일 구조 요약

```
src/
├── agents/
│   ├── business_analyst.py
│   ├── content_strategist.py
│   ├── outline_reviewer.py
│   ├── web_search_agent.py
│   ├── writer.py (✏️ 강화됨)
│   ├── editor.py
│   ├── code_example_agent.py (🆕 신규)
│   └── exercise_generator.py (🆕 신규)
│
├── config/
│   └── settings.py (✏️ 확장됨)
│
├── export/ (🆕 신규 모듈)
│   ├── __init__.py
│   └── export_manager.py
│
├── graph/
│   ├── state.py (✏️ 확장됨)
│   └── workflow.py (⏳ 튜토리얼 워크플로우 필요)
│
├── templates/
│   └── outline_templates.py (✏️ 확장됨)
│
└── utils/ (🆕 신규 모듈)
    ├── __init__.py
    └── code_validator.py

output/
└── tutorial/ (🆕 자동 생성 내보내기 디렉토리)
    ├── chapter-01-*.md
    ├── chapter-02-*.md
    └── ...
```

**범례**:
- 🆕 신규: 완전히 새로운 파일/모듈
- ✏️ 강화됨/확장됨: 새 기능이 있는 기존 파일
- ⏳ 업데이트 필요: 구현 필요

---

## 🔮 남은 작업

### Phase 4 (일부): 워크플로우 통합

**작업**: `src/graph/workflow.py`에 `create_tutorial_workflow()` 생성

**필요한 흐름**:
```
Business Analyst → Content Strategist → Outline Reviewer →
[목차 검토 루프] → 사용자 승인 →
🆕 Code Example Generator → Web Search → Writer (코드 포함) →
Editor → 🆕 Exercise Generator → 🆕 Export Chapter → END
```

### Phase 5: CLI 및 Main 업데이트

**필요한 변경사항**: CLI에 튜토리얼 모드 추가, main.py 인수 파서 업데이트

### Phase 6: 엔드투엔드 테스트

**테스트 시나리오**:
1. 전체 파이프라인으로 Chapter 1 (변수) 생성
2. Chapter 2 (데이터 타입) 생성 및 일관성 검증
3. 의도적으로 잘못된 코드로 코드 검증 테스트
4. 다양한 개념으로 연습문제 생성 테스트
5. 제목에 특수 문자가 있는 내보내기 테스트

---

## 💡 모범 사례

### 튜토리얼 작성자를 위한 팁

1. **주제 선택**
   - 집중적이고 초보자에게 적합한 주제 선택
   - 챕터당 하나의 개념 (변수만, "변수와 함수" 아님)

2. **챕터 번호 매기기**
   - 순차적 번호 사용 (1, 2, 3...)
   - 논리적 진행 유지 (간단한 것 → 복잡한 것)

3. **코드 검토**
   - 출판 전 생성된 코드 항상 검토
   - 검증은 문법 오류만 잡음, 논리 오류는 잡지 못함
   - 모든 코드 예제를 수동으로 테스트

---

## 🐛 알려진 제한사항

1. **멀티 챕터 조율 없음**
   - 챕터가 독립적임
   - 챕터 간 참조 없음
   - 수동 통합 필요

2. **코드 실행 없음**
   - 검증만 (실행 없음)
   - 논리 오류 감지 안 됨
   - 무한 루프 감지 안 됨

3. **연습문제 다양성**
   - 고정된 연습문제 수
   - 템플릿 기반 생성
   - 고급 주제에 대한 창의성 부족 가능

---

## 🔄 향후 개선사항

### 단기 (다음 스프린트)

1. **Book Manager Agent**
   - 여러 챕터 조율
   - 챕터 간 일관성 유지
   - 목차 자동 생성

2. **코드 실행 샌드박스**
   - 안전한 실행 환경
   - 실제 출력 캡처
   - 논리 정확성 검증

### 장기 (향후 릴리스)

1. **대화형 연습문제**
   - 웹 기반 코드 러너
   - 즉각적인 피드백
   - 진행 상황 추적

2. **다국어 지원**
   - JavaScript, Java, C++ 템플릿
   - 언어별 검증기
   - 통합 연습문제 프레임워크

---

## 📚 참고 자료

### 내부 문서
- [멀티 에이전트 아키텍처](./multi-agent-architecture.md)
- [구현 가이드](./implementation-guide.md)
- [API 레퍼런스](./api-reference.md)

### 외부 리소스
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [Python AST 모듈](https://docs.python.org/3/library/ast.html)
- [PEP 8 스타일 가이드](https://peps.python.org/pep-0008/)

---

## 🙋 자주 묻는 질문 (FAQ)

**Q: Python이 아닌 다른 튜토리얼에 사용할 수 있나요?**
A: 직접적으로는 안 됩니다. 코드 검증기와 예제가 Python 전용입니다. 언어별 검증기와 템플릿을 만들어야 합니다.

**Q: 연습문제 난이도를 어떻게 커스터마이즈하나요?**
A: `src/config/settings.py`의 설정을 수정하거나 환경 변수를 통해 재정의하세요. 연습문제 생성기의 temperature를 조정하여 창의성을 높이거나 낮출 수 있습니다.

**Q: 더 많은 연습문제 유형을 추가할 수 있나요?**
A: 네! `state.py`에 새 TypedDict 클래스를 추가하고, `ExerciseGeneratorAgent`를 새 생성 메서드로 업데이트하며, `export_manager.py`를 수정하여 포맷하세요.

**Q: LLM이 잘못된 코드를 생성하면 어떻게 되나요?**
A: 검증기가 문법 오류를 잡고 재시도합니다. 논리 오류의 경우 여전히 수동 검토가 필요합니다. 향후 버전에서 테스트 케이스 실행 추가를 고려하세요.

---

## ✅ 구현 체크리스트

### 완료됨 ✅
- [x] 8개 섹션을 가진 PYTHON_TUTORIAL_TEMPLATE
- [x] 코드 검증 유틸리티 (AST 기반)
- [x] 재시도 로직이 있는 코드 예제 에이전트
- [x] 연습문제 생성기 (3가지 유형)
- [x] 튜토리얼 내보내기 매니저
- [x] 상태 스키마 확장 (4개 새 TypedDict)
- [x] 설정 구성 (9개 새 설정)
- [x] Writer 에이전트 코드 통합
- [x] 문서화 (이 파일)

### 진행 중 ⏳
- [ ] 튜토리얼 워크플로우 그래프 생성
- [ ] 워크플로우 컴파일러 모드 지원
- [ ] CLI 튜토리얼 모드 구현
- [ ] Main.py 인수 파서 업데이트

### 테스트 🧪
- [ ] 검증기 단위 테스트
- [ ] 에이전트 단위 테스트
- [ ] 워크플로우 통합 테스트
- [ ] 엔드투엔드 챕터 생성 테스트
- [ ] 엣지 케이스 테스트 (오류, 재시도)

---

**문서 버전**: 1.0
**마지막 업데이트**: 2025-12-27
**작성자**: Claude Code Assistant
**상태**: 구현 완료 (핵심 기능)
