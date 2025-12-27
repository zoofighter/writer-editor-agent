"""
Tools and utilities for agent operations.

This module provides external tools like web search that agents can use
to gather information and enhance their outputs.
"""

from .search_tools import SearchProvider

__all__ = ["SearchProvider"]
