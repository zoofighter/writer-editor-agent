"""
Export Manager for assembling and exporting books to various formats.

This module handles:
- Chapter markdown export
- Book assembly from multiple chapters
- PDF generation via pandoc
- Table of contents generation
- Bibliography/glossary generation
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..config.settings import settings


class ExportManager:
    """
    Manages export of chapters and complete books to various formats.

    Supports markdown export, book assembly, and PDF generation.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the Export Manager.

        Args:
            output_dir: Optional output directory override
        """
        self.output_dir = Path(output_dir or settings.book_output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_chapter(
        self,
        chapter_number: int,
        chapter_content: str,
        book_metadata: Dict[str, Any],
        chapter_metadata: Optional[Dict[str, Any]] = None,
        formulas: Optional[List[Dict[str, Any]]] = None,
        diagrams: Optional[List[Dict[str, Any]]] = None,
        bibliography: Optional[str] = None
    ) -> str:
        """
        Export a single chapter to markdown file.

        Args:
            chapter_number: Chapter number
            chapter_content: Main chapter content
            book_metadata: Book metadata dict
            chapter_metadata: Optional chapter-specific metadata
            formulas: Optional list of MathFormula dicts for this chapter
            diagrams: Optional list of Diagram dicts for this chapter
            bibliography: Optional bibliography text for this chapter

        Returns:
            Path to exported chapter file
        """
        # Create book directory
        book_title = book_metadata.get('book_title', 'Untitled Book')
        book_dir = self.output_dir / self._sanitize_filename(book_title)
        book_dir.mkdir(parents=True, exist_ok=True)

        # Create chapter filename
        chapter_filename = f"chapter_{chapter_number:02d}.md"
        chapter_path = book_dir / chapter_filename

        # Build complete chapter content
        content = self._build_chapter_content(
            chapter_number,
            chapter_content,
            chapter_metadata,
            formulas,
            diagrams,
            bibliography
        )

        # Write to file
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(chapter_path)

    def export_book(
        self,
        book_metadata: Dict[str, Any],
        chapter_export_paths: Dict[int, str],
        table_of_contents: Dict[str, Any],
        terminology_glossary: Dict[str, Any],
        cross_references: List[Dict[str, Any]],
        fact_check_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Assemble complete book from individual chapters.

        Args:
            book_metadata: Book metadata dict
            chapter_export_paths: Mapping of chapter_number to file path
            table_of_contents: TableOfContents dict
            terminology_glossary: Terminology glossary dict
            cross_references: List of CrossReference dicts
            fact_check_results: Optional fact-check results

        Returns:
            Path to assembled book file
        """
        book_title = book_metadata.get('book_title', 'Untitled Book')
        book_dir = self.output_dir / self._sanitize_filename(book_title)
        book_dir.mkdir(parents=True, exist_ok=True)

        # Create book filename
        book_filename = "complete_book.md"
        book_path = book_dir / book_filename

        # Build complete book content
        content = []

        # Title page
        content.append(self._build_title_page(book_metadata))
        content.append("\n\\pagebreak\n\n")

        # Table of contents
        content.append(self._build_table_of_contents(table_of_contents))
        content.append("\n\\pagebreak\n\n")

        # Chapters
        sorted_chapters = sorted(chapter_export_paths.items())
        for chapter_num, chapter_path in sorted_chapters:
            if os.path.exists(chapter_path):
                with open(chapter_path, 'r', encoding='utf-8') as f:
                    chapter_content = f.read()
                    content.append(chapter_content)
                    content.append("\n\\pagebreak\n\n")

        # Appendices
        content.append(self._build_glossary(terminology_glossary))
        content.append("\n\\pagebreak\n\n")

        if fact_check_results:
            content.append(self._build_fact_check_appendix(fact_check_results))
            content.append("\n\\pagebreak\n\n")

        # Combine all content
        full_content = "".join(content)

        # Write to file
        with open(book_path, 'w', encoding='utf-8') as f:
            f.write(full_content)

        return str(book_path)

    def export_pdf(
        self,
        markdown_path: str,
        book_metadata: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate PDF from markdown using pandoc.

        Args:
            markdown_path: Path to markdown file
            book_metadata: Book metadata dict

        Returns:
            Path to generated PDF file, or None if generation failed
        """
        if not settings.generate_pdf:
            return None

        # Check if pandoc is available
        pandoc_cmd = settings.pandoc_path or "pandoc"
        if not self._check_pandoc_available(pandoc_cmd):
            print("Warning: pandoc not found. Skipping PDF generation.")
            return None

        # Create PDF filename
        pdf_path = markdown_path.replace('.md', '.pdf')

        # Pandoc command
        cmd = [
            pandoc_cmd,
            markdown_path,
            "-o", pdf_path,
            "--pdf-engine=xelatex",  # Better Unicode support
            "-V", "geometry:margin=1in",
            "-V", f"title={book_metadata.get('book_title', 'Untitled')}",
            "-V", f"author={book_metadata.get('author', 'Unknown Author')}",
            "-V", f"date={datetime.now().strftime('%Y-%m-%d')}",
            "--toc",  # Table of contents
            "--toc-depth=2",
            "--number-sections",
            "--highlight-style=tango"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                return pdf_path
            else:
                print(f"PDF generation failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print("PDF generation timed out")
            return None
        except Exception as e:
            print(f"PDF generation error: {e}")
            return None

    # Helper methods

    def _build_chapter_content(
        self,
        chapter_number: int,
        main_content: str,
        chapter_metadata: Optional[Dict[str, Any]],
        formulas: Optional[List[Dict[str, Any]]],
        diagrams: Optional[List[Dict[str, Any]]],
        bibliography: Optional[str]
    ) -> str:
        """Build complete chapter content with all elements."""
        content = []

        # Chapter header
        chapter_title = chapter_metadata.get('title', f'Chapter {chapter_number}') if chapter_metadata else f'Chapter {chapter_number}'
        content.append(f"# Chapter {chapter_number}: {chapter_title}\n\n")

        # Main content
        content.append(main_content)
        content.append("\n\n")

        # Formulas index (if any)
        if formulas:
            content.append("## Formulas\n\n")
            for formula in formulas:
                formula_id = formula.get('formula_id', '')
                description = formula.get('description', '')
                content.append(f"- **{formula_id}**: {description}\n")
            content.append("\n")

        # Diagrams index (if any)
        if diagrams:
            content.append("## Diagrams\n\n")
            for diagram in diagrams:
                diagram_id = diagram.get('diagram_id', '')
                caption = diagram.get('caption', '')
                content.append(f"- **{diagram_id}**: {caption}\n")
            content.append("\n")

        # Bibliography (if any)
        if bibliography:
            content.append(bibliography)
            content.append("\n")

        return "".join(content)

    def _build_title_page(self, book_metadata: Dict[str, Any]) -> str:
        """Build book title page."""
        title = book_metadata.get('book_title', 'Untitled Book')
        author = book_metadata.get('author', 'Unknown Author')
        description = book_metadata.get('description', '')
        version = book_metadata.get('version', '1.0.0')
        created_at = book_metadata.get('created_at', datetime.now().isoformat())

        content = f"""---
title: "{title}"
author: "{author}"
date: {created_at[:10]}
version: {version}
---

# {title}

**Author:** {author}

**Version:** {version}

**Published:** {created_at[:10]}

"""

        if description:
            content += f"""## Description

{description}

"""

        return content

    def _build_table_of_contents(self, table_of_contents: Dict[str, Any]) -> str:
        """Build table of contents section."""
        content = ["# Table of Contents\n\n"]

        chapters = table_of_contents.get('chapters', [])
        for chapter in chapters:
            num = chapter.get('number', 0)
            title = chapter.get('title', f'Chapter {num}')
            summary = chapter.get('summary', '')

            content.append(f"{num}. **{title}**\n")
            if summary:
                content.append(f"   {summary}\n")
            content.append("\n")

        return "".join(content)

    def _build_glossary(self, terminology_glossary: Dict[str, Any]) -> str:
        """Build glossary/terminology section."""
        if not terminology_glossary:
            return "# Glossary\n\n*No terminology defined.*\n"

        content = ["# Glossary\n\n"]

        # Sort terms alphabetically
        sorted_terms = sorted(terminology_glossary.items())

        for term, entry in sorted_terms:
            definition = entry.get('definition', '')
            first_chapter = entry.get('first_introduced_chapter', 0)
            aliases = entry.get('aliases', [])

            content.append(f"**{term}**\n")
            content.append(f": {definition}\n")

            if aliases:
                content.append(f"  *Also known as: {', '.join(aliases)}*\n")

            content.append(f"  *First introduced in Chapter {first_chapter}*\n")
            content.append("\n")

        return "".join(content)

    def _build_fact_check_appendix(self, fact_check_results: List[Dict[str, Any]]) -> str:
        """Build fact-checking appendix."""
        content = ["# Appendix: Fact-Checking Report\n\n"]

        # Count by status
        status_counts = {}
        for result in fact_check_results:
            status = result.get('verification_status', 'unverified')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Summary
        content.append("## Summary\n\n")
        content.append(f"- Total Claims Verified: {len(fact_check_results)}\n")
        for status, count in status_counts.items():
            content.append(f"- {status.title()}: {count}\n")
        content.append("\n")

        # Group by chapter
        by_chapter = {}
        for result in fact_check_results:
            chapter = result.get('chapter_number', 0)
            if chapter not in by_chapter:
                by_chapter[chapter] = []
            by_chapter[chapter].append(result)

        # Detail by chapter
        for chapter_num in sorted(by_chapter.keys()):
            content.append(f"## Chapter {chapter_num}\n\n")

            for result in by_chapter[chapter_num]:
                claim = result.get('claim', '')
                status = result.get('verification_status', 'unverified')
                confidence = result.get('confidence_score', 0.0)
                sources = result.get('sources', [])

                content.append(f"**Claim:** {claim}\n")
                content.append(f"- **Status:** {status}\n")
                content.append(f"- **Confidence:** {confidence:.2f}\n")

                if sources:
                    content.append(f"- **Sources:**\n")
                    for source in sources[:5]:  # Limit to 5 sources
                        content.append(f"  - {source}\n")

                content.append("\n")

        return "".join(content)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Limit length
        if len(filename) > 100:
            filename = filename[:100]

        return filename.strip()

    def _check_pandoc_available(self, pandoc_cmd: str) -> bool:
        """Check if pandoc is available."""
        try:
            result = subprocess.run(
                [pandoc_cmd, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False


# Convenience functions

def export_chapter_to_file(
    state: Dict[str, Any],
    export_manager: Optional[ExportManager] = None
) -> str:
    """
    Export current chapter from workflow state.

    Args:
        state: Workflow state dict
        export_manager: Optional ExportManager instance

    Returns:
        Path to exported chapter file
    """
    manager = export_manager or ExportManager()

    chapter_number = state.get('chapter_number', 1)
    chapter_content = state.get('current_draft', '')
    book_metadata = state.get('book_metadata', {})
    chapter_metadata = state.get('chapter_metadata')

    # Filter formulas and diagrams for this chapter
    all_formulas = state.get('math_formulas', [])
    chapter_formulas = [
        f for f in all_formulas
        if f.get('chapter_number') == chapter_number
    ]

    all_diagrams = state.get('diagrams', [])
    chapter_diagrams = [
        d for d in all_diagrams
        if d.get('chapter_number') == chapter_number
    ]

    # Generate bibliography if available
    bibliography = None  # Could extract from bibliography agent results

    return manager.export_chapter(
        chapter_number,
        chapter_content,
        book_metadata,
        chapter_metadata,
        chapter_formulas,
        chapter_diagrams,
        bibliography
    )


def export_complete_book(
    state: Dict[str, Any],
    export_manager: Optional[ExportManager] = None,
    generate_pdf: bool = None
) -> Dict[str, Optional[str]]:
    """
    Export complete book from workflow state.

    Args:
        state: Workflow state dict
        export_manager: Optional ExportManager instance
        generate_pdf: Optional PDF generation override

    Returns:
        Dict with 'markdown' and 'pdf' paths
    """
    manager = export_manager or ExportManager()

    book_metadata = state.get('book_metadata', {})
    chapter_export_paths = state.get('chapter_export_paths', {})
    table_of_contents = state.get('table_of_contents', {})
    terminology_glossary = state.get('terminology_glossary', {})
    cross_references = state.get('cross_references', [])
    fact_check_results = state.get('fact_check_results', [])

    # Export markdown
    markdown_path = manager.export_book(
        book_metadata,
        chapter_export_paths,
        table_of_contents,
        terminology_glossary,
        cross_references,
        fact_check_results
    )

    # Export PDF if requested
    pdf_path = None
    if generate_pdf or (generate_pdf is None and settings.generate_pdf):
        pdf_path = manager.export_pdf(markdown_path, book_metadata)

    return {
        'markdown': markdown_path,
        'pdf': pdf_path
    }
