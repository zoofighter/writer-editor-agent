"""
Exercise Generator Agent for creating Python tutorial practice exercises.

This agent specializes in generating various types of educational exercises:
- Multiple choice questions for concept understanding
- Fill-in-the-blank code exercises
- Coding challenges with varying difficulty levels
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from ..llm.client import LMStudioClient
from ..graph.state import (
    MultipleChoiceQuestion,
    FillInBlankExercise,
    CodingChallenge,
    ChapterExercises
)
from ..config.settings import settings


class ExerciseGeneratorAgent:
    """
    Specialized agent for generating tutorial practice exercises.

    Uses a moderate temperature (0.4) to balance creativity in question
    generation with consistency in format and correctness.
    """

    SYSTEM_PROMPT = """You are an educational assessment specialist focused on teaching Python to complete beginners.

Your role is to create high-quality practice exercises that reinforce learning and assess understanding.

When creating exercises:
1. **Align with Content**: Exercises must directly relate to what was just taught
2. **Progressive Difficulty**: Start easy, build to moderate challenge
3. **Clear Instructions**: Beginners must understand exactly what's being asked
4. **Constructive Feedback**: Explanations should teach, not just correct
5. **Realistic Scenarios**: Use practical, relatable examples
6. **Avoid Tricks**: Test understanding, not ability to spot gotchas

**Critical**: Output valid JSON in the exact format requested. No markdown, no extra text."""

    MC_GENERATION_PROMPT = """Generate {num_questions} multiple choice questions about: {concept}

Chapter context:
{context}

Code examples shown:
{code_examples}

Requirements for EACH question:
- Test conceptual understanding (not just syntax memorization)
- 4 answer options
- Only ONE correct answer
- Distractors should be plausible but clearly wrong to someone who understood the concept
- Explanation should teach WHY the answer is correct

Output as JSON array:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Why this is correct and others are wrong"
  }},
  ...
]

Output ONLY the JSON array, no markdown or extra text."""

    FILL_IN_BLANK_PROMPT = """Generate {num_exercises} fill-in-the-blank coding exercises about: {concept}

Chapter context:
{context}

Code examples shown:
{code_examples}

Requirements for EACH exercise:
- Code template with one blank to fill (mark as _____ or [BLANK])
- The blank should be a key concept from the chapter
- Description of what the code should accomplish
- Correct answer that completes the code
- Optional hint (if the blank is tricky)

Output as JSON array:
[
  {{
    "description": "What this code does",
    "code_template": "Code with _____ for blank",
    "correct_answer": "What goes in the blank",
    "hint": "Optional hint or null"
  }},
  ...
]

Output ONLY the JSON array, no markdown or extra text."""

    CODING_CHALLENGE_PROMPT = """Generate {num_challenges} coding challenges about: {concept}

Difficulty level: {difficulty}
Chapter context:
{context}

Code examples shown:
{code_examples}

Requirements for EACH challenge:
- Clear problem description
- Realistic beginner scenario
- Difficulty: {difficulty}
  - easy: Direct application of what was taught
  - medium: Combine 2-3 concepts
  - hard: Requires thinking beyond examples
- Optional starter code template
- Complete solution code with comments
- 2-3 test cases showing input/output
- Optional hints (especially for medium/hard)

Output as JSON array:
[
  {{
    "title": "Short challenge title",
    "description": "Detailed problem description",
    "difficulty": "{difficulty}",
    "starter_code": "Optional template or null",
    "solution": "Complete solution with comments",
    "test_cases": [
      {{"input": "input description", "output": "expected output"}},
      ...
    ],
    "hints": ["hint 1", "hint 2"] or null
  }},
  ...
]

