"""
Command line interface for GroundCite - AI-powered query analysis library.

This module provides a command-line interface for interacting with the GroundCite
library's query analysis capabilities. It offers commands for analyzing queries,
configuring AI providers, and managing analysis settings.
"""

from typing import Dict, Optional, Any
import click
import json
import asyncio
from pathlib import Path

# Import GroundCite core components  
from .config.settings import AppSettings
from .core.di.core_di import CoreDi
from .core.agents import AIAgent
from .exceptions import GroundCiteError, ConfigurationError

# Rich library for enhanced terminal output
from rich.console import Console
from rich.table import Table
from rich import print as rich_print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Initialize rich console for beautiful terminal output
console = Console()


@click.group()
@click.version_option(version="1.1.0")
def gemini_groundcite_cli():
    """
    GroundCite - AI-powered query analysis and research tool.
    
    Analyze queries using multiple AI providers, web search, content validation,
    and structured data parsing. Perfect for research, fact-checking, and 
    comprehensive query analysis workflows.
    """
    pass


# Maintain backward compatibility
cli = gemini_groundcite_cli


DEFAULT_PARSING_SCHEMA = """{
  "title": "AnalysisResult",
  "type": "object",
  "properties": {
    "summary": {
      "title": "Summary",
      "type": "string",
      "description": "Brief summary of the analysis"
    },
    "key_findings": {
      "title": "Key Findings",
      "type": "array",
      "items": {"type": "string"},
      "description": "Main findings from the analysis"
    },
    "confidence_score": {
      "title": "Confidence Score",
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence level of the analysis (0-1)"
    }
  },
  "required": ["summary", "key_findings"]
}"""


@gemini_groundcite_cli.command(name="analyze")
@click.option('--query', '-q', required=True, help='Query to analyze and research')
@click.option('--validate', '-v', is_flag=True, help='Enable AI-powered content validation')
@click.option('--parse', '-p', is_flag=True, help='Enable structured data parsing')
@click.option('--schema', '-s', default=DEFAULT_PARSING_SCHEMA, help='JSON schema for parsing results')
@click.option('--gemini-key', help='Google Gemini API key')
@click.option('--openai-key', help='OpenAI API key') 
@click.option('--provider', type=click.Choice(['gemini', 'openai']), default='gemini', 
              help='AI provider for parsing operations')
@click.option('--search_model', '-sm', default='gemini-2.5-flash', help='Model name for search request')
@click.option('--validate_model', '-vm', default='gemini-2.5-flash', help='Model name for validation request')
@click.option('--parse_model', '-pm', default='gemini-2.5-flash', help='Model name for parse request')

@click.option('--verbose', is_flag=True, help='Show detailed execution information')
def analyze_query(query: str, validate: bool, parse: bool, schema: str, 
                    gemini_key: Optional[str], openai_key: Optional[str], 
                    provider: str, search_model, validate_model, parse_model, verbose: bool):
    """
    Analyze a query using AI-powered research and analysis.
    
    This command performs comprehensive query analysis including:
    - Web search for relevant information
    - AI-powered content validation (optional)
    - Structured data parsing (optional)
    
    Examples:
        gemini_groundcite analyze -q "What are the latest developments in AI?" --gemini-key your_gemini_key
        gemini_groundcite analyze -q "Company X financials" --validate --parse --gemini-key your_gemini_key
        gemini_groundcite analyze -q "Market trends" --provider openai --verbose --gemini-key your_gemini_key
    """
    try:
        # Show progress indicator for long-running operations
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Initialize configuration
            progress_task = progress.add_task("Initializing analysis configuration...", total=None)
            
            settings: AppSettings = AppSettings()
            
            # Configure analysis parameters
            settings.ANALYSIS_CONFIG.query = query
            settings.ANALYSIS_CONFIG.validate = validate
            settings.ANALYSIS_CONFIG.parse = parse
            settings.ANALYSIS_CONFIG.parse_schema = schema if parse else None
            
            # Configure AI provider settings
            if gemini_key:
                settings.AI_CONFIG.gemini_ai_key_primary = gemini_key
            if openai_key:
                settings.AI_CONFIG.open_ai_key = openai_key
            
            settings.AI_CONFIG.parsing_provider = provider
            settings.AI_CONFIG.search_model_name = search_model
            settings.AI_CONFIG.validate_model_name = validate_model
            settings.AI_CONFIG.parse_model_name = parse_model
            
            # Validate configuration
            progress.update(progress_task, description="Validating configuration...")
            is_valid, errors = settings.validate_all_configurations()
            if not is_valid:
                raise ConfigurationError(
                    "Invalid configuration for analysis",
                    {"errors": errors}
                )
            
            # Initialize AI agent
            progress.update(progress_task, description="Initializing AI agent...")

            agent = AIAgent(settings=settings)
            
            # Execute analysis
            progress.update(progress_task, description="Executing query analysis...")
            analysis_results = asyncio.run(agent.analyze_query())
            
            progress.update(progress_task, description="Formatting results...", completed=100)
        
        # Display comprehensive results
        _display_analysis_results(analysis_results, query, verbose)
        
    except GroundCiteError as e:
        console.print(f"\n❌ GroundCite Error: {e.message}", style="red")
        if verbose and e.details:
            console.print(f"Details: {json.dumps(e.details, indent=2)}", style="dim red")
        raise click.ClickException(str(e))
    except Exception as e:
        console.print(f"\n❌ Unexpected Error: {e}", style="red")
        if verbose:
            import traceback
            console.print(traceback.format_exc(), style="dim red")
        raise click.ClickException(str(e))


