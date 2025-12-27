"""
Outline templates for different document types.

These templates provide structured outlines that guide the Content Strategist
agent to create consistent, high-quality content structures.
"""

from typing import Dict, List, Any, Optional


# Blog Post Template
BLOG_POST_TEMPLATE = {
    "name": "blog_post",
    "description": "Standard blog post structure with engaging hook and practical content",
    "sections": [
        {
            "section_id": "hook",
            "title": "Introduction/Hook",
            "purpose": "Grab reader attention and introduce the topic",
            "key_points": [
                "Attention-grabbing opening",
                "Why this topic matters",
                "What readers will learn"
            ],
            "estimated_length": "150-250 words",
            "research_needed": False,
            "search_queries": []
        },
        {
            "section_id": "context",
            "title": "Background/Context",
            "purpose": "Provide necessary background information",
            "key_points": [
                "Current situation or problem",
                "Why it's relevant now",
                "Key terminology or concepts"
            ],
            "estimated_length": "200-300 words",
            "research_needed": True,
            "search_queries": [
                "{topic} current trends",
                "{topic} statistics",
                "{topic} background"
            ]
        },
        {
            "section_id": "main_content",
            "title": "Main Content",
            "purpose": "Deliver the core value and insights",
            "key_points": [
                "Primary insights or arguments",
                "Supporting evidence",
                "Multiple perspectives if relevant"
            ],
            "estimated_length": "500-800 words",
            "research_needed": True,
            "search_queries": [
                "{topic} best practices",
                "{topic} expert opinions",
                "{topic} research"
            ]
        },
        {
            "section_id": "practical",
            "title": "Practical Examples/Application",
            "purpose": "Show how to apply the information",
            "key_points": [
                "Real-world examples",
                "Step-by-step guidance if applicable",
                "Tips and recommendations"
            ],
            "estimated_length": "300-500 words",
            "research_needed": True,
            "search_queries": [
                "{topic} examples",
                "{topic} case studies",
                "{topic} how to"
            ]
        },
        {
            "section_id": "conclusion",
            "title": "Conclusion",
            "purpose": "Summarize and provide next steps",
            "key_points": [
                "Key takeaways",
                "Call to action",
                "Future outlook or next steps"
            ],
            "estimated_length": "150-250 words",
            "research_needed": False,
            "search_queries": []
        }
    ]
}


# Technical Article Template
TECHNICAL_ARTICLE_TEMPLATE = {
    "name": "technical_article",
    "description": "In-depth technical documentation or article structure",
    "sections": [
        {
            "section_id": "abstract",
            "title": "Abstract/Summary",
            "purpose": "Provide high-level overview of the technical content",
            "key_points": [
                "Problem statement",
                "Proposed solution or approach",
                "Key findings or results"
            ],
            "estimated_length": "100-150 words",
            "research_needed": False,
            "search_queries": []
        },
        {
            "section_id": "introduction",
            "title": "Introduction",
            "purpose": "Introduce the technical problem and context",
            "key_points": [
                "Technical background",
                "Problem definition",
                "Scope and objectives"
            ],
            "estimated_length": "300-400 words",
            "research_needed": True,
            "search_queries": [
                "{topic} technical overview",
                "{topic} specifications",
                "{topic} requirements"
            ]
        },
        {
            "section_id": "technical_details",
            "title": "Technical Details/Methodology",
            "purpose": "Explain the technical implementation or approach",
            "key_points": [
                "Architecture or design",
                "Implementation details",
                "Technical specifications"
            ],
            "estimated_length": "600-1000 words",
            "research_needed": True,
            "search_queries": [
                "{topic} architecture",
                "{topic} implementation",
                "{topic} technical documentation"
            ]
        },
        {
            "section_id": "results",
            "title": "Results/Performance",
            "purpose": "Present outcomes and analysis",
            "key_points": [
                "Performance metrics",
                "Comparison with alternatives",
                "Limitations and trade-offs"
            ],
            "estimated_length": "400-600 words",
            "research_needed": True,
            "search_queries": [
                "{topic} benchmarks",
                "{topic} performance",
                "{topic} comparison"
            ]
        },
        {
            "section_id": "conclusion",
            "title": "Conclusion/Future Work",
            "purpose": "Summarize findings and suggest next steps",
            "key_points": [
                "Summary of contributions",
                "Practical implications",
                "Future directions"
            ],
            "estimated_length": "200-300 words",
            "research_needed": False,
            "search_queries": []
        }
    ]
}


