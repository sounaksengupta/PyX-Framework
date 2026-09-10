from pyx.engine import TestDefinitionError, run_test_definition


def test_runs_a_keyword_test_and_resolves_variables() -> None:
    result = run_test_definition(
        {
            "name": "Greeting",
            "steps": [
                {"keyword": "SET_VARIABLE", "args": {"name": "message", "value": "hello"}},
                {"keyword": "ASSERT_EQUALS", "args": {"actual": "${message}", "expected": "hello"}},
            ],
        }
    )

    assert result.passed
    assert [step.keyword for step in result.steps] == ["SET_VARIABLE", "ASSERT_EQUALS"]


def test_stops_after_a_failed_assertion() -> None:
    result = run_test_definition(
        {
            "name": "Failure",
            "steps": [
                {"keyword": "ASSERT_EQUALS", "args": {"actual": 1, "expected": 2}},
                {"keyword": "SET_VARIABLE", "args": {"name": "never", "value": "set"}},
            ],
        }
    )

    assert not result.passed
    assert len(result.steps) == 1
    assert result.steps[0].error == "Expected 2, got 1."


def test_rejects_a_test_without_steps() -> None:
    try:
        run_test_definition({"name": "Empty", "steps": []})
    except TestDefinitionError as exc:
        assert "steps" in str(exc)
    else:
        raise AssertionError("Expected TestDefinitionError")
