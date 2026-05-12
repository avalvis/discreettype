# Discreet Code Typing Practice

A professional, minimal terminal-based typing practice app designed for developers. It mimics the "Monkeytype" experience while maintaining a subdued, work-safe aesthetic within Windows Terminal or PowerShell.

## 🚀 Key Features

- **Virtual Overlay Engine:** High-performance interaction model that allows typing directly over syntax-highlighted code with zero visual lag.
- **Dual Interaction Modes:**
  - **Standard Mode:** Practice strict character-by-character accuracy.
  - **IDE Mode (NEW):** Train with modern editor conveniences including **Auto-Pairing** (brackets/quotes) and **Indentation Assist** (automatic whitespace skipping).
- **Vibrant High-Contrast Themes:** Professional IDE-inspired syntax highlighting optimized for readability on dark terminal backgrounds.
- **Infinite Variety with GitHub Explorer:** Dynamically fetch truly random production code from the top 50 most-starred repositories on GitHub.
- **Intelligent Caching:** Automatic local caching of GitHub snippets for seamless offline practice.
- **Discreet "Boss Key":** Press `F12` to instantly mask the app as a professional build log or system utility.
- **Performance Analytics:** Detailed session summaries with WPM, Accuracy, and historical trend tracking.

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
- **Enter:** Move to the next line (Auto-skips indentation in IDE Mode).
- **Tab:** Progress through indentation blocks.
- **Backspace:** Correct mistakes (the original character is restored).
- **F12:** Toggle Discreet Mode (Boss Key).
- **Ctrl+C:** Gracefully exit the current session or menu.

## 🏗️ Architecture

- `src/typing_tool/main.py`: Main dashboard and multi-session loop.
- `src/typing_tool/ui/typing.py`: The core "Virtual Overlay" rendering engine and high-contrast theme.
- `src/typing_tool/ui/app.py`: TUI interaction logic including IDE-assist features.
- `src/typing_tool/storage/github_api.py`: Dynamic GitHub search and content fetching.
- `src/typing_tool/storage/snippets.py`: Multi-source snippet management and categorization.

## 📂 Project Structure
```text
typing-tool/
├── data/snippets/      # Local curated snippet datasets
├── src/typing_tool/    # Core application package
├── tests/              # Unit tests for session and metrics
└── pyproject.toml      # Dependency and project configuration
```
