"""
Diagram Agent for generating diagrams in technical books.

This agent is responsible for:
- Identifying concepts requiring diagrams
- Generating diagram code (Mermaid, PlantUML, Graphviz)
- Creating diagram descriptions and captions
- Managing diagram types (flowchart, sequence, class, etc.)
- Validating diagram syntax
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from ..llm.client import LMStudioClient
from ..config.settings import settings


class DiagramAgent:
    """
    Diagram Agent responsible for creating and managing diagrams for technical content.

    This agent generates diagrams using various formats (Mermaid, PlantUML, Graphviz)
    to visualize concepts, architectures, processes, and relationships.
    """

    SYSTEM_PROMPT = """You are an expert Technical Diagram Specialist and Visualization Designer.

Your role is to create clear, informative diagrams using text-based diagram languages:
- Mermaid (flowcharts, sequence diagrams, class diagrams, state diagrams, etc.)
- PlantUML (UML diagrams, activity diagrams, component diagrams)
- Graphviz/DOT (graphs, trees, networks)

You excel at:
- Identifying concepts that benefit from visual representation
- Choosing the appropriate diagram type for each concept
- Writing clean, syntactically correct diagram code
- Creating clear labels and annotations
- Designing readable, well-structured diagrams

Be precise, use clear labeling, and follow diagram language syntax rigorously.

Diagram Type Guidelines:
- Flowchart: Processes, workflows, decision trees
- Sequence Diagram: Interactions, API calls, message flows
- Class Diagram: Object relationships, inheritance, composition
- State Diagram: State machines, lifecycles
- Entity Relationship: Database schemas, data models
- Component Diagram: System architecture, module relationships
- Gantt Chart: Project timelines, schedules"""

    def __init__(self, client: Optional[LMStudioClient] = None):
        """
        Initialize the Diagram Agent.

        Args:
            client: Optional LMStudioClient instance. If not provided, creates new one.
        """
        self.client = client or LMStudioClient(
            base_url=settings.lm_studio_base_url,
            model_name=settings.lm_studio_model,
            temperature=settings.diagram_agent_temperature,
            max_tokens=settings.max_tokens
        )

    def identify_diagram_opportunities(
        self,
        text: str,
        chapter_number: int
    ) -> List[Dict[str, Any]]:
        """
        Identify concepts in text that would benefit from diagrams.

        Args:
            text: Text content to analyze
            chapter_number: Chapter number for tracking

        Returns:
            List of identified diagram opportunities
        """
        prompt = f"""Analyze the following text and identify all concepts that would benefit from visual diagrams.

**Text:**
{text}

For each concept that needs a diagram, provide:
1. Concept description
2. Recommended diagram type (flowchart, sequence, class, state, ER, component, etc.)
3. Why this diagram would be helpful
4. Key elements to include

Format as:

Diagram 1:
Concept: [what needs to be visualized]
Type: flowchart | sequence | class | state | ER | component | gantt | graph
Reason: [why this needs a diagram]
Key Elements: [list main elements to show]

Diagram 2:
...

