"""
Tutorial Export Manager for saving tutorial chapters as markdown files.

Handles exporting complete chapters with code examples, exercises, and metadata
to properly formatted markdown files suitable for tutorial books.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import re


class TutorialExportManager:
    """
    Manages export of tutorial chapters to markdown format.

    Creates well-structured markdown files with:
    - YAML frontmatter for metadata
    - Proper heading hierarchy
    - Formatted code blocks
    - Collapsible exercise answers
    """

    def __init__(self, output_dir: str = "output/tutorial"):
        """
        Initialize the export manager.

        Args:
            output_dir: Directory where chapters will be exported

        Example:
            >>> manager = TutorialExportManager("output/tutorial")
            >>> manager.output_dir.exists()
            True
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_chapter(
        self,
        chapter_number: int,
        chapter_title: str,
        content: str,
        exercises: Optional[Dict[str, Any]] = None,
        code_examples: Optional[Dict[str, List[str]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Export a single chapter to a markdown file.

        Args:
            chapter_number: Chapter number (for file naming)
            chapter_title: Chapter title
            content: Main chapter content (markdown)
            exercises: Chapter exercises (MC, fill-in-blank, coding challenges)
            code_examples: Code examples by section
            metadata: Additional metadata (learning objectives, etc.)

        Returns:
            Path to the exported file

        Example:
            >>> manager = TutorialExportManager()
            >>> path = manager.export_chapter(
            ...     chapter_number=1,
            ...     chapter_title="Variables and Data Types",
            ...     content="# Variables\\n\\nContent here...",
            ...     exercises={"multiple_choice": [...], ...}
            ... )
            >>> path.exists()
            True
        """
        # Generate filename
        slug = self._create_slug(chapter_title)
        filename = f"chapter-{chapter_number:02d}-{slug}.md"
        filepath = self.output_dir / filename

        # Build markdown content
        markdown_parts = []

        # YAML frontmatter
        markdown_parts.append(self._generate_frontmatter(
            chapter_number=chapter_number,
            chapter_title=chapter_title,
            metadata=metadata
        ))

        # Main chapter content
        markdown_parts.append(content)

        # Code examples section (if separate from content)
        if code_examples:
            markdown_parts.append("\n---\n")
            markdown_parts.append(self._format_code_examples_section(code_examples))

        # Exercises section
        if exercises:
            markdown_parts.append("\n---\n")
            markdown_parts.append(self._format_exercises_section(exercises))

        # Write to file
        full_markdown = "\n\n".join(markdown_parts)
        filepath.write_text(full_markdown, encoding='utf-8')

        return filepath

    def _create_slug(self, title: str) -> str:
        """
        Create URL-friendly slug from title.

        Args:
            title: Chapter title

        Returns:
            Slugified string

        Example:
            >>> manager = TutorialExportManager()
            >>> manager._create_slug("Variables & Data Types")
            'variables-data-types'
        """
        # Convert to lowercase
        slug = title.lower()
        # Remove special characters, replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')
        return slug

    def _generate_frontmatter(
        self,
        chapter_number: int,
        chapter_title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate YAML frontmatter for the markdown file.

        Args:
            chapter_number: Chapter number
            chapter_title: Chapter title
            metadata: Additional metadata

        Returns:
            YAML frontmatter string

        Example:
            >>> manager = TutorialExportManager()
            >>> fm = manager._generate_frontmatter(1, "Introduction")
            >>> assert "chapter: 1" in fm
        """
        meta = metadata or {}

        frontmatter = [
            "---",
            f"chapter: {chapter_number}",
            f"title: \"{chapter_title}\"",
            f"date: {datetime.now().strftime('%Y-%m-%d')}",
        ]

        # Add optional metadata
        if "learning_objectives" in meta:
            frontmatter.append("learning_objectives:")
            for obj in meta["learning_objectives"]:
                frontmatter.append(f"  - {obj}")

        if "prerequisites" in meta:
            frontmatter.append("prerequisites:")
            for prereq in meta["prerequisites"]:
                frontmatter.append(f"  - {prereq}")

        if "estimated_time" in meta:
            frontmatter.append(f"estimated_time: \"{meta['estimated_time']}\"")

        frontmatter.append("---")

        return "\n".join(frontmatter)

    def _format_code_examples_section(self, code_examples: Dict[str, List[str]]) -> str:
        """
        Format code examples as a separate section.

        Args:
            code_examples: Code examples by section ID

        Returns:
            Formatted markdown string

        Example:
            >>> manager = TutorialExportManager()
            >>> examples = {"intro": ["print('hi')"]}
            >>> formatted = manager._format_code_examples_section(examples)
            >>> assert "```python" in formatted
        """
        lines = ["## Code Examples"]

        for section_id, examples in code_examples.items():
            section_title = section_id.replace('_', ' ').title()
            lines.append(f"\n### {section_title}")

            for i, code in enumerate(examples, start=1):
                lines.append(f"\n**Example {i}:**\n")
                lines.append("```python")
                lines.append(code)
                lines.append("```")

        return "\n".join(lines)

    def _format_exercises_section(self, exercises: Dict[str, Any]) -> str:
        """
        Format exercises section with collapsible answers.

        Args:
            exercises: ChapterExercises dictionary

        Returns:
            Formatted markdown string with exercises

        Example:
            >>> manager = TutorialExportManager()
            >>> exercises = {
            ...     "multiple_choice": [{
            ...         "question": "What is 2+2?",
            ...         "options": ["3", "4", "5", "6"],
            ...         "correct_answer": 1,
            ...         "explanation": "2+2=4"
            ...     }]
            ... }
            >>> formatted = manager._format_exercises_section(exercises)
            >>> assert "## Practice Exercises" in formatted
        """
        lines = ["## Practice Exercises"]

        # Multiple choice questions
        mc_questions = exercises.get("multiple_choice", [])
        if mc_questions:
            lines.append("\n### Multiple Choice Questions")
            for i, q in enumerate(mc_questions, start=1):
                lines.append(f"\n**Question {i}:** {q['question']}")
                for j, option in enumerate(q['options']):
                    letter = chr(65 + j)  # A, B, C, D
                    lines.append(f"{letter}. {option}")

                # Collapsible answer
                lines.append("\n<details>")
                lines.append("<summary>Show Answer</summary>")
                lines.append("")
                correct_letter = chr(65 + q['correct_answer'])
                lines.append(f"**Answer:** {correct_letter}")
                lines.append(f"\n**Explanation:** {q['explanation']}")
                lines.append("</details>")

        # Fill-in-the-blank exercises
        fib_exercises = exercises.get("fill_in_blank", [])
        if fib_exercises:
            lines.append("\n### Fill in the Blank")
            for i, ex in enumerate(fib_exercises, start=1):
                lines.append(f"\n**Exercise {i}:** {ex['description']}")
                lines.append("\n```python")
                lines.append(ex['code_template'])
                lines.append("```")

                if ex.get('hint'):
                    lines.append(f"\n💡 *Hint: {ex['hint']}*")

                # Collapsible answer
                lines.append("\n<details>")
                lines.append("<summary>Show Answer</summary>")
                lines.append("")
                lines.append("```python")
                lines.append(ex['correct_answer'])
                lines.append("```")
                lines.append("</details>")

        # Coding challenges
        challenges = exercises.get("coding_challenges", [])
        if challenges:
            lines.append("\n### Coding Challenges")
            for i, ch in enumerate(challenges, start=1):
                lines.append(f"\n**Challenge {i}: {ch['title']}** ({ch['difficulty']})")
                lines.append(f"\n{ch['description']}")

                # Test cases
                if ch.get('test_cases'):
                    lines.append("\n**Test Cases:**")
                    for tc in ch['test_cases']:
                        lines.append(f"- Input: `{tc.get('input', 'N/A')}` → Output: `{tc.get('output', 'N/A')}`")

                # Starter code
                if ch.get('starter_code'):
                    lines.append("\n**Starter Code:**")
                    lines.append("```python")
                    lines.append(ch['starter_code'])
                    lines.append("```")

                # Hints
                if ch.get('hints'):
                    lines.append("\n<details>")
                    lines.append("<summary>Hints</summary>")
                    lines.append("")
                    for hint_num, hint in enumerate(ch['hints'], start=1):
                        lines.append(f"{hint_num}. {hint}")
                    lines.append("</details>")

                # Solution
                lines.append("\n<details>")
                lines.append("<summary>Show Solution</summary>")
                lines.append("")
                lines.append("```python")
                lines.append(ch['solution'])
                lines.append("```")
                lines.append("</details>")

        return "\n".join(lines)

    def list_exported_chapters(self) -> List[Path]:
        """
        List all exported chapter files.

        Returns:
            List of Path objects for chapter files

        Example:
            >>> manager = TutorialExportManager()
            >>> chapters = manager.list_exported_chapters()
            >>> all(ch.suffix == '.md' for ch in chapters)
            True
        """
        return sorted(self.output_dir.glob("chapter-*.md"))

    def get_chapter_path(self, chapter_number: int) -> Optional[Path]:
        """
        Get the path for a specific chapter number.

        Args:
            chapter_number: Chapter number to find

        Returns:
            Path to the chapter file, or None if not found

        Example:
            >>> manager = TutorialExportManager()
            >>> # After exporting chapter 1
            >>> path = manager.get_chapter_path(1)
            >>> path.name.startswith('chapter-01-')
            True
        """
        pattern = f"chapter-{chapter_number:02d}-*.md"
        matches = list(self.output_dir.glob(pattern))
        return matches[0] if matches else None


# Node function for LangGraph integration
def export_chapter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for exporting a tutorial chapter.

    Exports the final chapter with all content, code examples, and exercises
    to a markdown file.

    Args:
        state: Workflow state containing chapter content and exercises

    Returns:
        Updated state with export_path set

    Example:
        >>> state = {
        ...     "chapter_number": 1,
        ...     "topic": "Variables",
        ...     "current_draft": "# Variables\\n\\nContent...",
        ...     "code_examples_by_section": {...},
        ...     "chapter_exercises": {...}
        ... }
        >>> updated_state = export_chapter_node(state)
        >>> assert "export_path" in updated_state
    """
    from ..config.settings import settings

    # Initialize export manager
    output_dir = getattr(settings, 'tutorial_output_dir', 'output/tutorial')
    manager = TutorialExportManager(output_dir)

    # Extract data from state
    chapter_number = state.get("chapter_number", 1)
    topic = state.get("topic", "Python Tutorial")
    content = state.get("current_draft", "")
    code_examples = state.get("code_examples_by_section", {})
    exercises = state.get("chapter_exercises")
    metadata = state.get("chapter_metadata", {})

    # Add auto-generated metadata
    if not metadata:
        metadata = {}
    if "generated_date" not in metadata:
        metadata["generated_date"] = datetime.now().isoformat()

    try:
        # Export the chapter
        filepath = manager.export_chapter(
            chapter_number=chapter_number,
            chapter_title=topic,
            content=content,
            exercises=exercises,
            code_examples=code_examples,
            metadata=metadata
        )

        return {
            "export_path": str(filepath),
            "conversation_history": [{
                "role": "system",
                "content": f"Chapter {chapter_number} exported to {filepath.name}",
                "timestamp": datetime.now().isoformat()
            }]
        }

    except Exception as e:
        print(f"Error exporting chapter: {e}")
        return {
            "export_path": None,
            "conversation_history": [{
                "role": "system",
                "content": f"Export failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }]
        }