# Maintain backward compatibility
@gemini_groundcite_cli.command(name="analyze-legacy")
@click.option('--query', '-q', required=True, help='Query to analyze')
@click.option('--validate', '-v', is_flag=True, help='Should validate')
@click.option('--parse', '-p', is_flag=True, help='Should parse')
@click.option('--schema', '-s', default=DEFAULT_PARSING_SCHEMA, help='Schema for parsing')
def legacy_analyze(query, validate, parse, schema):
    """Legacy analyze command for backward compatibility."""
    return analyze_query(query, validate, parse, schema, None, None, 'gemini', False)



def _display_analysis_results(results: Dict[str, Any], query: str, verbose: bool = False):
    """
    Display comprehensive analysis results with rich formatting.
    
    Args:
        results (Dict[str, Any]): Analysis results from the AI agent
        query (str): Original query that was analyzed
        verbose (bool): Whether to show detailed information
    """
    console.print()
    
    # Display query in a panel
    console.print(Panel(
        query,
        title="[bold blue]Query Analyzed[/bold blue]",
        border_style="blue"
    ))
    
    # Check if analysis was successful
    if not results:
        console.print("\n⚠️  Analysis completed but returned no results", style="yellow")
        return
    
    # Main results table
    table = Table(title="Analysis Results", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", no_wrap=True, width=20)
    table.add_column("Status", style="green", width=15)
    table.add_column("Details", style="yellow")
    
    # Analysis completion status
    completed = results.get("completed", False)
    table.add_row("Overall Status", 
                 "✅ Completed" if completed else "❌ Failed",
                 "Analysis pipeline executed successfully" if completed else "Pipeline execution encountered issues")
    
    # Search results
    search_content = results.get("search_results") or results.get("search_content")
    if search_content:
        search_count = len(search_content) if isinstance(search_content, list) else 1
        table.add_row("Web Search", "✅ Completed", f"Found {search_count} relevant sources")
    else:
        table.add_row("Web Search", "❌ No Results", "No relevant information found")
    
    # Validation results
    validation_enabled = results.get("execution_metrics", {}).get("nodes_completion_status", {}).get("validation", False)
    if validation_enabled:
        validated_content = results.get("validated_content")
        validation_status = "✅ Completed" if validated_content else "❌ Failed"
        table.add_row("Content Validation", validation_status, 
                     "AI validated search results" if validated_content else "Validation process failed")
    
    # Parsing results  
    parsing_enabled = results.get("execution_metrics", {}).get("nodes_completion_status", {}).get("parsing", False)
    if parsing_enabled:
        final_content = results.get("final_content") 
        parsing_status = "✅ Completed" if final_content else "❌ Failed"
        table.add_row("Data Parsing", parsing_status,
                     "Extracted structured data" if final_content else "Failed to parse results")
    
    console.print("\n")
    console.print(table)
    
    # Display main answer/content
    final_content = results.get("final_content") 
    if final_content:
        console.print("\n")
        console.print(Panel(
            str(final_content),
            title="[bold green]Analysis Results[/bold green]",
            border_style="green"
        ))
    
    # Show execution metrics if verbose
    if verbose:
        _display_execution_metrics(results.get("execution_metrics", {}))
    
    # Show success message
    if completed:
        console.print("\n✅ Analysis completed successfully!", style="green")
    else:
        console.print("\n⚠️  Analysis completed with issues", style="yellow")


def _display_execution_metrics(metrics: Dict[str, Any]):
    """Display detailed execution metrics."""
    if not metrics:
        return
        
    console.print("\n")
    metrics_table = Table(title="Execution Metrics", show_header=True, header_style="bold cyan")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="yellow")
    
    # Basic metrics
    if "execution_time_seconds" in metrics:
        metrics_table.add_row("Execution Time", f"{metrics['execution_time_seconds']:.2f} seconds")
    
    if "total_nodes_executed" in metrics:
        metrics_table.add_row("Nodes Executed", str(metrics["total_nodes_executed"]))
    
    if "correlation_id" in metrics:
        metrics_table.add_row("Correlation ID", metrics["correlation_id"])
    
    # Token usage
    if "token_usage" in metrics and metrics["token_usage"]:
        token_info = []
        for operation, tokens in metrics["token_usage"].items():
            if tokens:
                token_info.append(f"{operation}: {tokens}")
        if token_info:
            metrics_table.add_row("Token Usage", " | ".join(token_info))
    
    console.print(metrics_table)


