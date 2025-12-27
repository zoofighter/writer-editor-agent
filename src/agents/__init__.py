"""
Agent implementations for the Writer-Editor review loop system.

This module contains all agent implementations including node functions
for use in LangGraph workflows.
"""

from .writer import WriterAgent, writer_node
from .editor import EditorAgent, editor_node
from .business_analyst import BusinessAnalystAgent, business_analyst_node
from .content_strategist import ContentStrategistAgent, content_strategist_node
from .outline_reviewer import OutlineReviewerAgent, outline_reviewer_node
from .web_search_agent import WebSearchAgent, web_search_node
from .book_coordinator_agent import BookCoordinatorAgent, book_coordinator_node
from .bibliography_agent import BibliographyAgent, bibliography_node
from .fact_check_agent import FactCheckAgent, fact_check_node
from .math_formula_agent import MathFormulaAgent, math_formula_node
from .diagram_agent import DiagramAgent, diagram_node
from .cross_reference_agent import CrossReferenceAgent, cross_reference_node

# Tutorial book agents
try:
    from .code_example_generator import CodeExampleGeneratorAgent, code_example_generator_node
    from .exercise_generator import ExerciseGeneratorAgent, exercise_generator_node
    _tutorial_agents_available = True
except ImportError:
    _tutorial_agents_available = False

__all__ = [
    # Original agent classes
    "WriterAgent",
    "EditorAgent",
    "BusinessAnalystAgent",
    "ContentStrategistAgent",
    "OutlineReviewerAgent",
    "WebSearchAgent",
    # Book system agent classes
    "BookCoordinatorAgent",
    "BibliographyAgent",
    "FactCheckAgent",
    "MathFormulaAgent",
    "DiagramAgent",
    "CrossReferenceAgent",
    # Original node functions
    "writer_node",
    "editor_node",
    "business_analyst_node",
    "content_strategist_node",
    "outline_reviewer_node",
    "web_search_node",
    # Book system node functions
    "book_coordinator_node",
    "bibliography_node",
    "fact_check_node",
    "math_formula_node",
    "diagram_node",
    "cross_reference_node",
]

# Add tutorial agents to exports if available
if _tutorial_agents_available:
    __all__.extend([
        "CodeExampleGeneratorAgent",
        "ExerciseGeneratorAgent",
        "code_example_generator_node",
        "exercise_generator_node",
    ])
