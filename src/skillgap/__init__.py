"""Example-driven trigger coverage testing for agent skill corpora."""
from .skillgap import (
    ExampleResult,
    Skill,
    coverage,
    evaluate,
    load_skills_json,
    matching_skills,
    normalize,
    render_report,
    unused_skills,
)

__all__ = [
    "ExampleResult",
    "Skill",
    "coverage",
    "evaluate",
    "load_skills_json",
    "matching_skills",
    "normalize",
    "render_report",
    "unused_skills",
]
