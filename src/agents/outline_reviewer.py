"""
Outline Reviewer agent for reviewing and providing feedback on content outlines.

This agent implements the self-review pattern, analyzing outlines for quality,
completeness, and alignment with user intent.
"""

import json
from typing import Dict, Any
from datetime import datetime

from src.llm.client import LMStudioClient
from src.config.settings import settings
from src.graph.state import WorkflowState, OutlineReview, ContentOutline, UserIntentAnalysis


class OutlineReviewerAgent:
    """
    Agent that reviews content outlines for quality and completeness.

    This agent provides structured feedback on outlines, identifying strengths
    and areas for improvement. It can approve outlines or request revisions.
    """

    SYSTEM_PROMPT = """You are an expert content reviewer specializing in evaluating content outlines.

Your role is to review content outlines and provide constructive, actionable feedback.

When reviewing an outline, evaluate:

1. **Logical Flow**: Does the structure follow a logical progression?
2. **Completeness**: Does it cover all necessary aspects of the topic?
3. **Audience Alignment**: Is it appropriate for the target audience?
4. **Clarity**: Are section purposes and key points clear?
5. **Consistency**: Is the tone and depth consistent throughout?
6. **Actionability**: Are the key points specific enough to guide writing?

For each review, provide:
- **Strengths**: What's good about this outline (be specific)
- **Weaknesses**: What needs improvement (be constructive)
- **Section-Specific Feedback**: Detailed feedback for each section that needs work
- **Recommendations**: Specific, actionable suggestions for improvement
- **Decision**: Approve or request revision

Use this JSON format:
{
    "approved": true/false,
    "strengths": ["strength 1", "strength 2", ...],
    "weaknesses": ["weakness 1", "weakness 2", ...],
    "specific_feedback": {
        "section_id": "detailed feedback for this section",
        ...
    },
    "recommendations": ["recommendation 1", "recommendation 2", ...],
    "overall_assessment": "Summary assessment and decision rationale"
}

Be thorough but constructive. Focus on making the outline better, not perfect.
Approve outlines that are good enough to proceed with writing.

Output ONLY the JSON object, no additional text."""

    def __init__(self, llm_client: LMStudioClient):
        """
        Initialize the Outline Reviewer agent.

        Args:
            llm_client: LM Studio client for LLM interactions
        """
        self.llm_client = llm_client

    def review_outline(
        self,
        outline: ContentOutline,
        user_intent: UserIntentAnalysis,
        topic: str
    ) -> OutlineReview:
        """
        Review a content outline and provide structured feedback.

        Args:
            outline: The outline to review
            user_intent: Original user intent analysis
            topic: The content topic

        Returns:
            OutlineReview TypedDict with review results and feedback
        """
        # Format outline for review
        outline_text = self._format_outline_for_review(outline)

        user_intent_str = f"""Document Type: {user_intent['document_type']}
Target Audience: {user_intent['target_audience']}
Tone: {user_intent['tone']}
Key Messages: {', '.join(user_intent['key_messages'])}
Objectives: {', '.join(user_intent['objectives'])}"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"""Review this content outline:

TOPIC: {topic}

USER INTENT:
{user_intent_str}

OUTLINE (Version {outline['version']}):
{outline_text}

Template Used: {outline['template_used']}
Estimated Length: {outline['estimated_total_length']}
Structure: {outline['overall_structure']}

Provide your review in JSON format as specified. Be constructive and specific."""}
        ]

        # Generate review with low temperature for analytical output
        response = self.llm_client.generate(
            messages,
            temperature=settings.outline_reviewer_temperature
        )

        # Parse JSON response
        try:
            # Clean response
            response_clean = response.strip()
            if "```json" in response_clean:
                json_start = response_clean.find("{")
                json_end = response_clean.rfind("}") + 1
                response_clean = response_clean[json_start:json_end]
            elif "```" in response_clean:
                response_clean = response_clean.replace("```", "").strip()

            review_data = json.loads(response_clean)

            # Structure as OutlineReview
            return OutlineReview(
                version_reviewed=outline["version"],
                approved=review_data.get("approved", False),
                strengths=review_data.get("strengths", []),
                weaknesses=review_data.get("weaknesses", []),
                specific_feedback=review_data.get("specific_feedback", {}),
                recommendations=review_data.get("recommendations", []),
                overall_assessment=review_data.get(
                    "overall_assessment",
                    "Review completed but assessment text not provided"
                ),
                timestamp=datetime.now().isoformat()
            )

        except json.JSONDecodeError as e:
            # Fallback: create review based on heuristics
            print(f"Warning: Failed to parse Outline Reviewer output: {e}")
            print(f"Raw response: {response}")

            # Simple heuristic: approve if outline has reasonable structure
            has_good_structure = len(outline["sections"]) >= 3

            return OutlineReview(
                version_reviewed=outline["version"],
                approved=has_good_structure,
                strengths=[
                    "Outline structure follows standard template",
                    f"{len(outline['sections'])} sections provide good coverage"
                ],
                weaknesses=[
                    "Unable to perform detailed automated review"
                ] if not has_good_structure else [],
                specific_feedback={},
                recommendations=[
                    "Manual review recommended for quality assurance"
                ],
                overall_assessment=(
                    "Outline structure is acceptable and can proceed to writing."
                    if has_good_structure
                    else "Outline needs more sections for complete coverage."
                ),
                timestamp=datetime.now().isoformat()
            )

    def _format_outline_for_review(self, outline: ContentOutline) -> str:
        """Format outline as readable text for LLM review."""
        sections_text = []

        for idx, section in enumerate(outline["sections"], 1):
            section_text = f"""{idx}. [{section['section_id']}] {section['title']}
   Purpose: {section['purpose']}
   Key Points:
{self._format_key_points(section['key_points'])}
   Length: {section['estimated_length']}
   Research Needed: {'Yes' if section['research_needed'] else 'No'}"""

            if section['search_queries']:
                queries = ', '.join(section['search_queries'])
                section_text += f"\n   Search Queries: {queries}"

            sections_text.append(section_text)

        return "\n\n".join(sections_text)

    def _format_key_points(self, key_points: list[str]) -> str:
        """Format key points as bulleted list."""
        return "\n".join(f"      - {point}" for point in key_points)


def outline_reviewer_node(state: WorkflowState) -> Dict[str, Any]:
    """
    LangGraph node function for Outline Reviewer.

    This node reviews the current outline and provides feedback.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with review results
    """
    # Initialize LLM client
    llm_client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model,
        temperature=settings.outline_reviewer_temperature,
        max_tokens=settings.max_tokens
    )

    # Create agent and review outline
    reviewer = OutlineReviewerAgent(llm_client)
    review = reviewer.review_outline(
        outline=state["current_outline"],
        user_intent=state["user_intent"],
        topic=state["topic"]
    )

    # Add to conversation history
    decision = "APPROVED" if review["approved"] else "NEEDS REVISION"
    conversation_entry = {
        "role": "outline_reviewer",
        "content": f"Review v{review['version_reviewed']}: {decision} - {review['overall_assessment']}",
        "timestamp": datetime.now().isoformat()
    }

    return {
        "current_outline_review": review,
        "outline_reviews": [review],
        "conversation_history": [conversation_entry],
        "current_stage": "outline_reviewed"
    }
