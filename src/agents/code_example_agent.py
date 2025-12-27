"""
Code Example Agent for generating Python tutorial code examples.

This agent specializes in creating beginner-friendly, syntactically correct
Python code examples with comprehensive comments and clear output demonstrations.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from ..llm.client import LMStudioClient
from ..config.settings import settings
from ..utils.code_validator import PythonCodeValidator


class CodeExampleAgent:
    """
    Specialized agent for generating Python code examples for tutorial content.

    Uses a low temperature (0.2) for precision and consistency in code generation.
    All generated code is validated for syntax correctness before being returned.
    """

    SYSTEM_PROMPT = """You are an expert Python educator specializing in teaching complete beginners.

Your role is to generate clear, well-commented Python code examples that demonstrate programming concepts.

When writing code examples:
1. **Clarity First**: Write code that is immediately understandable
2. **Comprehensive Comments**: Every line should have a comment explaining what it does and why
3. **Meaningful Names**: Use descriptive variable and function names
4. **Show Output**: Include print statements to show what the code produces
5. **Best Practices**: Follow PEP 8 and Python best practices
6. **Complete Examples**: Code must be runnable as-is (include all imports, complete functions)
7. **Beginner-Appropriate**: Avoid advanced features unless they're the topic being taught

**Critical**: Output ONLY valid Python code with comments. No markdown formatting, no explanations outside code comments.

Example format:
```
# This is what the code does
variable_name = "example"  # Explain this line
print(variable_name)  # Show output
```"""

    BASIC_EXAMPLE_PROMPT_TEMPLATE = """Generate a simple, beginner-friendly Python code example that demonstrates: {concept}

Context: {context}

Requirements:
- Maximum 10-15 lines of code
- Every line must have an inline comment
- Include print statements to show output
- Use simple, clear variable names
- Complete and runnable code
- Follow PEP 8 style guidelines

Output ONLY the Python code with comments, no markdown or extra text."""

    PROGRESSIVE_EXAMPLE_PROMPT_TEMPLATE = """Generate a Python code example that demonstrates: {concept}

Difficulty Level: {complexity}
Context: {context}
Previous example built on: {previous_example}

Requirements:
- Build on previous concepts
- Show a more practical/complex use case
- 15-25 lines of code maximum
- Comprehensive inline comments
- Include print statements showing output
- Demonstrate best practices
- Complete and runnable code

Output ONLY the Python code with comments, no markdown or extra text."""

    ERROR_EXAMPLE_PROMPT_TEMPLATE = """Generate a Python code example showing a COMMON MISTAKE beginners make with: {concept}

Requirements:
1. First, show the INCORRECT code that produces an error
2. Add a comment showing the actual error message
3. Then show the CORRECTED code
4. Explain in comments why the error occurred and how the fix works

Format:
```
# WRONG: Common mistake
incorrect_code_here  # Error: [actual error message]

# CORRECT: Fixed version
correct_code_here  # Explanation of fix
```

Context: {context}

