"""
Template system for structured content generation.

This module provides templates for various document types to ensure
consistent and high-quality content structure.
"""

from .outline_templates import (
    get_outline_template,
    list_available_templates,
    BLOG_POST_TEMPLATE,
    TECHNICAL_ARTICLE_TEMPLATE,
    MARKETING_COPY_TEMPLATE,
)

__all__ = [
    "get_outline_template",
    "list_available_templates",
    "BLOG_POST_TEMPLATE",
    "TECHNICAL_ARTICLE_TEMPLATE",
    "MARKETING_COPY_TEMPLATE",
]
