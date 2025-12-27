"""
State schema definition for the Writer-Editor review loop workflow.

This module defines the TypedDict schemas used by LangGraph to manage
the state of the Writer-Editor collaborative workflow.
"""

from typing import TypedDict, List, Optional, Annotated, Dict, Any
from operator import add


class UserIntentAnalysis(TypedDict):
    """
    Output from the Business Analyst agent.

    Attributes:
        document_type: Type of document (blog, article, marketing, technical, etc.)
        target_audience: Primary audience for the content
        tone: Desired tone (professional, casual, technical, friendly, etc.)
        key_messages: List of key messages to convey
        constraints: Any constraints or requirements (length, format, style, etc.)
        objectives: Main objectives of the content
    """
    document_type: str
    target_audience: str
    tone: str
    key_messages: List[str]
    constraints: List[str]
    objectives: List[str]


class OutlineSection(TypedDict):
    """
    Represents a single section in the content outline.

    Attributes:
        section_id: Unique identifier for the section
        title: Section title
        purpose: Purpose of this section
        key_points: Main points to cover in this section
        estimated_length: Estimated word count or paragraph count
        research_needed: Whether web research is needed for this section
        search_queries: List of search queries if research is needed
    """
    section_id: str
    title: str
    purpose: str
    key_points: List[str]
    estimated_length: str
    research_needed: bool
    search_queries: List[str]


class ContentOutline(TypedDict):
    """
    Output from the Content Strategist agent.

    Attributes:
        version: Version number of this outline
        sections: List of sections in the outline
        overall_structure: Description of the overall structure
        estimated_total_length: Estimated total word count
        template_used: Name of the template used (if any)
        timestamp: ISO format timestamp of creation
    """
    version: int
    sections: List[OutlineSection]
    overall_structure: str
    estimated_total_length: str
    template_used: Optional[str]
    timestamp: str


class OutlineReview(TypedDict):
    """
    Output from the Outline Reviewer agent.

    Attributes:
        version_reviewed: Version number of the outline reviewed
        approved: Whether the outline is approved
        strengths: What's good about the outline
        weaknesses: Areas needing improvement
        specific_feedback: Detailed feedback for each section
        recommendations: Specific recommendations for improvement
        overall_assessment: Summary assessment
        timestamp: ISO format timestamp of review
    """
    version_reviewed: int
    approved: bool
    strengths: List[str]
    weaknesses: List[str]
    specific_feedback: Dict[str, str]  # section_id -> feedback
    recommendations: List[str]
    overall_assessment: str
    timestamp: str


class SearchResult(TypedDict):
    """
    A single web search result.

    Attributes:
        title: Title of the search result
        url: URL of the source
        snippet: Brief snippet/summary
        relevance_score: Relevance score (if available)
        source: Search provider (duckduckgo, tavily, serper)
    """
    title: str
    url: str
    snippet: str
    relevance_score: Optional[float]
    source: str


class SectionResearch(TypedDict):
    """
    Research data collected for a specific section.

    Attributes:
        section_id: ID of the section this research is for
        search_queries: Queries used for this section
        results: List of search results
        summary: LLM-generated summary of the research
        key_facts: Extracted key facts
        sources: List of source URLs
        timestamp: ISO format timestamp of research
    """
    section_id: str
    search_queries: List[str]
    results: List[SearchResult]
    summary: str
    key_facts: List[str]
    sources: List[str]
    timestamp: str


class ReviewIteration(TypedDict):
    """
    Represents a single iteration in the review loop.

    Attributes:
        iteration_number: The iteration count (0-indexed)
        draft: The draft content for this iteration
        feedback: The editor's feedback (None if not yet reviewed)
        timestamp: ISO format timestamp of when the iteration started
    """
    iteration_number: int
    draft: str
    feedback: Optional[str]
    timestamp: str


class MultipleChoiceQuestion(TypedDict):
    """
    A multiple choice question for tutorial exercises.

    Attributes:
        question: The question text
        options: List of answer options (typically 4)
        correct_answer: Index of the correct option (0-based)
        explanation: Explanation of why the answer is correct
    """
    question: str
    options: List[str]
    correct_answer: int
    explanation: str


class FillInBlankExercise(TypedDict):
    """
    A fill-in-the-blank coding exercise.

    Attributes:
        description: Description of what the code should do
        code_template: Code with blanks marked as _____ or [BLANK]
        correct_answer: The correct code to fill in the blank
        hint: Optional hint for the student
    """
    description: str
    code_template: str
    correct_answer: str
    hint: Optional[str]


