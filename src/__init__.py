"""
Writer-Editor Review Loop Agent System.

A LangGraph-based multi-agent system for collaborative content creation
with human-in-the-loop pattern.
"""

__version__ = "1.0.0"
__author__ = "Writer-Editor Team"

from .config import settings
from .graph import compile_workflow, create_initial_state
from .ui import CLI

__all__ = [
    "settings",
    "compile_workflow",
    "create_initial_state",
    "CLI",
]
