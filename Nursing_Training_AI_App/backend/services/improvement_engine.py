"""
Improvement Engine — uses Gemini API to generate specific improvement proposals
based on failure patterns detected by continuous_learning.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from core.mcp_rag_config import mcp_rag_config

logger = logging.getLogger(__name__)


@dataclass
class ImprovementProposal:
    priority: str  # critical / high / medium / low
    category: str  # e.g. "add_questions", "modify_questions", "training_focus"
    description: str
    affected_specialty: str
    affected_band: str
    affected_dimension: Optional[str] = None
    action_items: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ImprovementEngine:
    """Generates improvement proposals using Gemini API."""

    def __init__(self) -> None:
        self.gemini_api_key = mcp_rag_config.gemini_api_key
        self.gemini_model = mcp_rag_config.gemini_model

    def generate_proposals(
        self,
        failure_patterns: List[Dict[str, Any]],
        weak_areas: List[Dict[str, Any]],
    ) -> List[ImprovementProposal]:
        """Generate improvement proposals for detected failure patterns and weak areas."""
        if not failure_patterns and not weak_areas:
            return []

        if self.gemini_api_key:
            try:
                return self._generate_with_gemini(failure_patterns, weak_areas)
            except Exception as exc:
                logger.warning("Gemini API unavailable for improvement proposals: %s", exc)

        # Fallback: rule-based proposals
        return self._rule_based_proposals(failure_patterns, weak_areas)

    def _generate_with_gemini(
        self,
        failure_patterns: List[Dict[str, Any]],
        weak_areas: List[Dict[str, Any]],
    ) -> List[ImprovementProposal]:
        import google.generativeai as genai

        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel(self.gemini_model)

        prompt = f"""
You are an NHS nursing training curriculum expert. Based on the following failure patterns
and weak areas from a nursing training AI platform, generate specific, actionable improvement
proposals.

FAILURE PATTERNS (high failure rate areas):
{json.dumps(failure_patterns[:10], indent=2)}

WEAK AREAS (low average scores per dimension):
{json.dumps(weak_areas[:15], indent=2)}

Generate a JSON array of improvement proposals. Each proposal must have:
- priority: "critical", "high", "medium", or "low"
- category: one of "add_questions", "modify_questions", "training_focus", "curriculum_change"
- description: specific actionable description (e.g. "Add 10 questions about Safeguarding for Cardiology Band 5")
- affected_specialty: the specialty name
- affected_band: the band name
- affected_dimension: the clinical dimension (or null)
- action_items: list of 2-4 specific actions

Return ONLY the JSON array, no markdown.
"""
        response = model.generate_content(prompt)
        content = response.text.strip()
        if content.startswith("```"):
            content = content.split("```", 2)[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.rsplit("```", 1)[0].strip()

        raw_proposals = json.loads(content)
        proposals: List[ImprovementProposal] = []
        for p in raw_proposals:
            proposals.append(
                ImprovementProposal(
                    priority=p.get("priority", "medium"),
                    category=p.get("category", "training_focus"),
                    description=p.get("description", ""),
                    affected_specialty=p.get("affected_specialty", ""),
                    affected_band=p.get("affected_band", ""),
                    affected_dimension=p.get("affected_dimension"),
                    action_items=p.get("action_items", []),
                )
            )
        return proposals

    def _rule_based_proposals(
        self,
        failure_patterns: List[Dict[str, Any]],
        weak_areas: List[Dict[str, Any]],
    ) -> List[ImprovementProposal]:
        """Generate simple rule-based proposals when Gemini is unavailable."""
        proposals: List[ImprovementProposal] = []

        for pattern in failure_patterns[:10]:
            sp = pattern.get("specialty", "unknown")
            bd = pattern.get("band", "unknown")
            fr = pattern.get("failure_rate", 0)
            dim = pattern.get("weakest_dimension")
            priority = "critical" if fr >= 50 else "high" if fr >= 30 else "medium"
            proposals.append(
                ImprovementProposal(
                    priority=priority,
                    category="add_questions",
                    description=(
                        f"Add additional practice questions for {sp.upper()} {bd.upper()} "
                        f"({fr:.0f}% failure rate)"
                    ),
                    affected_specialty=sp,
                    affected_band=bd,
                    affected_dimension=dim,
                    action_items=[
                        f"Create 10+ new questions targeting {dim or 'core competencies'}",
                        "Review existing questions for clarity and relevance",
                        f"Schedule targeted revision sessions for {sp} {bd} staff",
                    ],
                )
            )

        for area in weak_areas[:10]:
            sp = area.get("specialty", "unknown")
            bd = area.get("band", "unknown")
            dim = area.get("dimension", "unknown")
            avg = area.get("avg_score", 0)
            severity = area.get("severity", "medium")
            priority = "critical" if severity == "critical" else "high" if severity == "high" else "medium"
            proposals.append(
                ImprovementProposal(
                    priority=priority,
                    category="training_focus",
                    description=(
                        f"Improve {dim.replace('_', ' ')} training for "
                        f"{sp.upper()} {bd.upper()} (avg score: {avg})"
                    ),
                    affected_specialty=sp,
                    affected_band=bd,
                    affected_dimension=dim,
                    action_items=[
                        f"Add dedicated {dim.replace('_', ' ')} module",
                        "Increase question weight for this dimension",
                        "Provide targeted learning resources",
                    ],
                )
            )

        proposals.sort(key=lambda p: {"critical": 0, "high": 1, "medium": 2, "low": 3}[p.priority])
        return proposals


improvement_engine = ImprovementEngine()