# Marketing Copy Template
MARKETING_COPY_TEMPLATE = {
    "name": "marketing_copy",
    "description": "Persuasive marketing content structure",
    "sections": [
        {
            "section_id": "headline",
            "title": "Headline/Value Proposition",
            "purpose": "Capture attention and communicate core value",
            "key_points": [
                "Compelling headline",
                "Unique value proposition",
                "Clear benefit statement"
            ],
            "estimated_length": "50-100 words",
            "research_needed": True,
            "search_queries": [
                "{topic} benefits",
                "{topic} value proposition"
            ]
        },
        {
            "section_id": "problem",
            "title": "Problem/Pain Points",
            "purpose": "Identify customer problems and pain points",
            "key_points": [
                "Customer challenges",
                "Current pain points",
                "Cost of inaction"
            ],
            "estimated_length": "150-250 words",
            "research_needed": True,
            "search_queries": [
                "{topic} customer problems",
                "{topic} pain points",
                "{topic} challenges"
            ]
        },
        {
            "section_id": "solution",
            "title": "Solution/Features",
            "purpose": "Present the solution and key features",
            "key_points": [
                "How it solves the problem",
                "Key features",
                "Differentiators"
            ],
            "estimated_length": "300-500 words",
            "research_needed": True,
            "search_queries": [
                "{topic} features",
                "{topic} solutions",
                "{topic} competitors"
            ]
        },
        {
            "section_id": "benefits",
            "title": "Benefits/Results",
            "purpose": "Emphasize outcomes and benefits",
            "key_points": [
                "Tangible benefits",
                "ROI or value metrics",
                "Success stories"
            ],
            "estimated_length": "200-400 words",
            "research_needed": True,
            "search_queries": [
                "{topic} results",
                "{topic} success stories",
                "{topic} ROI"
            ]
        },
        {
            "section_id": "social_proof",
            "title": "Social Proof/Testimonials",
            "purpose": "Build credibility and trust",
            "key_points": [
                "Customer testimonials",
                "Case studies",
                "Statistics or achievements"
            ],
            "estimated_length": "150-300 words",
            "research_needed": True,
            "search_queries": [
                "{topic} testimonials",
                "{topic} reviews",
                "{topic} case studies"
            ]
        },
        {
            "section_id": "cta",
            "title": "Call to Action",
            "purpose": "Drive conversion with clear next steps",
            "key_points": [
                "Clear action step",
                "Urgency or incentive",
                "Risk reversal"
            ],
            "estimated_length": "100-200 words",
            "research_needed": False,
            "search_queries": []
        }
    ]
}


# Python Tutorial Template
PYTHON_TUTORIAL_TEMPLATE = {
    "name": "python_tutorial",
    "description": "Step-by-step Python tutorial chapter for complete beginners",
    "sections": [
        {
            "section_id": "introduction",
            "title": "Chapter Introduction",
            "purpose": "Introduce the chapter topic and learning objectives",
            "key_points": [
                "What will be covered in this chapter",
                "Why this concept is important",
                "How it connects to previous chapters (if applicable)",
                "Clear learning objectives"
            ],
            "estimated_length": "150-250 words",
            "research_needed": False,
            "search_queries": [],
            "requires_code": False
        },
        {
            "section_id": "concept_explanation",
            "title": "Concept Explanation",
            "purpose": "Explain the core programming concept in beginner-friendly language",
            "key_points": [
                "Define the concept without jargon",
                "Use real-world analogies",
                "Break down complex ideas into simple parts",
                "Explain 'why' not just 'how'"
            ],
            "estimated_length": "300-500 words",
            "research_needed": True,
            "search_queries": [
                "{topic} Python beginner explanation",
                "{topic} Python simple analogy",
                "{topic} Python tutorial"
            ],
            "requires_code": False
        },
        {
            "section_id": "basic_examples",
            "title": "Basic Examples",
            "purpose": "Show simple, clear code examples that demonstrate the concept",
            "key_points": [
                "Start with the simplest possible example",
                "Add comments to explain every line",
                "Show expected output for each example",
                "Use meaningful variable names"
            ],
            "estimated_length": "200-300 words",
            "research_needed": False,
            "search_queries": [],
            "requires_code": True,
            "code_complexity": "basic",
            "num_code_examples": 2
        },
        {
            "section_id": "progressive_examples",
            "title": "Progressive Examples",
            "purpose": "Build on basic examples with slightly more complex scenarios",
            "key_points": [
                "Show how to combine concepts",
                "Introduce variations",
                "Demonstrate practical use cases",
                "Maintain beginner-appropriate complexity"
            ],
            "estimated_length": "300-400 words",
            "research_needed": False,
            "search_queries": [],
            "requires_code": True,
            "code_complexity": "intermediate",
            "num_code_examples": 3
        },
        {
            "section_id": "common_mistakes",
            "title": "Common Mistakes and How to Avoid Them",
            "purpose": "Highlight typical beginner errors and their solutions",
            "key_points": [
                "Show common errors with actual error messages",
                "Explain why the error occurs",
                "Provide the correct solution",
                "Include debugging tips"
            ],
            "estimated_length": "200-300 words",
            "research_needed": True,
            "search_queries": [
                "{topic} Python common mistakes",
                "{topic} Python errors beginners",
                "{topic} Python debugging"
            ],
            "requires_code": True,
            "code_complexity": "basic",
            "num_code_examples": 2
        },
        {
            "section_id": "practical_application",
            "title": "Practical Application",
            "purpose": "Show a real-world mini-project using the chapter's concepts",
            "key_points": [
                "Create a complete, runnable example",
                "Solve a realistic beginner problem",
                "Tie together multiple concepts from the chapter",
                "Provide step-by-step implementation guide"
            ],
            "estimated_length": "300-500 words",
            "research_needed": True,
            "search_queries": [
                "{topic} Python beginner project",
                "{topic} Python real-world example",
                "{topic} Python practical use"
            ],
            "requires_code": True,
            "code_complexity": "intermediate",
            "num_code_examples": 1
        },
        {
            "section_id": "key_takeaways",
            "title": "Key Takeaways",
            "purpose": "Summarize the chapter's main points and reinforce learning",
            "key_points": [
                "List 3-5 key points learned",
                "Quick reference of syntax covered",
                "Preview of next chapter (if applicable)",
                "Encourage further practice"
            ],
            "estimated_length": "150-200 words",
            "research_needed": False,
            "search_queries": [],
            "requires_code": False
        },
        {
            "section_id": "exercises",
            "title": "Practice Exercises",
            "purpose": "Provide hands-on exercises to reinforce understanding",
            "key_points": [
                "Include multiple choice questions for concept understanding",
                "Add fill-in-the-blank code exercises",
                "Provide coding challenges with varying difficulty",
                "Include answer key in collapsible section"
            ],
            "estimated_length": "Varies (exercises only)",
            "research_needed": False,
            "search_queries": [],
            "requires_code": False,
            "exercise_types": {
                "multiple_choice": 4,
                "fill_in_blank": 3,
                "coding_challenges": 3
            }
        }
    ]
}


