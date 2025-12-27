# 범용 서적 제작 시스템 (General-Purpose Book System)

## 📋 개요

현재 Python 튜토리얼 북 확장 시스템을 **완전한 범용 서적 제작 시스템**으로 확장하여 다양한 유형의 책을 제작할 수 있도록 구축합니다.

### 목표 서적 유형

1. **Python 튜토리얼** - 프로그래밍 교육서 (이미 지원 중)
2. **구글의 역사** - 서술형/내러티브 책
3. **GPT 모형 이해 지침서** - 기술 가이드북
4. **일반 논픽션** - 범용 논픽션 도서

### 주요 기능

| 기능 | 설명 | 상태 |
|------|------|------|
| 📚 **책 레벨 관리** | TOC, 챕터 의존성, 크로스 참조 | 🔜 계획됨 |
| 🧮 **수식 지원** | LaTeX 수식 생성 및 검증 | 🔜 계획됨 |
| 📊 **다이어그램** | Mermaid, PlantUML 다이어그램 | 🔜 계획됨 |
| ✓ **팩트 체크** | 역사/기술 내용 사실 확인 | 🔜 계획됨 |
| 📖 **참고문헌** | 자동 인용 및 참고문헌 생성 | 🔜 계획됨 |
| 📄 **PDF 내보내기** | Pandoc을 통한 PDF 변환 | 🔜 계획됨 |

---

## 🏗 시스템 아키텍처

### 책 생성 워크플로우

```
사용자 입력 (책 제목, 유형, 챕터 수)
    ↓
BookCoordinator (책 구조 계획)
    ├─ TOC 생성
    ├─ 챕터 의존성 정의
    └─ 용어 사전 초기화
    ↓
User Intervention 1 (책 계획 승인)
    ↓
For each chapter (의존성 순서대로):
    ├─ 챕터 워크플로우 실행
    │   ├─ Content Strategist (목차)
    │   ├─ Outline Reviewer
    │   ├─ Web Search (필요시)
    │   ├─ Writer
    │   └─ Editor
    ├─ 특수 콘텐츠 추가
    │   ├─ MathFormulaAgent (수식)
    │   ├─ DiagramAgent (다이어그램)
    │   └─ BibliographyAgent (인용)
    ├─ FactCheck (역사/기술 책)
    └─ Export Chapter
    ↓
CrossReferenceAgent (참조 검증)
    ↓
BibliographyAgent (참고문헌 컴파일)
    ↓
Assemble Book (책 조립)
    ├─ Title Page
    ├─ TOC
    ├─ All Chapters
    ├─ Glossary
    └─ Bibliography
    ↓
Export (Markdown + PDF)
```

---

## 🎯 신규 컴포넌트

### 1. 상태 스키마 확장

**파일**: `src/graph/state.py`

#### 신규 TypedDict 타입

```python
class BookMetadata(TypedDict):
    """Book-level metadata."""
    book_title: str
    book_type: str  # tutorial, history, technical_guide, narrative, general
    author: Optional[str]
    description: Optional[str]
    target_audience: Optional[str]
    estimated_chapters: Optional[int]
    language: str
    created_at: str
    version: str

class ChapterDependency(TypedDict):
    """Chapter dependency information."""
    chapter_number: int
    depends_on: List[int]  # 선행 챕터 번호
    prerequisite_concepts: List[str]
    introduces_concepts: List[str]

class CrossReference(TypedDict):
    """Cross-reference between chapters."""
    source_chapter: int
    target_chapter: int
    reference_text: str
    reference_type: str  # see_also, prerequisite, example, definition

class TerminologyEntry(TypedDict):
    """Terminology/glossary entry."""
    term: str
    definition: str
    first_introduced_chapter: int
    aliases: List[str]
    related_terms: List[str]

class TableOfContents(TypedDict):
    """Book table of contents."""
    chapters: List[dict]  # [{"number": 1, "title": "...", "summary": "..."}, ...]
    generated_at: str
    total_estimated_length: int

class FactCheckResult(TypedDict):
    """Fact-checking result for a claim."""
    claim: str
    chapter_number: int
    verification_status: str  # verified, unverified, disputed, false
    sources: List[str]
    confidence_score: float  # 0.0-1.0
    notes: Optional[str]
    checked_at: str

class MathFormula(TypedDict):
    """Math formula in LaTeX."""
    formula_id: str
    latex_code: str
    chapter_number: int
    description: str
    is_inline: bool

class Diagram(TypedDict):
    """Diagram specification."""
    diagram_id: str
    diagram_type: str  # mermaid, plantuml, graphviz
    code: str
    chapter_number: int
    caption: str
    description: str
```

