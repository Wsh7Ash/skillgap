from skillgap.skillgap import (
    Skill,
    coverage,
    evaluate,
    load_skills_json,
    matching_skills,
    normalize,
    render_report,
    unused_skills,
)


def _corpus():
    return [
        Skill("deploy", triggers=["deploy", "ship to production"]),
        Skill("rollback", triggers=["rollback", "revert"]),
        Skill("logs", triggers=["logs", "show errors"]),
    ]


def test_normalize_lowercases_and_collapses():
    assert normalize("  Hello   World \n") == "hello world"


def test_single_match_is_ok():
    results = evaluate(["please deploy this"], _corpus())
    assert results[0].matched == ["deploy"]
    assert results[0].status == "ok"


def test_no_match_is_gap():
    results = evaluate(["what's the weather"], _corpus())
    assert results[0].matched == []
    assert results[0].status == "gap"


def test_multiple_matches_is_ambiguous():
    results = evaluate(["deploy then rollback if logs look bad"], _corpus())
    assert len(results[0].matched) == 3
    assert results[0].status == "ambiguous"


def test_matching_is_case_and_whitespace_tolerant():
    hits = matching_skills("Please   DEPLOY now", _corpus())
    assert hits == ["deploy"]


def test_whole_word_match_no_substring_false_positive():
    # "deploy" should not match inside "deployment" as a bare trigger? It will,
    # because "deployment" contains deploy as a prefix but whole-word guard
    # prevents it. Verify the guard rejects a substring inside a longer word.
    skills = [Skill("deploy", triggers=["ploy"])]
    assert matching_skills("deploy this", skills) == []


def test_multiword_trigger():
    skills = [Skill("rollback", triggers=["ship to production"])]
    assert matching_skills("let's ship to production today", skills) == ["rollback"]


def test_coverage_counts():
    results = evaluate(
        ["deploy this", "weather?", "deploy and rollback"], _corpus()
    )
    counts = coverage(results)
    assert counts == {"ok": 1, "gap": 1, "ambiguous": 1}


def test_unused_skills():
    results = evaluate(["deploy only"], _corpus())
    dead = unused_skills(results, _corpus())
    assert set(dead) == {"rollback", "logs"}


def test_render_report():
    results = evaluate(["deploy this", "weather?"], _corpus())
    report = render_report(results, _corpus())
    assert "2 example(s)" in report
    assert "GAP" in report


def test_load_skills_json(tmp_path):
    p = tmp_path / "corpus.json"
    p.write_text('[{"name":"a","triggers":["alpha"]}]', encoding="utf-8")
    skills = load_skills_json(p)
    assert skills[0].name == "a"
    assert skills[0].triggers == ["alpha"]
