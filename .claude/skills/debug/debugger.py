"""
Debug harness: re-runs a pytest test with rich introspection.

Usage:
    python .claude/skills/debug/debugger.py <test_node_id> [extra pytest args...]

Example:
    python .claude/skills/debug/debugger.py tests/test_foo.py::test_bar
    python .claude/skills/debug/debugger.py tests/test_foo.py::TestClass::test_bar -k slow

What it captures:
- Full traceback with local variables at every frame
- All captured stdout / stderr from the test
- pytest warnings
- A summary of every assertion that failed (AssertionError body)
"""

import sys
import os
import traceback
import pprint
import subprocess
import textwrap


# ---------------------------------------------------------------------------
# Inline pytest plugin — hooks into the test run to dump frame locals
# ---------------------------------------------------------------------------

class DebugPlugin:
    """pytest plugin that prints rich failure info after each failed test."""

    def pytest_runtest_logreport(self, report):
        if report.when != "call" or report.passed:
            return

        print("\n" + "=" * 70)
        print(f"DEBUG REPORT  —  {report.nodeid}")
        print("=" * 70)

        if report.failed:
            self._print_longrepr(report)

        if hasattr(report, "capstdout") and report.capstdout:
            print("\n--- captured stdout ---")
            print(report.capstdout)

        if hasattr(report, "capstderr") and report.capstderr:
            print("\n--- captured stderr ---")
            print(report.capstderr)

    def _print_longrepr(self, report):
        longrepr = report.longrepr
        # longrepr can be a string, a tuple, or a ExceptionInfo-like object
        if isinstance(longrepr, str):
            print(longrepr)
            return
        if isinstance(longrepr, tuple):
            # (path, lineno, message)
            print("\n".join(str(x) for x in longrepr))
            return

        # It's a ReprExceptionInfo / ExceptionChainRepr
        try:
            # Print the repr as pytest would normally show it
            print(str(longrepr))
        except Exception:
            pass

        # Now try to walk the real traceback for local variables
        exc_info = getattr(report, "_excinfo", None)
        if exc_info is not None:
            self._dump_locals(exc_info)

    def _dump_locals(self, exc_info):
        exc_type, exc_value, exc_tb = exc_info
        print("\n--- local variables per frame (innermost last) ---")
        frames = []
        tb = exc_tb
        while tb is not None:
            frames.append(tb.tb_frame)
            tb = tb.tb_next

        for frame in frames:
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            funcname = frame.f_code.co_name
            # Skip pytest internals
            if "_pytest" in filename or "pluggy" in filename:
                continue
            print(f"\n  File {filename!r}, line {lineno}, in {funcname}")
            local_vars = {
                k: v for k, v in frame.f_locals.items()
                if not k.startswith("__")
            }
            if local_vars:
                for name, value in local_vars.items():
                    try:
                        formatted = pprint.pformat(value, width=120, depth=4)
                    except Exception as e:
                        formatted = f"<could not format: {e}>"
                    # indent multi-line values
                    indented = textwrap.indent(formatted, "      ")
                    print(f"    {name} =\n{indented}")
            else:
                print("    (no local variables)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    test_node_id = sys.argv[1]
    extra_args = sys.argv[2:]

    try:
        import pytest
    except ImportError:
        print("ERROR: pytest is not installed in the current environment.")
        print("Install it with:  pip install pytest")
        sys.exit(1)

    print(f"Running: pytest {test_node_id} {' '.join(extra_args)}")
    print("(with enhanced debug output)\n")

    # -s  → don't capture stdio so the plugin can show it
    # -v  → verbose names
    # --tb=long → full tracebacks
    args = [
        test_node_id,
        "-s",
        "-v",
        "--tb=long",
        "--no-header",
        *extra_args,
    ]

    exit_code = pytest.main(args, plugins=[DebugPlugin()])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