#### WorkflowState 확장

```python
class WorkflowState(TypedDict):
    # ... 기존 필드 유지 ...

    # ===== Book-Level Fields =====
    book_metadata: Optional[BookMetadata]
    table_of_contents: Optional[TableOfContents]
    chapter_dependencies: Annotated[List[ChapterDependency], add]
    cross_references: Annotated[List[CrossReference], add]
    terminology_glossary: Dict[str, TerminologyEntry]

    # Multi-chapter coordination
    completed_chapters: List[int]
    current_book_stage: str  # planning, writing, reviewing, finalizing

    # Special content support
    math_formulas: Annotated[List[MathFormula], add]
    diagrams: Annotated[List[Diagram], add]
    fact_check_results: Annotated[List[FactCheckResult], add]

    # Export paths
    book_export_path: Optional[str]
    chapter_export_paths: Dict[int, str]
```

### 2. 신규 템플릿

**파일**: `src/templates/outline_templates.py`

#### HISTORICAL_BOOK_TEMPLATE

```python
HISTORICAL_BOOK_TEMPLATE = {
    "name": "historical_book",
    "description": "Narrative-driven historical book with fact-checking support",
    "book_type": "history",
    "sections": [
        {
            "section_id": "historical_context",
            "title": "Historical Context",
            "purpose": "Set the time period and background",
            "requires_fact_check": True,
            "requires_citations": True,
            "estimated_length": 500
        },
        {
            "section_id": "key_events",
            "title": "Key Events",
            "purpose": "Chronological narrative of main events",
            "requires_fact_check": True,
            "requires_citations": True,
            "requires_timeline": True,
            "estimated_length": 1500
        },
        # ... more sections ...
    ],
    "special_features": {
        "fact_checking": True,
        "citation_management": True,
        "timeline_generation": True,
        "primary_source_linking": True
    }
}
```

#### TECHNICAL_GUIDE_TEMPLATE

```python
TECHNICAL_GUIDE_TEMPLATE = {
    "name": "technical_guide",
    "description": "Technical guide with math formulas and diagrams (e.g., GPT model guide)",
    "book_type": "technical_guide",
    "sections": [
        {
            "section_id": "introduction",
            "title": "Introduction",
            "purpose": "Overview and motivation",
            "estimated_length": 600
        },
        {
            "section_id": "fundamentals",
            "title": "Fundamental Concepts",
            "purpose": "Core concepts and terminology",
            "requires_diagrams": True,
            "requires_terminology": True,
            "estimated_length": 1200
        },
        {
            "section_id": "technical_details",
            "title": "Technical Details",
            "purpose": "In-depth technical explanation",
            "requires_math": True,
            "requires_diagrams": True,
            "requires_fact_check": True,
            "estimated_length": 2000
        },
        # ... more sections ...
    ],
    "special_features": {
        "math_formulas": True,
        "diagrams": True,
        "fact_checking": True,
        "citation_management": True,
        "glossary": True
    }
}
```

### 3. 신규 에이전트 (6개)

#### 3.1 BookCoordinatorAgent

**파일**: `src/agents/book_coordinator_agent.py`

**역할**: 책 전체 구조 관리 및 조율

**주요 기능**:
- 책 전체 TOC 생성
- 챕터 의존성 정의
- 용어 일관성 관리
- 크로스 참조 계획

