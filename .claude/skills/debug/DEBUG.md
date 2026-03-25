---
name: debug
description: Debug helper script for a python unit test
user-invokable: true
---

Use this skill when a pytest test fails and the reason is not obvious from the normal output. It re-runs the failing test with a custom debug harness that captures local variable values at every frame, full tracebacks, and all stdout/stderr.

## When to invoke

- A test just failed and the error message alone is insufficient to understand why.
- You need to inspect intermediate variable state inside the test or the code under test.
- Captured output from a previous run is missing or truncated.

## How to run

The debugger is a standalone Python script located at:

```
.claude/skills/debug/debugger.py
```

Run it with:

```bash
python .claude/skills/debug/debugger.py <test_node_id> [extra pytest args...]
```

**Examples:**

```bash
# Single test function
python .claude/skills/debug/debugger.py tests/test_foo.py::test_bar

# Test method inside a class
python .claude/skills/debug/debugger.py tests/test_foo.py::TestClass::test_bar

# Pass extra pytest flags (e.g. mark filter)
python .claude/skills/debug/debugger.py tests/test_foo.py::test_bar -k "not slow"
```

If the project uses a virtual environment, activate it first or prefix with the venv python:

```bash
.venv/bin/python .claude/skills/debug/debugger.py <test_node_id>
```

## What the output includes

- **Full traceback** with `--tb=long`
- **Local variables** at every non-pytest frame, pretty-printed with types and values
- **Captured stdout / stderr** from the test body
- pytest warnings and verbose test names

## Steps to follow

1. Identify the failing test node ID from the previous test run output (e.g. `tests/test_auth.py::test_login_invalid_password`).
2. Run the debugger script with that node ID.
3. Read the `--- local variables per frame ---` section to find unexpected values.
4. Cross-reference with the source file and traceback line numbers to pinpoint the bug.
5. Fix the issue, then re-run the normal test suite to confirm.
