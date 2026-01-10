"""Production CLI interface for the Hallucination-Free LLM Engine.

Provides commands for:
- Ingesting documents into the knowledge base
- Querying the engine with natural language questions
- Viewing knowledge base statistics
"""

import argparse
from graph import build_hallucination_free_graph, run_query
from retriever import HybridRetriever
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel
import sys


console = Console()


def ingest_command(args):
    """Handle document ingestion."""
    retriever = HybridRetriever()
    
    console.print(f"\n[yellow]📥 Ingesting documents...[/yellow]")
    
    try:
        num_chunks = retriever.ingest_documents(
            source_urls=args.urls if args.urls else None,
            source_files=args.files if args.files else None
        )
        
        console.print(f"[green]✅ Successfully indexed {num_chunks} chunks[/green]")
        
        # Show updated stats
        stats = retriever.get_stats()
        console.print(f"\n[cyan]📊 Knowledge Base Stats:[/cyan]")
        for key, value in stats.items():
            console.print(f"  {key}: {value}")
            
    except Exception as e:
        console.print(f"[red]❌ Ingestion failed: {e}[/red]")
        sys.exit(1)


def query_command(args):
    """Handle query execution."""
    retriever = HybridRetriever()
    
    # Check if we have documents
    stats = retriever.get_stats()
    if stats["total_documents"] == 0:
        console.print("[yellow]⚠️ Warning: No documents in knowledge base[/yellow]")
        console.print("[yellow]The engine will attempt web search as fallback[/yellow]\n")
    
    # Build graph
    console.print("[cyan]🏗️ Building engine...[/cyan]")
    app = build_hallucination_free_graph(retriever)
    
    # Run query
    console.print(f"\n[bold cyan]❓ Query:[/bold cyan] {args.question}\n")
    
    try:
        result = run_query(app, args.question, verbose=False)
        
        generation = result.get("generation")
        
        if generation:
            # Display answer in a panel
            answer_panel = Panel(
                generation.answer,
                title="[bold green]Answer[/bold green]",
                border_style="green"
            )
            console.print(answer_panel)
            
            # Display confidence
            confidence_color = {
                "High": "green",
                "Medium": "yellow",
                "Low": "red"
            }.get(generation.confidence, "white")
            
            console.print(f"\n[bold]Confidence:[/bold] [{confidence_color}]{generation.confidence}[/{confidence_color}]")
            
            # Display reasoning
            console.print(f"\n[bold]Reasoning:[/bold]")
            console.print(generation.reasoning)
            
            # Display citations in a table
            console.print(f"\n[bold]Citations:[/bold]")
            citation_table = Table(show_header=True, header_style="bold magenta")
            citation_table.add_column("Source ID", style="cyan", width=10)
            citation_table.add_column("Quote", style="white")
            citation_table.add_column("Relevance", style="green", width=10)
            
            for cit in generation.citations:
                citation_table.add_row(
                    str(cit.source_id),
                    cit.quote,
                    f"{cit.relevance_score:.2f}"
                )
            
            console.print(citation_table)
            
            # Display metadata if available
            if generation.metadata:
                console.print(f"\n[dim]Metadata: {generation.metadata}[/dim]")
            
        else:
            console.print("[red]❌ No answer generated[/red]")
            if result.get("errors"):
                console.print(f"[red]Errors:[/red]")
                for error in result["errors"]:
                    console.print(f"  - {error}")
                    
    except Exception as e:
        console.print(f"[red]❌ Query failed: {e}[/red]")
        sys.exit(1)


def stats_command(args):
    """Display knowledge base statistics."""
    retriever = HybridRetriever()
    stats = retriever.get_stats()
    
    console.print("\n[bold cyan]📊 Knowledge Base Statistics[/bold cyan]")
    console.print("="*60)
    
    stats_table = Table(show_header=False, box=None)
    stats_table.add_column("Key", style="cyan", width=25)
    stats_table.add_column("Value", style="white")
    
    for key, value in stats.items():
        stats_table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(stats_table)
    console.print("="*60 + "\n")


def clear_command(args):
    """Clear the knowledge base."""
    if not args.confirm:
        console.print("[yellow]⚠️ This will delete all documents from the knowledge base[/yellow]")
        console.print("[yellow]Use --confirm to proceed[/yellow]")
        return
    
    retriever = HybridRetriever()
    retriever.clear_collection()
    console.print("[green]✅ Knowledge base cleared[/green]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hallucination-Free LLM Engine - Grammar-constrained RAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest documents from URLs
  python main.py ingest --urls https://example.com/doc1 https://example.com/doc2
  
  # Ingest documents from files
  python main.py ingest --files document.pdf article.txt
  
  # Query the engine
  python main.py query "What is retrieval-augmented generation?"
  
  # View statistics
  python main.py stats
  
  # Clear knowledge base
  python main.py clear --confirm
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents into knowledge base")
    ingest_parser.add_argument("--urls", nargs="+", help="URLs to scrape and index")
    ingest_parser.add_argument("--files", nargs="+", help="File paths to index (PDFs, text files)")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query the engine")
    query_parser.add_argument("question", type=str, help="Question to answer")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="View knowledge base statistics")
    
    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear knowledge base")
    clear_parser.add_argument("--confirm", action="store_true", help="Confirm deletion")
    
    args = parser.parse_args()
    
    # Display banner
    console.print("\n[bold cyan]🧠 Hallucination-Free LLM Engine[/bold cyan]")
    console.print("[dim]Grammar-Constrained RAG with Self-Verification[/dim]\n")
    
    # Route to appropriate command
    if args.command == "ingest":
        if not args.urls and not args.files:
            console.print("[red]Error: Must provide --urls or --files[/red]")
            sys.exit(1)
        ingest_command(args)
    elif args.command == "query":
        query_command(args)
    elif args.command == "stats":
        stats_command(args)
    elif args.command == "clear":
        clear_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