class CodingChallenge(TypedDict):
    """
    A coding challenge for practice.

    Attributes:
        title: Challenge title
        description: Detailed description of the problem
        difficulty: Difficulty level (easy, medium, hard)
        starter_code: Optional starter code template
        solution: Complete solution code
        test_cases: List of test cases (input -> expected output)
        hints: Optional list of hints
    """
    title: str
    description: str
    difficulty: str
    starter_code: Optional[str]
    solution: str
    test_cases: List[Dict[str, str]]  # {"input": "...", "output": "..."}
    hints: Optional[List[str]]


class ChapterExercises(TypedDict):
    """
    Complete set of exercises for a tutorial chapter.

    Attributes:
        chapter_number: Chapter number this exercise set belongs to
        multiple_choice: List of multiple choice questions
        fill_in_blank: List of fill-in-the-blank exercises
        coding_challenges: List of coding challenges
        timestamp: ISO format timestamp of generation
    """
    chapter_number: int
    multiple_choice: List[MultipleChoiceQuestion]
    fill_in_blank: List[FillInBlankExercise]
    coding_challenges: List[CodingChallenge]
    timestamp: str


# ===== Book-Level TypedDict Types =====


class BookMetadata(TypedDict):
    """
    Book-level metadata for multi-chapter books.

    Attributes:
        book_title: Full title of the book
        book_type: Type (tutorial, history, technical_guide, narrative, general)
        author: Author name(s)
        description: Book description
        target_audience: Target reader description
        estimated_chapters: Expected number of chapters
        language: Primary language (en, ko, etc.)
        created_at: Creation timestamp (ISO format)
        version: Book version
    """
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
    """
    Chapter dependency information for managing chapter order.

    Attributes:
        chapter_number: Current chapter number
        depends_on: List of chapter numbers this chapter depends on
        prerequisite_concepts: Concepts that must be understood first
        introduces_concepts: New concepts introduced in this chapter
    """
    chapter_number: int
    depends_on: List[int]
    prerequisite_concepts: List[str]
    introduces_concepts: List[str]


class CrossReference(TypedDict):
    """
    Cross-reference between chapters.

    Attributes:
        source_chapter: Chapter where reference is made
        target_chapter: Chapter being referenced
        reference_text: Text of the reference
        reference_type: Type (see_also, prerequisite, example, definition)
    """
    source_chapter: int
    target_chapter: int
    reference_text: str
    reference_type: str  # see_also, prerequisite, example, definition


class TerminologyEntry(TypedDict):
    """
    Terminology/glossary entry for consistent term usage.

    Attributes:
        term: The term/concept
        definition: Definition
        first_introduced_chapter: Chapter where first defined
        aliases: Alternative names for the term
        related_terms: Related concepts
    """
    term: str
    definition: str
    first_introduced_chapter: int
    aliases: List[str]
    related_terms: List[str]


class TableOfContents(TypedDict):
    """
    Book table of contents.

    Attributes:
        chapters: List of chapter entries with number, title, summary
        generated_at: When TOC was generated (ISO format)
        total_estimated_length: Total estimated word count
    """
    chapters: List[Dict[str, Any]]  # [{"number": 1, "title": "...", "summary": "..."}, ...]
    generated_at: str
    total_estimated_length: int


class FactCheckResult(TypedDict):
    """
    Fact-checking result for a claim in historical or technical books.

    Attributes:
        claim: The claim being checked
        chapter_number: Chapter containing the claim
        verification_status: Status (verified, unverified, disputed, false)
        sources: Supporting sources
        confidence_score: Confidence (0.0-1.0)
        notes: Additional notes
        checked_at: Timestamp (ISO format)
    """
    claim: str
    chapter_number: int
    verification_status: str  # verified, unverified, disputed, false
    sources: List[str]
    confidence_score: float
    notes: Optional[str]
    checked_at: str


class MathFormula(TypedDict):
    """
    Math formula in LaTeX for technical books.

    Attributes:
        formula_id: Unique identifier
        latex_code: LaTeX formula code
        chapter_number: Chapter containing formula
        description: What the formula represents
        is_inline: True for inline, False for display mode
    """
    formula_id: str
    latex_code: str
    chapter_number: int
    description: str
    is_inline: bool


class Diagram(TypedDict):
    """
    Diagram specification for technical books.

    Attributes:
        diagram_id: Unique identifier
        diagram_type: Type (mermaid, plantuml, graphviz)
        code: Diagram code
        chapter_number: Chapter containing diagram
        caption: Diagram caption
        description: What the diagram illustrates
    """
    diagram_id: str
    diagram_type: str  # mermaid, plantuml, graphviz
    code: str
    chapter_number: int
    caption: str
    description: str