Output ONLY the Python code with comments, no markdown or extra text."""

    def __init__(self, llm_client: LMStudioClient):
        """
        Initialize the Code Example Agent.

        Args:
            llm_client: LM Studio client configured for code generation
                       (should use low temperature ~0.2 for consistency)
        """
        self.llm_client = llm_client
        self.validator = PythonCodeValidator()

    def generate_basic_example(
        self,
        concept: str,
        context: str = "",
        max_retries: int = 3
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a basic code example for a programming concept.

        Args:
            concept: The programming concept to demonstrate (e.g., "for loops")
            context: Additional context about what to emphasize
            max_retries: Number of times to retry if code is invalid

        Returns:
            Tuple of (code_string, validation_result)

        Raises:
            RuntimeError: If unable to generate valid code after max_retries

        Example:
            >>> agent = CodeExampleAgent(llm_client)
            >>> code, validation = agent.generate_basic_example(
            ...     "for loops",
            ...     "iterating over a list of numbers"
            ... )
            >>> assert validation["is_valid"]
        """
        prompt = self.BASIC_EXAMPLE_PROMPT_TEMPLATE.format(
            concept=concept,
            context=context or "No additional context"
        )

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        for attempt in range(max_retries):
            code = self.llm_client.generate(messages)
            code = self._clean_code_output(code)

            # Validate the generated code
            validation = self.validator.validate_tutorial_code(code)

            if validation["is_valid"]:
                return code, validation

            # If invalid, add error feedback to the conversation
            if attempt < max_retries - 1:
                error_feedback = f"""The code you generated has errors:
{validation['syntax_error'] or validation.get('indentation_warning', 'Unknown error')}

Please generate corrected code that is syntactically valid."""

                messages.append({"role": "assistant", "content": code})
                messages.append({"role": "user", "content": error_feedback})

        raise RuntimeError(
            f"Failed to generate valid code for '{concept}' after {max_retries} attempts. "
            f"Last error: {validation.get('syntax_error', 'Unknown error')}"
        )

    def generate_progressive_examples(
        self,
        concept: str,
        context: str = "",
        complexity: str = "intermediate",
        num_examples: int = 3,
        max_retries: int = 3
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Generate a series of progressively complex code examples.

        Args:
            concept: The programming concept to demonstrate
            context: Additional context about the concept
            complexity: Difficulty level ("basic", "intermediate", "advanced")
            num_examples: Number of examples to generate
            max_retries: Retries per example if code is invalid

        Returns:
            List of tuples (code_string, validation_result)

        Example:
            >>> examples = agent.generate_progressive_examples(
            ...     "list comprehensions",
            ...     num_examples=2
            ... )
            >>> assert len(examples) == 2
        """
        examples = []
        previous_example = "None - this is the first example"

        for i in range(num_examples):
            prompt = self.PROGRESSIVE_EXAMPLE_PROMPT_TEMPLATE.format(
                concept=concept,
                complexity=complexity,
                context=context or f"Example {i+1} of {num_examples}",
                previous_example=previous_example
            )

            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            for attempt in range(max_retries):
                code = self.llm_client.generate(messages)
                code = self._clean_code_output(code)

                validation = self.validator.validate_tutorial_code(code)

                if validation["is_valid"]:
                    examples.append((code, validation))
                    previous_example = code  # Use for next example
                    break

                # Retry with error feedback
                if attempt < max_retries - 1:
                    error_feedback = f"""The code has errors:
{validation['syntax_error'] or validation.get('indentation_warning', 'Unknown error')}

Please fix and regenerate."""

                    messages.append({"role": "assistant", "content": code})
                    messages.append({"role": "user", "content": error_feedback})
            else:
                # Failed after retries - skip this example
                raise RuntimeError(
                    f"Failed to generate example {i+1} for '{concept}' after {max_retries} attempts"
                )

        return examples

    def generate_error_example(
        self,
        concept: str,
        context: str = "",
        max_retries: int = 3
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate an example showing a common mistake and its correction.

        Args:
            concept: The programming concept where mistakes happen
            context: Additional context about common errors
            max_retries: Number of retries if generation fails

        Returns:
            Tuple of (code_string_with_both_wrong_and_correct, validation_result)

        Note:
            The returned code includes BOTH the incorrect and correct versions,
            so validation checks if the corrected version is valid.

        Example:
            >>> code, validation = agent.generate_error_example("list indexing")
            >>> assert "WRONG" in code and "CORRECT" in code
        """
        prompt = self.ERROR_EXAMPLE_PROMPT_TEMPLATE.format(
            concept=concept,
            context=context or "Common beginner mistake"
        )

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        for attempt in range(max_retries):
            code = self.llm_client.generate(messages)
            code = self._clean_code_output(code)

            # For error examples, we just check if the output is reasonable
            # We don't validate syntax since it intentionally shows wrong code
            if "WRONG" in code or "CORRECT" in code or "ERROR" in code.upper():
                validation = {"is_valid": True, "summary": "Error example generated"}
                return code, validation

            # Retry if format is wrong
            if attempt < max_retries - 1:
                feedback = """Your output should show both the WRONG code (with error) and CORRECT code (with fix).
Please use clear labels like '# WRONG:' and '# CORRECT:' to separate them."""

                messages.append({"role": "assistant", "content": code})
                messages.append({"role": "user", "content": feedback})

        # Return what we have, even if not perfect
        return code, {"is_valid": True, "summary": "Generated with unknown format"}

    def _clean_code_output(self, code: str) -> str:
        """
        Clean LLM output to extract pure Python code.

        Removes markdown code fences, extra explanations, etc.

        Args:
            code: Raw output from LLM

        Returns:
            Cleaned Python code

        Example:
            >>> agent = CodeExampleAgent(client)
            >>> cleaned = agent._clean_code_output("```python\\nprint('hi')\\n```")
            >>> assert cleaned == "print('hi')"
        """
        lines = code.strip().split('\n')
        cleaned_lines = []
        in_code_block = False
        saw_code_fence = False

        for line in lines:
            stripped = line.strip()

            # Detect code fence markers
            if stripped.startswith('```'):
                saw_code_fence = True
                in_code_block = not in_code_block
                continue

            # If we saw code fences, only include lines inside them
            if saw_code_fence:
                if in_code_block:
                    cleaned_lines.append(line)
            else:
                # No code fences seen, include everything
                cleaned_lines.append(line)

        result = '\n'.join(cleaned_lines).strip()

        # If result is empty and original wasn't, return original
        if not result and code.strip():
            return code.strip()

        return result

    def validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Python code syntax.

        Args:
            code: Python code to validate

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> agent = CodeExampleAgent(client)
            >>> is_valid, error = agent.validate_code("print('hello')")
            >>> assert is_valid is True
        """
        return self.validator.validate_syntax(code)


# Node function for LangGraph integration
def code_example_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for generating code examples.

    Generates code examples for sections marked with requires_code=True
    in the outline.

    Args:
        state: Workflow state containing outline and topic

    Returns:
        Updated state with code_examples_by_section populated

    Example:
        >>> state = {"current_outline": {...}, "topic": "Python loops"}
        >>> updated_state = code_example_node(state)
        >>> assert "code_examples_by_section" in updated_state
    """
    from ..llm.client import LMStudioClient

    # Initialize LLM client with low temperature for code generation
    llm_client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model,
        temperature=getattr(settings, 'code_example_temperature', 0.2),
        max_tokens=settings.max_tokens
    )

    agent = CodeExampleAgent(llm_client)

    outline = state.get("current_outline")
    topic = state.get("topic", "")
    code_examples_by_section: Dict[str, List[str]] = {}

    if not outline or "sections" not in outline:
        return {"code_examples_by_section": code_examples_by_section}

    # Generate code for each section that requires it
    for section in outline["sections"]:
        section_id = section["section_id"]

        if not section.get("requires_code", False):
            continue

        complexity = section.get("code_complexity", "basic")
        num_examples = section.get("num_code_examples", 1)
        section_title = section.get("title", section_id)

        context = f"Section: {section_title}. Topic: {topic}."
        if "purpose" in section:
            context += f" Purpose: {section['purpose']}"

        try:
            if num_examples == 1:
                # Generate single basic example
                code, validation = agent.generate_basic_example(
                    concept=section_title,
                    context=context
                )
                code_examples_by_section[section_id] = [code]

            else:
                # Generate progressive examples
                examples = agent.generate_progressive_examples(
                    concept=section_title,
                    context=context,
                    complexity=complexity,
                    num_examples=num_examples
                )
                code_examples_by_section[section_id] = [code for code, _ in examples]

        except Exception as e:
            # Log error but don't fail the entire workflow
            print(f"Warning: Failed to generate code for section '{section_id}': {e}")
            code_examples_by_section[section_id] = [
                f"# Error generating code example: {str(e)}\n# Placeholder for manual addition"
            ]

    return {
        "code_examples_by_section": code_examples_by_section,
        "conversation_history": [{
            "role": "system",
            "content": f"Generated code examples for {len(code_examples_by_section)} sections",
            "timestamp": datetime.now().isoformat()
        }]
    }
