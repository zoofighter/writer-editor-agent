"""
Python code validation utilities for tutorial code examples.

Provides syntax validation, code quality checks, and beginner-friendly error reporting.
"""

import ast
from typing import Tuple, List, Dict, Any, Optional


class PythonCodeValidator:
    """
    Validates Python code for syntax correctness and quality.

    Designed specifically for tutorial code examples where correctness
    and clarity are critical for beginner education.
    """

    @staticmethod
    def validate_syntax(code: str) -> Tuple[bool, Optional[str]]:
        """
        Check if code is syntactically valid Python.

        Args:
            code: Python code string to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if code is syntactically correct
            - error_message: None if valid, otherwise error description

        Example:
            >>> validator = PythonCodeValidator()
            >>> is_valid, error = validator.validate_syntax("print('hello')")
            >>> assert is_valid is True
            >>> is_valid, error = validator.validate_syntax("print('hello'")
            >>> assert is_valid is False
            >>> assert "SyntaxError" in error
        """
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            error_msg = f"Syntax error on line {e.lineno}: {e.msg}"
            if e.text:
                error_msg += f"\n  {e.text.strip()}"
                if e.offset:
                    error_msg += f"\n  {' ' * (e.offset - 1)}^"
            return False, error_msg
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def check_line_length(code: str, max_length: int = 79) -> List[str]:
        """
        Check for PEP 8 line length violations.

        Args:
            code: Python code string to check
            max_length: Maximum allowed line length (default: 79 per PEP 8)

        Returns:
            List of warnings for lines exceeding max_length

        Example:
            >>> code = "x = 1\\nprint('This is a very long line that exceeds the PEP 8 recommended maximum line length of 79 characters')"
            >>> warnings = PythonCodeValidator.check_line_length(code)
            >>> assert len(warnings) == 1
        """
        warnings = []
        lines = code.split('\n')
        for i, line in enumerate(lines, start=1):
            if len(line) > max_length:
                warnings.append(
                    f"Line {i} exceeds {max_length} characters ({len(line)} chars): {line[:50]}..."
                )
        return warnings

    @staticmethod
    def check_indentation_consistency(code: str) -> Tuple[bool, Optional[str]]:
        """
        Check if code uses consistent indentation (spaces vs tabs).

        Args:
            code: Python code string to check

        Returns:
            Tuple of (is_consistent, warning_message)

        Example:
            >>> code = "def foo():\\n    x = 1\\n\\ty = 2"  # Mixed spaces and tabs
            >>> is_consistent, warning = PythonCodeValidator.check_indentation_consistency(code)
            >>> assert is_consistent is False
        """
        lines = code.split('\n')
        has_spaces = False
        has_tabs = False

        for i, line in enumerate(lines, start=1):
            if line and line[0] in (' ', '\t'):
                if line[0] == ' ':
                    has_spaces = True
                elif line[0] == '\t':
                    has_tabs = True

                if has_spaces and has_tabs:
                    return False, f"Mixed spaces and tabs detected (problematic around line {i})"

        return True, None

    @staticmethod
    def extract_code_blocks(text: str) -> List[str]:
        """
        Extract Python code blocks from markdown-formatted text.

        Args:
            text: Markdown text potentially containing code blocks

        Returns:
            List of code block contents

        Example:
            >>> text = "Some text\\n```python\\nprint('hello')\\n```\\nMore text"
            >>> blocks = PythonCodeValidator.extract_code_blocks(text)
            >>> assert len(blocks) == 1
            >>> assert blocks[0] == "print('hello')"
        """
        code_blocks = []
        in_code_block = False
        current_block = []

        for line in text.split('\n'):
            if line.strip().startswith('```python') or line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    if current_block:
                        code_blocks.append('\n'.join(current_block))
                        current_block = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)

        # Handle unclosed code block
        if current_block:
            code_blocks.append('\n'.join(current_block))

        return code_blocks

    @classmethod
    def validate_tutorial_code(
        cls,
        code: str,
        check_line_length: bool = True,
        max_line_length: int = 79,
        check_indentation: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive validation for tutorial code examples.

        Performs multiple validation checks and returns a detailed report.

        Args:
            code: Python code string to validate
            check_line_length: Whether to check for PEP 8 line length
            max_line_length: Maximum allowed line length
            check_indentation: Whether to check indentation consistency

        Returns:
            Dictionary with validation results:
            {
                "is_valid": bool,
                "syntax_valid": bool,
                "syntax_error": Optional[str],
                "line_length_warnings": List[str],
                "indentation_warning": Optional[str],
                "summary": str
            }

        Example:
            >>> code = "print('Hello, World!')"
            >>> result = PythonCodeValidator.validate_tutorial_code(code)
            >>> assert result["is_valid"] is True
            >>> assert result["syntax_valid"] is True
        """
        result = {
            "is_valid": True,
            "syntax_valid": False,
            "syntax_error": None,
            "line_length_warnings": [],
            "indentation_warning": None,
            "summary": ""
        }

        # Check syntax
        syntax_valid, syntax_error = cls.validate_syntax(code)
        result["syntax_valid"] = syntax_valid
        result["syntax_error"] = syntax_error

        if not syntax_valid:
            result["is_valid"] = False
            result["summary"] = f"Code has syntax errors: {syntax_error}"
            return result

        # Check line length
        if check_line_length:
            line_warnings = cls.check_line_length(code, max_line_length)
            result["line_length_warnings"] = line_warnings
            # Note: Long lines are warnings, not errors for tutorial code

        # Check indentation
        if check_indentation:
            indentation_ok, indentation_warning = cls.check_indentation_consistency(code)
            result["indentation_warning"] = indentation_warning
            if not indentation_ok:
                result["is_valid"] = False
                result["summary"] = f"Indentation issue: {indentation_warning}"
                return result

        # Success summary
        warnings_count = len(result["line_length_warnings"])
        if warnings_count > 0:
            result["summary"] = f"Code is valid with {warnings_count} style warning(s)"
        else:
            result["summary"] = "Code is valid"

        return result

    @classmethod
    def validate_code_in_markdown(cls, markdown_text: str) -> Dict[str, Any]:
        """
        Validate all Python code blocks in markdown text.

        Args:
            markdown_text: Markdown-formatted text with code blocks

        Returns:
            Dictionary with validation results for all code blocks:
            {
                "total_blocks": int,
                "valid_blocks": int,
                "invalid_blocks": int,
                "blocks": List[Dict] with individual block results
            }

        Example:
            >>> md = "# Tutorial\\n```python\\nprint('hi')\\n```"
            >>> result = PythonCodeValidator.validate_code_in_markdown(md)
            >>> assert result["total_blocks"] == 1
            >>> assert result["valid_blocks"] == 1
        """
        code_blocks = cls.extract_code_blocks(markdown_text)

        results = {
            "total_blocks": len(code_blocks),
            "valid_blocks": 0,
            "invalid_blocks": 0,
            "blocks": []
        }

        for i, code in enumerate(code_blocks, start=1):
            validation = cls.validate_tutorial_code(code)
            validation["block_number"] = i
            results["blocks"].append(validation)

            if validation["is_valid"]:
                results["valid_blocks"] += 1
            else:
                results["invalid_blocks"] += 1

        return results
