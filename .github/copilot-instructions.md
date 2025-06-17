---
description: Master instructions file for Copilot coding directives. Points to modular instruction files.
applyTo: "**"
---

# GitHub Copilot Modular Coding Directives

The main instructions have been split into several modular files in the `.github/instructions/` folder.  
Each file covers one important topic.  
Use the following links to view the details of each instruction:

## Reasoning

These rules are mandatory and must be followed strictly. They are designed to:

- Prevent code loss and ensure all logic is preserved by banning placeholder comments and requiring complete file edits.
- Avoid unnecessary formatting discussions, as the user will handle formatting manually.
- Ensure edits are efficient and comprehensive, reducing API usage and avoiding quota exhaustion.
- Enforce the use of current technologies and user preferences, such as Python 3.12+ and PySide6.
- Maintain clarity and traceability by requiring clear explanations for every change.
- Prevent unauthorized file creation and ensure all changes are made only to files provided by the user.
- Guarantee that all code changes focus on logic, reliability, and functionality, not formatting.

Copilot must not argue, ignore, or bypass these rules for any reason.