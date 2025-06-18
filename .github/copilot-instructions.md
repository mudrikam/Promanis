---
description: Comprehensive GitHub Copilot coding directives.
applyTo: "**"
---

# GitHub Copilot Comprehensive Coding Directives

This document contains all coding directives and guidelines for GitHub Copilot to follow when assisting with code.

## Core Principles

These rules are mandatory and must be followed strictly. They are designed to:

- Prevent code loss and ensure all logic is preserved by banning placeholder comments and requiring complete file edits.
- Avoid unnecessary formatting discussions, as the user will handle formatting manually.
- Ensure edits are efficient and comprehensive, reducing API usage and avoiding quota exhaustion.
- Enforce the use of current technologies and user preferences, such as Python 3.12+ and PySide6.
- Maintain clarity and traceability by requiring clear explanations for every change.
- Prevent unauthorized file creation and ensure all changes are made only to files provided by the user.
- Guarantee that all code changes focus on logic, reliability, and functionality, not formatting.

Copilot must not argue, ignore, or bypass these rules for any reason.

## 1. Version and Technology Preferences

- Always use the latest version (2025 or current year).
- Do not recommend outdated versions.
- Python default: 3.12+.
- For GUI, always use PySide6, not PyQt.
- Do not add custom styling to PySide6 without explicit request - vanilla PySide6 is already attractive and functional.
- When styling is requested, use rounded corners and adequate padding on buttons (5px).
- Always use PySide6 + QtAwesome 6 combination for GUI applications.

**Reasoning**: These rules ensure compatibility, security, and user preference. PySide6's default styling is clean and professional, reducing the need for custom CSS unless specifically requested. The user prefers PySide6 + QtAwesome combination and likes rounded corners with proper padding when custom styling is applied. Copilot must not suggest outdated technologies or ignore these requirements.

## 2. Response Guidelines

- If you encounter formatting issues, proceed with functional code suggestions.
- Never mention formatting issues.
- Edit code cleanly without change-tracking comments.
- Always provide the complete file content in a single response.
- Use clear variable names and easy-to-understand logic.
- Always include a brief explanation of the reason for changes.

**Reasoning**: These rules ensure clarity, prevent unnecessary discussion, and maintain efficient communication. Copilot must not ignore or argue with these guidelines.

## 3. Indentation and Formatting Ban

- Do not discuss, fix, or comment on indentation, spacing, tabs, or newlines.
- Completely ignore indentation-related errors.
- Focus only on code logic and functionality.
- The user will handle formatting manually.
- Do not create new files just because Copilot detects an error message that is not visible to the user.
- Never claim a file is "completely broken" due to formatting or indentation.
- Do not attempt to "fix" indentation by removing or adding indents/tabs, as this can cause an endless loop where Copilot keeps changing indentation without solving the real problem.

**Reasoning**: Formatting is the user's responsibility. Copilot must not mention, attempt to fix, or create new files due to formatting issues, as this can cause endless, unproductive edit cycles and confusion. Only the user determines when a file is broken.

**Analogy**: Trying to fix indentation automatically is like a snake eating its own tail: Copilot adds or removes indents, then tries to fix the result again, creating an endless loop without ever solving the real issue. This endless loop will quickly exhaust Copilot's API quota and can result in the user being temporarily banned by GitHub.

## 4. File Creation Restrictions

- Do not create new files without explicit user permission.
- Do not suggest creating files via terminal or direct methods.
- Do not suggest installing libraries or running test files from the terminal.
- All edits must be made directly in the code so changes are visible.
- Only edit existing files, unless the user requests a new file.

**Reasoning**: This prevents unwanted files, hidden changes, and ensures all modifications are user-controlled and visible. Copilot must not bypass this restriction.

## 5. Error Handling Priority

- Prioritize fixing logic and functionality errors.
- Second, improve code reliability.
- Ignore all formatting issues.

**Reasoning**: Focus on code correctness and reliability. Formatting is not a concern for Copilot.

## 6. Efficient Editing Mandate

- Make all necessary changes in one comprehensive response.
- Do not make small edits per line or per function.
- Do not split changes across multiple responses.
- Combine all modifications into a single complete file edit.

**Reasoning**: Efficient editing prevents quota exhaustion and ensures all changes are applied at once. Copilot must not split edits.

## 7. Edit Explanation Requirement

- Provide a brief and clear explanation for each code change.
- Explain the reason for adding, removing, or modifying functions.
- Focus on the reason for the change, not technical details.

**Reasoning**: Explanations help the user understand the intent behind changes. Copilot must always provide them.

## 8. Complete Code Editing Mandate

- Do not use placeholders for existing code.
- Always include the entire file content when editing.
- If you cannot include all code, do not make the edit.

**Reasoning**: This prevents code loss and ensures all logic is preserved. Copilot must never use placeholders or partial edits.

## 9. Comment and Documentation Standards

- Do not add change-tracking, removal, or TODO comments without request.
- Only add meaningful functional documentation.
- Documentation comments must be in clear, easy-to-understand English.
- Do not use comments for version control or change tracking.
- Focus on the reason (WHY), not technical details of the change.

**Reasoning**: Comments should clarify intent in plain English, not track changes. Copilot must not add unnecessary comments or use comments for version control.

## 10. Code Modification Approach

- Do not use placeholder comments like `// ...existing code...`.
- Do not omit any existing code sections when editing.
- Always provide the entire file content when editing.
- Include all functions, variables, and logic.

**Reasoning**: Placeholders risk code loss. Copilot must always provide the full file content to ensure nothing is lost.