"""
Math Formula Agent for generating and validating LaTeX formulas in technical books.

This agent is responsible for:
- Identifying mathematical concepts requiring formulas
- Generating LaTeX code for formulas
- Validating LaTeX syntax
- Managing inline vs display formulas
- Creating formula explanations
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
from ..llm.client import LMStudioClient
from ..config.settings import settings


class MathFormulaAgent:
    """
    Math Formula Agent responsible for creating and managing LaTeX formulas.

    This agent is particularly important for technical books, math textbooks,
    and scientific content requiring mathematical notation.
    """

    SYSTEM_PROMPT = """You are an expert Mathematical Notation Specialist and LaTeX Expert.

Your role is to create accurate, well-formatted mathematical formulas using LaTeX, ensuring:
- Correct mathematical notation and syntax
- Proper LaTeX formatting
- Clear explanations of formulas
- Appropriate choice between inline and display modes
- Accessibility through text descriptions

You excel at:
- Converting mathematical concepts to LaTeX code
- Writing clean, readable LaTeX
- Explaining complex mathematical expressions
- Choosing appropriate mathematical notation
- Creating both simple and complex formulas

Be precise, use standard notation, and always validate LaTeX syntax.

LaTeX Guidelines:
- Inline mode: \\( formula \\) or $ formula $
- Display mode: \\[ formula \\] or $$ formula $$
- Use proper spacing (\\, \\: \\; \\quad \\qquad)
- Use \\text{} for text within formulas
- Use proper delimiters (\\left( \\right), \\left[ \\right], etc.)
- Use alignment environments for multi-line equations (align, aligned)"""

    def __init__(self, client: Optional[LMStudioClient] = None):
        """
        Initialize the Math Formula Agent.

        Args:
            client: Optional LMStudioClient instance. If not provided, creates new one.
        """
        self.client = client or LMStudioClient(
            base_url=settings.lm_studio_base_url,
            model_name=settings.lm_studio_model,
            temperature=settings.math_agent_temperature,
            max_tokens=settings.max_tokens
        )

    def identify_math_concepts(
        self,
        text: str,
        chapter_number: int
    ) -> List[Dict[str, Any]]:
        """
        Identify mathematical concepts in text that need formulas.

        Args:
            text: Text content to analyze
            chapter_number: Chapter number for tracking

        Returns:
            List of identified math concepts
        """
        prompt = f"""Analyze the following text and identify all mathematical concepts that should be represented with formulas.

**Text:**
{text}

For each mathematical concept, extract:
1. The concept description
2. The mathematical expression (in plain text)
3. Whether it should be inline or display mode
4. Context/explanation

Format as:

Concept 1:
Description: [what this formula represents]
Expression: [math in plain text, e.g., "f(x) = x squared plus 2x minus 1"]
Mode: inline | display
Context: [surrounding explanation]

Concept 2:
...