```python
class BookCoordinatorAgent:
    """Coordinates multi-chapter book creation."""

    SYSTEM_PROMPT = """You are a Book Coordinator specializing in planning and organizing multi-chapter books.

Your responsibilities:
1. Create comprehensive table of contents for the entire book
2. Define chapter dependencies and prerequisites
3. Maintain terminology consistency across chapters
4. Plan cross-references between chapters
5. Ensure logical flow and structure

Output Format (JSON):
{
  "table_of_contents": {
    "chapters": [
      {
        "number": 1,
        "title": "Chapter Title",
        "summary": "Brief summary",
        "estimated_length": 2000,
        "key_concepts": ["concept1", "concept2"]
      }
    ]
  },
  "dependencies": [...],
  "terminology": {...}
}
"""

    def plan_book_structure(
        self,
        book_title: str,
        book_type: str,
        user_intent: dict,
        estimated_chapters: int = 15
    ) -> dict:
        """Generate complete book structure with TOC and dependencies."""
        pass
```

#### 3.2 BibliographyAgent

**파일**: `src/agents/bibliography_agent.py`

**역할**: 참고문헌 및 인용 관리

**주요 기능**:
- 인용 추적
- 참고문헌 포맷팅 (APA, MLA, Chicago)
- 출처 유효성 검증

```python
class BibliographyAgent:
    """Manages citations and bibliography for books."""

    def add_citation(self, source: dict, chapter_number: int) -> str:
        """Add a citation and return citation ID."""
        pass

    def generate_bibliography(self, citations: List[dict], style: str = "APA") -> str:
        """Generate formatted bibliography."""
        pass
```

#### 3.3 FactCheckAgent

**파일**: `src/agents/fact_check_agent.py`

**역할**: 사실 확인 및 검증

**주요 기능**:
- 사실 주장 추출
- 웹 검색 기반 검증
- 신뢰도 점수 할당
- 논란/허위 주장 플래그

```python
class FactCheckAgent:
    """Fact-checks claims in historical and technical books."""

    def extract_claims(self, content: str, chapter_number: int) -> List[str]:
        """Extract factual claims from content."""
        pass

    def verify_claim(self, claim: str, search_results: List[dict]) -> dict:
        """Verify a single claim against search results."""
        pass
```

#### 3.4 MathFormulaAgent

**파일**: `src/agents/math_formula_agent.py`

**역할**: 수식 생성 및 관리

**주요 기능**:
- LaTeX 수식 생성
- 구문 검증
- 수식 설명 제공

```python
class MathFormulaAgent:
    """Generates and manages mathematical formulas in LaTeX."""

    def generate_formula(self, concept: str, context: str) -> dict:
        """Generate LaTeX formula for a concept."""
        pass

    def validate_latex(self, latex_code: str) -> tuple:
        """Validate LaTeX syntax. Returns (is_valid, error_message)."""
        pass
```

#### 3.5 DiagramAgent

**파일**: `src/agents/diagram_agent.py`

**역할**: 다이어그램 생성

**주요 기능**:
- Mermaid/PlantUML/Graphviz 다이어그램 생성
- 구문 검증
- 적절한 다이어그램 유형 선택

```python
class DiagramAgent:
    """Generates diagrams using Mermaid, PlantUML, or other formats."""

    def generate_diagram(
        self,
        concept: str,
        diagram_type: str,
        context: str
    ) -> dict:
        """Generate diagram code for a concept."""
        pass

    def validate_syntax(self, code: str, diagram_type: str) -> tuple:
        """Validate diagram syntax."""
        pass
```

#### 3.6 CrossReferenceAgent

**파일**: `src/agents/cross_reference_agent.py`

**역할**: 챕터 간 참조 검증

**주요 기능**:
- 크로스 참조 식별
- 참조 대상 존재 확인
- 용어 일관성 검증

```python
class CrossReferenceAgent:
    """Validates and manages cross-chapter references."""

    def extract_references(self, content: str, chapter_number: int) -> List[dict]:
        """Extract cross-references from chapter content."""
        pass

    def validate_references(
        self,
        references: List[dict],
        completed_chapters: List[int]
    ) -> List[dict]:
        """Validate that all references point to existing content."""
        pass
```

### 4. 워크플로우 확장

**파일**: `src/graph/workflow.py`

#### create_book_workflow()