# Template Registry
TEMPLATE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "blog_post": BLOG_POST_TEMPLATE,
    "blog": BLOG_POST_TEMPLATE,  # Alias
    "technical_article": TECHNICAL_ARTICLE_TEMPLATE,
    "technical": TECHNICAL_ARTICLE_TEMPLATE,  # Alias
    "article": TECHNICAL_ARTICLE_TEMPLATE,  # Alias
    "marketing_copy": MARKETING_COPY_TEMPLATE,
    "marketing": MARKETING_COPY_TEMPLATE,  # Alias
    "python_tutorial": PYTHON_TUTORIAL_TEMPLATE,
    "tutorial": PYTHON_TUTORIAL_TEMPLATE,  # Alias
}


def get_outline_template(document_type: str) -> Optional[Dict[str, Any]]:
    """
    Get an outline template by document type.

    Args:
        document_type: Type of document (blog_post, technical_article, marketing_copy, etc.)

    Returns:
        Template dictionary or None if not found

    Example:
        >>> template = get_outline_template("blog_post")
        >>> print(template["description"])
        Standard blog post structure with engaging hook and practical content
    """
    return TEMPLATE_REGISTRY.get(document_type.lower())


def list_available_templates() -> List[str]:
    """
    List all available template names.

    Returns:
        List of unique template names (aliases excluded)

    Example:
        >>> templates = list_available_templates()
        >>> print(templates)
        ['blog_post', 'technical_article', 'marketing_copy']
    """
    seen = set()
    result = []
    for name, template in TEMPLATE_REGISTRY.items():
        template_name = template["name"]
        if template_name not in seen:
            seen.add(template_name)
            result.append(template_name)
    return sorted(result)


def customize_template(
    template: Dict[str, Any],
    topic: str,
    customizations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Customize a template with topic-specific information.

    Args:
        template: Base template dictionary
        topic: The content topic
        customizations: Optional customization overrides

    Returns:
        Customized template with topic-specific search queries

    Example:
        >>> template = get_outline_template("blog_post")
        >>> custom = customize_template(template, "AI in healthcare")
        >>> print(custom["sections"][1]["search_queries"][0])
        AI in healthcare current trends
    """
    import copy
    customized = copy.deepcopy(template)

    # Replace {topic} placeholders in search queries
    for section in customized["sections"]:
        section["search_queries"] = [
            query.format(topic=topic) for query in section["search_queries"]
        ]

    # Apply custom overrides if provided
    if customizations:
        if "estimated_total_length" in customizations:
            customized["estimated_total_length"] = customizations["estimated_total_length"]
        if "additional_sections" in customizations:
            customized["sections"].extend(customizations["additional_sections"])

    return customized
