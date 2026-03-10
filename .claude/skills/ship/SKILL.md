---
name: ship
description: Take unstaged/uncommitted changes, create a branch, commit, push, and open a PR. Usage: /ship [optional hint]
user-invokable: true
---

Take the current uncommitted changes and ship them as a pull request.

Follow these steps exactly:

## 1. Understand the changes

Run these in parallel:
- `git diff` — unstaged changes
- `git diff --cached` — staged changes
- `git status` — untracked files
- `git log -5 --oneline` — recent commits for context

## 2. Determine the base branch

Run `git remote show origin | grep 'HEAD branch'` to find the default branch (usually `main` or `master`). Use that as the base.

## 3. Generate branch name and commit message

Analyze the diff to understand what changed and why. Use the optional hint if provided: $ARGUMENTS

- Branch name: lowercase, hyphenated, ≤50 chars, no ticket prefix. Format: `<type>/<short-description>` (e.g. `fix/null-check-login`, `feat/export-csv`, `refactor/auth-service`)
- Commit message: imperative mood, concise, ≤72 chars subject line. Add a blank line + body if nuance is needed.

## 4. Create branch and commit

First, check the current branch with `git branch --show-current` and compare it against the base branch from step 2.

- If already on a feature branch (not the base branch): skip `git checkout -b`, use the existing branch as-is. Also check if a PR already exists with `gh pr view 2>/dev/null` — if it does, skip straight to step 6 (update the PR description if needed, or just return the existing PR URL).
- If on the base branch: create a new branch with `git checkout -b <branch-name>`.

Stage all relevant changed/new files (prefer specific paths over `git add -A`, but use judgment). Then commit with the generated message using this format:

```
git commit -m "$(cat <<'EOF'
<subject line>

<optional body>

Co-Authored-By: Claude
EOF
)"
```

If a pre-commit hook fails, fix the underlying issue and retry — do NOT use `--no-verify`.

## 5. Push

```
git push -u origin <branch-name>
```

## 6. Create the PR

Write a PR title (≤70 chars) and body using this template:

```
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
- <bullet 1>
- <bullet 2>

## Changes
- <file or area>: <what changed>

## Test plan
- [ ] <how to verify>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## 7. Return the PR URL

Output the PR URL so the user can open it directly.