Output ONLY the JSON array, no markdown or extra text."""

    def __init__(self, llm_client: LMStudioClient):
        """
        Initialize the Exercise Generator Agent.

        Args:
            llm_client: LM Studio client configured for exercise generation
                       (should use moderate temperature ~0.4)
        """
        self.llm_client = llm_client

    def generate_multiple_choice(
        self,
        concept: str,
        chapter_content: str,
        code_examples: List[str],
        num_questions: int = 4
    ) -> List[MultipleChoiceQuestion]:
        """
        Generate multiple choice questions for concept understanding.

        Args:
            concept: The main concept being tested
            chapter_content: Full chapter text for context
            code_examples: Code examples from the chapter
            num_questions: Number of questions to generate

        Returns:
            List of MultipleChoiceQuestion dictionaries

        Example:
            >>> agent = ExerciseGeneratorAgent(llm_client)
            >>> questions = agent.generate_multiple_choice(
            ...     "for loops",
            ...     "Chapter content here...",
            ...     ["for i in range(5):\\n    print(i)"],
            ...     num_questions=3
            ... )
            >>> assert len(questions) == 3
        """
        code_examples_str = "\n\n".join(
            f"Example {i+1}:\n{code}" for i, code in enumerate(code_examples)
        ) if code_examples else "No code examples"

        prompt = self.MC_GENERATION_PROMPT.format(
            num_questions=num_questions,
            concept=concept,
            context=chapter_content[:500],  # Truncate for context
            code_examples=code_examples_str[:500]
        )

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.llm_client.generate(messages)
        questions = self._parse_json_response(response, expected_count=num_questions)

        # Validate and convert to TypedDict format
        validated_questions = []
        for q in questions:
            if self._validate_mc_question(q):
                validated_questions.append(q)

        # If we didn't get enough valid questions, pad with a fallback
        while len(validated_questions) < num_questions:
            validated_questions.append(self._create_fallback_mc_question(concept))

        return validated_questions[:num_questions]

    def generate_fill_in_blank(
        self,
        concept: str,
        chapter_content: str,
        code_examples: List[str],
        num_exercises: int = 3
    ) -> List[FillInBlankExercise]:
        """
        Generate fill-in-the-blank code exercises.

        Args:
            concept: The concept being practiced
            chapter_content: Full chapter text for context
            code_examples: Code examples from the chapter
            num_exercises: Number of exercises to generate

        Returns:
            List of FillInBlankExercise dictionaries

        Example:
            >>> exercises = agent.generate_fill_in_blank(
            ...     "variables",
            ...     "Chapter content...",
            ...     ["x = 5"],
            ...     num_exercises=2
            ... )
            >>> assert len(exercises) == 2
        """
        code_examples_str = "\n\n".join(
            f"Example {i+1}:\n{code}" for i, code in enumerate(code_examples)
        ) if code_examples else "No code examples"

        prompt = self.FILL_IN_BLANK_PROMPT.format(
            num_exercises=num_exercises,
            concept=concept,
            context=chapter_content[:500],
            code_examples=code_examples_str[:500]
        )

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.llm_client.generate(messages)
        exercises = self._parse_json_response(response, expected_count=num_exercises)

        # Validate and convert
        validated_exercises = []
        for ex in exercises:
            if self._validate_fill_in_blank(ex):
                validated_exercises.append(ex)

        # Pad if needed
        while len(validated_exercises) < num_exercises:
            validated_exercises.append(self._create_fallback_fill_in_blank(concept))

        return validated_exercises[:num_exercises]

    def generate_coding_challenges(
        self,
        concept: str,
        chapter_content: str,
        code_examples: List[str],
        difficulty: str = "easy",
        num_challenges: int = 3
    ) -> List[CodingChallenge]:
        """
        Generate coding challenges for practice.

        Args:
            concept: The concept to practice
            chapter_content: Full chapter text for context
            code_examples: Code examples from the chapter
            difficulty: Difficulty level (easy, medium, hard)
            num_challenges: Number of challenges to generate

        Returns:
            List of CodingChallenge dictionaries

        Example:
            >>> challenges = agent.generate_coding_challenges(
            ...     "functions",
            ...     "Chapter content...",
            ...     ["def greet():\\n    print('hi')"],
            ...     difficulty="easy",
            ...     num_challenges=2
            ... )
            >>> assert len(challenges) == 2
        """
        code_examples_str = "\n\n".join(
            f"Example {i+1}:\n{code}" for i, code in enumerate(code_examples)
        ) if code_examples else "No code examples"

        prompt = self.CODING_CHALLENGE_PROMPT.format(
            num_challenges=num_challenges,
            concept=concept,
            difficulty=difficulty,
            context=chapter_content[:500],
            code_examples=code_examples_str[:500]
        )

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.llm_client.generate(messages)
        challenges = self._parse_json_response(response, expected_count=num_challenges)

        # Validate and convert
        validated_challenges = []
        for ch in challenges:
            if self._validate_coding_challenge(ch):
                validated_challenges.append(ch)

        # Pad if needed
        while len(validated_challenges) < num_challenges:
            validated_challenges.append(self._create_fallback_coding_challenge(concept, difficulty))

        return validated_challenges[:num_challenges]

    def _parse_json_response(self, response: str, expected_count: int) -> List[Dict]:
        """
        Parse JSON response from LLM, handling various formats.

        Args:
            response: Raw LLM response
            expected_count: Expected number of items

        Returns:
            List of dictionaries
        """
        # Remove markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            cleaned = '\n'.join(lines[1:-1])  # Remove first and last line

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return [parsed]  # Single item
            else:
                return []
        except json.JSONDecodeError:
            # Fallback: return empty list
            print(f"Warning: Failed to parse JSON response: {cleaned[:100]}...")
            return []

    def _validate_mc_question(self, q: Dict) -> bool:
        """Check if MC question has required fields."""
        required = ["question", "options", "correct_answer", "explanation"]
        return (all(field in q for field in required) and
                isinstance(q["options"], list) and
                len(q["options"]) >= 2 and
                isinstance(q["correct_answer"], int) and
                0 <= q["correct_answer"] < len(q["options"]))

    def _validate_fill_in_blank(self, ex: Dict) -> bool:
        """Check if fill-in-blank exercise has required fields."""
        required = ["description", "code_template", "correct_answer"]
        return all(field in ex for field in required)

    def _validate_coding_challenge(self, ch: Dict) -> bool:
        """Check if coding challenge has required fields."""
        required = ["title", "description", "difficulty", "solution", "test_cases"]
        return (all(field in ch for field in required) and
                isinstance(ch["test_cases"], list))

    def _create_fallback_mc_question(self, concept: str) -> MultipleChoiceQuestion:
        """Create a fallback MC question if generation fails."""
        return {
            "question": f"Which statement about {concept} is correct?",
            "options": [
                f"{concept} is an important Python concept",
                f"{concept} is not used in Python",
                f"{concept} only works in Python 2",
                f"{concept} is deprecated"
            ],
            "correct_answer": 0,
            "explanation": f"{concept} is indeed an important Python concept covered in this chapter."
        }

    def _create_fallback_fill_in_blank(self, concept: str) -> FillInBlankExercise:
        """Create a fallback fill-in-blank exercise if generation fails."""
        return {
            "description": f"Complete this code that demonstrates {concept}",
            "code_template": f"# TODO: Add code demonstrating {concept}\n_____",
            "correct_answer": f"# Code for {concept}",
            "hint": "Review the examples in the chapter"
        }

    def _create_fallback_coding_challenge(self, concept: str, difficulty: str) -> CodingChallenge:
        """Create a fallback coding challenge if generation fails."""
        return {
            "title": f"Practice {concept}",
            "description": f"Write a program that demonstrates your understanding of {concept}.",
            "difficulty": difficulty,
            "starter_code": f"# Write your code here using {concept}",
            "solution": f"# Solution demonstrating {concept}\npass",
            "test_cases": [{"input": "N/A", "output": f"Demonstrates {concept}"}],
            "hints": [f"Review the {concept} section in this chapter"]
        }


# Node function for LangGraph integration
def exercise_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for generating chapter exercises.

    Generates multiple choice questions, fill-in-the-blank exercises,
    and coding challenges based on the chapter content.

    Args:
        state: Workflow state containing draft, code examples, and chapter info

    Returns:
        Updated state with chapter_exercises populated

    Example:
        >>> state = {
        ...     "current_draft": "Chapter content...",
        ...     "code_examples_by_section": {...},
        ...     "chapter_number": 1
        ... }
        >>> updated_state = exercise_generator_node(state)
        >>> assert "chapter_exercises" in updated_state
    """
    from ..llm.client import LMStudioClient

    # Initialize LLM client with moderate temperature for exercise generation
    llm_client = LMStudioClient(
        base_url=settings.lm_studio_base_url,
        model_name=settings.lm_studio_model,
        temperature=getattr(settings, 'exercise_generator_temperature', 0.4),
        max_tokens=settings.max_tokens
    )

    agent = ExerciseGeneratorAgent(llm_client)

    # Extract context from state
    chapter_content = state.get("current_draft", "")
    code_examples_by_section = state.get("code_examples_by_section", {})
    chapter_number = state.get("chapter_number", 1)
    topic = state.get("topic", "Python programming")

    # Flatten all code examples
    all_code_examples = []
    for examples in code_examples_by_section.values():
        all_code_examples.extend(examples)

    # Generate exercises
    try:
        mc_questions = agent.generate_multiple_choice(
            concept=topic,
            chapter_content=chapter_content,
            code_examples=all_code_examples,
            num_questions=getattr(settings, 'mc_questions_per_chapter', 4)
        )

        fill_in_blank = agent.generate_fill_in_blank(
            concept=topic,
            chapter_content=chapter_content,
            code_examples=all_code_examples,
            num_exercises=getattr(settings, 'fill_in_blank_per_chapter', 3)
        )

        coding_challenges = agent.generate_coding_challenges(
            concept=topic,
            chapter_content=chapter_content,
            code_examples=all_code_examples,
            difficulty="easy",
            num_challenges=getattr(settings, 'coding_challenges_per_chapter', 3)
        )

        exercises: ChapterExercises = {
            "chapter_number": chapter_number,
            "multiple_choice": mc_questions,
            "fill_in_blank": fill_in_blank,
            "coding_challenges": coding_challenges,
            "timestamp": datetime.now().isoformat()
        }

        return {
            "chapter_exercises": exercises,
            "conversation_history": [{
                "role": "system",
                "content": f"Generated {len(mc_questions)} MC, {len(fill_in_blank)} fill-in-blank, "
                          f"and {len(coding_challenges)} coding challenges",
                "timestamp": datetime.now().isoformat()
            }]
        }

    except Exception as e:
        print(f"Error generating exercises: {e}")
        # Return minimal exercises on error
        return {
            "chapter_exercises": {
                "chapter_number": chapter_number,
                "multiple_choice": [],
                "fill_in_blank": [],
                "coding_challenges": [],
                "timestamp": datetime.now().isoformat()
            },
            "conversation_history": [{
                "role": "system",
                "content": f"Exercise generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }]
        }
