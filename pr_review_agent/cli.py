"""Command-line interface for PR Review Agent."""

import os
import json
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from .core.agent import PRReviewAgent
from .core.models import AnalysisConfig, IssueSeverity

# Load environment variables
load_dotenv()

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def main():
    """PR Review Agent - Intelligent code review for multiple git servers."""
    pass


@main.command()
@click.option('--provider', '-p', 
              type=click.Choice(['github', 'gitlab', 'bitbucket']),
              required=True,
              help='Git server provider')
@click.option('--repo', '-r', 
              required=True,
              help='Repository in format owner/repo')
@click.option('--pr', '-n', 
              type=int,
              required=True,
              help='Pull request number')
@click.option('--ai-suggestions', 
              is_flag=True,
              help='Enable AI-powered suggestions')
@click.option('--post-comments', 
              is_flag=True,
              help='Post comments directly on the PR')
@click.option('--output-format', 
              type=click.Choice(['text', 'json']),
              default='text',
              help='Output format')
@click.option('--severity-threshold',
              type=click.Choice(['low', 'medium', 'high', 'critical']),
              default='medium',
              help='Minimum severity threshold for issues')
@click.option('--disable-tools',
              multiple=True,
              help='Disable specific analysis tools')
def review(provider, repo, pr, ai_suggestions, post_comments, output_format, 
           severity_threshold, disable_tools):
    """Review a pull request."""
    
    # Create configuration
    config = AnalysisConfig(
        enable_ai_analysis=ai_suggestions,
        severity_threshold=IssueSeverity(severity_threshold),
        enable_pylint='pylint' not in disable_tools,
        enable_flake8='flake8' not in disable_tools,
        enable_black='black' not in disable_tools,
        enable_mypy='mypy' not in disable_tools,
        enable_bandit='bandit' not in disable_tools,
        enable_safety='safety' not in disable_tools
    )
    
    # Create agent
    agent = PRReviewAgent(config)
    
    # Show progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing PR...", total=None)
        
        try:
            result = agent.review_pr(
                provider=provider,
                repo=repo,
                pr_number=pr,
                post_comments=post_comments
            )
            progress.update(task, description="Analysis complete!")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return
    
    # Display results
    if output_format == 'json':
        _display_json_output(result)
    else:
        _display_text_output(result)


def _display_text_output(result):
    """Display results in text format."""
    console.print("\n" + "="*60)
    console.print(f"[bold blue]PR Review Results[/bold blue]")
    console.print("="*60)
    
    # PR Info
    pr_info = result.pr_info
    console.print(f"\n[bold]PR #{pr_info.number}: {pr_info.title}[/bold]")
    console.print(f"Author: {pr_info.author}")
    console.print(f"Files: {len(pr_info.files_changed)} | +{pr_info.additions} -{pr_info.deletions}")
    console.print(f"Analysis time: {result.analysis_duration:.2f}s")
    
    # Overall Score
    score = result.feedback.overall_score
    score_color = "green" if score >= 8 else "yellow" if score >= 6 else "red"
    console.print(f"\n[bold {score_color}]Overall Score: {score}/10[/bold {score_color}]")
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(Panel(result.feedback.summary, title="Review Summary"))
    
    # Issues Table
    if result.feedback.issues:
        console.print(f"\n[bold]Issues Found ({len(result.feedback.issues)}):[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan", no_wrap=True)
        table.add_column("Line", justify="right")
        table.add_column("Severity", justify="center")
        table.add_column("Category", justify="center")
        table.add_column("Message", style="white")
        
        for issue in result.feedback.issues[:20]:  # Show first 20 issues
            severity_color = {
                "low": "green",
                "medium": "yellow", 
                "high": "red",
                "critical": "bold red"
            }.get(issue.severity.value, "white")
            
            table.add_row(
                issue.file_path,
                str(issue.line_number),
                f"[{severity_color}]{issue.severity.value.upper()}[/{severity_color}]",
                issue.category.value,
                issue.message[:100] + "..." if len(issue.message) > 100 else issue.message
            )
        
        console.print(table)
        
        if len(result.feedback.issues) > 20:
            console.print(f"\n[dim]... and {len(result.feedback.issues) - 20} more issues[/dim]")
    
    # Suggestions
    if result.feedback.suggestions:
        console.print(f"\n[bold]Suggestions:[/bold]")
        for i, suggestion in enumerate(result.feedback.suggestions[:10], 1):
            console.print(f"  {i}. {suggestion}")
    
    # Strengths
    if result.feedback.strengths:
        console.print(f"\n[bold green]Strengths:[/bold green]")
        for strength in result.feedback.strengths:
            console.print(f"  • {strength}")


def _display_json_output(result):
    """Display results in JSON format."""
    output = {
        "pr_info": {
            "number": result.pr_info.number,
            "title": result.pr_info.title,
            "author": result.pr_info.author,
            "files_changed": result.pr_info.files_changed,
            "additions": result.pr_info.additions,
            "deletions": result.pr_info.deletions
        },
        "feedback": {
            "overall_score": result.feedback.overall_score,
            "summary": result.feedback.summary,
            "issues_count": len(result.feedback.issues),
            "suggestions": result.feedback.suggestions,
            "strengths": result.feedback.strengths
        },
        "analysis_duration": result.analysis_duration,
        "provider": result.provider
    }
    
    console.print(json.dumps(output, indent=2, default=str))


@main.command()
@click.option('--provider', '-p',
              type=click.Choice(['github', 'gitlab', 'bitbucket']),
              required=True,
              help='Git server provider')
@click.option('--repo', '-r',
              required=True,
              help='Repository in format owner/repo')
@click.option('--pr', '-n',
              type=int,
              required=True,
              help='Pull request number')
def diff(provider, repo, pr):
    """Show the diff for a pull request."""
    from .providers import GitHubProvider, GitLabProvider, BitbucketProvider
    
    # Get provider
    if provider == 'github':
        pr_provider = GitHubProvider()
    elif provider == 'gitlab':
        pr_provider = GitLabProvider()
    elif provider == 'bitbucket':
        pr_provider = BitbucketProvider()
    else:
        console.print(f"[red]Unsupported provider: {provider}[/red]")
        return
    
    try:
        diff_content = pr_provider.get_diff(repo, pr)
        console.print(diff_content)
    except Exception as e:
        console.print(f"[red]Error fetching diff: {e}[/red]")


@main.command()
def config():
    """Show current configuration."""
    console.print("[bold]PR Review Agent Configuration[/bold]\n")
    
    # Check environment variables
    env_vars = {
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "GITLAB_TOKEN": os.getenv("GITLAB_TOKEN"),
        "GITLAB_URL": os.getenv("GITLAB_URL"),
        "BITBUCKET_USERNAME": os.getenv("BITBUCKET_USERNAME"),
        "BITBUCKET_APP_PASSWORD": os.getenv("BITBUCKET_APP_PASSWORD"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY")
    }
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Variable", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Value", style="dim")
    
    for var, value in env_vars.items():
        status = "✅ Set" if value else "❌ Not set"
        display_value = "***" if value else "Not configured"
        table.add_row(var, status, display_value)
    
    console.print(table)


if __name__ == '__main__':
    main()
