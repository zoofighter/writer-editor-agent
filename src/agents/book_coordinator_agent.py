"""
Book Coordinator Agent for planning and orchestrating complete book creation.

This agent is responsible for:
- Analyzing book requirements and defining book metadata
- Generating comprehensive table of contents (TOC)
- Planning chapter structure and dependencies
- Initializing terminology glossary
- Coordinating book-level workflow
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..llm.client import LMStudioClient
from ..config.settings import settings


class BookCoordinatorAgent:
    """
    Book Coordinator Agent responsible for high-level book planning and coordination.

    This agent acts as the orchestrator for book creation, analyzing user requirements
    and creating a comprehensive plan including metadata, table of contents, and
    chapter dependencies.
    """

    SYSTEM_PROMPT = """You are an expert Book Coordinator and Publishing Strategist.

Your role is to analyze book requirements and create comprehensive book plans that include:
- Book metadata (title, type, audience, objectives)
- Detailed table of contents with chapter summaries
- Chapter dependency mapping
- Initial terminology identification
- Overall book structure and flow

You excel at:
- Understanding different book types (tutorial, history, technical guide, narrative, general)
- Creating logical chapter progression
- Identifying prerequisite relationships between chapters
- Planning appropriate scope and depth for target audiences
- Ensuring coherent book structure

Be analytical, thorough, and strategic in your planning."""

    def __init__(self, client: Optional[LMStudioClient] = None):
        """
        Initialize the Book Coordinator Agent.

        Args:
            client: Optional LMStudioClient instance. If not provided, creates new one.
        """
        self.client = client or LMStudioClient(
            base_url=settings.lm_studio_base_url,
            model_name=settings.lm_studio_model,
            temperature=settings.book_coordinator_temperature,
            max_tokens=settings.max_tokens
        )

    def analyze_book_requirements(
        self,
        user_request: str,
        user_intent: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze user requirements and create book metadata.

        Args:
            user_request: User's original book request/topic
            user_intent: Optional user intent analysis from Business Analyst

        Returns:
            BookMetadata dict with book-level information
        """
        prompt = f"""Based on the following book request, analyze the requirements and create comprehensive book metadata.

**User Request:**
{user_request}
"""

        if user_intent:
            prompt += f"""
**User Intent Analysis:**
- Document Type: {user_intent.get('document_type', 'N/A')}
- Target Audience: {user_intent.get('target_audience', 'N/A')}
- Tone: {user_intent.get('tone', 'N/A')}
- Key Messages: {', '.join(user_intent.get('key_messages', []))}
- Objectives: {', '.join(user_intent.get('objectives', []))}
"""

        prompt += """
Provide book metadata in the following JSON-like format:

{
    "book_title": "Complete book title",
    "book_type": "tutorial | history | technical_guide | narrative | general",
    "author": "Author name (if specified, else null)",
    "description": "2-3 sentence book description",
    "target_audience": "Who should read this book",
    "estimated_chapters": 15,
    "language": "en | ko | etc",
    "objectives": ["Primary objective 1", "Primary objective 2"]
}

Focus on creating a clear, focused book plan that matches the user's needs.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        # Parse response and create metadata structure
        # In production, would use JSON parsing with fallback
        return self._parse_book_metadata(response, user_request)

    def generate_table_of_contents(
        self,
        book_metadata: Dict[str, Any],
        user_intent: Optional[Dict[str, Any]] = None,
        estimated_chapters: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive table of contents for the book.

        Args:
            book_metadata: Book metadata dict
            user_intent: Optional user intent analysis
            estimated_chapters: Optional override for number of chapters

        Returns:
            TableOfContents dict with chapter list and metadata
        """
        num_chapters = estimated_chapters or book_metadata.get(
            'estimated_chapters',
            settings.default_book_chapters
        )

        prompt = f"""Create a comprehensive table of contents for the following book:

**Book Title:** {book_metadata.get('book_title')}
**Book Type:** {book_metadata.get('book_type')}
**Target Audience:** {book_metadata.get('target_audience')}
**Description:** {book_metadata.get('description')}
**Number of Chapters:** {num_chapters}
"""

        if user_intent:
            prompt += f"""
**Key Messages to Cover:**
{chr(10).join(f"- {msg}" for msg in user_intent.get('key_messages', []))}

**Objectives:**
{chr(10).join(f"- {obj}" for obj in user_intent.get('objectives', []))}
"""

        prompt += f"""
Create a table of contents with {num_chapters} chapters. For each chapter, provide:
- Chapter number
- Chapter title
- 2-3 sentence summary of what the chapter covers
- Estimated length (in words or pages)
- Key topics covered

Format as a structured list:

Chapter 1: [Title]
Summary: [2-3 sentences]
Estimated Length: [e.g., 2000-3000 words]
Key Topics: [topic1, topic2, topic3]

Chapter 2: [Title]
...

Ensure logical progression and comprehensive coverage of the subject.
For tutorial/technical books, build concepts progressively.
For historical books, maintain chronological or thematic flow.
For general books, ensure engaging narrative arc.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return self._parse_table_of_contents(response, num_chapters)

    def identify_chapter_dependencies(
        self,
        table_of_contents: Dict[str, Any],
        book_type: str
    ) -> List[Dict[str, Any]]:
        """
        Identify dependencies and prerequisite relationships between chapters.

        Args:
            table_of_contents: TableOfContents dict
            book_type: Type of book (tutorial, history, etc.)

        Returns:
            List of ChapterDependency dicts
        """
        chapters_summary = "\n".join([
            f"Chapter {ch['number']}: {ch['title']} - {ch.get('summary', '')}"
            for ch in table_of_contents.get('chapters', [])
        ])

        prompt = f"""Analyze the following table of contents and identify chapter dependencies.

