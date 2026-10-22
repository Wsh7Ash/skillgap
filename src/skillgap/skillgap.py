"""Example-driven trigger coverage testing for agent skill corpora.

A skill declares triggers (keywords or phrases) meant to fire it for the right
user inputs. This module replays a set of example inputs against the corpus and
reports, per example, which skills would trigger — then flags the two failure
modes that are invisible until production:

- **coverage gap** — an example that matches *no* skill (the intent is unserved)
- **ambiguity** — an example that matches *more than one* skill (routing unclear)

Matching is deterministic and offline: a skill triggers if any of its trigger
phrases appears in the (normalized) input. Normalization lowercases and
collapses whitespace so phrasing noise does not create false gaps.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

_WS_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Lowercase and collapse whitespace so matching is phrasing-tolerant."""
    return _WS_RE.sub(" ", text.strip().lower())


@dataclass
class Skill:
    name: str
    triggers: list[str] = field(default_factory=list)
    description: str = ""

    def __post_init__(self) -> None:
        self.triggers = [normalize(t) for t in self.triggers if t and t.strip()]


@dataclass
class ExampleResult:
    example: str
    matched: list[str]  # skill names that trigger, in corpus order

    @property
    def status(self) -> str:
        if not self.matched:
            return "gap"
        if len(self.matched) > 1:
            return "ambiguous"
        return "ok"


def matching_skills(example: str, skills: list[Skill]) -> list[str]:
    """Return the names of skills whose triggers appear in the example."""
    text = normalize(example)
    hits = []
    for skill in skills:
        for trigger in skill.triggers:
            # Whole-word match on the trigger phrase.
            if re.search(r"(?<!\w)" + re.escape(trigger) + r"(?!\w)", text):
                hits.append(skill.name)
                break
    return hits


def evaluate(examples: list[str], skills: list[Skill]) -> list[ExampleResult]:
    """Run every example against the corpus."""
    return [ExampleResult(ex, matching_skills(ex, skills)) for ex in examples]


def coverage(results: list[ExampleResult]) -> dict[str, int]:
    counts = {"ok": 0, "gap": 0, "ambiguous": 0}
    for r in results:
        counts[r.status] += 1
    return counts


def unused_skills(results: list[ExampleResult], skills: list[Skill]) -> list[str]:
    """Skills that never matched any example (possible dead or over-specific)."""
    used = {name for r in results for name in r.matched}
    return [s.name for s in skills if s.name not in used]


def render_report(results: list[ExampleResult], skills: list[Skill]) -> str:
    lines = []
    counts = coverage(results)
    lines.append(
        f"{len(results)} example(s): {counts['ok']} ok, "
        f"{counts['gap']} gap, {counts['ambiguous']} ambiguous"
    )
    lines.append("")
    for r in results:
        if r.status == "ok":
            continue
        label = "GAP      " if r.status == "gap" else "AMBIGUOUS"
        detail = ", ".join(r.matched) if r.matched else "(none)"
        lines.append(f"{label} {r.example!r} -> {detail}")
    dead = unused_skills(results, skills)
    if dead:
        lines.append("")
        lines.append("Skills never triggered by any example: " + ", ".join(dead))
    if counts["gap"] == 0 and counts["ambiguous"] == 0:
        lines.append("All examples route to exactly one skill.")
    return "\n".join(lines)


def load_skills_json(path: str | Path) -> list[Skill]:
    """Load a corpus from JSON: [{"name":..., "triggers":[...], "description":...}]."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        Skill(name=d["name"], triggers=d.get("triggers", []), description=d.get("description", ""))
        for d in data
    ]
