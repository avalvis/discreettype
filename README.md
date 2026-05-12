# Discreet Code Typing Tool

A professional, minimal terminal-based typing practice app designed for developers. It mimics the "Monkeytype" experience while maintaining a subdued, work-safe aesthetic within Windows Terminal or PowerShell.

## 🚀 Key Features

- **IDE-Like Interaction:** A custom "Virtual Overlay" engine allows you to type directly over syntax-highlighted code.
- **Vibrant Syntax Highlighting:** Powered by Pygments, providing clear and professional code visuals for Python, TypeScript, SQL, Bash, and more.
- **Intelligent Indentation:** Full support for the **Tab key**, allowing you to navigate indentation blocks naturally.
- **Real-World Snippets:**
  - **Curated Local Library:** Hand-picked snippets for daily practice.
  - **Live GitHub Integration:** Fetch production-grade code directly from popular open-source repositories.
- **Discreet "Boss Key":** Press `F12` to instantly swap the UI for a fake build log/system status screen.
- **Session Analysis:** 
  - Real-time tracking of WPM, Accuracy, and Errors.
  - Historical trends and averages saved to local JSON persistence.
- **Keyboard-First Flow:** Seamless looping from snippet selection to results and back.

## 🛠️ Installation

Ensure you have **Python 3.12+** and **uv** installed.

```bash
# Clone the repository
git clone <repo-url>
cd typing-tool

# Sync dependencies and set up environment
uv sync
```

## ⌨️ Usage

Run the application from the project root:

```bash
uv run python -m typing_tool.main
```

### Key Bindings
- **Enter:** Move to the next line when you reach a newline.
- **Tab:** Progress through indentation blocks.
- **Backspace:** Correct mistakes (the original character is restored).
- **F12:** Toggle Discreet Mode (Boss Key).
- **Ctrl+C:** Exit the session.

## 🏗️ Architecture

- `src/typing_tool/main.py`: Interactive dashboard and session orchestration.
- `src/typing_tool/ui/typing.py`: The core "Virtual Overlay" rendering engine.
- `src/typing_tool/ui/app.py`: TUI layouts and keyboard interaction logic.
- `src/typing_tool/storage/snippets.py`: Multi-source snippet management (Local + GitHub).
- `src/typing_tool/storage/history.py`: JSON-based performance tracking.
- `src/typing_tool/core/session.py`: Metrics and accuracy calculation engine.

## 📂 Project Structure
```text
typing-tool/
├── data/snippets/      # Local curated snippet datasets
├── src/typing_tool/    # Core application package
├── tests/              # Unit tests for session and metrics
└── pyproject.toml      # Dependency and project configuration
```