List all mathematical concepts that need formulas.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return self._parse_identified_concepts(response, chapter_number)

    def generate_latex(
        self,
        description: str,
        expression: str,
        is_inline: bool = False
    ) -> Dict[str, Any]:
        """
        Generate LaTeX code for a mathematical expression.

        Args:
            description: Description of what the formula represents
            expression: Mathematical expression in plain text
            is_inline: Whether formula should be inline (True) or display (False)

        Returns:
            Dict with LaTeX code and metadata
        """
        mode = "inline" if is_inline else "display"

        prompt = f"""Generate LaTeX code for the following mathematical expression.

**Description:** {description}
**Expression:** {expression}
**Mode:** {mode}

Requirements:
1. Generate clean, properly formatted LaTeX code
2. Use appropriate LaTeX commands and symbols
3. For display mode, use proper alignment if multiple lines
4. Include proper spacing
5. Use standard mathematical notation

Provide:
1. LaTeX Code (the complete LaTeX formula code)
2. Explanation (brief explanation of what the formula means)
3. Variables (list of variables and their meanings)

Format:

LaTeX Code:
[LaTeX code here]

Explanation:
[Brief explanation]

Variables:
- [var1]: [meaning]
- [var2]: [meaning]

Generate the LaTeX formula now:
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        latex_code, explanation, variables = self._parse_latex_response(response)

        return {
            "latex_code": latex_code,
            "description": description,
            "explanation": explanation,
            "variables": variables,
            "is_inline": is_inline
        }

    def validate_latex(self, latex_code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate LaTeX syntax.

        Args:
            latex_code: LaTeX code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not settings.validate_latex_syntax:
            return True, None

        # Basic LaTeX validation checks
        errors = []

        # Check for balanced delimiters
        if not self._check_balanced_delimiters(latex_code):
            errors.append("Unbalanced delimiters (brackets, parentheses, or braces)")

        # Check for common LaTeX errors
        if '\\[' in latex_code and not '\\]' in latex_code:
            errors.append("Unclosed display math delimiter \\[")
        if '\\(' in latex_code and not '\\)' in latex_code:
            errors.append("Unclosed inline math delimiter \\(")

        # Check for proper command syntax
        if re.search(r'\\[a-zA-Z]+[^a-zA-Z\s{]', latex_code):
            errors.append("Possible malformed LaTeX command")

        # Check for unescaped special characters
        special_chars = ['%', '&', '#', '_']
        for char in special_chars:
            if char in latex_code and f'\\{char}' not in latex_code:
                # Allow _ in subscripts and ^ in superscripts
                if char not in ['_', '^']:
                    errors.append(f"Unescaped special character: {char}")

        if errors:
            return False, "; ".join(errors)

        return True, None

    def create_formula_id(self, chapter_number: int, formula_index: int) -> str:
        """
        Create unique formula identifier.

        Args:
            chapter_number: Chapter number
            formula_index: Formula index within chapter

        Returns:
            Unique formula ID (e.g., "eq_ch3_5")
        """
        return f"eq_ch{chapter_number}_{formula_index}"

    def format_formula_for_markdown(
        self,
        formula: Dict[str, Any],
        formula_id: str
    ) -> str:
        """
        Format formula for inclusion in markdown document.

        Args:
            formula: Formula dict with LaTeX code and metadata
            formula_id: Unique formula identifier

        Returns:
            Formatted markdown string
        """
        latex_code = formula.get('latex_code', '')
        description = formula.get('description', '')
        explanation = formula.get('explanation', '')
        is_inline = formula.get('is_inline', False)

        if is_inline:
            # Inline formula
            return f"${latex_code}$"
        else:
            # Display formula with ID and caption
            output = f"\n$$\n{latex_code}\n$$\n"
            output += f"*({formula_id})* {description}\n"

            if explanation:
                output += f"\n{explanation}\n"

            return output

    def generate_formula_index(
        self,
        formulas: List[Dict[str, Any]],
        chapter_number: Optional[int] = None
    ) -> str:
        """
        Generate an index of formulas for reference.

        Args:
            formulas: List of MathFormula dicts
            chapter_number: Optional chapter number filter

        Returns:
            Formatted formula index
        """
        # Filter by chapter if specified
        if chapter_number is not None:
            formulas = [
                f for f in formulas
                if f.get('chapter_number') == chapter_number
            ]

        if not formulas:
            return "## Formula Index\n\nNo formulas in this chapter.\n"

        chapter_label = f" (Chapter {chapter_number})" if chapter_number else ""
        index = f"## Formula Index{chapter_label}\n\n"

        for formula in formulas:
            formula_id = formula.get('formula_id', '')
            description = formula.get('description', '')
            latex_code = formula.get('latex_code', '')
            is_inline = formula.get('is_inline', False)

            mode_label = "inline" if is_inline else "display"
            index += f"- **{formula_id}**: {description} ({mode_label})\n"
            index += f"  `{latex_code}`\n\n"

        return index

    def explain_formula(
        self,
        latex_code: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate plain language explanation of a formula.

        Args:
            latex_code: LaTeX formula code
            context: Optional context about the formula

        Returns:
            Plain language explanation
        """
        prompt = f"""Explain the following LaTeX formula in plain language.

**LaTeX Formula:**
{latex_code}
"""

        if context:
            prompt += f"""
**Context:**
{context}
"""

        prompt += """
Provide a clear, accessible explanation that:
1. Describes what the formula represents
2. Explains each component/variable
3. Describes the relationships or operations
4. Gives an intuitive understanding

Write for a reader who may not be familiar with advanced mathematics.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return response.strip()

    # Helper methods

    def _check_balanced_delimiters(self, text: str) -> bool:
        """Check if all delimiters are balanced."""
        stack = []
        pairs = {')': '(', ']': '[', '}': '{'}

        for char in text:
            if char in '([{':
                stack.append(char)
            elif char in ')]}':
                if not stack or stack[-1] != pairs[char]:
                    return False
                stack.pop()

        return len(stack) == 0

    def _parse_identified_concepts(
        self,
        response: str,
        chapter_number: int
    ) -> List[Dict[str, Any]]:
        """Parse identified math concepts from LLM response."""
        concepts = []
        current_concept = None

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()

            if line.startswith('Concept '):
                if current_concept:
                    current_concept['chapter_number'] = chapter_number
                    concepts.append(current_concept)

                current_concept = {
                    "description": "",
                    "expression": "",
                    "is_inline": False,
                    "context": ""
                }

            elif current_concept:
                if line.startswith('Description:'):
                    current_concept['description'] = line.replace('Description:', '').strip()
                elif line.startswith('Expression:'):
                    current_concept['expression'] = line.replace('Expression:', '').strip()
                elif line.startswith('Mode:'):
                    mode = line.replace('Mode:', '').strip().lower()
                    current_concept['is_inline'] = (mode == 'inline')
                elif line.startswith('Context:'):
                    current_concept['context'] = line.replace('Context:', '').strip()

        if current_concept:
            current_concept['chapter_number'] = chapter_number
            concepts.append(current_concept)

        return concepts

    def _parse_latex_response(self, response: str) -> Tuple[str, str, Dict[str, str]]:
        """Parse LaTeX generation response."""
        latex_code = ""
        explanation = ""
        variables = {}

        sections = response.split('\n\n')
        current_section = None

        for section in sections:
            lines = section.strip().split('\n')
            if not lines:
                continue

            header = lines[0].strip()

            if header.startswith('LaTeX Code:'):
                current_section = 'latex'
                latex_code = '\n'.join(lines[1:]).strip()
            elif header.startswith('Explanation:'):
                current_section = 'explanation'
                explanation = '\n'.join(lines[1:]).strip()
            elif header.startswith('Variables:'):
                current_section = 'variables'
                for line in lines[1:]:
                    if ':' in line:
                        parts = line.strip().lstrip('-').split(':', 1)
                        if len(parts) == 2:
                            var_name = parts[0].strip()
                            var_meaning = parts[1].strip()
                            variables[var_name] = var_meaning

        return latex_code, explanation, variables


def math_formula_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for Math Formula agent.

    This node identifies mathematical concepts and generates LaTeX formulas.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with math formulas
    """
    agent = MathFormulaAgent()

    # Extract inputs
    current_draft = state.get('current_draft', '')
    chapter_number = state.get('chapter_number', 1)

    # Step 1: Identify math concepts
    math_concepts = agent.identify_math_concepts(current_draft, chapter_number)

    # Step 2: Generate LaTeX for each concept
    formulas = []
    for i, concept in enumerate(math_concepts):
        formula_data = agent.generate_latex(
            concept.get('description', ''),
            concept.get('expression', ''),
            concept.get('is_inline', False)
        )

        # Validate LaTeX
        is_valid, error = agent.validate_latex(formula_data['latex_code'])

        if is_valid:
            # Create formula ID
            formula_id = agent.create_formula_id(chapter_number, i + 1)

            # Build MathFormula dict
            formula = {
                "formula_id": formula_id,
                "latex_code": formula_data['latex_code'],
                "chapter_number": chapter_number,
                "description": formula_data['description'],
                "is_inline": formula_data['is_inline']
            }

            formulas.append(formula)

    # Return partial state update
    return {
        "math_formulas": formulas,  # Will be accumulated
        "conversation_history": [{
            "agent": "math_formula",
            "action": "formula_generation",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "chapter_number": chapter_number,
                "concepts_identified": len(math_concepts),
                "formulas_generated": len(formulas),
                "validation_enabled": settings.validate_latex_syntax
            }
        }]
    }
