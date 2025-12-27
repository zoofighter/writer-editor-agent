"""
Fact Check Agent for verifying claims in historical and technical books.

This agent is responsible for:
- Identifying factual claims in content
- Verifying claims against reliable sources
- Providing verification status and confidence scores
- Tracking sources for fact-checking
- Generating fact-check reports
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..llm.client import LMStudioClient
from ..config.settings import settings


class FactCheckAgent:
    """
    Fact Check Agent responsible for verifying factual claims in book content.

    This agent is particularly important for historical books, technical guides,
    and any content making factual claims that need verification.
    """

    SYSTEM_PROMPT = """You are an expert Fact Checker and Verification Specialist.

Your role is to identify and verify factual claims in written content, ensuring:
- Accurate identification of verifiable claims
- Rigorous fact-checking against reliable sources
- Clear verification status and confidence assessment
- Proper source attribution for verified facts

You excel at:
- Distinguishing factual claims from opinions or interpretations
- Assessing source reliability and credibility
- Identifying potential inaccuracies or disputed claims
- Providing nuanced verification statuses
- Explaining verification reasoning

Be thorough, objective, and precise in your fact-checking. Always distinguish between:
- Verified facts (strong evidence from multiple reliable sources)
- Unverified claims (insufficient evidence, needs more sources)
- Disputed facts (conflicting evidence or interpretations)
- False claims (contradicted by reliable evidence)

Provide confidence scores (0.0-1.0) for your assessments."""

    def __init__(self, client: Optional[LMStudioClient] = None):
        """
        Initialize the Fact Check Agent.

        Args:
            client: Optional LMStudioClient instance. If not provided, creates new one.
        """
        self.client = client or LMStudioClient(
            base_url=settings.lm_studio_base_url,
            model_name=settings.lm_studio_model,
            temperature=settings.fact_check_agent_temperature,
            max_tokens=settings.max_tokens
        )

    def identify_claims(
        self,
        text: str,
        chapter_number: int
    ) -> List[Dict[str, Any]]:
        """
        Identify factual claims in text that require verification.

        Args:
            text: Text content to analyze
            chapter_number: Chapter number for tracking

        Returns:
            List of identified claims with metadata
        """
        prompt = f"""Analyze the following text and identify all factual claims that can be verified.

**Text:**
{text}

For each factual claim, extract:
1. The exact claim statement
2. Claim type (historical fact, date, statistic, technical specification, etc.)
3. Why this claim needs verification
4. What would be needed to verify it

Do NOT extract:
- Opinions or subjective statements
- General knowledge that doesn't need citation
- Hypothetical scenarios

Format as:

Claim 1:
Statement: [exact claim]
Type: historical fact | date | statistic | technical spec | etc
Needs Verification: [reason]
Verification Method: [what sources/evidence needed]

Claim 2:
...

