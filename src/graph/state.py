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


class WorkflowState(TypedDict):
    """
    Main state schema for the Writer-Editor review loop.

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
