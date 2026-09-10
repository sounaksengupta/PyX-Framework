"""Core test loading and execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

import yaml

VARIABLE_PATTERN = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")


class TestDefinitionError(ValueError):
    """Raised when a YAML test definition is invalid."""


class TestExecutionError(RuntimeError):
    """Raised when a keyword cannot be executed."""


@dataclass
class RuntimeContext:
    variables: dict[str, Any] = field(default_factory=dict)

    def resolve(self, value: Any) -> Any:
        if isinstance(value, str):
            match = VARIABLE_PATTERN.fullmatch(value)
            if match:
                name = match.group(1)
                if name not in self.variables:
                    raise TestExecutionError(f"Variable '{name}' is not defined.")
                return self.variables[name]
            return value
        if isinstance(value, list):
            return [self.resolve(item) for item in value]
        if isinstance(value, dict):
            return {key: self.resolve(item) for key, item in value.items()}
        return value


@dataclass(frozen=True)
class StepResult:
    keyword: str
    passed: bool
    error: str | None = None


@dataclass(frozen=True)
class TestResult:
    name: str
    steps: list[StepResult]

    @property
    def passed(self) -> bool:
        return all(step.passed for step in self.steps)


def _set_variable(context: RuntimeContext, *, name: str, value: Any) -> None:
    context.variables[name] = value


def _assert_equals(context: RuntimeContext, *, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise AssertionError(f"Expected {expected!r}, got {actual!r}.")


KEYWORDS = {
    "SET_VARIABLE": _set_variable,
    "ASSERT_EQUALS": _assert_equals,
}


def load_test_file(path: Path) -> dict[str, Any]:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise TestDefinitionError(f"Cannot read test file: {path}") from exc
    except yaml.YAMLError as exc:
        raise TestDefinitionError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(document, dict) or not isinstance(document.get("test"), dict):
        raise TestDefinitionError("Test file must contain a top-level 'test' mapping.")
    return document["test"]


def run_test_definition(test: dict[str, Any]) -> TestResult:
    name = test.get("name")
    steps = test.get("steps")
    if not isinstance(name, str) or not name:
        raise TestDefinitionError("Test requires a non-empty 'name'.")
    if not isinstance(steps, list) or not steps:
        raise TestDefinitionError("Test requires a non-empty 'steps' list.")

    context = RuntimeContext()
    results: list[StepResult] = []
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict) or not isinstance(step.get("keyword"), str):
            raise TestDefinitionError(f"Step {index} requires a string 'keyword'.")
        keyword = step["keyword"].upper()
        args = step.get("args", {})
        if not isinstance(args, dict):
            raise TestDefinitionError(f"Step {index} args must be a mapping.")
        handler = KEYWORDS.get(keyword)
        if handler is None:
            raise TestExecutionError(f"Unknown keyword '{keyword}'.")
        try:
            handler(context, **context.resolve(args))
        except (AssertionError, TestExecutionError, TypeError) as exc:
            results.append(StepResult(keyword=keyword, passed=False, error=str(exc)))
            break
        results.append(StepResult(keyword=keyword, passed=True))
    return TestResult(name=name, steps=results)


def run_test_file(path: Path) -> TestResult:
    return run_test_definition(load_test_file(path))
