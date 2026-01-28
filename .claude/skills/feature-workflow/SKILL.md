---
name: feature-workflow
description: Create branch, implement feature, run tests, and push to origin
disable-model-invocation: true
argument-hint: [task description]
---

# Feature Workflow

Execute the full feature implementation workflow for this task: $ARGUMENTS

## Steps

1. **Create a new branch** from `main` with a descriptive name based on the task
2. **Implement the feature** as described in the task
3. **Run tests** with `pytest -v` to verify changes work
4. **Commit changes** with small, logical commits — each commit should represent a single complete change
5. **If all tests pass**, push the branch to origin with `git push -u origin <branch-name>`
6. **If tests fail**, fix the issues and re-run until they pass before pushing

## Rules

- Follow the project's CLAUDE.md guidelines
- Activate the virtual environment before running anything
- Add relevant tests when adding a new feature
- Run typecheck when done making code changes
