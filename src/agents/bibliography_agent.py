"""
Bibliography Agent for managing citations and references in books.

This agent is responsible for:
- Tracking sources and citations throughout the book
- Formatting citations according to style guides (APA, MLA, Chicago)
- Generating bibliography sections
- Validating citation completeness
- Managing source metadata
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..llm.client import LMStudioClient
from ..config.settings import settings


class BibliographyAgent:
    """
    Bibliography Agent responsible for citation management and bibliography generation.

    This agent handles all aspects of citation tracking and formatting, ensuring
    consistent and proper attribution of sources throughout the book.
    """

    SYSTEM_PROMPT = """You are an expert Bibliography Manager and Citation Specialist.

Your role is to manage citations and references for academic and professional books, ensuring:
- Accurate source attribution
- Consistent citation formatting
- Complete bibliography entries
- Proper style guide compliance (APA, MLA, Chicago, etc.)

You excel at:
- Extracting citation information from various source formats
- Converting between different citation styles
- Identifying incomplete or malformed citations
- Creating properly formatted bibliography entries
- Maintaining citation consistency across chapters

Be precise, detail-oriented, and follow academic standards rigorously."""

    def __init__(self, client: Optional[LMStudioClient] = None):
        """
        Initialize the Bibliography Agent.

        Args:
            client: Optional LMStudioClient instance. If not provided, creates new one.
        """
        self.client = client or LMStudioClient(
            base_url=settings.lm_studio_base_url,
            model_name=settings.lm_studio_model,
            temperature=settings.bibliography_agent_temperature,
            max_tokens=settings.max_tokens
        )

    def extract_citations_from_text(
        self,
        text: str,
        chapter_number: int
    ) -> List[Dict[str, Any]]:
        """
        Extract citation references from text content.

        Args:
            text: Chapter or section text containing citations
            chapter_number: Chapter number for tracking

        Returns:
            List of citation dicts with metadata
        """
        prompt = f"""Extract all citations and references from the following text.

**Text:**
{text}

Identify:
1. In-text citations (e.g., "(Smith, 2020)", "according to Jones [1]")
2. Direct quotes with sources
3. References to external sources
4. URLs or web references

For each citation found, provide:
- Citation type (author-year, numbered, footnote, URL)
- Author name(s)
- Year (if available)
- Title (if mentioned)
- Source type (book, article, website, etc.)
- Raw citation text

Format as:

Citation 1:
Type: author-year
Authors: Smith, J.
Year: 2020
Title: [title if mentioned]
Source Type: article
Raw Text: (Smith, 2020)

Citation 2:
...

