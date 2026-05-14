import json
import sys
from pathlib import Path
from .storage.snippets import SnippetManager
from .storage.history import HistoryManager
from .ui.app import TypingApp
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.live import Live
from rich.spinner import Spinner

from .ui.menu import select_item

def show_main_menu(console: Console, snippet_manager: SnippetManager):
    try:
        console.clear()
        console.print(Panel.fit(
            "[bold blue]Discreet Typing Tool[/bold blue]\n[dim]Improve your code-typing speed and accuracy.[/dim]",
            border_style="blue"
        ))

        while True:
            categories = snippet_manager.get_categories()
            # Add Exit as an option in the interactive menu
            menu_items = categories + ["Exit"]

            choice = select_item("Select a category", menu_items)

            if not choice or choice == "Exit":
                return None

            category = choice

            if category == "GitHub Explorer":
                languages = ["Python", "TypeScript", "JavaScript", "SQL", "Bash"]
                selected_lang = select_item("Select a language to explore", languages)
                if not selected_lang:
                    continue

                with Live(Spinner("dots", text=f" Fetching random {selected_lang} snippet from GitHub..."), console=console, transient=True):
                    snippet = snippet_manager.fetch_random_github_snippet(selected_lang)

                if not snippet:
                    console.print("[red]Error: Could not fetch snippet. Check your connection or try a different language.[/red]")
                    continue
                return (snippet, selected_lang)

            # Local categories
            snippets = snippet_manager.get_snippets_by_category(category)
            labels = [f"[{s.language}] {s.title} ({s.difficulty})" for s in snippets]

            selected_snippet = select_item(f"Snippets in {category}", snippets, labels=labels)
            if not selected_snippet:
                continue
            return (selected_snippet, None)
    except (KeyboardInterrupt, EOFError):
        return None

def show_results(console: Console, result, history_manager: HistoryManager):
    try:
        console.clear()
        history_manager.save_result(result)
        
        console.print(Panel.fit("[bold green]Session Summary[/bold green]", border_style="green"))
        
        table = Table(box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold white")
        
        table.add_row("WPM", f"{result.wpm:.1f}")
        table.add_row("Accuracy", f"{result.accuracy:.1f}%")
        table.add_row("Time", f"{result.completion_time:.2f}s")
        table.add_row("Errors", f"[red]{result.errors}[/red]")
        
        console.print(table)
        
        stats = history_manager.get_stats()
        if stats:
            console.print(Panel(
                f"Average: [bold]{stats['avg_wpm']:.1f} WPM[/bold] | [bold]{stats['avg_accuracy']:.1f}% Accuracy[/bold]\n"
                f"Total Sessions: {stats['total_sessions']}",
                title="Historical Trends",
                border_style="dim"
            ))

        choice = select_item(
            "What next?",
            ["Try Another Snippet", "Exit"],
            full_screen=False,
            erase_when_done=False,
        )
        return choice == "Try Another Snippet"
    except (KeyboardInterrupt, EOFError):
        return False

def main():
    console = Console()
    snippet_manager = SnippetManager()
    history_manager = HistoryManager()
    should_exit = False
    
    while True:
        selection = show_main_menu(console, snippet_manager)
        if not selection:
            break
        selected_snippet, github_language = selection
            
        # Select Interaction Mode
        modes = [
            ("ide", "IDE Mode (Auto-pairs, Indentation assist)"),
            ("standard", "Standard (Strict accuracy)")
        ]
        
        mode_choice = select_item(
            "Select Interaction Mode", 
            [m[0] for m in modes], 
            labels=[m[1] for m in modes]
        )
        
        if not mode_choice:
            continue

        while True:
            app = TypingApp(
                selected_snippet,
                mode=mode_choice,
                allow_refresh=bool(github_language),
            )
            result = app.run()

            if result == "refresh_snippet" and github_language:
                with Live(Spinner("dots", text=f" Fetching another {github_language} snippet from GitHub..."), console=console, transient=True):
                    refreshed = snippet_manager.fetch_random_github_snippet(github_language)
                if refreshed:
                    selected_snippet = refreshed
                continue

            if result:
                if not show_results(console, result, history_manager):
                    should_exit = True
                break

            # Cancelled session
            break

        if should_exit:
            break

    console.print("\n[dim]Happy coding.[/dim]")

if __name__ == "__main__":
    main()
