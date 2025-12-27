"""
Business Analyst agent for analyzing user intent and requirements.

This agent analyzes the user's request to understand what type of content
they want to create and what their goals are.
"""

import json
from typing import Dict, Any
from datetime import datetime

from src.llm.client import LMStudioClient
from src.config.settings import settings
from src.graph.state import WorkflowState, UserIntentAnalysis


class BusinessAnalystAgent:
    """
    Agent that analyzes user intent and content requirements.

    This agent uses analytical prompting (low temperature) to understand
    what the user wants to achieve and provides structured analysis.
    """

    SYSTEM_PROMPT = """You are a professional business analyst specializing in content strategy.
Your role is to analyze user requests and extract key information about their content needs.

When analyzing a content request, identify:
1. **Document Type**: What kind of content (blog post, article, marketing copy, technical doc, etc.)
2. **Target Audience**: Who will read this content
3. **Tone**: What style is appropriate (professional, casual, technical, friendly, etc.)
4. **Key Messages**: What are the main points to communicate
5. **Constraints**: Any requirements (length, format, style guidelines, etc.)
6. **Objectives**: What should this content achieve

Provide your analysis in the following JSON format:
{
    "document_type": "blog_post|technical_article|marketing_copy|other",
    "target_audience": "description of the target audience",
    "tone": "professional|casual|technical|friendly|other",
    "key_messages": ["message 1", "message 2", "message 3"],
    "constraints": ["constraint 1", "constraint 2"],
    "objectives": ["objective 1", "objective 2"]
}

Be specific and actionable. Base your analysis on the user's request and reasonable assumptions
for the content type.

Output ONLY the JSON object, no additional text or explanation."""

    def __init__(self, llm_client: LMStudioClient):
        """
        Initialize the Business Analyst agent.

        Args:
            llm_client: LM Studio client for LLM interactions
        """
        self.llm_client = llm_client

    def analyze_intent(self, topic: str) -> UserIntentAnalysis:
        """
        Analyze the user's intent based on their topic request.

        Args:
            topic: The content topic requested by the user

        Returns:
            UserIntentAnalysis TypedDict with structured analysis

        Example:
            >>> analyst = BusinessAnalystAgent(llm_client)
            >>> intent = analyst.analyze_intent("AI in healthcare")
            >>> print(intent["document_type"])
            blog_post
        """
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"""Analyze this content request:

Topic: {topic}

Provide your analysis in JSON format as specified."""}
        ]

        # Use low temperature for analytical output
        response = self.llm_client.generate(
            messages,
            temperature=settings.business_analyst_temperature
        )

        # Parse JSON response
        try:
            # Try to extract JSON from response (in case LLM adds extra text)
            response_clean = response.strip()
            if "```json" in response_clean:
                # Extract JSON from code block
                json_start = response_clean.find("{")
                json_end = response_clean.rfind("}") + 1
                response_clean = response_clean[json_start:json_end]
            elif "```" in response_clean:
                # Remove code block markers
                response_clean = response_clean.replace("```", "").strip()

            analysis = json.loads(response_clean)

            # Ensure all required fields are present
            return UserIntentAnalysis(
                document_type=analysis.get("document_type", "blog_post"),
                target_audience=analysis.get("target_audience", "General audience"),
                tone=analysis.get("tone", "professional"),
                key_messages=analysis.get("key_messages", []),
                constraints=analysis.get("constraints", []),
                objectives=analysis.get("objectives", ["Inform and engage readers"])
            )
        except json.JSONDecodeError as e:
            # Fallback to reasonable defaults if JSON parsing fails
            print(f"Warning: Failed to parse Business Analyst output: {e}")
            print(f"Raw response: {response}")

            return UserIntentAnalysis(
                document_type="blog_post",
                target_audience="General audience interested in the topic",
                tone="professional",
                key_messages=[f"Explore {topic}", f"Provide insights on {topic}"],
                constraints=["Clear and engaging writing", "Well-structured content"],
                objectives=["Inform readers", "Engage audience", "Provide value"]
            )


def business_analyst_node(state: WorkflowState) -> Dict[str, Any]:
    """
    LangGraph node function for Business Analyst.

    This node analyzes the user's topic and extracts intent and requirements.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with user_intent and updated conversation history
    """
    # Initialize LLM client
    llm_client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model,
        temperature=settings.business_analyst_temperature,
        max_tokens=settings.max_tokens
    )

    # Create agent and analyze intent
    analyst = BusinessAnalystAgent(llm_client)
    user_intent = analyst.analyze_intent(state["topic"])

    # Add to conversation history
    conversation_entry = {
        "role": "business_analyst",
        "content": f"Intent Analysis: {json.dumps(user_intent, indent=2)}",
        "timestamp": datetime.now().isoformat()
    }

    return {
        "user_intent": user_intent,
        "conversation_history": [conversation_entry],
        "current_stage": "intent_analysis_complete"
    }