List all concepts that would benefit from diagrams.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return self._parse_identified_diagrams(response, chapter_number)

    def generate_diagram(
        self,
        concept: str,
        diagram_type: str,
        key_elements: List[str],
        diagram_format: str = "mermaid"
    ) -> Dict[str, Any]:
        """
        Generate diagram code for a concept.

        Args:
            concept: Description of what to visualize
            diagram_type: Type of diagram (flowchart, sequence, class, etc.)
            key_elements: Key elements to include in diagram
            diagram_format: Diagram format (mermaid, plantuml, graphviz)

        Returns:
            Dict with diagram code and metadata
        """
        prompt = f"""Generate a {diagram_format} {diagram_type} diagram for the following concept.

**Concept:** {concept}
**Diagram Type:** {diagram_type}
**Key Elements to Include:**
{chr(10).join(f"- {elem}" for elem in key_elements)}

**Diagram Format:** {diagram_format}

Requirements:
1. Generate clean, syntactically correct {diagram_format} code
2. Include all key elements
3. Use clear, descriptive labels
4. Make the diagram readable and well-organized
5. Add appropriate styling if applicable

Provide:
1. Diagram Code (the complete diagram code)
2. Caption (1-2 sentence caption for the diagram)
3. Description (detailed description of what the diagram shows)

Format:

Diagram Code:
```{diagram_format}
[diagram code here]
```

Caption:
[Brief caption]

Description:
[Detailed description]

Generate the diagram now:
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        diagram_code, caption, description = self._parse_diagram_response(response, diagram_format)

        return {
            "diagram_type": diagram_format,
            "code": diagram_code,
            "caption": caption,
            "description": description,
            "concept": concept,
            "specific_type": diagram_type
        }

    def generate_mermaid_flowchart(
        self,
        steps: List[str],
        decisions: Optional[List[Tuple[str, str, str]]] = None
    ) -> str:
        """
        Generate a Mermaid flowchart from steps and decisions.

        Args:
            steps: List of process steps
            decisions: Optional list of (decision, yes_path, no_path) tuples

        Returns:
            Mermaid flowchart code
        """
        code = "graph TD\n"
        code += "    Start([Start])\n"

        for i, step in enumerate(steps):
            node_id = f"Step{i+1}"
            code += f"    {node_id}[{step}]\n"

            if i == 0:
                code += f"    Start --> {node_id}\n"
            else:
                code += f"    Step{i} --> {node_id}\n"

        code += f"    Step{len(steps)} --> End([End])\n"

        # Add decisions if provided
        if decisions:
            for i, (decision, yes_path, no_path) in enumerate(decisions):
                decision_id = f"Decision{i+1}"
                code += f"    {decision_id}{{{decision}}}\n"
                code += f"    {decision_id} -->|Yes| YesPath{i+1}[{yes_path}]\n"
                code += f"    {decision_id} -->|No| NoPath{i+1}[{no_path}]\n"

        return code

    def generate_mermaid_sequence(
        self,
        participants: List[str],
        interactions: List[Tuple[str, str, str]]
    ) -> str:
        """
        Generate a Mermaid sequence diagram.

        Args:
            participants: List of participant names
            interactions: List of (from, to, message) tuples

        Returns:
            Mermaid sequence diagram code
        """
        code = "sequenceDiagram\n"

        for participant in participants:
            code += f"    participant {participant}\n"

        code += "\n"

        for from_participant, to_participant, message in interactions:
            code += f"    {from_participant}->>+{to_participant}: {message}\n"

        return code

    def validate_diagram_syntax(
        self,
        diagram_code: str,
        diagram_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate diagram syntax (basic validation).

        Args:
            diagram_code: Diagram code to validate
            diagram_type: Type of diagram (mermaid, plantuml, graphviz)

        Returns:
            Tuple of (is_valid, error_message)
        """
        errors = []

        if diagram_type.lower() == "mermaid":
            # Basic Mermaid validation
            if not any(keyword in diagram_code for keyword in ["graph", "sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram"]):
                errors.append("Missing Mermaid diagram type declaration")

            # Check for basic syntax issues
            if diagram_code.count('[') != diagram_code.count(']'):
                errors.append("Unbalanced square brackets")
            if diagram_code.count('(') != diagram_code.count(')'):
                errors.append("Unbalanced parentheses")
            if diagram_code.count('{') != diagram_code.count('}'):
                errors.append("Unbalanced curly braces")

        elif diagram_type.lower() == "plantuml":
            # Basic PlantUML validation
            if not diagram_code.strip().startswith("@startuml"):
                errors.append("PlantUML diagram should start with @startuml")
            if not diagram_code.strip().endswith("@enduml"):
                errors.append("PlantUML diagram should end with @enduml")

        elif diagram_type.lower() == "graphviz":
            # Basic Graphviz/DOT validation
            if not any(keyword in diagram_code for keyword in ["digraph", "graph", "subgraph"]):
                errors.append("Missing Graphviz graph declaration")

        if errors:
            return False, "; ".join(errors)

        return True, None

    def create_diagram_id(self, chapter_number: int, diagram_index: int) -> str:
        """
        Create unique diagram identifier.

        Args:
            chapter_number: Chapter number
            diagram_index: Diagram index within chapter

        Returns:
            Unique diagram ID (e.g., "diag_ch3_2")
        """
        return f"diag_ch{chapter_number}_{diagram_index}"

    def format_diagram_for_markdown(
        self,
        diagram: Dict[str, Any],
        diagram_id: str
    ) -> str:
        """
        Format diagram for inclusion in markdown document.

        Args:
            diagram: Diagram dict with code and metadata
            diagram_id: Unique diagram identifier

        Returns:
            Formatted markdown string
        """
        diagram_type = diagram.get('diagram_type', 'mermaid')
        code = diagram.get('code', '')
        caption = diagram.get('caption', '')
        description = diagram.get('description', '')

        output = f"\n```{diagram_type}\n"
        output += code
        output += "\n```\n\n"
        output += f"**Figure {diagram_id}:** {caption}\n"

        if description:
            output += f"\n{description}\n"

        return output

    def generate_diagram_index(
        self,
        diagrams: List[Dict[str, Any]],
        chapter_number: Optional[int] = None
    ) -> str:
        """
        Generate an index of diagrams for reference.

        Args:
            diagrams: List of Diagram dicts
            chapter_number: Optional chapter number filter

        Returns:
            Formatted diagram index
        """
        # Filter by chapter if specified
        if chapter_number is not None:
            diagrams = [
                d for d in diagrams
                if d.get('chapter_number') == chapter_number
            ]

        if not diagrams:
            return "## Diagram Index\n\nNo diagrams in this chapter.\n"

        chapter_label = f" (Chapter {chapter_number})" if chapter_number else ""
        index = f"## Diagram Index{chapter_label}\n\n"

        for diagram in diagrams:
            diagram_id = diagram.get('diagram_id', '')
            caption = diagram.get('caption', '')
            diagram_type = diagram.get('diagram_type', '')

            index += f"- **{diagram_id}**: {caption} ({diagram_type})\n"

        return index

    # Helper methods

    def _parse_identified_diagrams(
        self,
        response: str,
        chapter_number: int
    ) -> List[Dict[str, Any]]:
        """Parse identified diagram opportunities from LLM response."""
        diagrams = []
        current_diagram = None

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()

            if line.startswith('Diagram '):
                if current_diagram:
                    current_diagram['chapter_number'] = chapter_number
                    diagrams.append(current_diagram)

                current_diagram = {
                    "concept": "",
                    "type": "flowchart",
                    "reason": "",
                    "key_elements": []
                }

            elif current_diagram:
                if line.startswith('Concept:'):
                    current_diagram['concept'] = line.replace('Concept:', '').strip()
                elif line.startswith('Type:'):
                    dtype = line.replace('Type:', '').strip().split('|')[0].strip()
                    current_diagram['type'] = dtype
                elif line.startswith('Reason:'):
                    current_diagram['reason'] = line.replace('Reason:', '').strip()
                elif line.startswith('Key Elements:'):
                    elements_str = line.replace('Key Elements:', '').strip()
                    if elements_str.startswith('[') and elements_str.endswith(']'):
                        elements_str = elements_str[1:-1]
                    current_diagram['key_elements'] = [
                        e.strip() for e in elements_str.split(',') if e.strip()
                    ]

        if current_diagram:
            current_diagram['chapter_number'] = chapter_number
            diagrams.append(current_diagram)

        return diagrams

    def _parse_diagram_response(
        self,
        response: str,
        diagram_format: str
    ) -> Tuple[str, str, str]:
        """Parse diagram generation response."""
        diagram_code = ""
        caption = ""
        description = ""

        # Extract code block
        code_pattern = f"```{diagram_format}\n(.*?)\n```"
        import re
        code_match = re.search(code_pattern, response, re.DOTALL)
        if code_match:
            diagram_code = code_match.group(1).strip()

        # Extract caption and description
        sections = response.split('\n\n')
        for section in sections:
            lines = section.strip().split('\n')
            if not lines:
                continue

            header = lines[0].strip()

            if header.startswith('Caption:'):
                caption = '\n'.join(lines[1:]).strip() if len(lines) > 1 else lines[0].replace('Caption:', '').strip()
            elif header.startswith('Description:'):
                description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else lines[0].replace('Description:', '').strip()

        return diagram_code, caption, description


