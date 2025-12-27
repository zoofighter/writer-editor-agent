"""
Editor agent for reviewing and providing feedback on drafts.

This agent provides detailed, constructive feedback on written content,
checking for quality, coherence, and alignment with the outline and user intent.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from src.llm.client import LMStudioClient
from src.config.settings import settings
from src.graph.state import WorkflowState, ContentOutline, UserIntentAnalysis


class EditorAgent:
    """
    Agent that reviews drafts and provides structured feedback.

    The Editor uses analytical prompting (low temperature) to provide
    thorough, constructive feedback that helps improve the content.
    """

    SYSTEM_PROMPT = """You are a professional editor specializing in content review and improvement.

Your role is to review written content and provide constructive, actionable feedback that helps writers improve their work.

When reviewing content, evaluate:

1. **Structure & Organization**: Does it follow the intended outline? Is the flow logical?
2. **Clarity**: Is the writing clear and easy to understand?
3. **Completeness**: Does it cover all necessary points from the outline?
4. **Quality**: Is the writing engaging, well-written, and error-free?
5. **Audience Alignment**: Is it appropriate for the target audience and tone?
6. **Intent Alignment**: Does it achieve the stated objectives?

Provide feedback in this structure:

**Strengths:**
- [What's working well - be specific]

**Areas for Improvement:**
- [Specific, actionable suggestions for improvement]

**Outline Adherence:**
- [How well does it follow the outline? What's missing or out of place?]

**Recommendations:**
- [Prioritized list of what to address in revision]

**Overall Assessment:**
[1-2 sentence summary and whether this is ready or needs revision]

Be constructive and specific. Focus on making the content better, not perfect.
Provide actionable guidance that the writer can implement."""

    def __init__(self, llm_client: LMStudioClient):
        """
        Initialize the Editor agent.

        Args:
            llm_client: LM Studio client for LLM interactions
        """
        self.llm_client = llm_client

    def review_draft(
        self,
        draft: str,
        outline: Optional[ContentOutline],
        user_intent: Optional[UserIntentAnalysis],
        topic: str,
        iteration: int
    ) -> str:
        """
        Review a draft and provide structured feedback.

        Args:
            draft: The draft content to review
            outline: The content outline (if available)
            user_intent: User intent analysis (if available)
            topic: The content topic
            iteration: Current iteration number

        Returns:
            Structured feedback as a string
        """
        # Build context for review
        context_parts = [f"Topic: {topic}"]

        if user_intent:
            context_parts.append(f"Document Type: {user_intent['document_type']}")
            context_parts.append(f"Target Audience: {user_intent['target_audience']}")
            context_parts.append(f"Tone: {user_intent['tone']}")
            context_parts.append(f"Objectives: {', '.join(user_intent['objectives'])}")

        if outline:
            outline_text = self._format_outline_for_review(outline)
            context_parts.append(f"\nOUTLINE:\n{outline_text}")

        context = "\n".join(context_parts)

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"""Review this draft (Iteration {iteration}):

CONTEXT:
{context}

DRAFT:
{draft}

Provide your editorial feedback following the specified structure."""}
        ]

        # Generate feedback with analytical temperature
        feedback = self.llm_client.generate(
            messages,
            temperature=settings.editor_temperature
        )

        return feedback

    def _format_outline_for_review(self, outline: ContentOutline) -> str:
        """Format outline as readable text for review context."""
        sections = []
        for section in outline["sections"]:
            section_text = f"- {section['title']}: {section['purpose']}"
            sections.append(section_text)

        return "\n".join(sections)


def editor_node(state: WorkflowState) -> Dict[str, Any]:
    """
    LangGraph node function for Editor.

    This node reviews the current draft and provides feedback.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with feedback
    """
    # Initialize LLM client
    llm_client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model,
        temperature=settings.editor_temperature,
        max_tokens=settings.max_tokens
    )

    # Create agent
    editor = EditorAgent(llm_client)

    # Review the draft
    feedback = editor.review_draft(
        draft=state["current_draft"],
        outline=state.get("current_outline"),
        user_intent=state.get("user_intent"),
        topic=state["topic"],
        iteration=state["iteration_count"]
    )

    # Update the latest iteration with feedback
    latest_iteration = state["iterations"][-1] if state["iterations"] else None
    if latest_iteration:
        # Note: This updates the iteration dict but LangGraph state may need special handling
        # The iteration was already added by writer_node, we just reference it here
        pass

    # Add to conversation history
    conversation_entry = {
        "role": "editor",
        "content": feedback,
        "iteration": state["iteration_count"],
        "timestamp": datetime.now().isoformat()
    }

    return {
        "current_feedback": feedback,
        "conversation_history": [conversation_entry],
        "current_stage": "draft_reviewed"
    }
