"""
LangGraph workflow implementation for Writer-Editor review loop.

This module defines the complete workflow graph that orchestrates all agents
and implements both simple (Writer-Editor) and advanced (multi-agent) workflows.
"""

from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    from langgraph_checkpoint_sqlite import SqliteSaver
from langgraph.types import interrupt

from src.graph.state import WorkflowState
from src.config.settings import settings

# Import all node functions
from src.agents import (
    business_analyst_node,
    content_strategist_node,
    outline_reviewer_node,
    web_search_node,
    writer_node,
    editor_node,
    book_coordinator_node,
    bibliography_node,
    fact_check_node,
    math_formula_node,
    diagram_node,
    cross_reference_node,
)


# ===== User Intervention Nodes =====

def outline_intervention_node(state: WorkflowState) -> Dict[str, Any]:
    """
    User intervention node for outline review.

    This node pauses execution to show the user the outline and get approval.

    Args:
        state: Current workflow state

    Returns:
        State update with user's decision
    """
    outline = state["current_outline"]
    review = state["current_outline_review"]

    # Display outline and review to user
    prompt_message = f"""
=== OUTLINE REVIEW (Version {outline['version']}) ===

Structure: {outline['overall_structure']}
Estimated Length: {outline['estimated_total_length']}

REVIEW RESULT: {'✓ APPROVED' if review['approved'] else '✗ NEEDS REVISION'}

Strengths:
{chr(10).join('  - ' + s for s in review['strengths'])}

{('Weaknesses:' + chr(10) + chr(10).join('  - ' + w for w in review['weaknesses'])) if review['weaknesses'] else ''}

Overall Assessment:
{review['overall_assessment']}

---

Revisions made: {state['outline_revision_count']} / {state['max_outline_revisions']}

What would you like to do?
- 'proceed': Proceed with this outline (even if not approved)
- 'revise': Request outline revision
"""

    # Interrupt and wait for user decision
    user_decision = interrupt(prompt_message)

    return {
        "user_decision": user_decision,
        "current_stage": "outline_decision_made"
    }


def draft_intervention_node(state: WorkflowState) -> Dict[str, Any]:
    """
    User intervention node for draft review.

    This node pauses execution to show the user the draft and feedback.

    Args:
        state: Current workflow state

    Returns:
        State update with user's decision
    """
    draft = state["current_draft"]
    feedback = state["current_feedback"]
    iteration = state["iteration_count"]

    prompt_message = f"""
=== DRAFT REVIEW (Iteration {iteration}) ===

DRAFT:
{draft[:500]}{'...' if len(draft) > 500 else ''}

EDITOR FEEDBACK:
{feedback}

---

Iterations: {iteration + 1} / {state['max_iterations']}

What would you like to do?
- 'continue': Request revision based on feedback
- 'stop': Accept this draft and end
"""

    # Interrupt and wait for user decision
    user_decision = interrupt(prompt_message)

    # Increment iteration count if continuing
    new_iteration_count = state["iteration_count"] + 1 if user_decision == "continue" else state["iteration_count"]

    return {
        "user_decision": user_decision,
        "iteration_count": new_iteration_count,
        "current_stage": "draft_decision_made"
    }


# ===== Routing Functions =====

def should_approve_outline(state: WorkflowState) -> Literal["approved", "revise", "max_revisions"]:
    """
    Determine if outline should proceed based on review.

    Args:
        state: Current workflow state

    Returns:
        Next node name: 'approved', 'revise', or 'max_revisions'
    """
    review = state["current_outline_review"]

    # Check if max revisions reached
    if state["outline_revision_count"] >= state["max_outline_revisions"]:
        return "max_revisions"

    # Check if approved
    if review["approved"]:
        return "approved"
    else:
        return "revise"


def route_outline_decision(state: WorkflowState) -> Literal["proceed", "revise"]:
    """
    Route based on user's outline decision.

    Args:
        state: Current workflow state

    Returns:
        Next node name: 'proceed' or 'revise'
    """
    decision = state.get("user_decision", "proceed")

    if decision == "revise":
        return "revise"
    else:
        return "proceed"


def should_continue_draft(state: WorkflowState) -> Literal["writer", "end"]:
    """
    Determine if draft review loop should continue.

    Args:
        state: Current workflow state

    Returns:
        Next node name: 'writer' or 'end'
    """
    # Check if max iterations reached
    if state["iteration_count"] >= state["max_iterations"]:
        return "end"

    # Check user decision
    decision = state.get("user_decision", "stop")
    if decision == "continue":
        return "writer"
    else:
        return "end"


# ===== Workflow Creation Functions =====

