"""
Writer agent implementation for creating and revising drafts.

The Writer agent is responsible for:
- Creating initial drafts based on a given topic
- Revising drafts based on editor feedback
"""

from typing import Dict, Any
from datetime import datetime

from ..llm.client import LMStudioClient
from ..graph.state import WorkflowState
from ..config.settings import settings


class WriterAgent:
    """
    Writer agent responsible for creating and revising drafts.

    The Writer uses a creative writing style (higher temperature) to
    produce engaging and well-structured content.
    """

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
        """
        Initialize the Writer agent.

        Args:
            llm_client: LM Studio client for LLM generation
        """
        self.llm_client = llm_client

    def create_initial_draft(self, topic: str) -> str:
        """
        Create the first draft based on the given topic.

        Args:
            topic: The writing topic

        Returns:
            The initial draft content
        """
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Write a draft article about: {topic}"}
        ]
        return self.llm_client.generate(messages)

    def revise_draft(self, current_draft: str, feedback: str) -> str:
        """
        Revise the draft based on editor feedback.

        Args:
            current_draft: The current version of the draft
            feedback: The editor's feedback

        Returns:
            The revised draft content
        """
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
    """
    LangGraph node function for the Writer agent.

    This function is called by the LangGraph workflow.

    Args:
        state: Current workflow state

    Returns:
        Partial state update dictionary with:
        - current_draft: The new or revised draft
        - iterations: New iteration record
        - conversation_history: New message record
    """
    # Initialize client with writer-specific temperature
    llm_client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model,
        temperature=settings.writer_temperature,
        max_tokens=settings.max_tokens
    )

    writer = WriterAgent(llm_client)

    # First iteration: create initial draft
    if state["iteration_count"] == 0:
        draft = writer.create_initial_draft(state["topic"])
    else:
        # Subsequent iterations: revise based on feedback
        draft = writer.revise_draft(
            state["current_draft"],
            state["current_feedback"]
        )

    # Create iteration record
    iteration = {
        "iteration_number": state["iteration_count"],
        "draft": draft,
        "feedback": None,
        "timestamp": datetime.now().isoformat()
    }

    # Add to conversation history
    message = {
        "role": "writer",
        "content": draft,
        "iteration": state["iteration_count"]
    }

    # Return partial state update
    # LangGraph will automatically merge these into the full state
    return {
        "current_draft": draft,
        "iterations": [iteration],
        "conversation_history": [message]
    }