```python
def create_book_workflow() -> StateGraph:
    """
    Create workflow for generating an entire book.

    Workflow:
    1. Book Coordinator plans book structure (TOC + dependencies)
    2. User approves book plan
    3. For each chapter:
       a. Run chapter workflow
       b. Add special content (math, diagrams, citations)
       c. Fact-check if required
       d. Export chapter
    4. Cross-Reference Agent validates all references
    5. Bibliography Agent compiles all citations
    6. Assemble final book
    7. Export book as markdown and PDF
    """

    workflow = StateGraph(WorkflowState)

    # Book planning nodes
    workflow.add_node("book_coordinator", book_coordinator_node)
    workflow.add_node("book_plan_intervention", book_plan_intervention_node)

    # Chapter generation (loop)
    workflow.add_node("chapter_selector", chapter_selector_node)
    workflow.add_node("chapter_workflow", chapter_workflow_node)
    workflow.add_node("add_special_content", add_special_content_node)
    workflow.add_node("fact_check", fact_check_node)
    workflow.add_node("export_chapter", export_chapter_node)

    # Book finalization nodes
    workflow.add_node("cross_reference_validation", cross_reference_validation_node)
    workflow.add_node("compile_bibliography", compile_bibliography_node)
    workflow.add_node("assemble_book", assemble_book_node)
    workflow.add_node("export_book", export_book_node)

    # ... edges configuration ...

    return workflow
```

### 5. Export 시스템 확장

**파일**: `src/export/export_manager.py`

#### export_book()

```python
def export_book(
    self,
    book_metadata: Dict[str, Any],
    table_of_contents: Dict[str, Any],
    chapter_paths: Dict[int, Path],
    bibliography: Optional[str] = None,
    glossary: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Export complete book with TOC, chapters, and bibliography.

    Creates:
        - complete-book.md (all content in one file)
        - book-metadata.json (structured metadata)
    """
    pass
```

#### export_pdf()

```python
def export_pdf(
    self,
    markdown_path: Path,
    output_path: Optional[Path] = None
) -> Path:
    """
    Convert markdown book to PDF using pandoc.

    Requires:
        - pandoc installed (brew install pandoc on macOS)
        - Optional: LaTeX for better formatting
    """
    pass
```

---

## 📖 사용 시나리오

### 시나리오 1: Python 튜토리얼 북 생성

```bash
python main.py --mode book \
    --book-title "Python for Complete Beginners" \
    --book-type tutorial \
    --chapters 20 \
    --export-pdf
```

**워크플로우**:
1. BookCoordinator plans 20 chapters
2. User approves TOC
3. For each chapter:
   - Content generation
   - Code examples
   - Exercises
4. Assemble book
5. Export markdown + PDF

**결과**:
- `python-for-complete-beginners-complete.md`
- `python-for-complete-beginners-complete.pdf`
- 20 individual chapter files

### 시나리오 2: 구글의 역사 (History Book)

```bash
python main.py --mode book \
    --book-title "구글의 역사" \
    --book-type history \
    --chapters 15 \
    --export-pdf
```

**특수 기능**:
- ✓ Fact-checking for historical claims
- 📅 Timeline generation
- 📚 Primary source citations
- ✓ Verified dates and events

### 시나리오 3: GPT 모형 이해 지침서

```bash
python main.py --mode book \
    --book-title "GPT 모형을 이해하기 위한 지침서" \
    --book-type technical_guide \
    --chapters 12 \
    --export-pdf
```

**특수 기능**:
- 🧮 LaTeX formulas (attention mechanism, softmax, etc.)
- 📊 Mermaid diagrams (transformer architecture)
- ✓ Technical accuracy verification
- 📖 Comprehensive glossary

---

## 🔧 설정

**파일**: `src/config/settings.py`

