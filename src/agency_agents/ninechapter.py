"""NineChapter behavioral and task context overlays.

Canonical home for persona-side runtime overlay generation.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Behavioral overlay (chat + agentic)
# ---------------------------------------------------------------------------

def build_behavioral_overlay(role: Dict[str, Any]) -> str:
    dims = role.get("dimensions") or {}
    if not dims:
        return ""

    def score(dim: str) -> int:
        entry = dims.get(dim)
        if isinstance(entry, dict):
            return int(entry.get("score", 0))
        if isinstance(entry, (int, float)):
            return int(entry)
        return 0

    clauses: List[str] = []

    cv = score("core_values")
    if cv >= 90:
        clauses.append(
            "Name uncertainty explicitly — never present incomplete findings as settled conclusions."
        )
        clauses.append(
            "Before stating a conclusion, verify it against at least 2 independent "
            "sources or pieces of evidence."
        )
    elif cv >= 75:
        clauses.append("Flag significant uncertainties before stating conclusions.")

    cs = score("cognitive_style")
    if cs >= 90:
        clauses.append(
            "Structure responses systematically: break the problem into components before synthesizing."
        )
        clauses.append(
            "Response density: be comprehensive and detailed — brevity is not a virtue "
            "when depth is needed to give a complete answer."
        )
    elif cs >= 75:
        clauses.append("Organize complex responses into clear sections.")

    so = score("social_orientation")
    if so >= 90:
        clauses.append(
            "When clarification is needed, ask one focused question at a time — never a list."
        )
        clauses.append(
            "Teach as you answer: explain the reasoning behind conclusions, "
            "not just the conclusions themselves."
        )
    elif so >= 75:
        clauses.append("Ask one focused clarifying question at a time — never a list.")

    er = score("emotional_reaction")
    if er >= 90:
        clauses.append(
            "Welcome pushback as a refinement opportunity — engage it directly with evidence, "
            "not defensiveness."
        )
        clauses.append(
            "State your position clearly and directly. Do not hedge every sentence "
            "with qualifiers when the evidence supports a clear conclusion."
        )

    ad = score("adaptability")
    if ad >= 85:
        clauses.append(
            "Work with incomplete information methodically: label gaps explicitly "
            "rather than avoiding them."
        )
        clauses.append(
            "Escalation threshold: only surface a blocker to the user when "
            "all tool alternatives are genuinely exhausted — uncertainty alone is not a blocker."
        )

    if not clauses:
        return ""

    lines = "\n".join(f"- {c}" for c in clauses)
    return f"## Behavioral calibration\n{lines}\n\n"


# ---------------------------------------------------------------------------
# Task context overlay (agentic tasks only)
# ---------------------------------------------------------------------------

def build_task_context(role: Dict[str, Any]) -> str:
    blocks: List[str] = []

    success = role.get("success_patterns") or {}
    if success:
        lines = "\n".join(f"- **{k}:** {v}" for k, v in success.items())
        blocks.append(
            "## What a complete answer looks like for this role\n"
            "Check your FINAL_ANSWER against the applicable pattern before submitting:\n"
            + lines
        )

    escalation = role.get("escalation_rules") or {}
    if escalation:
        escalate_lines = "\n".join(
            f"  - {r}" for r in escalation.get("escalate_when", [])
        )
        no_escalate_lines = "\n".join(
            f"  - {r}" for r in escalation.get("do_not_escalate_when", [])
        )
        esc_block = "## When to escalate (use ask_user)\n"
        if escalate_lines:
            esc_block += f"Escalate when:\n{escalate_lines}\n"
        if no_escalate_lines:
            esc_block += f"Do NOT escalate when:\n{no_escalate_lines}\n"
        blocks.append(esc_block)

    if not blocks:
        return ""

    return "\n\n".join(blocks) + "\n\n"


# ---------------------------------------------------------------------------
# Capability summary
# ---------------------------------------------------------------------------

_CAPABILITY_CATALOG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "config", "capability_catalog.json"
)
_capability_catalog_cache: Dict[str, Any] = {}


def _load_capability_catalog() -> Dict[str, Any]:
    global _capability_catalog_cache
    if _capability_catalog_cache:
        return _capability_catalog_cache
    try:
        with open(_CAPABILITY_CATALOG_PATH, encoding="utf-8") as f:
            _capability_catalog_cache = json.load(f)
    except Exception:
        _capability_catalog_cache = {}
    return _capability_catalog_cache


def build_capability_summary(role: Dict[str, Any]) -> str:
    capabilities: List[str] = role.get("capabilities") or []
    if not capabilities:
        return ""

    catalog = _load_capability_catalog()
    categories = catalog.get("categories", {})

    lines = [
        f"- **{cap}** — {categories.get(cap, {}).get('description', cap)}"
        for cap in capabilities
    ]

    return (
        "## Your Capabilities\n"
        + "\n".join(lines)
        + "\n\n"
        "Discover the specific tools for each capability from the tool schema "
        "provided with this prompt. If a task requires something not covered "
        "above, use `ask_user` to escalate.\n\n"
    )
