# PyTestX

PyTestX is a Python-native, keyword-driven test automation framework. It is being built in small, usable releases, beginning with a YAML test runner and an extensible keyword registry.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pyx run examples\smoke.yaml
```

Expected result:

```text
PyTestX Test Runner
Test: Smoke test
  PASS SET_VARIABLE
  PASS ASSERT_EQUALS

PASSED (2 steps)
```

## Test format

```yaml
test:
  name: Smoke test
  steps:
    - keyword: SET_VARIABLE
      args:
        name: greeting
        value: hello
    - keyword: ASSERT_EQUALS
      args:
        actual: ${greeting}
        expected: hello
```

Values of the form `${variable}` are resolved from the test's runtime context.

## Development

```powershell
pytest
ruff check .
```

## Roadmap

The initial release deliberately keeps the surface area small. Planned increments add HTTP/API keywords, database plugins, data-driven execution, reporting, parallel runs, containers, and CI/CD.