```python
class Settings(BaseSettings):
    # ... 기존 설정 유지 ...

    # ===== Book System Settings =====
    # Book Coordinator Agent
    book_coordinator_temperature: float = 0.3
    default_book_chapters: int = 15

    # Fact Check Agent
    fact_check_agent_temperature: float = 0.2
    fact_check_confidence_threshold: float = 0.7
    enable_fact_checking: bool = True

    # Math Formula Agent
    math_agent_temperature: float = 0.2
    validate_latex_syntax: bool = True

    # Diagram Agent
    diagram_agent_temperature: float = 0.3
    default_diagram_type: str = "mermaid"

    # Bibliography Agent
    bibliography_agent_temperature: float = 0.2
    default_citation_style: str = "APA"

    # Cross Reference Agent
    cross_reference_agent_temperature: float = 0.2

    # Book Export
    book_output_dir: str = "output/books"
    auto_export_book: bool = True
    generate_pdf: bool = True
    pandoc_path: Optional[str] = None

    # Book Workflow
    max_chapters_per_book: int = 30
    require_user_approval_per_chapter: bool = False
    enable_cross_reference_validation: bool = True
    enable_terminology_consistency_check: bool = True
```

---

## 📦 구현 단계

### Phase 1: 기초 인프라 (1주)
- ✅ 상태 스키마 확장
- ✅ 설정 업데이트
- ✅ 유틸리티 모듈

### Phase 2: 템플릿 시스템 (3일)
- ✅ HISTORICAL_BOOK_TEMPLATE
- ✅ TECHNICAL_GUIDE_TEMPLATE
- ✅ GENERAL_NONFICTION_TEMPLATE

### Phase 3: 신규 에이전트 (2-3주)
- ✅ BookCoordinatorAgent
- ✅ BibliographyAgent
- ✅ FactCheckAgent
- ✅ MathFormulaAgent
- ✅ DiagramAgent
- ✅ CrossReferenceAgent

### Phase 4: 워크플로우 확장 (1-2주)
- ✅ create_book_workflow()
- ✅ 라우팅 함수들
- ✅ 노드 함수들

### Phase 5: Export 시스템 (1주)
- ✅ export_book()
- ✅ export_pdf()
- ✅ TOC 생성

### Phase 6: CLI 및 통합 (3-5일)
- ✅ main.py 업데이트
- ✅ CLI 구현

### Phase 7: 테스트 및 문서화 (1주)
- ✅ 유닛 테스트
- ✅ 통합 테스트
- ✅ 문서 업데이트

---

## 📋 체크리스트

### 기능 요구사항

- [ ] Python 튜토리얼 생성 가능
- [ ] 역사책 생성 가능
- [ ] 기술 가이드 생성 가능
- [ ] 자동 TOC 생성
- [ ] 챕터 의존성 관리
- [ ] LaTeX 수식 지원
- [ ] 다이어그램 생성
- [ ] 팩트 체크
- [ ] 참고문헌 자동 생성
- [ ] PDF 내보내기
- [ ] 크로스 참조 검증
- [ ] 용어 일관성 검증

### 품질 기준

- [ ] 챕터 간 용어 일관성 유지
- [ ] 크로스 참조 자동 검증
- [ ] 완전한 참고문헌 컴파일
- [ ] 논리적 챕터 순서
- [ ] 전문적인 출력 품질

---

## 🚀 시작하기

1. **의존성 설치**

```bash
pip install pypandoc pylatex
brew install pandoc  # macOS
```

2. **책 생성 예제**

```bash
# Python 튜토리얼
python main.py --mode book \
    --book-title "Python Basics" \
    --book-type tutorial \
    --chapters 15

# 역사책
python main.py --mode book \
    --book-title "구글의 역사" \
    --book-type history \
    --chapters 12

# 기술 가이드
python main.py --mode book \
    --book-title "Understanding GPT" \
    --book-type technical_guide \
    --chapters 10
```

---

## 📚 참고 자료

- [Pandoc User Guide](https://pandoc.org/MANUAL.html)
- [Mermaid Documentation](https://mermaid.js.org/)
- [PlantUML Documentation](https://plantuml.com/)
- [LaTeX Mathematics](https://en.wikibooks.org/wiki/LaTeX/Mathematics)
- [APA Citation Style](https://apastyle.apa.org/)

---

## 🔮 향후 계획

- [ ] 웹 UI 추가
- [ ] 더 많은 언어 지원
- [ ] 이미지 생성 통합
- [ ] 협업 기능
- [ ] 버전 관리 시스템
