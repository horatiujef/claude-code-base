---
name: clawd
description: Run a long running task based on a particular topic
user-invokable: true
---

Work on $ARGUMENTS topic if specified, otherwise pick one from the list below at random.

## 1. General Topics

- Security improvements (e.g. input validation, dependency vulnerabilities, unsafe patterns)
- Dependency upgrades (patch or minor version bumps only; verify nothing breaks)
- Improve test coverage and quality
- Simplify code (without reducing functionality or lowering quality)

## 2. Guidelines

- Start from a clean working tree (no uncommitted changes)
- Scan the codebase, then pick the single best opportunity for the chosen topic
- The opportunity must be clear, atomic, and self-contained — do not mix unrelated concerns in one PR
- Keep the change focused: ideally under 500 lines of source code (excluding tests and generated files); slightly over is fine, but avoid sprawling diffs
- Run tests after making changes; they must pass before shipping
- Ship with "/ship done" at the end