# Legacy function for backward compatibility
def format_category_data(table: Table, category_data: Optional[Dict], query: str):
    """Format and add category data to the table (legacy function)."""
    table.add_row("Query", query)
    
    if category_data is None:
        table.add_row("Status", "[red]No data returned[/red]")
        return False
    elif isinstance(category_data, dict):
        if not category_data:
            table.add_row("Status", "[yellow]Empty results[/yellow]")
            return False
        
        for key, value in category_data.items():
            if isinstance(value, (dict, list)):
                formatted_value = json.dumps(value, indent=2)
                table.add_row(str(key).title(), f"[dim]{formatted_value}[/dim]")
            elif isinstance(value, str) and len(value) > 100:
                table.add_row(str(key).title(), f"{value[:100]}...")
            else:
                table.add_row(str(key).title(), str(value))
        return True
    else:
        table.add_row("Results", str(category_data))
        return True


# Add configuration management commands
@gemini_groundcite_cli.command(name="config")
@click.option('--show', is_flag=True, help='Show current configuration')
@click.option('--validate', is_flag=True, help='Validate current configuration')
def manage_config(show: bool, validate: bool):
    """Manage GroundCite configuration settings."""
    try:
        settings: AppSettings = CoreDi.global_instance().resolve(AppSettings)
        
        if show:
            config_summary = settings.get_configuration_summary()
            console.print("\n")
            console.print(Panel(
                json.dumps(config_summary, indent=2),
                title="[bold blue]Current Configuration[/bold blue]",
                border_style="blue"
            ))
        
        if validate:
            is_valid, errors = settings.validate_all_configurations()
            if is_valid:
                console.print("\n✅ Configuration is valid!", style="green")
            else:
                console.print("\n❌ Configuration has errors:", style="red")
                for error in errors:
                    console.print(f"  • {error}", style="red")
    
    except Exception as e:
        console.print(f"❌ Error managing configuration: {e}", style="red")
        raise click.ClickException(str(e))


@gemini_groundcite_cli.command(name="version")
def show_version():
    """Show GroundCite version and system information."""
    from . import __version__, __author__, __description__
    
    version_info = f"""
GroundCite v{__version__}
{__description__}

Author: {__author__}
Python Library for AI-powered Query Analysis
    """
    
    console.print(Panel(
        version_info.strip(),
        title="[bold green]GroundCite Information[/bold green]",
        border_style="green"
    ))


# Main entry point functions
def main():
    """Main entry point for the GroundCite CLI."""
    try:
        gemini_groundcite_cli()
    except KeyboardInterrupt:
        console.print("\n\n👋 Operation cancelled by user", style="yellow")
    except click.ClickException:
        raise  # Let click handle these
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {e}", style="red")
        raise click.ClickException(str(e))


def cli_main():
    """Alternative entry point (backward compatibility)."""
    main()


if __name__ == "__main__":
    main()