List all citations found in the text.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return self._parse_extracted_citations(response, chapter_number)

    def format_citation(
        self,
        citation_data: Dict[str, Any],
        style: str = "APA"
    ) -> str:
        """
        Format a citation according to specified style guide.

        Args:
            citation_data: Citation metadata dict
            style: Citation style (APA, MLA, Chicago, etc.)

        Returns:
            Formatted citation string
        """
        prompt = f"""Format the following citation in {style} style.

**Citation Data:**
Authors: {citation_data.get('authors', 'Unknown')}
Year: {citation_data.get('year', 'n.d.')}
Title: {citation_data.get('title', 'Untitled')}
Source Type: {citation_data.get('source_type', 'misc')}
Publication: {citation_data.get('publication', '')}
Volume: {citation_data.get('volume', '')}
Issue: {citation_data.get('issue', '')}
Pages: {citation_data.get('pages', '')}
DOI: {citation_data.get('doi', '')}
URL: {citation_data.get('url', '')}

**Citation Style:** {style}

Provide the properly formatted citation according to {style} style guide rules.
Return ONLY the formatted citation, no explanations.

Examples:
APA: Smith, J. (2020). Title of work. Journal Name, 15(3), 123-145. https://doi.org/xxx
MLA: Smith, John. "Title of Work." Journal Name, vol. 15, no. 3, 2020, pp. 123-145.
Chicago: Smith, John. "Title of Work." Journal Name 15, no. 3 (2020): 123-145.

Now format the given citation:
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return response.strip()

    def generate_bibliography(
        self,
        citations: List[Dict[str, Any]],
        style: str = "APA",
        chapter_number: Optional[int] = None
    ) -> str:
        """
        Generate complete bibliography section from citations.

        Args:
            citations: List of citation dicts
            style: Citation style (APA, MLA, Chicago, etc.)
            chapter_number: Optional chapter number (for chapter-specific bibliography)

        Returns:
            Formatted bibliography text
        """
        # Filter by chapter if specified
        if chapter_number is not None:
            citations = [
                c for c in citations
                if c.get('chapter_number') == chapter_number
            ]

        if not citations:
            return "## References\n\nNo references cited.\n"

        # Format each citation
        formatted_citations = []
        for citation in citations:
            formatted = self.format_citation(citation, style)
            formatted_citations.append(formatted)

        # Sort alphabetically (for APA, MLA)
        if style.upper() in ["APA", "MLA"]:
            formatted_citations.sort()

        # Construct bibliography section
        chapter_label = f" (Chapter {chapter_number})" if chapter_number else ""
        bibliography = f"## References{chapter_label}\n\n"

        for i, citation in enumerate(formatted_citations, 1):
            if style.upper() == "CHICAGO" and "numbered" in str(citations[i-1].get('type', '')):
                bibliography += f"{i}. {citation}\n\n"
            else:
                bibliography += f"{citation}\n\n"

        return bibliography

    def validate_citations(
        self,
        citations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate citation completeness and identify missing information.

        Args:
            citations: List of citation dicts to validate

        Returns:
            Validation report with issues and recommendations
        """
        issues = []
        incomplete_citations = []

        for i, citation in enumerate(citations):
            citation_issues = []

            # Check required fields
            if not citation.get('authors'):
                citation_issues.append("Missing author information")
            if not citation.get('year'):
                citation_issues.append("Missing publication year")
            if not citation.get('title'):
                citation_issues.append("Missing title")

            # Check source-type specific requirements
            source_type = citation.get('source_type', '')

            if source_type == 'article':
                if not citation.get('publication'):
                    citation_issues.append("Missing journal/publication name")
            elif source_type == 'book':
                if not citation.get('publisher'):
                    citation_issues.append("Missing publisher information")
            elif source_type == 'website':
                if not citation.get('url'):
                    citation_issues.append("Missing URL")
                if not citation.get('access_date'):
                    citation_issues.append("Missing access date")

            if citation_issues:
                incomplete_citations.append({
                    "citation_index": i,
                    "raw_text": citation.get('raw_text', ''),
                    "issues": citation_issues
                })

        return {
            "total_citations": len(citations),
            "valid_citations": len(citations) - len(incomplete_citations),
            "incomplete_citations": len(incomplete_citations),
            "issues": incomplete_citations,
            "validation_passed": len(incomplete_citations) == 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    def create_citation_metadata(
        self,
        source_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create structured citation metadata from source information.

        Args:
            source_info: Raw source information

        Returns:
            Structured citation metadata dict
        """
        return {
            "authors": source_info.get('authors', 'Unknown'),
            "year": source_info.get('year', 'n.d.'),
            "title": source_info.get('title', 'Untitled'),
            "source_type": source_info.get('source_type', 'misc'),
            "publication": source_info.get('publication', ''),
            "volume": source_info.get('volume', ''),
            "issue": source_info.get('issue', ''),
            "pages": source_info.get('pages', ''),
            "publisher": source_info.get('publisher', ''),
            "doi": source_info.get('doi', ''),
            "url": source_info.get('url', ''),
            "access_date": source_info.get('access_date', ''),
            "chapter_number": source_info.get('chapter_number', None),
            "created_at": datetime.utcnow().isoformat()
        }

    def merge_duplicate_citations(
        self,
        citations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify and merge duplicate citations.

        Args:
            citations: List of citation dicts

        Returns:
            Deduplicated list of citations
        """
        unique_citations = {}

        for citation in citations:
            # Create key from author + year + title
            key = (
                citation.get('authors', '').lower(),
                str(citation.get('year', '')),
                citation.get('title', '').lower()[:50]
            )

            if key in unique_citations:
                # Merge chapter numbers
                existing = unique_citations[key]
                existing_chapters = existing.get('chapter_numbers', [])
                new_chapter = citation.get('chapter_number')

                if new_chapter and new_chapter not in existing_chapters:
                    existing_chapters.append(new_chapter)
                    existing['chapter_numbers'] = existing_chapters
            else:
                citation['chapter_numbers'] = [citation.get('chapter_number')] if citation.get('chapter_number') else []
                unique_citations[key] = citation

        return list(unique_citations.values())

    # Helper methods

    def _parse_extracted_citations(
        self,
        response: str,
        chapter_number: int
    ) -> List[Dict[str, Any]]:
        """Parse extracted citations from LLM response."""
        citations = []
        current_citation = None

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()

            if line.startswith('Citation '):
                if current_citation:
                    current_citation['chapter_number'] = chapter_number
                    citations.append(current_citation)

                current_citation = {
                    "authors": "",
                    "year": "",
                    "title": "",
                    "source_type": "misc",
                    "raw_text": ""
                }

            elif current_citation:
                if line.startswith('Type:'):
                    current_citation['citation_type'] = line.replace('Type:', '').strip()
                elif line.startswith('Authors:'):
                    current_citation['authors'] = line.replace('Authors:', '').strip()
                elif line.startswith('Year:'):
                    current_citation['year'] = line.replace('Year:', '').strip()
                elif line.startswith('Title:'):
                    current_citation['title'] = line.replace('Title:', '').strip()
                elif line.startswith('Source Type:'):
                    current_citation['source_type'] = line.replace('Source Type:', '').strip()
                elif line.startswith('Raw Text:'):
                    current_citation['raw_text'] = line.replace('Raw Text:', '').strip()

        if current_citation:
            current_citation['chapter_number'] = chapter_number
            citations.append(current_citation)

        return citations


def bibliography_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for Bibliography agent.

    This node processes draft content to extract and manage citations.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with bibliography data
    """
    agent = BibliographyAgent()

    # Extract current draft and chapter number
    current_draft = state.get('current_draft', '')
    chapter_number = state.get('chapter_number', 1)
    book_metadata = state.get('book_metadata', {})

    # Extract citations from draft
    citations = agent.extract_citations_from_text(current_draft, chapter_number)

    # Validate citations
    validation_report = agent.validate_citations(citations)

    # Generate bibliography
    citation_style = book_metadata.get('citation_style', settings.default_citation_style)
    bibliography_text = agent.generate_bibliography(citations, citation_style, chapter_number)

    # Return partial state update
    return {
        "conversation_history": [{
            "agent": "bibliography",
            "action": "citation_extraction",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "chapter_number": chapter_number,
                "citations_found": len(citations),
                "validation_passed": validation_report['validation_passed'],
                "citation_style": citation_style
            }
        }]
    }
