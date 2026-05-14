# DiscreetType 😶‍🌫️⌨️

A professional, minimal terminal-based typing practice app for Windows Terminal and PowerShell.

DiscreetType brings a Monkeytype-inspired typing experience into the terminal while keeping the whole vibe clean, subdued, and work-safe.

> Built for developers who want to practice on real code without opening a flashy browser typing site.

## ✨ Why DiscreetType?

Most typing apps feel playful, noisy, or generic. DiscreetType is designed to feel like a tool you would actually keep and use — fast, focused, keyboard-first, and polished enough to blend naturally into a professional setup. [cite:1][cite:3]

### At a glance

- 😌 **Clean and discreet** — looks at home in Windows Terminal / PowerShell
- ⚡ **Fast and keyboard-first** — no mouse-heavy flow, no browser friction
- 💻 **Code-oriented practice** — train on syntax-highlighted snippets instead of generic text
- 🧠 **Smart IDE-style helpers** — optional assistive behavior for a more natural coding rhythm
- 📊 **Session stats** — track WPM, accuracy, and progress over time
- 🕶️ **Boss key included** — instantly switch to a harmless professional-looking screen with `F12`

## 🚀 Key Features

### 🪄 Virtual Overlay Engine
A high-performance interaction model that lets you type directly over syntax-highlighted code with near-zero visual lag.

### 🎯 Dual Interaction Modes
Choose the style of practice that fits your mood:

- **Standard Mode** — strict character-by-character accuracy
- **IDE Mode** — modern editor-style conveniences like:
  - auto-pairing for brackets and quotes
  - indentation assist
  - smoother code-oriented practice flow

### 🎨 IDE-Inspired Themes
Professional, high-contrast syntax highlighting designed for dark terminal backgrounds and long sessions.

### 🌍 GitHub Explorer
Fetch truly random production code from top-starred GitHub repositories for nearly endless variety.

### 🗂️ Intelligent Caching
Automatically cache snippets locally so repeat sessions stay smooth and offline practice stays possible.

### 🕶️ Discreet Mode
Press `F12` at any time to mask the app as a build log or system utility screen.

### 📈 Performance Analytics
Get session summaries with WPM, accuracy, and historical trend tracking.

## 🛠️ Quick Start

### Windows

A smart launcher is included in the project root:

```bat
run.bat
```

Or simply **double-click `run.bat`**.

The launcher automatically:

1. Verifies that `uv` is installed
2. Synchronizes dependencies and environment
3. Launches the application correctly

## 📦 Manual Setup

### Requirements

- Windows
- Windows Terminal or PowerShell
- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv)

### Install and run manually

```bash
uv sync
uv run python -m typing_tool.main
```

## ⌨️ Usage

Once launched, everything is designed to stay fast and keyboard-driven.

### Key Bindings

- `↑ / ↓` — Navigate menus
- `Enter` — Confirm selection / move to the next line
- `Esc` — Go back one menu level
- `Tab` — Progress through indentation blocks
- `Right Arrow` — In IDE mode, move past auto-completed closers or skip the current line comment
- `Left Arrow` — In IDE mode, undo the most recent comment skip
- `Backspace` — Correct mistakes
- `F12` — Toggle Discreet Mode
- `Ctrl+C` — Gracefully exit the current session or menu

## 🧩 What makes it different?

DiscreetType is not trying to be just another generic typing test.

It is built around a very specific idea: a typing practice tool that feels modern and satisfying, but still looks subtle and professional enough to use comfortably in real-world work environments. That is the niche. [cite:1][cite:3]

## 🏗️ Architecture

- `src/typing_tool/main.py` — Main dashboard and multi-session loop
- `src/typing_tool/ui/typing.py` — Core virtual overlay rendering engine and theme logic
- `src/typing_tool/ui/app.py` — TUI interaction logic and IDE-assist behavior
- `src/typing_tool/ui/menu.py` — Keyboard-navigable menu system
- `src/typing_tool/storage/github_api.py` — Dynamic GitHub search and content fetching
- `src/typing_tool/storage/snippets.py` — Snippet management, sourcing, and categorization

## 📂 Project Structure

```text
typing-tool/
├── data/snippets/      # Local curated snippet datasets
├── src/typing_tool/    # Core application package
├── tests/              # Unit tests for session and metrics
├── pyproject.toml      # Dependency and project configuration
└── run.bat             # Smart Windows launcher
```

## 🖥️ Optional: Create a Clean Desktop Shortcut

For a nicer day-to-day launch flow:

1. **Right-click** `run.bat`
2. Select **Send to > Desktop (create shortcut)**
3. **Right-click** the new shortcut and open **Properties**
4. Under the **Shortcut** tab, click **Change Icon...**
5. Choose a neutral system icon from `shell32.dll` or `imageres.dll`, or use a custom `.ico`

A terminal or code-themed icon usually fits the aesthetic best.

## 🛣️ Roadmap

Ideas for future versions:

- More snippet sources and language filters
- Better progress history and trend views
- Theme customization
- Packaged standalone release
- Local streaks and achievement tracking
- Linux support

## 🤝 Contributing

Suggestions, bug reports, and improvements are welcome.

If something feels awkward, slow, visually off, or just not polished enough, open an issue.

## 📄 License

Antonis Valvis
