---
description: Ban on discussing or fixing indentation and formatting.
applyTo: "**"
---

# Indentation and Formatting Ban

- Do not discuss, fix, or comment on indentation, spacing, tabs, or newlines.
- Completely ignore indentation-related errors.
- Focus only on code logic and functionality.
- The user will handle formatting manually.
- Do not create new files just because Copilot detects an error message that is not visible to the user.
- Never claim a file is "completely broken" due to formatting or indentation.
- Do not attempt to "fix" indentation by removing or adding indents/tabs, as this can cause an endless loop where Copilot keeps changing indentation without solving the real problem.

## Reasoning

Formatting is the user's responsibility. Copilot must not mention, attempt to fix, or create new files due to formatting issues, as this can cause endless, unproductive edit cycles and confusion. Only the user determines when a file is broken.

## Analogy  
Trying to fix indentation automatically is like a snake eating its own tail: Copilot adds or removes indents, then tries to fix the result again, creating an endless loop without ever solving the real issue. This endless loop will quickly exhaust Copilot's API quota and can result in the user being temporarily banned by GitHub.
