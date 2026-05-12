# Project overview

This project is a discreet code-typing practice application designed to run in Windows Terminal / PowerShell.

The product should look like a professional internal developer tool, not a game. The user may run it on a highly visible monitor in a work environment, so the interface must appear work-adjacent and subdued.

## Product intent
The app helps users improve typing speed and accuracy specifically for code.

Primary use case:
- The user selects a programming language.
- The app displays a code snippet.
- The user types the snippet as accurately as possible.
- The app scores the result and identifies recurring weak spots.

## UX principles
- Prefer minimal, clean, modern presentation.
- Aim for terminal-native elegance rather than trying to mimic a browser exactly.
- The interface should resemble a developer productivity tool or internal engineering utility.
- Avoid anything that looks playful, gamified, childish, or flashy.
- Use restrained color and spacing.
- Keep the screen discreet and credible in a workplace setting.
- Keyboard-first navigation only.
- Support dark theme first.

## Technical direction
Preferred initial stack:
- Python 3.14+ (latest)
- prompt_toolkit for terminal interaction and editable input
- Pygments for syntax highlighting
- rich for layout, tables, panels, and visual polish

Alternative:
- textual may be introduced only if needed for a better full-screen TUI architecture.
- Do not choose a browser app unless terminal delivery proves meaningfully inferior for the required UX.

## Scope priorities
MVP first:
1. Local snippets from bundled files
2. Language selection
3. Typing session view
4. Input capture and snippet comparison
5. Session metrics
6. Improvement analysis
7. Session summary

Later:
- Remote snippet fetching
- User profiles
- Persistent history
- More advanced analytics
- Theme variations
- Packaging as standalone executable

## Snippet strategy
- Start with bundled curated snippets in a simple local format such as JSON, YAML, or .py/.js text files with metadata.
- Snippets should be realistic, short-to-medium length, and representative of real coding.
- Avoid copyrighted bulk code dumps.
- Prefer hand-curated or synthetic-but-realistic snippets.

Each snippet should ideally include:
- id
- language
- difficulty
- title
- code
- tags
- source_type

## Metrics and analysis
At minimum, support:
- WPM or CPM
- Accuracy
- Completion time
- Raw vs corrected errors if practical
- Per-character or per-token mismatch counts
- Frequent error categories

Improvement analysis should prioritize:
- Brackets and parentheses
- Quotes
- Colon/semicolon confusion
- Indentation
- Number row and shifted symbols
- Underscore, dash, equals, plus
- Common coding punctuation patterns

## Architecture expectations
Use a clean modular structure under `src/`.
Separate concerns clearly:
- app entrypoint
- rendering / UI
- input session handling
- snippet loading
- metrics engine
- analysis engine
- theme/styling
- config

Avoid large monolithic files.
Prefer small, focused modules.

## Code quality rules
- Type hints throughout
- Clear dataclasses or pydantic-style models where useful
- Tests for metrics and comparison logic
- Keep side effects at the edges
- Document non-obvious terminal limitations
- Make Windows Terminal support a first-class concern

## Decision rules
Before implementing any major subsystem:
1. Evaluate feasibility in Windows Terminal.
2. Prefer the simplest solution that preserves a polished UX.
3. If a feature is awkward in terminal, propose a terminal-friendly version before escalating complexity.
4. If terminal is the wrong medium for a requirement, explicitly say so and propose the cleanest fallback.

## Design rules
- No neon cyberpunk styling
- No gamer vocabulary
- No celebratory animations that make it look recreational
- No overly colorful heatmaps in the main typing view
- Prefer muted syntax colors and subtle panels
- Use terminology such as session, analysis, snippet, language, metrics, summary

## Workflow for Gemini CLI
When working on this project:
1. Start with planning before coding large features.
2. For substantial changes, propose the plan first.
3. Keep README.md updated as the architecture changes.
4. Preserve a clear MVP path.
5. Do not add unnecessary dependencies.
6. Favor maintainability over cleverness.

## Deliverable expectations
Unless asked otherwise, work in this order:
1. Feasibility assessment
2. Plan
3. Project scaffold
4. Core snippet/session flow
5. Metrics and analysis
6. Polish and refinement
7. Packaging/documentation
