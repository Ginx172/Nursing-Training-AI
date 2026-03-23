"""
Improvement engine: generates Gemini-powered ImprovementProposals;
falls back to rule-based proposals when API is unavailable.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx


@dataclass
class ImprovementProposal:
    """A single actionable improvement proposal."""
    specialty: str
    band: str
    dimension: str
    title: str
    description: str
    actions: List[str] = field(default_factory=list)
    priority: str = "medium"   # low | medium | high
    source: str = "rule_based"  # rule_based | gemini


class ImprovementEngine:
    """Generates improvement proposals for weak areas using Gemini or rule-based fallback."""

    _RULE_TEMPLATES: Dict[str, Dict[str, str]] = {
        "knowledge_depth": {
            "title": "Strengthen knowledge depth",
            "description": "Scores indicate shallow theoretical grounding.",
            "actions": [
                "Review NICE guidelines for the specialty",
                "Complete e-learning modules on core topics",
                "Schedule a knowledge review session with a senior colleague",
            ],
            "priority": "high",
        },
        "clinical_reasoning": {
            "title": "Enhance clinical reasoning",
            "description": "Decision-making under assessment conditions needs improvement.",
            "actions": [
                "Practice structured case analysis (SBAR)",
                "Join a clinical simulation workshop",
                "Reflect on recent patient cases using a learning journal",
            ],
            "priority": "high",
        },
        "safety_awareness": {
            "title": "Improve safety awareness",
            "description": "Safety-critical items are being missed or deprioritised.",
            "actions": [
                "Complete statutory and mandatory safety training",
                "Review Never Events and local serious incident reports",
                "Shadow a senior practitioner during high-acuity shifts",
            ],
            "priority": "high",
        },
        "communication": {
            "title": "Develop communication skills",
            "description": "Communication dimension scores are below target.",
            "actions": [
                "Practice SBAR handover with peers",
                "Attend a communication skills workshop",
                "Request feedback from supervisors on documentation quality",
            ],
            "priority": "medium",
        },
        "leadership": {
            "title": "Build leadership competencies",
            "description": "Leadership indicators are below band expectations.",
            "actions": [
                "Enrol in a leadership development programme",
                "Seek opportunities to lead team briefings",
                "Identify a leadership mentor within the organisation",
            ],
            "priority": "medium",
        },
    }

    def __init__(self) -> None:
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate_proposals(
        self, weak_areas: List[Dict[str, Any]]
    ) -> List[ImprovementProposal]:
        """Generate proposals for a list of weak-area dicts."""
        proposals: List[ImprovementProposal] = []
        for area in weak_areas:
            proposal = await self._proposal_for_area(area)
            if proposal:
                proposals.append(proposal)
        return proposals

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _proposal_for_area(self, area: Dict[str, Any]) -> Optional[ImprovementProposal]:
        specialty = area.get("specialty", "general")
        band = area.get("band", "band_5")
        dimension = area.get("dimension", "knowledge_depth")
        avg_score = area.get("avg_score", 0.0)

        if self.gemini_api_key:
            try:
                return await self._gemini_proposal(specialty, band, dimension, avg_score)
            except Exception:
                pass  # fall through to rule-based

        return self._rule_based_proposal(specialty, band, dimension)

    async def _gemini_proposal(
        self, specialty: str, band: str, dimension: str, avg_score: float
    ) -> ImprovementProposal:
        prompt = (
            f"You are an expert NHS nursing educator. A healthcare professional at {band} level "
            f"in the {specialty} specialty has an average score of {avg_score:.1f}/100 on the "
            f"'{dimension}' competency dimension. "
            "Provide an actionable improvement proposal as JSON with keys: "
            "'title' (str), 'description' (str), 'actions' (list of 3 strings), 'priority' (low|medium|high)."
        )
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.gemini_model}:generateContent?key={self.gemini_api_key}"
        )
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"temperature": 0.4, "maxOutputTokens": 512}},
            )
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            if text.startswith("```"):
                text = text.split("```", 2)[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.rsplit("```", 1)[0]
            data = json.loads(text.strip())

        return ImprovementProposal(
            specialty=specialty,
            band=band,
            dimension=dimension,
            title=data.get("title", ""),
            description=data.get("description", ""),
            actions=data.get("actions", []),
            priority=data.get("priority", "medium"),
            source="gemini",
        )

    def _rule_based_proposal(
        self, specialty: str, band: str, dimension: str
    ) -> ImprovementProposal:
        template = self._RULE_TEMPLATES.get(dimension, self._RULE_TEMPLATES["knowledge_depth"])
        return ImprovementProposal(
            specialty=specialty,
            band=band,
            dimension=dimension,
            title=template["title"],
            description=template["description"],
            actions=list(template["actions"]),
            priority=template["priority"],
            source="rule_based",
        )


improvement_engine = ImprovementEngine()