class WorkflowState(TypedDict):
    """
    Main state schema for the Writer-Editor review loop and book generation.

    This state is shared across all nodes in the LangGraph workflow.
    Nodes return partial updates that are automatically merged by LangGraph.

    Attributes:
        # Original Writer-Editor fields
        topic: The writing topic provided by the user
        current_draft: The latest version of the draft
        current_feedback: The latest feedback from the editor
        iterations: Complete history of all review iterations (accumulated using add reducer)
        iteration_count: Current iteration number (0-indexed)
        user_decision: User's decision at intervention point (continue/stop/revise)
        max_iterations: Maximum allowed iterations before auto-termination
        conversation_history: Complete chat history between agents (accumulated using add reducer)

        # Multi-agent expansion fields
        user_intent: Analysis from Business Analyst agent
        outlines: Complete history of all outline versions (accumulated using add reducer)
        current_outline: Latest version of the outline
        outline_version: Current outline version number
        outline_reviews: Complete history of outline reviews (accumulated using add reducer)
        current_outline_review: Latest outline review
        outline_revision_count: Number of times outline has been revised
        max_outline_revisions: Maximum allowed outline revisions before auto-proceed
        research_data: Complete history of all research (accumulated using add reducer)
        research_by_section: Research data organized by section_id
        current_stage: Current workflow stage (intent/outline/research/draft/edit)

        # Tutorial book extension fields
        code_examples_by_section: Code examples organized by section_id
        code_validation_results: Validation results for generated code (section_id -> (is_valid, error))
        chapter_exercises: Generated exercises for the chapter
        chapter_number: Current chapter number (for tutorial books)
        chapter_metadata: Additional metadata for the chapter (title, learning objectives, etc.)
        export_path: Path where the chapter was exported

        # Book-level fields
        book_metadata: Metadata for the entire book (title, type, author, etc.)
        table_of_contents: Generated table of contents for the book
        chapter_dependencies: Chapter dependency information (accumulated using add reducer)
        cross_references: Cross-references between chapters (accumulated using add reducer)
        terminology_glossary: Glossary of terms used across the book
        completed_chapters: List of chapter numbers that have been completed
        current_book_stage: Current stage of book creation (planning/writing/reviewing/finalizing)
        math_formulas: LaTeX formulas used in the book (accumulated using add reducer)
        diagrams: Diagrams (Mermaid/PlantUML) used in the book (accumulated using add reducer)
        fact_check_results: Fact-checking results (accumulated using add reducer)
        book_export_path: Path to the assembled complete book
        chapter_export_paths: Mapping of chapter_number to export file path

    Notes:
        - Fields with Annotated[List[T], add] use the add reducer to accumulate items
        - This means each node can append to the list by returning new items
        - LangGraph automatically merges these into the existing list
        - Optional fields maintain backward compatibility with simple Writer-Editor workflow
    """
    # Original Writer-Editor fields
    topic: str
    current_draft: str
    current_feedback: str
    iterations: Annotated[List[ReviewIteration], add]
    iteration_count: int
    user_decision: str
    max_iterations: int
    conversation_history: Annotated[List[dict], add]

    # Multi-agent expansion fields
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

    # Tutorial book extension fields
    code_examples_by_section: Dict[str, List[str]]
    code_validation_results: Dict[str, tuple]  # section_id -> (is_valid, error_message)
    chapter_exercises: Optional[ChapterExercises]
    chapter_number: Optional[int]
    chapter_metadata: Optional[Dict[str, Any]]
    export_path: Optional[str]

    # Book-level fields
    book_metadata: Optional[BookMetadata]
    table_of_contents: Optional[TableOfContents]
    chapter_dependencies: Annotated[List[ChapterDependency], add]
    cross_references: Annotated[List[CrossReference], add]
    terminology_glossary: Dict[str, TerminologyEntry]  # term -> entry
    completed_chapters: List[int]  # List of completed chapter numbers
    current_book_stage: str  # planning, writing, reviewing, finalizing
    math_formulas: Annotated[List[MathFormula], add]
    diagrams: Annotated[List[Diagram], add]
    fact_check_results: Annotated[List[FactCheckResult], add]
    book_export_path: Optional[str]  # Path to assembled book
    chapter_export_paths: Dict[int, str]  # chapter_number -> path
