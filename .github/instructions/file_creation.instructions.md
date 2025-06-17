---
description: Restriction on creating new files without explicit permission.
applyTo: "**"
---

# File Creation Restrictions

- Do not create new files without explicit user permission.
- Do not suggest creating files via terminal or direct methods.
- Do not suggest installing libraries or running test files from the terminal.
- All edits must be made directly in the code so changes are visible.
- Only edit existing files, unless the user requests a new file.

## Reasoning

This prevents unwanted files, hidden changes, and ensures all modifications are user-controlled and visible. Copilot must not bypass this restriction.
