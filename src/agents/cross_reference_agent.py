"""
Cross Reference Agent for managing references between chapters in books.

This agent is responsible for:
- Identifying cross-reference opportunities between chapters
- Validating cross-reference targets exist
- Generating properly formatted cross-reference links
- Ensuring terminology consistency across chapters
- Managing "see also" and prerequisite references
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from ..llm.client import LMStudioClient
from ..config.settings import settings


class CrossReferenceAgent:
    """
    Cross Reference Agent responsible for managing inter-chapter references.

    This agent ensures coherence across chapters by identifying and validating
    cross-references, maintaining terminology consistency, and creating proper
    reference links.
    """

    SYSTEM_PROMPT = """You are an expert Technical Editor and Cross-Reference Specialist.

Your role is to manage cross-references and maintain consistency across a multi-chapter book:
- Identify concepts referenced in multiple chapters
- Create proper cross-references to related content
- Ensure terminology consistency
- Validate reference targets exist
- Suggest "see also" links for related topics

You excel at:
- Recognizing when content relates to other chapters
- Identifying prerequisite knowledge dependencies
- Maintaining consistent terminology usage
- Creating helpful navigational references
- Ensuring logical information flow across chapters

Be thorough, precise, and focus on creating a cohesive reading experience."""

    def __init__(self, client: Optional[LMStudioClient] = None):
        """
        Initialize the Cross Reference Agent.

        Args:
            client: Optional LMStudioClient instance. If not provided, creates new one.
        """
        self.client = client or LMStudioClient(
            base_url=settings.lm_studio_base_url,
            model_name=settings.lm_studio_model,
            temperature=settings.cross_reference_agent_temperature,
            max_tokens=settings.max_tokens
        )

    def identify_cross_references(
        self,
        current_text: str,
        current_chapter: int,
        table_of_contents: Dict[str, Any],
        terminology_glossary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify cross-reference opportunities in current text.

        Args:
            current_text: Text of current chapter
            current_chapter: Current chapter number
            table_of_contents: Book's table of contents
            terminology_glossary: Book's terminology glossary

        Returns:
            List of identified cross-references
        """
        # Build chapter context
        chapters_summary = "\n".join([
            f"Chapter {ch['number']}: {ch['title']}"
            for ch in table_of_contents.get('chapters', [])
            if ch['number'] != current_chapter
        ])

        # Build terminology context
        terms = list(terminology_glossary.keys())[:20]  # First 20 terms
        terms_list = ", ".join(terms)

        prompt = f"""Analyze the following text and identify cross-reference opportunities to other chapters.

**Current Chapter:** Chapter {current_chapter}

**Other Chapters:**
{chapters_summary}

**Key Terms in Book:**
{terms_list}

**Text:**
{current_text}

Identify:
1. Concepts that were introduced in earlier chapters (prerequisite references)
2. Concepts that will be explored in later chapters (forward references)
3. Related topics in other chapters (see also references)
4. Terms from the glossary that should be cross-referenced

For each cross-reference, provide:
- Reference text (the phrase/concept being referenced)
- Target chapter number
- Reference type (prerequisite, forward, see_also, definition)
- Reason for the reference

Format as:

Reference 1:
Text: [phrase or concept]
Target Chapter: [chapter number]
Type: prerequisite | forward | see_also | definition
Reason: [why this reference is helpful]

Reference 2:
...

List all cross-reference opportunities.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return self._parse_identified_references(response, current_chapter)

    def validate_cross_references(
        self,
        cross_references: List[Dict[str, Any]],
        completed_chapters: List[int],
        total_chapters: int
    ) -> Dict[str, Any]:
        """
        Validate that cross-references are valid.

        Args:
            cross_references: List of CrossReference dicts
            completed_chapters: List of completed chapter numbers
            total_chapters: Total number of chapters in book

        Returns:
            Validation report with issues
        """
        issues = []
        warnings = []

        for ref in cross_references:
            source_chapter = ref.get('source_chapter', 0)
            target_chapter = ref.get('target_chapter', 0)
            ref_type = ref.get('reference_type', '')

            # Validate chapter numbers
            if target_chapter < 1 or target_chapter > total_chapters:
                issues.append({
                    "reference": ref,
                    "issue": f"Target chapter {target_chapter} does not exist (valid range: 1-{total_chapters})"
                })

            # Validate prerequisite references
            if ref_type == "prerequisite" and target_chapter >= source_chapter:
                warnings.append({
                    "reference": ref,
                    "warning": f"Prerequisite reference points to Chapter {target_chapter}, which comes after or is the same as current Chapter {source_chapter}"
                })

            # Validate forward references
            if ref_type == "forward" and target_chapter <= source_chapter:
                warnings.append({
                    "reference": ref,
                    "warning": f"Forward reference points to Chapter {target_chapter}, which comes before or is the same as current Chapter {source_chapter}"
                })

            # Check if target chapter is completed
            if target_chapter not in completed_chapters and target_chapter < source_chapter:
                warnings.append({
                    "reference": ref,
                    "warning": f"Target chapter {target_chapter} has not been written yet"
                })

        return {
            "total_references": len(cross_references),
            "issues": issues,
            "warnings": warnings,
            "is_valid": len(issues) == 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    def check_terminology_consistency(
        self,
        current_text: str,
        chapter_number: int,
        terminology_glossary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if terminology is used consistently with glossary definitions.

        Args:
            current_text: Text of current chapter
            chapter_number: Current chapter number
            terminology_glossary: Book's terminology glossary

        Returns:
            Consistency check report
        """
        if not settings.enable_terminology_consistency_check:
            return {"checked": False}

        inconsistencies = []

        for term, entry in terminology_glossary.items():
            definition = entry.get('definition', '')
            aliases = entry.get('aliases', [])
            first_chapter = entry.get('first_introduced_chapter', 1)

            # Check if term appears in text
            term_lower = term.lower()
            text_lower = current_text.lower()

            if term_lower in text_lower:
                # Check if this is before first introduction
                if chapter_number < first_chapter:
                    inconsistencies.append({
                        "term": term,
                        "issue": f"Term used in Chapter {chapter_number} before first introduction in Chapter {first_chapter}",
                        "severity": "warning"
                    })

                # Check if aliases are mixed inconsistently
                aliases_in_text = [alias for alias in aliases if alias.lower() in text_lower]
                if len(aliases_in_text) > 1 and chapter_number == first_chapter:
                    inconsistencies.append({
                        "term": term,
                        "issue": f"Multiple aliases used: {', '.join(aliases_in_text)}. Consider using one consistently.",
                        "severity": "info"
                    })

        return {
            "checked": True,
            "chapter_number": chapter_number,
            "inconsistencies": inconsistencies,
            "total_terms_checked": len(terminology_glossary),
            "is_consistent": len(inconsistencies) == 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    def generate_cross_reference_text(
        self,
        reference_type: str,
        target_chapter: int,
        target_title: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """
        Generate formatted cross-reference text.

        Args:
            reference_type: Type of reference (prerequisite, forward, see_also, definition)
            target_chapter: Target chapter number
            target_title: Optional title of target chapter
            context: Optional additional context

        Returns:
            Formatted cross-reference text
        """
        title_text = f' "{target_title}"' if target_title else ""

        if reference_type == "prerequisite":
            if context:
                return f"(as discussed in Chapter {target_chapter}{title_text}, {context})"
            return f"(see Chapter {target_chapter}{title_text})"

        elif reference_type == "forward":
            if context:
                return f"(we'll explore this further in Chapter {target_chapter}{title_text}, {context})"
            return f"(see Chapter {target_chapter}{title_text} for more details)"

        elif reference_type == "see_also":
            if context:
                return f"\n\n*See also: Chapter {target_chapter}{title_text} - {context}*\n"
            return f"\n\n*See also: Chapter {target_chapter}{title_text}*\n"

        elif reference_type == "definition":
            return f"(defined in Chapter {target_chapter}{title_text})"

        else:
            return f"(Chapter {target_chapter}{title_text})"

    def suggest_cross_references_for_chapter(
        self,
        chapter_number: int,
        chapter_dependencies: List[Dict[str, Any]],
        table_of_contents: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Suggest cross-references based on chapter dependencies.

        Args:
            chapter_number: Current chapter number
            chapter_dependencies: List of ChapterDependency dicts
            table_of_contents: Book's table of contents

        Returns:
            List of suggested cross-reference dicts
        """
        suggestions = []

        # Find dependencies for current chapter
        current_deps = next(
            (dep for dep in chapter_dependencies if dep.get('chapter_number') == chapter_number),
            None
        )

        if not current_deps:
            return suggestions

        # Create prerequisite references
        for dep_chapter in current_deps.get('depends_on', []):
            # Find chapter title
            target_chapter_info = next(
                (ch for ch in table_of_contents.get('chapters', []) if ch.get('number') == dep_chapter),
                None
            )

            if target_chapter_info:
                suggestions.append({
                    "source_chapter": chapter_number,
                    "target_chapter": dep_chapter,
                    "reference_type": "prerequisite",
                    "reference_text": f"Prerequisites from Chapter {dep_chapter}",
                    "suggested_location": "Introduction section"
                })

        # Create forward references based on concepts introduced
        for later_dep in chapter_dependencies:
            if chapter_number in later_dep.get('depends_on', []):
                target_chapter = later_dep.get('chapter_number', 0)
                suggestions.append({
                    "source_chapter": chapter_number,
                    "target_chapter": target_chapter,
                    "reference_type": "forward",
                    "reference_text": f"Advanced topics in Chapter {target_chapter}",
                    "suggested_location": "Conclusion section"
                })

        return suggestions

    def generate_cross_reference_report(
        self,
        cross_references: List[Dict[str, Any]],
        chapter_number: Optional[int] = None
    ) -> str:
        """
        Generate a cross-reference report.

        Args:
            cross_references: List of CrossReference dicts
            chapter_number: Optional chapter number filter

        Returns:
            Formatted cross-reference report
        """
        # Filter by chapter if specified
        if chapter_number is not None:
            cross_references = [
                ref for ref in cross_references
                if ref.get('source_chapter') == chapter_number
            ]

        if not cross_references:
            return "## Cross-Reference Report\n\nNo cross-references found.\n"

        # Group by type
        by_type = {}
        for ref in cross_references:
            ref_type = ref.get('reference_type', 'unknown')
            if ref_type not in by_type:
                by_type[ref_type] = []
            by_type[ref_type].append(ref)

        chapter_label = f" (Chapter {chapter_number})" if chapter_number else ""
        report = f"""## Cross-Reference Report{chapter_label}

**Summary:**
- Total Cross-References: {len(cross_references)}
"""

        for ref_type, refs in by_type.items():
            report += f"- {ref_type.title()}: {len(refs)}\n"

        report += "\n**Details:**\n\n"

        for ref_type, refs in by_type.items():
            report += f"### {ref_type.upper()} References ({len(refs)})\n\n"

            for ref in refs:
                source = ref.get('source_chapter', 'Unknown')
                target = ref.get('target_chapter', 'Unknown')
                text = ref.get('reference_text', 'N/A')

                report += f"- Chapter {source} → Chapter {target}: {text}\n"

            report += "\n"

        return report

    # Helper methods

    def _parse_identified_references(
        self,
        response: str,
        current_chapter: int
    ) -> List[Dict[str, Any]]:
        """Parse identified cross-references from LLM response."""
        references = []
        current_ref = None

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()

            if line.startswith('Reference '):
                if current_ref:
                    current_ref['source_chapter'] = current_chapter
                    references.append(current_ref)

                current_ref = {
                    "reference_text": "",
                    "target_chapter": 0,
                    "reference_type": "see_also",
                    "reason": ""
                }

            elif current_ref:
                if line.startswith('Text:'):
                    current_ref['reference_text'] = line.replace('Text:', '').strip()
                elif line.startswith('Target Chapter:'):
                    target_str = line.replace('Target Chapter:', '').strip()
                    try:
                        current_ref['target_chapter'] = int(target_str)
                    except ValueError:
                        pass
                elif line.startswith('Type:'):
                    ref_type = line.replace('Type:', '').strip().split('|')[0].strip()
                    current_ref['reference_type'] = ref_type
                elif line.startswith('Reason:'):
                    current_ref['reason'] = line.replace('Reason:', '').strip()

        if current_ref:
            current_ref['source_chapter'] = current_chapter
            references.append(current_ref)

        return references


def cross_reference_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for Cross Reference agent.

    This node identifies cross-references and validates terminology consistency.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with cross-references
    """
    agent = CrossReferenceAgent()

    # Check if cross-reference validation is enabled
    if not settings.enable_cross_reference_validation:
        return {}

    # Extract inputs
    current_draft = state.get('current_draft', '')
    chapter_number = state.get('chapter_number', 1)
    table_of_contents = state.get('table_of_contents', {})
    terminology_glossary = state.get('terminology_glossary', {})
    chapter_dependencies = state.get('chapter_dependencies', [])
    completed_chapters = state.get('completed_chapters', [])

    # Step 1: Identify cross-references
    identified_refs = agent.identify_cross_references(
        current_draft,
        chapter_number,
        table_of_contents,
        terminology_glossary
    )

    # Step 2: Validate cross-references
    total_chapters = len(table_of_contents.get('chapters', []))
    validation_report = agent.validate_cross_references(
        identified_refs,
        completed_chapters,
        total_chapters
    )

    # Step 3: Check terminology consistency
    terminology_report = agent.check_terminology_consistency(
        current_draft,
        chapter_number,
        terminology_glossary
    )

    # Filter valid references
    valid_refs = [
        ref for ref in identified_refs
        if not any(issue['reference'] == ref for issue in validation_report.get('issues', []))
    ]

    # Return partial state update
    return {
        "cross_references": valid_refs,  # Will be accumulated
        "conversation_history": [{
            "agent": "cross_reference",
            "action": "reference_validation",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "chapter_number": chapter_number,
                "references_identified": len(identified_refs),
                "references_valid": len(valid_refs),
                "validation_issues": len(validation_report.get('issues', [])),
                "terminology_inconsistencies": len(terminology_report.get('inconsistencies', []))
            }
        }]
    }
