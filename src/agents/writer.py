"""
Writer agent implementation for creating and revising drafts.

The Writer agent is responsible for:
- Creating initial drafts based on a given topic
- Creating drafts based on outlines and research data
- Revising drafts based on editor feedback
"""

from typing import Dict, Any, Optional
from datetime import datetime

from ..llm.client import LMStudioClient
from ..graph.state import WorkflowState, ContentOutline, UserIntentAnalysis, SectionResearch
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

    def create_draft_from_outline(
        self,
        topic: str,
        outline: ContentOutline,
        user_intent: UserIntentAnalysis,
        research_by_section: Optional[Dict[str, SectionResearch]] = None
    ) -> str:
        """
        Create a draft based on a detailed outline and research data.

        This is the enhanced writing mode that uses the full multi-agent pipeline.

        Args:
            topic: The content topic
            outline: Structured outline with sections
            user_intent: User intent analysis
            research_by_section: Research data organized by section ID

        Returns:
            Complete draft following the outline
        """
        # Format outline for writer
        outline_text = self._format_outline_for_writing(outline)

        # Format research data if available
        research_text = ""
        if research_by_section:
            research_text = self._format_research_for_writing(
                outline,
                research_by_section
            )

        # Build enhanced prompt
        intent_context = f"""Target Audience: {user_intent['target_audience']}
Tone: {user_intent['tone']}
Key Messages to convey: {', '.join(user_intent['key_messages'])}
Objectives: {', '.join(user_intent['objectives'])}"""

        user_prompt = f"""Write a complete draft about: {topic}

USER INTENT:
{intent_context}

OUTLINE TO FOLLOW:
{outline_text}"""

        if research_text:
            user_prompt += f"""

RESEARCH FINDINGS:
{research_text}

Use the research findings to support your writing with facts, statistics, and insights. Cite sources naturally where appropriate."""

        user_prompt += """

Write the complete content following the outline structure. Make it engaging, well-structured, and informative.
Do not include meta-commentary or section labels - write the content fluidly."""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        return self.llm_client.generate(messages)

    def _format_outline_for_writing(self, outline: ContentOutline) -> str:
        """Format outline as guidance for the writer."""
        sections_text = []

        for idx, section in enumerate(outline["sections"], 1):
            section_text = f"""{idx}. {section['title']}
   Purpose: {section['purpose']}
   Key points to cover:
{self._format_key_points(section['key_points'])}
   Target length: {section['estimated_length']}"""
            sections_text.append(section_text)

        return "\n\n".join(sections_text)

    def _format_research_for_writing(
        self,
        outline: ContentOutline,
        research_by_section: Dict[str, SectionResearch]
    ) -> str:
        """Format research data as guidance for the writer."""
        research_parts = []

        for section in outline["sections"]:
            section_id = section["section_id"]
            if section_id in research_by_section:
                research = research_by_section[section_id]

                research_text = f"""For section "{section['title']}":

Summary:
{research['summary']}

Key Facts:
{self._format_key_points(research['key_facts'])}

Sources: {len(research['sources'])} sources available"""

                research_parts.append(research_text)

        return "\n\n---\n\n".join(research_parts) if research_parts else "No research data available."

    def _format_key_points(self, key_points: list) -> str:
        """Format key points as bulleted list."""
        return "\n".join(f"   - {point}" for point in key_points)

    def _integrate_code_examples(
        self,
        content: str,
        code_examples_by_section: Dict[str, list]
    ) -> str:
        """
        Integrate code examples into written content.

        Looks for markers like [CODE_EXAMPLE:section_id:N] and replaces them
        with actual code. If no markers found, code is appended to relevant sections.

        Args:
            content: The written content
            code_examples_by_section: Code examples organized by section_id

        Returns:
            Content with integrated code examples

        Example:
            >>> writer = WriterAgent(client)
            >>> content = "See example: [CODE_EXAMPLE:intro:0]"
            >>> code_map = {"intro": ["print('hi')"]}
            >>> result = writer._integrate_code_examples(content, code_map)
            >>> assert "```python" in result
        """
        import re

        # Pattern: [CODE_EXAMPLE:section_id:index]
        pattern = r'\[CODE_EXAMPLE:(\w+):(\d+)\]'

        def replace_marker(match):
            section_id = match.group(1)
            index = int(match.group(2))

            if section_id in code_examples_by_section:
                examples = code_examples_by_section[section_id]
                if index < len(examples):
                    code = examples[index]
                    return f"\n\n```python\n{code}\n```\n\n"

            # If code not found, keep marker
            return match.group(0)

        # Replace all markers
        result = re.sub(pattern, replace_marker, content)

        # If no markers were used, append code at the end of relevant sections
        if result == content and code_examples_by_section:
            # Simple approach: append all code examples at the end
            result += "\n\n## Code Examples\n\n"
            for section_id, examples in code_examples_by_section.items():
                section_title = section_id.replace('_', ' ').title()
                result += f"### {section_title}\n\n"
                for i, code in enumerate(examples, start=1):
                    result += f"**Example {i}:**\n\n```python\n{code}\n```\n\n"

        return result


def writer_node(state: WorkflowState) -> Dict[str, Any]:
    """
    LangGraph node function for the Writer agent.

    This function is called by the LangGraph workflow.
    It supports three modes:
    1. Outline-based writing (with research data) - multi-agent mode
    2. Simple initial draft - basic mode
    3. Revision based on feedback - both modes

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

    # Determine writing mode
    has_outline = state.get("current_outline") is not None
    has_user_intent = state.get("user_intent") is not None
    is_first_iteration = state["iteration_count"] == 0
    is_revision = state["iteration_count"] > 0

    # Mode 1: First iteration with outline (multi-agent mode)
    if is_first_iteration and has_outline and has_user_intent:
        draft = writer.create_draft_from_outline(
            topic=state["topic"],
            outline=state["current_outline"],
            user_intent=state["user_intent"],
            research_by_section=state.get("research_by_section")
        )
    # Mode 2: First iteration without outline (basic mode)
    elif is_first_iteration:
        draft = writer.create_initial_draft(state["topic"])
    # Mode 3: Revision mode (both modes)
    else:
        draft = writer.revise_draft(
            state["current_draft"],
            state["current_feedback"]
        )

    # Integrate code examples if available (for tutorial mode)
    code_examples = state.get("code_examples_by_section")
    if code_examples:
        draft = writer._integrate_code_examples(draft, code_examples)

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
        "iteration": state["iteration_count"],
        "timestamp": datetime.now().isoformat()
    }

    # Return partial state update
    # LangGraph will automatically merge these into the full state
    return {
        "current_draft": draft,
        "iterations": [iteration],
        "conversation_history": [message],
        "current_stage": "draft_created"
    }
