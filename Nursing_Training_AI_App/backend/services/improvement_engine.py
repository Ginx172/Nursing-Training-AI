"""
Improvement Engine — uses Gemini API to generate ImprovementProposal objects.
Falls back to rule-based generation when Gemini is unavailable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from core.mcp_rag_config import mcp_rag_config


@dataclass
class ImprovementProposal:
    priority: str               # "high" | "medium" | "low"
    category: str               # e.g. "curriculum", "assessment", "training_materials"
    description: str
    affected_specialty: Optional[str] = None
    affected_band: Optional[str] = None
    action_items: List[str] = field(default_factory=list)


class ImprovementEngine:
    """Generates improvement proposals from weak-area data."""

    def __init__(self) -> None:
        self.gemini_api_key = mcp_rag_config.gemini_api_key
        self.gemini_model = mcp_rag_config.gemini_model

    async def generate_proposals(
        self,
        weak_areas: List[Dict[str, Any]],
        failure_patterns: Optional[List[Dict[str, Any]]] = None,
    ) -> List[ImprovementProposal]:
        """Return proposals either from Gemini or rule-based fallback."""
        if self.gemini_api_key and weak_areas:
            try:
                return await self._gemini_proposals(weak_areas, failure_patterns or [])
            except Exception:
                pass
        return self._rule_based_proposals(weak_areas, failure_patterns or [])

    # ------------------------------------------------------------------ #
    # Gemini-powered proposals                                             #
    # ------------------------------------------------------------------ #

    async def _gemini_proposals(
        self,
        weak_areas: List[Dict[str, Any]],
        failure_patterns: List[Dict[str, Any]],
    ) -> List[ImprovementProposal]:
        prompt = f"""
You are an NHS nursing education improvement specialist.

Given the following weak areas detected in learner assessments:
{json.dumps(weak_areas, indent=2)}

And the following failure patterns:
{json.dumps(failure_patterns, indent=2)}

Generate a JSON array of improvement proposals. Each proposal must have:
- priority: "high", "medium", or "low"
- category: one of "curriculum", "assessment", "training_materials", "mentoring", "simulation"
- description: a concise description of the improvement
- affected_specialty: the specialty (or null for cross-cutting)
- affected_band: the NHS band (or null for cross-cutting)
- action_items: a list of 2-4 concrete action steps

Return ONLY the JSON array, no markdown fences.
"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent",
                params={"key": self.gemini_api_key},
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"temperature": 0.4, "maxOutputTokens": 2000}},
                timeout=60.0,
            )
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Strip markdown fences if present
            if "```" in text:
                parts = text.split("```")
                inner = parts[1]
                first_newline = inner.find("\n")
                if first_newline != -1 and not inner[:first_newline].strip().startswith("["):
                    inner = inner[first_newline + 1:]
                text = inner.strip()
            raw: List[Dict[str, Any]] = json.loads(text)
            return [ImprovementProposal(**{k: v for k, v in p.items() if k in ImprovementProposal.__dataclass_fields__}) for p in raw]

    # ------------------------------------------------------------------ #
    # Rule-based fallback                                                  #
    # ------------------------------------------------------------------ #

    def _rule_based_proposals(
        self,
        weak_areas: List[Dict[str, Any]],
        failure_patterns: List[Dict[str, Any]],
    ) -> List[ImprovementProposal]:
        proposals: List[ImprovementProposal] = []

        # One proposal per unique weak dimension
        seen_dims: set = set()
        for area in weak_areas:
            dim = area.get("dimension", "general")
            if dim in seen_dims:
                continue
            seen_dims.add(dim)
            avg = area.get("avg_score", 0.0)
            priority = "high" if avg < 40 else "medium" if avg < 55 else "low"
            proposals.append(ImprovementProposal(
                priority=priority,
                category="curriculum",
                description=f"Strengthen {dim.replace('_', ' ')} training materials (avg score: {avg:.1f}%)",
                affected_specialty=area.get("specialty"),
                affected_band=area.get("band"),
                action_items=[
                    f"Review and update {dim.replace('_', ' ')} curriculum content",
                    "Add targeted practice questions for this competency",
                    "Schedule dedicated simulation sessions",
                ],
            ))

        # High-failure patterns → mentoring proposals
        for pattern in failure_patterns:
            if pattern.get("failure_rate", 0) > 40:
                proposals.append(ImprovementProposal(
                    priority="high",
                    category="mentoring",
                    description=(
                        f"High failure rate ({pattern['failure_rate']:.1f}%) for "
                        f"{pattern.get('specialty', 'unknown')} band {pattern.get('band', 'unknown')}"
                    ),
                    affected_specialty=pattern.get("specialty"),
                    affected_band=pattern.get("band"),
                    action_items=[
                        "Assign dedicated clinical mentor",
                        "Implement weekly progress reviews",
                        "Create personalised remediation plan",
                    ],
                ))

        return proposals


# Module-level singleton
improvement_engine = ImprovementEngine()