List all verifiable factual claims.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return self._parse_identified_claims(response, chapter_number)

    def verify_claim(
        self,
        claim: str,
        research_data: Optional[List[Dict[str, Any]]] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a factual claim using available research data.

        Args:
            claim: The claim to verify
            research_data: Optional list of search results for verification
            context: Optional additional context

        Returns:
            FactCheckResult dict with verification status and sources
        """
        prompt = f"""Verify the following factual claim using the provided sources.

**Claim to Verify:**
{claim}
"""

        if context:
            prompt += f"""
**Context:**
{context}
"""

        if research_data:
            prompt += "\n**Available Sources:**\n"
            for i, source in enumerate(research_data[:10], 1):  # Limit to top 10 sources
                prompt += f"""
Source {i}:
Title: {source.get('title', 'Unknown')}
URL: {source.get('url', 'N/A')}
Snippet: {source.get('snippet', '')}
---
"""

        prompt += """
Based on the available sources, provide a fact-check assessment:

1. **Verification Status:** Choose ONE:
   - verified: Claim is supported by reliable sources
   - unverified: Insufficient evidence to confirm or deny
   - disputed: Conflicting evidence or interpretations exist
   - false: Claim is contradicted by reliable evidence

2. **Confidence Score:** (0.0-1.0)
   - 1.0 = Absolutely certain
   - 0.7-0.9 = High confidence
   - 0.5-0.7 = Moderate confidence
   - 0.3-0.5 = Low confidence
   - < 0.3 = Very uncertain

3. **Supporting Sources:** List source numbers that support the verification

4. **Notes:** Explain your verification reasoning, including:
   - Key evidence supporting your assessment
   - Any caveats or nuances
   - Suggestions for strengthening the claim if needed

Format:

Verification Status: [verified/unverified/disputed/false]
Confidence Score: [0.0-1.0]
Supporting Sources: [list source numbers or URLs]
Notes: [detailed explanation]
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = self.client.generate(messages)

        return self._parse_verification_result(response, claim, research_data)

    def batch_verify_claims(
        self,
        claims: List[str],
        research_by_section: Optional[Dict[str, Any]] = None,
        chapter_number: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Verify multiple claims in batch.

        Args:
            claims: List of claims to verify
            research_by_section: Research data organized by section
            chapter_number: Chapter number for tracking

        Returns:
            List of FactCheckResult dicts
        """
        results = []

        for claim in claims:
            # Find relevant research data for this claim
            relevant_research = self._find_relevant_research(claim, research_by_section)

            # Verify the claim
            verification = self.verify_claim(claim, relevant_research)
            verification['chapter_number'] = chapter_number

            results.append(verification)

        return results

    def generate_fact_check_report(
        self,
        fact_check_results: List[Dict[str, Any]],
        chapter_number: Optional[int] = None
    ) -> str:
        """
        Generate a fact-check report from verification results.

        Args:
            fact_check_results: List of FactCheckResult dicts
            chapter_number: Optional chapter number filter

        Returns:
            Formatted fact-check report
        """
        # Filter by chapter if specified
        if chapter_number is not None:
            fact_check_results = [
                r for r in fact_check_results
                if r.get('chapter_number') == chapter_number
            ]

        if not fact_check_results:
            return "## Fact-Check Report\n\nNo claims verified.\n"

        # Count by status
        status_counts = {
            'verified': 0,
            'unverified': 0,
            'disputed': 0,
            'false': 0
        }

        for result in fact_check_results:
            status = result.get('verification_status', 'unverified')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Build report
        chapter_label = f" (Chapter {chapter_number})" if chapter_number else ""
        report = f"""## Fact-Check Report{chapter_label}

**Summary:**
- Total Claims Verified: {len(fact_check_results)}
- Verified: {status_counts['verified']}
- Unverified: {status_counts['unverified']}
- Disputed: {status_counts['disputed']}
- False: {status_counts['false']}

**Detailed Results:**

"""

        # Group by status
        for status in ['false', 'disputed', 'unverified', 'verified']:
            status_results = [r for r in fact_check_results if r.get('verification_status') == status]

            if status_results:
                report += f"### {status.upper()} Claims ({len(status_results)})\n\n"

                for i, result in enumerate(status_results, 1):
                    confidence = result.get('confidence_score', 0.0)
                    claim = result.get('claim', 'Unknown claim')
                    notes = result.get('notes', 'No notes provided')
                    sources = result.get('sources', [])

                    report += f"""**{i}. {claim}**
- Confidence: {confidence:.2f}
- Sources: {', '.join(sources) if sources else 'None'}
- Notes: {notes}

"""

        return report

    def assess_overall_reliability(
        self,
        fact_check_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess overall reliability of book content based on fact-check results.

        Args:
            fact_check_results: List of all FactCheckResult dicts

        Returns:
            Overall reliability assessment dict
        """
        if not fact_check_results:
            return {
                "overall_score": 0.0,
                "assessment": "No fact-checking performed",
                "recommendation": "Consider fact-checking claims"
            }

        # Calculate metrics
        total = len(fact_check_results)
        verified = sum(1 for r in fact_check_results if r.get('verification_status') == 'verified')
        false_claims = sum(1 for r in fact_check_results if r.get('verification_status') == 'false')
        avg_confidence = sum(r.get('confidence_score', 0.0) for r in fact_check_results) / total

        # Calculate overall score (0.0-1.0)
        verified_ratio = verified / total
        false_ratio = false_claims / total
        overall_score = (verified_ratio * 0.5 + avg_confidence * 0.5) * (1 - false_ratio)

        # Determine assessment
        if overall_score >= 0.8:
            assessment = "Highly Reliable"
            recommendation = "Content is well-verified and trustworthy"
        elif overall_score >= 0.6:
            assessment = "Reliable"
            recommendation = "Content is generally reliable with minor concerns"
        elif overall_score >= 0.4:
            assessment = "Moderately Reliable"
            recommendation = "Some claims need additional verification"
        else:
            assessment = "Needs Improvement"
            recommendation = "Significant fact-checking issues detected"

        return {
            "overall_score": overall_score,
            "assessment": assessment,
            "recommendation": recommendation,
            "metrics": {
                "total_claims": total,
                "verified_claims": verified,
                "false_claims": false_claims,
                "average_confidence": avg_confidence,
                "verified_ratio": verified_ratio
            }
        }

    # Helper methods

    def _parse_identified_claims(
        self,
        response: str,
        chapter_number: int
    ) -> List[Dict[str, Any]]:
        """Parse identified claims from LLM response."""
        claims = []
        current_claim = None

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()

            if line.startswith('Claim '):
                if current_claim:
                    current_claim['chapter_number'] = chapter_number
                    claims.append(current_claim)

                current_claim = {
                    "statement": "",
                    "type": "",
                    "needs_verification": "",
                    "verification_method": ""
                }

            elif current_claim:
                if line.startswith('Statement:'):
                    current_claim['statement'] = line.replace('Statement:', '').strip()
                elif line.startswith('Type:'):
                    current_claim['type'] = line.replace('Type:', '').strip()
                elif line.startswith('Needs Verification:'):
                    current_claim['needs_verification'] = line.replace('Needs Verification:', '').strip()
                elif line.startswith('Verification Method:'):
                    current_claim['verification_method'] = line.replace('Verification Method:', '').strip()

        if current_claim:
            current_claim['chapter_number'] = chapter_number
            claims.append(current_claim)

        return claims

    def _parse_verification_result(
        self,
        response: str,
        claim: str,
        research_data: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Parse verification result from LLM response."""
        result = {
            "claim": claim,
            "verification_status": "unverified",
            "confidence_score": 0.5,
            "sources": [],
            "notes": "",
            "checked_at": datetime.utcnow().isoformat()
        }

        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()

            if line.startswith('Verification Status:'):
                status = line.replace('Verification Status:', '').strip().lower()
                if status in ['verified', 'unverified', 'disputed', 'false']:
                    result['verification_status'] = status

            elif line.startswith('Confidence Score:'):
                score_str = line.replace('Confidence Score:', '').strip()
                try:
                    score = float(score_str)
                    result['confidence_score'] = max(0.0, min(1.0, score))
                except ValueError:
                    pass

            elif line.startswith('Supporting Sources:'):
                sources_str = line.replace('Supporting Sources:', '').strip()
                # Extract URLs or source numbers
                if research_data:
                    result['sources'] = [
                        research_data[int(s.strip())-1].get('url', '')
                        for s in sources_str.split(',')
                        if s.strip().isdigit() and int(s.strip()) <= len(research_data)
                    ]

            elif line.startswith('Notes:'):
                result['notes'] = line.replace('Notes:', '').strip()

        return result

    def _find_relevant_research(
        self,
        claim: str,
        research_by_section: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find relevant research data for a claim."""
        if not research_by_section:
            return []

        # Simple keyword matching (in production, use better relevance scoring)
        relevant_results = []

        for section_id, research in research_by_section.items():
            results = research.get('results', [])
            for result in results:
                # Check if claim keywords appear in result
                snippet = result.get('snippet', '').lower()
                claim_words = claim.lower().split()[:5]  # First 5 words

                if any(word in snippet for word in claim_words):
                    relevant_results.append(result)

        return relevant_results[:10]  # Return top 10


def fact_check_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node function for Fact Check agent.

    This node identifies and verifies factual claims in the current draft.

    Args:
        state: Current workflow state

    Returns:
        Partial state update with fact-check results
    """
    agent = FactCheckAgent()

    # Check if fact-checking is enabled
    if not settings.enable_fact_checking:
        return {}

    # Extract inputs
    current_draft = state.get('current_draft', '')
    chapter_number = state.get('chapter_number', 1)
    research_by_section = state.get('research_by_section', {})

    # Step 1: Identify claims
    identified_claims = agent.identify_claims(current_draft, chapter_number)

    # Step 2: Verify claims
    fact_check_results = agent.batch_verify_claims(
        [c['statement'] for c in identified_claims],
        research_by_section,
        chapter_number
    )

    # Step 3: Filter by confidence threshold
    high_confidence_results = [
        r for r in fact_check_results
        if r.get('confidence_score', 0.0) >= settings.fact_check_confidence_threshold
    ]

    # Return partial state update
    return {
        "fact_check_results": high_confidence_results,  # Will be accumulated
        "conversation_history": [{
            "agent": "fact_check",
            "action": "claim_verification",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "chapter_number": chapter_number,
                "claims_identified": len(identified_claims),
                "claims_verified": len(high_confidence_results),
                "confidence_threshold": settings.fact_check_confidence_threshold
            }
        }]
    }