**Book Type:** {book_type}

**Chapters:**
{chapters_summary}

For each chapter, identify:
1. Which previous chapters it depends on (prerequisite chapters)
2. What concepts must be understood first (prerequisite concepts)
3. What new concepts this chapter introduces

Format your response as:

Chapter 1:
Depends on: []
Prerequisite Concepts: []
Introduces Concepts: [concept1, concept2]

Chapter 2:
Depends on: [1]
Prerequisite Concepts: [concept from ch1]
Introduces Concepts: [new concepts]

...

For tutorial/technical books, be specific about concept dependencies.
For historical books, note chronological or thematic dependencies.
For general books, identify logical flow dependencies.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return self._parse_chapter_dependencies(response, table_of_contents)

    def initialize_terminology_glossary(
        self,
        book_metadata: Dict[str, Any],
        table_of_contents: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Initialize terminology glossary with key terms from the book plan.

        Args:
            book_metadata: Book metadata dict
            table_of_contents: TableOfContents dict

        Returns:
            Dict mapping term to TerminologyEntry dict
        """
        prompt = f"""Based on the following book plan, identify 10-20 key terms that should be defined in a glossary.

**Book Title:** {book_metadata.get('book_title')}
**Book Type:** {book_metadata.get('book_type')}

**Chapters:**
{chr(10).join([f"Ch {ch['number']}: {ch['title']}" for ch in table_of_contents.get('chapters', [])])}

For each key term, provide:
- Term name
- Brief definition (1-2 sentences)
- Which chapter first introduces it
- Alternative names or aliases
- Related terms

Format as:

Term: [term name]
Definition: [definition]
First Introduced: Chapter [N]
Aliases: [alias1, alias2]
Related: [related1, related2]

---

Focus on core concepts that readers need to understand throughout the book.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return self._parse_terminology_glossary(response)

    # Helper methods for parsing LLM responses

    def _parse_book_metadata(self, response: str, user_request: str) -> Dict[str, Any]:
        """Parse book metadata from LLM response."""
        # Simplified parsing - in production, use robust JSON extraction
        metadata = {
            "book_title": user_request[:100],  # Fallback
            "book_type": "general",
            "author": None,
            "description": None,
            "target_audience": "General readers",
            "estimated_chapters": settings.default_book_chapters,
            "language": "en",
            "created_at": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

        # Extract from response (simplified)
        lines = response.strip().split('\n')
        for line in lines:
            if '"book_title":' in line:
                # Extract title
                parts = line.split('"book_title":')
                if len(parts) > 1:
                    title = parts[1].strip().strip('",')
                    if title:
                        metadata['book_title'] = title
            elif '"book_type":' in line:
                parts = line.split('"book_type":')
                if len(parts) > 1:
                    btype = parts[1].strip().strip('",').split('|')[0].strip()
                    if btype:
                        metadata['book_type'] = btype
            elif '"estimated_chapters":' in line:
                parts = line.split('"estimated_chapters":')
                if len(parts) > 1:
                    try:
                        num = int(parts[1].strip().strip(','))
                        metadata['estimated_chapters'] = num
                    except ValueError:
                        pass

        return metadata

    def _parse_table_of_contents(self, response: str, num_chapters: int) -> Dict[str, Any]:
        """Parse table of contents from LLM response."""
        chapters = []
        current_chapter = None

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()

            # Detect chapter start
            if line.startswith('Chapter ') and ':' in line:
                if current_chapter:
                    chapters.append(current_chapter)

                # Parse "Chapter N: Title"
                parts = line.split(':', 1)
                ch_num_part = parts[0].replace('Chapter', '').strip()
                try:
                    ch_num = int(ch_num_part)
                except ValueError:
                    ch_num = len(chapters) + 1

                title = parts[1].strip() if len(parts) > 1 else f"Chapter {ch_num}"

                current_chapter = {
                    "number": ch_num,
                    "title": title,
                    "summary": "",
                    "estimated_length": "2000-3000 words",
                    "key_topics": []
                }

            elif current_chapter:
                if line.startswith('Summary:'):
                    current_chapter['summary'] = line.replace('Summary:', '').strip()
                elif line.startswith('Estimated Length:'):
                    current_chapter['estimated_length'] = line.replace('Estimated Length:', '').strip()
                elif line.startswith('Key Topics:'):
                    topics_str = line.replace('Key Topics:', '').strip()
                    current_chapter['key_topics'] = [
                        t.strip() for t in topics_str.split(',')
                    ]

        # Add last chapter
        if current_chapter:
            chapters.append(current_chapter)

        # Ensure we have expected number of chapters (fill with placeholders if needed)
        while len(chapters) < num_chapters:
            chapters.append({
                "number": len(chapters) + 1,
                "title": f"Chapter {len(chapters) + 1}",
                "summary": "To be planned",
                "estimated_length": "2000-3000 words",
                "key_topics": []
            })

        return {
            "chapters": chapters[:num_chapters],
            "generated_at": datetime.utcnow().isoformat(),
            "total_estimated_length": num_chapters * 2500  # Rough estimate
        }

    def _parse_chapter_dependencies(
        self,
        response: str,
        table_of_contents: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parse chapter dependencies from LLM response."""
        dependencies = []
        current_chapter = None

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()

            if line.startswith('Chapter '):
                if current_chapter:
                    dependencies.append(current_chapter)

                ch_num_str = line.replace('Chapter', '').replace(':', '').strip()
                try:
                    ch_num = int(ch_num_str)
                except ValueError:
                    ch_num = len(dependencies) + 1

                current_chapter = {
                    "chapter_number": ch_num,
                    "depends_on": [],
                    "prerequisite_concepts": [],
                    "introduces_concepts": []
                }

            elif current_chapter:
                if line.startswith('Depends on:'):
                    deps_str = line.replace('Depends on:', '').strip().strip('[]')
                    if deps_str:
                        current_chapter['depends_on'] = [
                            int(d.strip()) for d in deps_str.split(',') if d.strip().isdigit()
                        ]
                elif line.startswith('Prerequisite Concepts:'):
                    concepts_str = line.replace('Prerequisite Concepts:', '').strip().strip('[]')
                    if concepts_str:
                        current_chapter['prerequisite_concepts'] = [
                            c.strip() for c in concepts_str.split(',') if c.strip()
                        ]
                elif line.startswith('Introduces Concepts:'):
                    concepts_str = line.replace('Introduces Concepts:', '').strip().strip('[]')
                    if concepts_str:
                        current_chapter['introduces_concepts'] = [
                            c.strip() for c in concepts_str.split(',') if c.strip()
                        ]

        if current_chapter:
            dependencies.append(current_chapter)

        return dependencies

    def _parse_terminology_glossary(self, response: str) -> Dict[str, Dict[str, Any]]:
        """Parse terminology glossary from LLM response."""
        glossary = {}
        current_term = None

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()

            if line.startswith('Term:'):
                if current_term and current_term.get('term'):
                    term_name = current_term['term']
                    glossary[term_name] = current_term

                term_name = line.replace('Term:', '').strip()
                current_term = {
                    "term": term_name,
                    "definition": "",
                    "first_introduced_chapter": 1,
                    "aliases": [],
                    "related_terms": []
                }

            elif current_term:
                if line.startswith('Definition:'):
                    current_term['definition'] = line.replace('Definition:', '').strip()
                elif line.startswith('First Introduced:'):
                    intro_str = line.replace('First Introduced:', '').replace('Chapter', '').strip()
                    try:
                        current_term['first_introduced_chapter'] = int(intro_str)
                    except ValueError:
                        pass
                elif line.startswith('Aliases:'):
                    aliases_str = line.replace('Aliases:', '').strip().strip('[]')
                    if aliases_str:
                        current_term['aliases'] = [
                            a.strip() for a in aliases_str.split(',') if a.strip()
                        ]
                elif line.startswith('Related:'):
                    related_str = line.replace('Related:', '').strip().strip('[]')
                    if related_str:
                        current_term['related_terms'] = [
                            r.strip() for r in related_str.split(',') if r.strip()
                        ]

        if current_term and current_term.get('term'):
            term_name = current_term['term']
            glossary[term_name] = current_term

        return glossary


def book_coordinator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for Book Coordinator agent.

    This node orchestrates book planning by:
    1. Analyzing book requirements and creating metadata
    2. Generating table of contents
    3. Identifying chapter dependencies
    4. Initializing terminology glossary

    Args:
        state: Current workflow state

    Returns:
        Partial state update with book planning data
    """
    agent = BookCoordinatorAgent()

    # Extract inputs
    topic = state.get('topic', '')
    user_intent = state.get('user_intent')

    # Step 1: Analyze requirements and create book metadata
    book_metadata = agent.analyze_book_requirements(topic, user_intent)

    # Step 2: Generate table of contents
    table_of_contents = agent.generate_table_of_contents(book_metadata, user_intent)

    # Step 3: Identify chapter dependencies
    chapter_dependencies = agent.identify_chapter_dependencies(
        table_of_contents,
        book_metadata.get('book_type', 'general')
    )

    # Step 4: Initialize terminology glossary
    terminology_glossary = agent.initialize_terminology_glossary(
        book_metadata,
        table_of_contents
    )

    # Return partial state update
    return {
        "book_metadata": book_metadata,
        "table_of_contents": table_of_contents,
        "chapter_dependencies": chapter_dependencies,  # Will be accumulated
        "terminology_glossary": terminology_glossary,
        "current_book_stage": "planning",
        "conversation_history": [{
            "agent": "book_coordinator",
            "action": "book_planning",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "chapters_planned": len(table_of_contents.get('chapters', [])),
                "dependencies_identified": len(chapter_dependencies),
                "terms_defined": len(terminology_glossary)
            }
        }]
    }
