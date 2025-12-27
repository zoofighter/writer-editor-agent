"""
State schema definition for the Writer-Editor review loop workflow.

This module defines the TypedDict schemas used by LangGraph to manage
the state of the Writer-Editor collaborative workflow.
"""

from typing import TypedDict, List, Optional, Annotated
from operator import add


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
        topic: The writing topic provided by the user
        current_draft: The latest version of the draft
        current_feedback: The latest feedback from the editor
        iterations: Complete history of all review iterations (accumulated using add reducer)
        iteration_count: Current iteration number (0-indexed)
        user_decision: User's decision at intervention point (continue/stop/revise)
        max_iterations: Maximum allowed iterations before auto-termination
        conversation_history: Complete chat history between agents (accumulated using add reducer)

    Notes:
        - Fields with Annotated[List[T], add] use the add reducer to accumulate items
        - This means each node can append to the list by returning new items
        - LangGraph automatically merges these into the existing list
    """
    topic: str
    current_draft: str
    current_feedback: str
    iterations: Annotated[List[ReviewIteration], add]
    iteration_count: int
    user_decision: str
    max_iterations: int
    conversation_history: Annotated[List[dict], add]