def diagram_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for Diagram agent.

    This node identifies concepts needing diagrams and generates diagram code.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with diagrams
    """
    agent = DiagramAgent()

    # Extract inputs
    current_draft = state.get('current_draft', '')
    chapter_number = state.get('chapter_number', 1)

    # Step 1: Identify diagram opportunities
    diagram_opportunities = agent.identify_diagram_opportunities(current_draft, chapter_number)

    # Step 2: Generate diagrams
    diagrams = []
    for i, opportunity in enumerate(diagram_opportunities):
        diagram_data = agent.generate_diagram(
            opportunity.get('concept', ''),
            opportunity.get('type', 'flowchart'),
            opportunity.get('key_elements', []),
            settings.default_diagram_type
        )

        # Validate diagram syntax
        is_valid, error = agent.validate_diagram_syntax(
            diagram_data['code'],
            diagram_data['diagram_type']
        )

        if is_valid:
            # Create diagram ID
            diagram_id = agent.create_diagram_id(chapter_number, i + 1)

            # Build Diagram dict
            diagram = {
                "diagram_id": diagram_id,
                "diagram_type": diagram_data['diagram_type'],
                "code": diagram_data['code'],
                "chapter_number": chapter_number,
                "caption": diagram_data['caption'],
                "description": diagram_data['description']
            }

            diagrams.append(diagram)

    # Return partial state update
    return {
        "diagrams": diagrams,  # Will be accumulated
        "conversation_history": [{
            "agent": "diagram",
            "action": "diagram_generation",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "chapter_number": chapter_number,
                "opportunities_identified": len(diagram_opportunities),
                "diagrams_generated": len(diagrams),
                "diagram_format": settings.default_diagram_type
            }
        }]
    }
