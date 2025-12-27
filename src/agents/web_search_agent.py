"""
Web Search agent for gathering information from the internet.

This agent executes web searches based on outline sections and summarizes
the findings to support content creation.
"""

from typing import Dict, Any, List
from datetime import datetime

from src.llm.client import LMStudioClient
from src.config.settings import settings
from src.graph.state import WorkflowState, SectionResearch, SearchResult, ContentOutline
from src.tools.search_tools import SearchProvider, search_multiple_queries, deduplicate_results


class WebSearchAgent:
    """
    Agent that performs web searches and summarizes findings.

    This agent:
    1. Identifies which outline sections need research
    2. Executes search queries for those sections
    3. Summarizes search results using LLM
    4. Extracts key facts and sources
    """

    SYSTEM_PROMPT = """You are a research assistant specializing in information synthesis.

Your role is to analyze web search results and create concise, useful summaries for content writers.

When summarizing search results:
1. Extract the most relevant and valuable information
2. Identify key facts, statistics, and insights
3. Note expert opinions and authoritative sources
4. Organize information logically
5. Cite sources appropriately

Provide:
- A coherent summary (2-3 paragraphs)
- A list of key facts (bullet points)
- Note which sources are most authoritative

Be accurate and objective. Focus on information that will help create high-quality content."""

    def __init__(self, llm_client: LMStudioClient, search_provider: SearchProvider):
        """
        Initialize the Web Search agent.

        Args:
            llm_client: LM Studio client for LLM interactions
            search_provider: Search provider for web searches
        """
        self.llm_client = llm_client
        self.search_provider = search_provider

    def research_sections(
        self,
        outline: ContentOutline,
        topic: str
    ) -> Dict[str, SectionResearch]:
        """
        Research all sections in the outline that need research.

        Args:
            outline: Content outline with sections
            topic: The overall content topic

        Returns:
            Dictionary mapping section_id to SectionResearch data
        """
        research_by_section = {}

        for section in outline["sections"]:
            if section["research_needed"] and section["search_queries"]:
                print(f"Researching section: {section['title']}")

                research = self.research_section(
                    section_id=section["section_id"],
                    section_title=section["title"],
                    search_queries=section["search_queries"],
                    topic=topic
                )

                research_by_section[section["section_id"]] = research

        return research_by_section

    def research_section(
        self,
        section_id: str,
        section_title: str,
        search_queries: List[str],
        topic: str
    ) -> SectionResearch:
        """
        Research a single section by executing its search queries.

        Args:
            section_id: Unique section identifier
            section_title: Section title
            search_queries: List of search queries for this section
            topic: Overall content topic

        Returns:
            SectionResearch TypedDict with search results and summary
        """
        # Execute all search queries for this section
        results_by_query = search_multiple_queries(
            queries=search_queries,
            provider=self.search_provider,
            max_results_per_query=settings.max_search_results_per_query
        )

        # Combine and deduplicate results
        all_results = []
        for results in results_by_query.values():
            all_results.extend(results)

        unique_results = deduplicate_results(all_results, by="url")

        # Generate summary using LLM
        summary, key_facts = self._summarize_results(
            section_title=section_title,
            results=unique_results,
            topic=topic
        )

        # Extract source URLs
        sources = [result["url"] for result in unique_results if result.get("url")]

        return SectionResearch(
            section_id=section_id,
            search_queries=search_queries,
            results=unique_results,
            summary=summary,
            key_facts=key_facts,
            sources=sources,
            timestamp=datetime.now().isoformat()
        )

    def _summarize_results(
        self,
        section_title: str,
        results: List[SearchResult],
        topic: str
    ) -> tuple[str, List[str]]:
        """
        Use LLM to summarize search results and extract key facts.

        Args:
            section_title: Title of the section being researched
            results: List of search results
            topic: Overall content topic

        Returns:
            Tuple of (summary_text, key_facts_list)
        """
        if not results:
            return "No search results available for this section.", []

        # Format search results for LLM
        results_text = self._format_results_for_prompt(results)

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"""Analyze these search results for a section about "{section_title}" in content about "{topic}".

SEARCH RESULTS:
{results_text}

Provide:
1. A concise summary (2-3 paragraphs) synthesizing the key information
2. A bulleted list of 5-8 key facts, statistics, or insights

Format your response as:

SUMMARY:
[Your summary here]

KEY FACTS:
- [Fact 1]
- [Fact 2]
- ...

Be specific and cite sources where appropriate."""}
        ]

        # Generate summary
        response = self.llm_client.generate(
            messages,
            temperature=0.3  # Lower temperature for factual accuracy
        )

        # Parse response into summary and key facts
        summary, key_facts = self._parse_summary_response(response)

        return summary, key_facts

    def _format_results_for_prompt(self, results: List[SearchResult]) -> str:
        """Format search results as readable text for LLM."""
        formatted = []

        for idx, result in enumerate(results[:10], 1):  # Limit to top 10 results
            result_text = f"""{idx}. {result['title']}
   Source: {result['url']}
   {result['snippet']}"""
            formatted.append(result_text)

        return "\n\n".join(formatted)

    def _parse_summary_response(self, response: str) -> tuple[str, List[str]]:
        """Parse LLM response into summary and key facts."""
        # Split by markers
        parts = response.split("KEY FACTS:")

        if len(parts) == 2:
            summary_part = parts[0].replace("SUMMARY:", "").strip()
            facts_part = parts[1].strip()

            # Extract bullet points from facts section
            key_facts = []
            for line in facts_part.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("•"):
                    fact = line.lstrip("-•").strip()
                    if fact:
                        key_facts.append(fact)

            return summary_part, key_facts
        else:
            # Fallback: treat entire response as summary
            return response.strip(), []


def web_search_node(state: WorkflowState) -> Dict[str, Any]:
    """
    LangGraph node function for Web Search.

    This node researches all sections in the outline that need research.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with research data
    """
    # Check if web search is enabled
    if not settings.enable_web_search:
        print("Web search is disabled in settings. Skipping research.")
        return {
            "research_by_section": {},
            "research_data": [],
            "current_stage": "research_skipped"
        }

    # Initialize LLM client
    llm_client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model,
        temperature=0.3,  # Lower temperature for research
        max_tokens=settings.max_tokens
    )

    # Initialize search provider
    try:
        search_provider = SearchProvider()
    except ValueError as e:
        print(f"Warning: Search provider initialization failed: {e}")
        print("Continuing without web search.")
        return {
            "research_by_section": {},
            "research_data": [],
            "current_stage": "research_skipped"
        }

    # Create agent
    researcher = WebSearchAgent(llm_client, search_provider)

    # Research all sections
    research_by_section = researcher.research_sections(
        outline=state["current_outline"],
        topic=state["topic"]
    )

    # Convert to list for state accumulation
    research_data_list = list(research_by_section.values())

    # Add to conversation history
    num_sections = len(research_by_section)
    total_sources = sum(len(r["sources"]) for r in research_data_list)

    conversation_entry = {
        "role": "web_search_agent",
        "content": f"Researched {num_sections} sections, found {total_sources} sources",
        "timestamp": datetime.now().isoformat()
    }

    return {
        "research_by_section": research_by_section,
        "research_data": research_data_list,
        "conversation_history": [conversation_entry],
        "current_stage": "research_complete"
    }
