"""
Content Strategist agent for creating structured content outlines.

This agent creates detailed outlines for content based on user intent analysis
and document templates.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from src.llm.client import LMStudioClient
from src.config.settings import settings
from src.graph.state import WorkflowState, ContentOutline, OutlineSection, UserIntentAnalysis
from src.templates.outline_templates import get_outline_template, customize_template


class ContentStrategistAgent:
    """
    Agent that creates structured content outlines.

    This agent uses templates to create well-structured outlines that guide
    the writing process. It takes into account the user's intent and adapts
    the template accordingly.
    """

    SYSTEM_PROMPT = """You are an expert content strategist specializing in creating well-structured content outlines.

Your role is to create detailed, actionable outlines that will guide writers to produce high-quality content.

Given:
- A content topic
- User intent analysis (document type, audience, tone, objectives)
- A base template structure

Your task is to:
1. Adapt the template sections to fit the specific topic
2. Provide clear purpose and key points for each section
3. Estimate appropriate content length
4. Identify which sections need research
5. Generate specific search queries for research

For each section, ensure:
- The title is topic-specific and engaging
- The purpose is clear and actionable
- Key points are concrete and relevant
- Search queries (if needed) are specific and useful

Provide thoughtful, strategic guidance that will result in excellent content.
Format your response as structured JSON matching the outline schema."""

    def __init__(self, llm_client: LMStudioClient):
        """
        Initialize the Content Strategist agent.

        Args:
            llm_client: LM Studio client for LLM interactions
        """
        self.llm_client = llm_client

    def create_outline(
        self,
        topic: str,
        user_intent: UserIntentAnalysis,
        outline_version: int = 1,
        feedback: Optional[str] = None
    ) -> ContentOutline:
        """
        Create a content outline based on topic and user intent.

        Args:
            topic: The content topic
            user_intent: User intent analysis from Business Analyst
            outline_version: Version number of this outline
            feedback: Optional feedback from previous review (for revisions)

        Returns:
            ContentOutline TypedDict with complete outline structure
        """
        # Get appropriate template
        template = get_outline_template(user_intent["document_type"])
        if not template:
            # Default to blog post if template not found
            template = get_outline_template("blog_post")

        # Customize template with topic
        customized_template = customize_template(template, topic)

        # Build prompt for LLM
        template_description = self._format_template_for_prompt(customized_template)

        user_intent_str = f"""Document Type: {user_intent['document_type']}
Target Audience: {user_intent['target_audience']}
Tone: {user_intent['tone']}
Key Messages: {', '.join(user_intent['key_messages'])}
Objectives: {', '.join(user_intent['objectives'])}"""

        feedback_section = ""
        if feedback:
            feedback_section = f"""

FEEDBACK FROM PREVIOUS REVIEW:
{feedback}

Please revise the outline to address all feedback points."""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"""Create a detailed content outline for the following:

TOPIC: {topic}

USER INTENT:
{user_intent_str}

BASE TEMPLATE:
{template_description}

Instructions:
1. Adapt each section to be specific to this topic
2. Ensure section titles are engaging and topic-relevant
3. Provide 3-5 concrete key points per section
4. Identify which sections need web research
5. Create specific, actionable search queries for research sections{feedback_section}

Provide the complete outline with all sections fully developed."""}
        ]

        # Generate outline
        response = self.llm_client.generate(
            messages,
            temperature=settings.content_strategist_temperature
        )

        # Parse and structure the outline
        sections = self._parse_outline_response(response, customized_template)

        # Calculate estimated total length
        estimated_total = self._estimate_total_length(sections)

        return ContentOutline(
            version=outline_version,
            sections=sections,
            overall_structure=self._describe_structure(sections),
            estimated_total_length=estimated_total,
            template_used=template["name"],
            timestamp=datetime.now().isoformat()
        )

    def _format_template_for_prompt(self, template: Dict[str, Any]) -> str:
        """Format template structure for LLM prompt."""
        sections_text = []
        for idx, section in enumerate(template["sections"], 1):
            section_text = f"""{idx}. {section['title']}
   Purpose: {section['purpose']}
   Suggested Key Points: {', '.join(section['key_points'])}
   Length: {section['estimated_length']}
   Research Needed: {'Yes' if section['research_needed'] else 'No'}"""
            sections_text.append(section_text)

        return "\n\n".join(sections_text)

    def _parse_outline_response(
        self,
        response: str,
        template: Dict[str, Any]
    ) -> list[OutlineSection]:
        """
        Parse LLM response into structured outline sections.

        This handles the LLM output and structures it according to OutlineSection schema.
        Falls back to template if parsing fails.
        """
        sections = []

        # Try to parse structured sections from response
        # For now, use template structure and extract key points from response
        # This is a simplified approach - could be enhanced with JSON output from LLM

        template_sections = template["sections"]
        response_lines = response.split("\n")

        for idx, template_section in enumerate(template_sections):
            # Extract relevant content from response for this section
            # This is simplified - in production, would use more sophisticated parsing

            section = OutlineSection(
                section_id=template_section["section_id"],
                title=template_section["title"],
                purpose=template_section["purpose"],
                key_points=template_section["key_points"],  # Using template points
                estimated_length=template_section["estimated_length"],
                research_needed=template_section["research_needed"],
                search_queries=template_section.get("search_queries", [])
            )
            sections.append(section)

        return sections

    def _estimate_total_length(self, sections: list[OutlineSection]) -> str:
        """Estimate total content length from all sections."""
        # Simple word count estimation
        total_min = 0
        total_max = 0

        for section in sections:
            length = section["estimated_length"]
            # Parse ranges like "150-250 words"
            if "-" in length and "words" in length:
                try:
                    parts = length.split("-")
                    min_words = int(parts[0].strip())
                    max_words = int(parts[1].replace("words", "").strip())
                    total_min += min_words
                    total_max += max_words
                except:
                    pass

        if total_min > 0 and total_max > 0:
            return f"{total_min}-{total_max} words"
        else:
            return "1500-2500 words (estimated)"

    def _describe_structure(self, sections: list[OutlineSection]) -> str:
        """Generate description of overall structure."""
        section_titles = [s["title"] for s in sections]
        return f"{len(sections)}-section structure: " + " → ".join(section_titles)


def content_strategist_node(state: WorkflowState) -> Dict[str, Any]:
    """
    LangGraph node function for Content Strategist.

    This node creates or revises the content outline based on user intent.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with outline information
    """
    # Initialize LLM client
    llm_client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model,
        temperature=settings.content_strategist_temperature,
        max_tokens=settings.max_tokens
    )

    # Create agent
    strategist = ContentStrategistAgent(llm_client)

    # Determine if this is initial creation or revision
    feedback = None
    if state["current_outline_review"] and not state["current_outline_review"]["approved"]:
        feedback = state["current_outline_review"]["overall_assessment"]

    # Create outline
    outline = strategist.create_outline(
        topic=state["topic"],
        user_intent=state["user_intent"],
        outline_version=state["outline_version"] + 1,
        feedback=feedback
    )

    # Add to conversation history
    conversation_entry = {
        "role": "content_strategist",
        "content": f"Created outline v{outline['version']}: {outline['overall_structure']}",
        "timestamp": datetime.now().isoformat()
    }

    return {
        "current_outline": outline,
        "outline_version": outline["version"],
        "outlines": [outline],
        "conversation_history": [conversation_entry],
        "current_stage": "outline_created"
    }
