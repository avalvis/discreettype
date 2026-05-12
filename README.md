# Discreet Code Typing Tool

A professional, minimal terminal-based typing practice app designed to run in Windows Terminal / PowerShell.

## Features
- **Overlay Interaction:** Type directly over syntax-highlighted code with real-time feedback.
- **Monkeytype-style Feedback:** Correct (White), Incorrect (Red), Untyped (Gray).
- **Discreet Look:** Subdued colors, minimal UI, and professional aesthetic.
- **Boss Key:** Press `F12` to immediately swap to a fake build output screen.
- **History Tracking:** Local JSON persistence of your typing stats.
- **Metrics:** WPM, Accuracy, and error counts.

## Installation
Ensure you have Python 3.12+ installed.

```bash
# Clone the repository
git clone <repo-url>
cd typing-tool

# Install dependencies using uv
uv sync
```

## Usage
Run the application from the project root:

```bash
uv run python -m typing_tool.main
```

## Key Bindings
- **Ctrl+C:** Exit the session.
- **F12:** Toggle Boss Key (Discreet Mode).
- **Backspaces:** Correct your mistakes.

## Architecture
- `src/typing_tool/main.py`: Main entry point and dashboard.
- `src/typing_tool/core/session.py`: Session logic and metrics.
- `src/typing_tool/ui/typing.py`: The custom overlay typing renderer.
- `src/typing_tool/ui/app.py`: TUI layout and orchestration.
- `src/typing_tool/storage/`: Data models and history persistence.
