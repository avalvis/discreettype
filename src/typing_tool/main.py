import json
import sys
from pathlib import Path
from .storage.models import Snippet
from .storage.history import HistoryManager
from .ui.app import TypingApp
from rich.console import Console
from rich.table import Table

def main():
    console = Console()
    history_manager = HistoryManager()
    
    # Load snippets
    snippets_path = Path("data/snippets/curated.json")
    if not snippets_path.exists():
        # Fallback for running from src/
        snippets_path = Path("../data/snippets/curated.json")
    
    if not snippets_path.exists():
        console.print(f"[red]Error: Snippets file not found at {snippets_path.absolute()}[/red]")
        sys.exit(1)
        
    with open(snippets_path, "r") as f:
        data = json.load(f)
        snippets = [Snippet(**s) for s in data]

    # Simple selection for MVP
    console.print("[bold blue]Discreet Typing Tool[/bold blue]")
    console.print("Select a snippet to practice:")
    for i, s in enumerate(snippets):
        console.print(f"{i+1}. [{s.language}] {s.title} ({s.difficulty})")
        
    try:
        choice = int(input("> ")) - 1
        if not (0 <= choice < len(snippets)):
            raise ValueError
    except (ValueError, KeyboardInterrupt):
        console.print("Exiting.")
        sys.exit(0)

    selected_snippet = snippets[choice]
    
    # Run the app
    app = TypingApp(selected_snippet)
    result = app.run()
    
    if result:
        # Save result
        history_manager.save_result(result)
        
        # Show results
        console.print("\n[bold green]Session Complete![/bold green]")
        table = Table(title="Performance Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("WPM", f"{result.wpm:.1f}")
        table.add_row("Accuracy", f"{result.accuracy:.1f}%")
        table.add_row("Time", f"{result.completion_time:.2f}s")
        table.add_row("Errors", str(result.errors))
        
        console.print(table)
        
        # Show historical stats
        stats = history_manager.get_stats()
        if stats:
            console.print(f"\n[dim]Historical Average: {stats['avg_wpm']:.1f} WPM | {stats['avg_accuracy']:.1f}% Accuracy | {stats['total_sessions']} sessions[/dim]")

if __name__ == "__main__":
    main()