def create_simple_workflow() -> StateGraph:
    """
    Create the simple Writer-Editor workflow (backward compatible).

    This is the original two-agent workflow:
    START → Writer → Editor → User Intervention → [continue/stop]

    Returns:
        StateGraph for the simple workflow
    """
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("writer", writer_node)
    workflow.add_node("editor", editor_node)
    workflow.add_node("user_intervention", draft_intervention_node)

    # Define edges
    workflow.add_edge("writer", "editor")
    workflow.add_edge("editor", "user_intervention")

    # Conditional edge based on user decision
    workflow.add_conditional_edges(
        "user_intervention",
        should_continue_draft,
        {
            "writer": "writer",
            "end": END
        }
    )

    # Set entry point
    workflow.set_entry_point("writer")

    return workflow


def create_multi_agent_workflow() -> StateGraph:
    """
    Create the complete multi-agent workflow.

    Workflow:
    START → Business Analyst → Content Strategist → Outline Reviewer
         → [Review Loop: max 3 times] → User Approval
         → Web Search → Writer → Editor → [Draft Loop: max 10 times] → END

    Returns:
        StateGraph for the multi-agent workflow
    """
    workflow = StateGraph(WorkflowState)

    # Add all nodes
    workflow.add_node("business_analyst", business_analyst_node)
    workflow.add_node("content_strategist", content_strategist_node)
    workflow.add_node("outline_reviewer", outline_reviewer_node)
    workflow.add_node("outline_intervention", outline_intervention_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("editor", editor_node)
    workflow.add_node("draft_intervention", draft_intervention_node)

    # Phase 1: Intent Analysis
    workflow.add_edge("business_analyst", "content_strategist")

    # Phase 2: Outline Creation and Review Loop
    workflow.add_edge("content_strategist", "outline_reviewer")

    # Outline review routing
    workflow.add_conditional_edges(
        "outline_reviewer",
        should_approve_outline,
        {
            "approved": "outline_intervention",
            "revise": "outline_intervention",
            "max_revisions": "outline_intervention"
        }
    )

    # User decision on outline
    workflow.add_conditional_edges(
        "outline_intervention",
        route_outline_decision,
        {
            "proceed": "web_search",
            "revise": "content_strategist"
        }
    )

    # Phase 3: Research
    workflow.add_edge("web_search", "writer")

    # Phase 4: Draft Creation and Review Loop
    workflow.add_edge("writer", "editor")
    workflow.add_edge("editor", "draft_intervention")

    # Draft review routing
    workflow.add_conditional_edges(
        "draft_intervention",
        should_continue_draft,
        {
            "writer": "writer",
            "end": END
        }
    )

    # Set entry point
    workflow.set_entry_point("business_analyst")

    return workflow


def create_initial_state_legacy(
    topic: str,
    mode: str = "multi-agent",
    max_iterations: int = None,
    max_outline_revisions: int = None
) -> WorkflowState:
    """
    Create initial state for workflow execution.

    Args:
        topic: The content topic
        mode: Workflow mode ('simple' or 'multi-agent')
        max_iterations: Maximum draft iterations (uses settings default if None)
        max_outline_revisions: Maximum outline revisions (uses settings default if None)

    Returns:
        Initial WorkflowState dictionary

    Example:
        >>> initial_state = create_initial_state("AI in healthcare", mode="multi-agent")
        >>> app = compile_workflow("multi-agent")
        >>> app.invoke(initial_state, config)
    """
    base_state = {
        "topic": topic,
        "current_draft": "",
        "current_feedback": "",
        "iterations": [],
        "iteration_count": 0,
        "user_decision": "",
        "max_iterations": max_iterations or settings.max_iterations,
        "conversation_history": [],
    }

    if mode == "multi-agent":
        base_state.update({
            "user_intent": None,
            "outlines": [],
            "current_outline": None,
            "outline_version": 0,
            "outline_reviews": [],
            "current_outline_review": None,
            "outline_revision_count": 0,
            "max_outline_revisions": max_outline_revisions or settings.max_outline_revisions,
            "research_data": [],
            "research_by_section": {},
            "current_stage": "initialized"
        })

    return base_state


# ===== Book Workflow =====

def chapter_intervention_node(state: WorkflowState) -> Dict[str, Any]:
    """
    User intervention node for chapter review in book workflow.

    Args:
        state: Current workflow state

    Returns:
        State update with user's decision
    """
    chapter_number = state.get("chapter_number", 1)
    current_draft = state.get("current_draft", "")
    book_metadata = state.get("book_metadata", {})

    prompt_message = f"""
=== CHAPTER {chapter_number} REVIEW ===

Book: {book_metadata.get('book_title', 'Untitled')}
Chapter {chapter_number}: [Title from draft]

Draft Preview:
{current_draft[:800]}{'...' if len(current_draft) > 800 else ''}

---

What would you like to do?
- 'approve': Approve this chapter and move to next
- 'revise': Request revision
- 'stop': Stop book generation
"""

    user_decision = interrupt(prompt_message)

    return {
        "user_decision": user_decision,
        "current_stage": "chapter_decision_made"
    }


def should_continue_chapter(state: WorkflowState) -> Literal["next_chapter", "revise", "end"]:
    """
    Route based on chapter review decision.

    Args:
        state: Current workflow state

    Returns:
        Next node name
    """
    decision = state.get("user_decision", "approve")

    if decision == "stop":
        return "end"
    elif decision == "revise":
        return "revise"
    else:
        return "next_chapter"


def should_continue_book(state: WorkflowState) -> Literal["write_chapter", "finalize"]:
    """
    Determine if more chapters should be written.

    Args:
        state: Current workflow state

    Returns:
        Next node name
    """
    book_metadata = state.get("book_metadata", {})
    completed_chapters = state.get("completed_chapters", [])
    estimated_chapters = book_metadata.get("estimated_chapters", settings.default_book_chapters)

    if len(completed_chapters) >= estimated_chapters:
        return "finalize"
    else:
        return "write_chapter"


def prepare_next_chapter_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Prepare state for writing next chapter.

    Args:
        state: Current workflow state

    Returns:
        State update for next chapter
    """
    current_chapter = state.get("chapter_number", 0)
    next_chapter = current_chapter + 1

    # Add current chapter to completed list
    completed_chapters = state.get("completed_chapters", [])
    if current_chapter > 0 and current_chapter not in completed_chapters:
        completed_chapters = completed_chapters + [current_chapter]

    return {
        "chapter_number": next_chapter,
        "current_draft": "",
        "current_feedback": "",
        "iteration_count": 0,
        "completed_chapters": completed_chapters,
        "current_stage": "writing_chapter"
    }


def create_book_workflow() -> StateGraph:
    """
    Create the complete book generation workflow.

    Workflow:
    START → Book Coordinator (plan entire book)
         → For each chapter:
              → Content Strategist (chapter outline)
              → Web Search (research)
              → Writer (draft)
              → [Optional] Fact Check
              → [Optional] Math Formulas
              → [Optional] Diagrams
              → [Optional] Bibliography
              → Cross Reference
              → Editor (review)
              → User Approval
         → Finalize Book (assemble all chapters)
         → END

    Returns:
        StateGraph for book workflow
    """
    workflow = StateGraph(WorkflowState)

    # Add all nodes
    workflow.add_node("business_analyst", business_analyst_node)
    workflow.add_node("book_coordinator", book_coordinator_node)
    workflow.add_node("prepare_chapter", prepare_next_chapter_node)
    workflow.add_node("content_strategist", content_strategist_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("fact_check", fact_check_node)
    workflow.add_node("math_formula", math_formula_node)
    workflow.add_node("diagram", diagram_node)
    workflow.add_node("bibliography", bibliography_node)
    workflow.add_node("cross_reference", cross_reference_node)
    workflow.add_node("editor", editor_node)
    workflow.add_node("chapter_intervention", chapter_intervention_node)

    # Phase 1: Book Planning
    workflow.add_edge("business_analyst", "book_coordinator")
    workflow.add_edge("book_coordinator", "prepare_chapter")

    # Phase 2: Chapter Writing Loop
    workflow.add_edge("prepare_chapter", "content_strategist")
    workflow.add_edge("content_strategist", "web_search")
    workflow.add_edge("web_search", "writer")

    # Phase 3: Enhancement Nodes (conditional based on book type)
    workflow.add_edge("writer", "fact_check")
    workflow.add_edge("fact_check", "math_formula")
    workflow.add_edge("math_formula", "diagram")
    workflow.add_edge("diagram", "bibliography")
    workflow.add_edge("bibliography", "cross_reference")

    # Phase 4: Review
    workflow.add_edge("cross_reference", "editor")
    workflow.add_edge("editor", "chapter_intervention")

    # Routing after chapter review
    workflow.add_conditional_edges(
        "chapter_intervention",
        should_continue_chapter,
        {
            "next_chapter": "prepare_chapter",
            "revise": "writer",
            "end": END
        }
    )

    # Set entry point
    workflow.set_entry_point("business_analyst")

    return workflow


def create_tutorial_workflow() -> StateGraph:
    """
    Create tutorial book workflow with exercise generation.

    This is similar to book workflow but includes code example and exercise nodes.

    Returns:
        StateGraph for tutorial book workflow
    """
    from src.agents import (
        code_example_generator_node,
        exercise_generator_node
    )

    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("business_analyst", business_analyst_node)
    workflow.add_node("book_coordinator", book_coordinator_node)
    workflow.add_node("prepare_chapter", prepare_next_chapter_node)
    workflow.add_node("content_strategist", content_strategist_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("code_examples", code_example_generator_node)
    workflow.add_node("exercises", exercise_generator_node)
    workflow.add_node("cross_reference", cross_reference_node)
    workflow.add_node("editor", editor_node)
    workflow.add_node("chapter_intervention", chapter_intervention_node)

    # Define edges
    workflow.add_edge("business_analyst", "book_coordinator")
    workflow.add_edge("book_coordinator", "prepare_chapter")
    workflow.add_edge("prepare_chapter", "content_strategist")
    workflow.add_edge("content_strategist", "web_search")
    workflow.add_edge("web_search", "writer")
    workflow.add_edge("writer", "code_examples")
    workflow.add_edge("code_examples", "exercises")
    workflow.add_edge("exercises", "cross_reference")
    workflow.add_edge("cross_reference", "editor")
    workflow.add_edge("editor", "chapter_intervention")

    # Routing
    workflow.add_conditional_edges(
        "chapter_intervention",
        should_continue_chapter,
        {
            "next_chapter": "prepare_chapter",
            "revise": "writer",
            "end": END
        }
    )

    workflow.set_entry_point("business_analyst")

    return workflow


def compile_workflow(mode: str = "multi-agent") -> Any:
    """
    Compile the workflow graph with checkpointing.

    Args:
        mode: Workflow mode ('simple', 'multi-agent', 'book', 'tutorial')

    Returns:
        Compiled workflow graph ready for execution

    Example:
        >>> app = compile_workflow("book")
        >>> config = {"configurable": {"thread_id": "my-book-session"}}
        >>> for event in app.stream(initial_state, config):
        ...     print(event)
    """
    # Create workflow based on mode
    if mode == "simple":
        workflow = create_simple_workflow()
    elif mode == "multi-agent":
        workflow = create_multi_agent_workflow()
    elif mode == "book":
        workflow = create_book_workflow()
    elif mode == "tutorial":
        workflow = create_tutorial_workflow()
    else:
        raise ValueError(f"Unknown workflow mode: {mode}. Use 'simple', 'multi-agent', 'book', or 'tutorial'.")

    # Set up checkpointer for state persistence
    # Use synchronous SQLite connection for SqliteSaver v3.x
    import sqlite3
    conn = sqlite3.connect(settings.checkpoint_db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    # Compile with checkpointer
    return workflow.compile(checkpointer=checkpointer)


def create_initial_state(
    topic: str,
    mode: str = "multi-agent",
    max_iterations: int = None,
    max_outline_revisions: int = None,
    book_type: str = None,
    estimated_chapters: int = None
) -> WorkflowState:
    """
    Create initial state for workflow execution.

    Args:
        topic: The content topic
        mode: Workflow mode ('simple', 'multi-agent', 'book', 'tutorial')
        max_iterations: Maximum draft iterations (uses settings default if None)
        max_outline_revisions: Maximum outline revisions (uses settings default if None)
        book_type: Type of book (for book/tutorial modes)
        estimated_chapters: Number of chapters (for book/tutorial modes)

    Returns:
        Initial WorkflowState dictionary

    Example:
        >>> initial_state = create_initial_state(
        ...     "GPT Model Guide",
        ...     mode="book",
        ...     book_type="technical_guide",
        ...     estimated_chapters=12
        ... )
        >>> app = compile_workflow("book")
        >>> app.invoke(initial_state, config)
    """
    base_state = {
        "topic": topic,
        "current_draft": "",
        "current_feedback": "",
        "iterations": [],
        "iteration_count": 0,
        "user_decision": "",
        "max_iterations": max_iterations or settings.max_iterations,
        "conversation_history": [],
    }

    if mode in ["multi-agent", "book", "tutorial"]:
        base_state.update({
            "user_intent": None,
            "outlines": [],
            "current_outline": None,
            "outline_version": 0,
            "outline_reviews": [],
            "current_outline_review": None,
            "outline_revision_count": 0,
            "max_outline_revisions": max_outline_revisions or settings.max_outline_revisions,
            "research_data": [],
            "research_by_section": {},
            "current_stage": "initialized"
        })

    if mode in ["book", "tutorial"]:
        base_state.update({
            "book_metadata": None,
            "table_of_contents": None,
            "chapter_dependencies": [],
            "cross_references": [],
            "terminology_glossary": {},
            "completed_chapters": [],
            "current_book_stage": "planning",
            "math_formulas": [],
            "diagrams": [],
            "fact_check_results": [],
            "book_export_path": None,
            "chapter_export_paths": {},
            "chapter_number": 0,
            "chapter_metadata": None,
            "export_path": None
        })

        if book_type:
            base_state["book_metadata"] = {
                "book_type": book_type,
                "estimated_chapters": estimated_chapters or settings.default_book_chapters
            }

    if mode == "tutorial":
        base_state.update({
            "code_examples_by_section": {},
            "code_validation_results": {},
            "chapter_exercises": None
        })

    return base_state
