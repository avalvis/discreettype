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

## 🛠️ Launching the Tool

### Smart Launcher (Windows)
A `run.bat` file is provided in the root directory. This script automatically:
1. Verifies that `uv` is installed.
2. Synchronizes your virtual environment and dependencies.
3. Launches the application in the correct environment.

Simply **double-click `run.bat`** to start.

### Create a Professional Shortcut
For the best experience, you can create a desktop shortcut with a custom icon:
1. **Right-click** `run.bat` and select **Send to > Desktop (create shortcut)**.
2. **Right-click** the new shortcut on your desktop and select **Properties**.
3. Under the **Shortcut** tab:
   - Click **Change Icon...**.
   - You can choose a professional system icon (e.g., in `shell32.dll` or `imageres.dll`) or point it to a custom `.ico` file.
   - *Recommendation:* A "terminal" or "code" icon works best for the discreet aesthetic.

## ⌨️ Usage

### Key Bindings
- **↑ / ↓ Arrows:** Navigate menus.
- **Enter:** Confirm selection / Move to next line in session.
- **Tab:** Progress through indentation blocks.
- **Right Arrow (IDE mode):** Move past auto-completed closers (for example `)` in `count(*)`) or skip the current line comment.
- **Left Arrow (IDE mode):** Undo the most recent comment skip.
- **Backspace:** Correct mistakes.
- **F12:** Toggle Discreet Mode (Boss Key).
- **Ctrl+C:** Gracefully exit the current session or menu.

## 🏗️ Architecture

- `src/typing_tool/main.py`: Main dashboard and multi-session loop.
- `src/typing_tool/ui/typing.py`: The core "Virtual Overlay" rendering engine and high-contrast theme.
- `src/typing_tool/ui/app.py`: TUI interaction logic including IDE-assist features.
- `src/typing_tool/ui/menu.py`: Interactive keyboard-navigable menu system.
- `src/typing_tool/storage/github_api.py`: Dynamic GitHub search and content fetching.
- `src/typing_tool/storage/snippets.py`: Multi-source snippet management and categorization.

## 📂 Project Structure
```text
typing-tool/
├── data/snippets/      # Local curated snippet datasets
├── src/typing_tool/    # Core application package
├── tests/              # Unit tests for session and metrics
├── pyproject.toml      # Dependency and project configuration
└── run.bat            # Smart Windows Launcher
```
