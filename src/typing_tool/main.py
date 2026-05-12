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

def show_main_menu(console: Console, snippet_manager: SnippetManager):
    console.clear()
    console.print(Panel.fit(
        "[bold blue]Discreet Typing Tool[/bold blue]\n[dim]Improve your code-typing speed and accuracy.[/dim]",
        border_style="blue"
    ))
    
    categories = snippet_manager.get_categories()
    console.print("\n[bold]Select a category:[/bold]")
    for i, cat in enumerate(categories):
        console.print(f" [bold cyan]{i+1}.[/bold cyan] {cat}")
    console.print(" [bold cyan]0.[/bold cyan] Exit")
    
    choice = IntPrompt.ask("\nChoice", choices=[str(i) for i in range(len(categories) + 1)])
    if choice == 0:
        return None
        
    category = categories[choice - 1]
    snippets = snippet_manager.get_snippets_by_category(category)
    
    console.print(f"\n[bold]Snippets in {category}:[/bold]")
    for i, s in enumerate(snippets):
        console.print(f" [bold cyan]{i+1}.[/bold cyan] [{s.language}] {s.title} ({s.difficulty})")
    
    s_choice = IntPrompt.ask("\nSelect snippet", choices=[str(i+1) for i in range(len(snippets))])
    return snippets[s_choice - 1]

def show_results(console: Console, result, history_manager: HistoryManager):
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

    console.print("\n[bold cyan]1.[/bold cyan] Try Another Snippet")
    console.print("[bold cyan]2.[/bold cyan] Exit")
    
    choice = IntPrompt.ask("\nWhat next?", choices=["1", "2"])
    return choice == 1

def main():
    console = Console()
    snippet_manager = SnippetManager()
    history_manager = HistoryManager()
    
    while True:
        selected_snippet = show_main_menu(console, snippet_manager)
        if not selected_snippet:
            break
            
        app = TypingApp(selected_snippet)
        result = app.run()
        
        if result:
            if not show_results(console, result, history_manager):
                break
        else:
            # Cancelled session
            continue

    console.print("\n[dim]Happy coding.[/dim]")

if __name__ == "__main__":
    main()
