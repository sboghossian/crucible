"""CLI entry point for crucible."""

from __future__ import annotations

import asyncio
import argparse
import logging
import os
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crucible — multi-agent research with adversarial debate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  crucible debate "Should we use microservices?" --options "yes,no,hybrid"
  crucible analyze --repo /path/to/repo --subject "my-project"
  crucible research "State of multi-agent AI frameworks 2025"
  crucible templates
  crucible templates --category "Software Development"
  crucible templates --search "marketing"
  crucible deploy seo_article --subject "Best practices for API design"
  crucible deploy web_app --plan
  crucible pipelines
  crucible pipeline full_product --subject "AI-powered legal assistant"
  crucible compose market_research product_spec web_app --subject "My SaaS idea"
""",
    )
    parser.add_argument(
        "--api-key", default=os.environ.get("ANTHROPIC_API_KEY"),
        help="Anthropic API key (default: ANTHROPIC_API_KEY env var)"
    )
    parser.add_argument(
        "--model", default="claude-opus-4-6",
        help="Claude model to use (default: claude-opus-4-6)"
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--personas-dir", default=None, metavar="DIR",
        help="Directory of YAML/JSON persona files to load (overrides built-in personas)"
    )
    parser.add_argument(
        "--plugins-dir", default=None, metavar="DIR",
        help="Directory of plugin .py files to discover and load"
    )
    parser.add_argument(
        "--plugin", default=None, metavar="MODULE.CLASS",
        help="Explicit plugin to load, e.g. my_module.MyAgent"
    )
    parser.add_argument(
        "--watch-plugins", action="store_true",
        help="Watch --plugins-dir for changes and hot-reload plugins (dev mode)"
    )

    subparsers = parser.add_subparsers(dest="command")

    # debate subcommand
    debate_parser = subparsers.add_parser("debate", help="Run a standalone debate")
    debate_parser.add_argument("topic", help="The topic to debate")
    debate_parser.add_argument(
        "--options", "-o", default="",
        help="Comma-separated list of options to consider"
    )
    debate_parser.add_argument(
        "--context", "-c", default="",
        help="Background context for the debaters"
    )
    debate_parser.add_argument(
        "--stream", action="store_true",
        help="Stream debate events in real-time with live terminal display"
    )

    # analyze subcommand
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a repository")
    analyze_parser.add_argument("--repo", "-r", required=True, help="Path to git repo")
    analyze_parser.add_argument("--subject", "-s", default="", help="Research subject")

    # research subcommand
    research_parser = subparsers.add_parser("research", help="Research a topic")
    research_parser.add_argument("query", help="Research query")

    # templates subcommand
    templates_parser = subparsers.add_parser(
        "templates", help="Browse the agent template marketplace"
    )
    templates_parser.add_argument(
        "--category", "-c", default="",
        help="Filter by category"
    )
    templates_parser.add_argument(
        "--search", "-s", default="",
        help="Search templates by keyword"
    )

    # history subcommand
    history_parser = subparsers.add_parser("history", help="Show debate history")
    history_parser.add_argument(
        "--limit", "-n", type=int, default=20,
        help="Number of debates to show (default: 20)"
    )
    history_parser.add_argument(
        "--db", default=".crucible_memory.db",
        help="Path to the SQLite memory database"
    )

    # stats subcommand
    stats_parser = subparsers.add_parser("stats", help="Show memory store statistics")
    stats_parser.add_argument(
        "--agent", "-a", default="",
        help="Show performance stats for a specific agent"
    )
    stats_parser.add_argument(
        "--db", default=".crucible_memory.db",
        help="Path to the SQLite memory database"
    )

    # deploy subcommand
    deploy_parser = subparsers.add_parser(
        "deploy", help="Deploy a template as an agent team"
    )
    deploy_parser.add_argument("template_name", help="Name of the template to deploy")
    deploy_parser.add_argument(
        "--subject", "-s", default="",
        help="Subject or topic for the agent team to work on"
    )
    deploy_parser.add_argument(
        "--plan", action="store_true",
        help="Show the deployment plan without running agents (no API key needed)"
    )

    # plugins subcommand
    plugins_parser = subparsers.add_parser("plugins", help="Manage and inspect plugins")
    plugins_subparsers = plugins_parser.add_subparsers(dest="plugins_command")
    plugins_list_parser = plugins_subparsers.add_parser("list", help="List registered plugins")
    plugins_list_parser.add_argument(
        "--plugins-dir", default=None, metavar="DIR",
        help="Also load plugins from this directory before listing"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # templates, history, stats, and plugins don't need an API key
    needs_api_key = args.command not in ("templates", "history", "stats", "plugins") and not (
        args.command == "deploy" and getattr(args, "plan", False)
    )

    if needs_api_key and not args.api_key:
        console.print("[red]Error: ANTHROPIC_API_KEY not set[/red]")
        sys.exit(1)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    asyncio.run(_run(args))


async def _run(args: Any) -> None:
    from rich.markdown import Markdown

    if args.command == "templates":
        _cmd_templates(args)
        return

    if args.command == "history":
        _cmd_history(args)
        return

    if args.command == "stats":
        _cmd_stats(args)
        return

    if args.command == "deploy":
        await _cmd_deploy(args)
        return

    if args.command == "plugins":
        _cmd_plugins(args)
        return

    from .core.orchestrator import Orchestrator

    orch = Orchestrator(api_key=args.api_key, model=args.model)

    # Load plugins before running any agents
    plugins_dir = getattr(args, "plugins_dir", None)
    plugin_module = getattr(args, "plugin", None)
    watch_plugins = getattr(args, "watch_plugins", False)

    if plugins_dir:
        orch.load_plugins_from(plugins_dir)
        if watch_plugins:
            from .plugins.loader import PluginWatcher
            watcher = PluginWatcher(plugins_dir)
            watcher.start()

    if plugin_module:
        orch.load_plugin_module(plugin_module)

    if args.command == "debate":
        options = [o.strip() for o in args.options.split(",") if o.strip()]
        if getattr(args, "stream", False):
            await _cmd_debate_streaming(args, options)
        else:
            console.print(Panel(
                f"[bold cyan]Debate Council convening...[/bold cyan]\n\n"
                f"Topic: [yellow]{args.topic}[/yellow]\n"
                f"Options: {options or 'open-ended'}",
                title="Crucible Debate",
            ))
            result = await orch.standalone_debate(
                topic=args.topic,
                context=args.context,
                options=options,
                verbose=args.verbose,
            )
            console.print(Panel(
                f"[bold green]Winner: {result.winner.upper()}[/bold green] "
                f"(score: {result.winner_score:.1f}/10)\n\n"
                f"[dim]Scores: {result.scores}[/dim]",
                title="Result",
            ))
            console.print(Markdown(result.decision or "No decision recorded."))

    elif args.command == "analyze":
        console.print(f"[cyan]Analyzing repo: {args.repo}[/cyan]")
        result = await orch.run(
            subject=args.subject or args.repo,
            repo_path=args.repo,
        )
        console.print(Panel(str(result.get("status")), title="Run complete"))

    elif args.command == "research":
        console.print(f"[cyan]Researching: {args.query}[/cyan]")
        result = await orch.run(
            subject=args.query,
            research_query=args.query,
            run_agents=["research", "pattern_analyst", "debate"],
        )
        console.print(Panel(str(result.get("status")), title="Run complete"))


async def _cmd_debate_streaming(args: Any, options: list[str]) -> None:
    """Run a debate with real-time streaming output using Rich."""
    import anthropic as _anthropic
    from .streaming import DebateRenderer
    from .streaming.stream import DebateStream

    renderer = DebateRenderer(console=console)
    client = _anthropic.AsyncAnthropic(api_key=args.api_key)
    stream = DebateStream(client=client, model=args.model)

    async for event in stream.run(
        topic=args.topic,
        context=getattr(args, "context", ""),
        options=options,
    ):
        renderer.render(event)


def _cmd_templates(args: Any) -> None:
    from .templates import registry

    if getattr(args, "search", ""):
        templates = registry.search(args.search)
        title = f"Templates matching '{args.search}'"
    elif getattr(args, "category", ""):
        all_by_cat = registry.list_categories()
        cat = args.category
        # Case-insensitive partial match
        matched = {
            k: v for k, v in all_by_cat.items()
            if cat.lower() in k.lower()
        }
        templates = [t for ts in matched.values() for t in ts]
        title = f"Templates in '{args.category}'"
    else:
        templates = registry.list_templates()
        title = "Agent Template Marketplace"

    if not templates:
        console.print("[yellow]No templates found.[/yellow]")
        return

    # Group by category
    by_cat: dict[str, list[Any]] = {}
    for t in templates:
        by_cat.setdefault(t.category, []).append(t)

    console.print()
    console.print(Panel(
        f"[bold cyan]{title}[/bold cyan]\n"
        f"[dim]{len(templates)} template(s) across {len(by_cat)} categor{'y' if len(by_cat) == 1 else 'ies'}[/dim]",
        title="Crucible",
    ))

    for category, cat_templates in sorted(by_cat.items()):
        table = Table(
            title=f"[bold]{category}[/bold]",
            show_header=True,
            header_style="bold magenta",
            expand=True,
        )
        table.add_column("Name", style="cyan", no_wrap=True, min_width=30)
        table.add_column("Description")
        table.add_column("Agents", justify="center", no_wrap=True)

        for t in sorted(cat_templates, key=lambda x: x.name):
            table.add_row(
                t.name,
                t.description[:100] + ("…" if len(t.description) > 100 else ""),
                str(len(t.agents)),
            )
        console.print(table)

    console.print()
    console.print(
        "[dim]Deploy a template:[/dim] [green]crucible deploy <name> --subject 'Your topic'[/green]"
    )
    console.print(
        "[dim]Preview a template:[/dim] [green]crucible deploy <name> --plan[/green]"
    )


async def _cmd_deploy(args: Any) -> None:
    from .templates import registry

    try:
        session = registry.deploy_template(
            args.template_name,
            api_key=getattr(args, "api_key", None),
            model=getattr(args, "model", "claude-opus-4-6"),
        )
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)

    tmpl = session.template
    plan = session.plan()

    console.print(Panel(
        f"[bold cyan]{tmpl.name}[/bold cyan]\n"
        f"[dim]{tmpl.description}[/dim]\n\n"
        f"Category: [yellow]{tmpl.category}[/yellow]  |  "
        f"Agents: [green]{len(tmpl.agents)}[/green]  |  "
        f"Version: {tmpl.version}",
        title="Template",
    ))

    # Show agent roster
    table = Table(title="Agent Team", show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan")
    table.add_column("Role")
    for agent in tmpl.agents:
        table.add_row(agent.name, agent.role)
    console.print(table)

    if tmpl.debate_topics:
        console.print(
            f"\n[bold]Debate Council topic:[/bold] {tmpl.debate_topics[0]}"
        )
        if len(tmpl.debate_topics) > 1:
            for opt in tmpl.debate_topics[1:]:
                console.print(f"  • {opt}")

    console.print("\n[bold]Expected outputs:[/bold]")
    for output in tmpl.expected_outputs:
        console.print(f"  ✓ {output}")

    if getattr(args, "plan", False):
        console.print(
            "\n[dim]Plan-only mode. Run without --plan to execute the agent team.[/dim]"
        )
        return

    subject = getattr(args, "subject", "") or tmpl.name
    console.print(
        f"\n[bold cyan]Deploying agent team...[/bold cyan] subject: [yellow]{subject}[/yellow]\n"
    )

    results = await session.run(subject=subject)

    for agent_name, data in results.items():
        if agent_name.startswith("_"):
            continue
        success = data.get("success", False)
        icon = "[green]✓[/green]" if success else "[red]✗[/red]"
        duration = f" ({data.get('duration_seconds', 0):.1f}s)" if "duration_seconds" in data else ""
        console.print(f"\n{icon} [bold]{agent_name}[/bold]{duration}")
        output = data.get("output", "")
        if output and len(str(output)) > 500:
            console.print(str(output)[:500] + "\n[dim]... (truncated, full output in results)[/dim]")
        elif output:
            console.print(str(output))
        if data.get("error"):
            console.print(f"  [red]Error: {data['error']}[/red]")

    meta = results.get("_meta", {})
    console.print(Panel(
        f"[bold green]Deployment complete[/bold green]\n"
        f"Run ID: [dim]{meta.get('run_id', 'n/a')}[/dim]\n"
        f"Expected outputs: {len(tmpl.expected_outputs)}",
        title="Done",
    ))


def _cmd_history(args: Any) -> None:
    from .memory.sqlite_store import SQLiteMemoryStore

    store = SQLiteMemoryStore(db_path=args.db)
    debates = store.get_debate_history(limit=args.limit)

    if not debates:
        console.print("[yellow]No debate history found.[/yellow]")
        return

    table = Table(
        title=f"Debate History (last {len(debates)})",
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("Date", no_wrap=True, style="dim")
    table.add_column("Topic")
    table.add_column("Winner", style="green", no_wrap=True)
    table.add_column("Score", justify="right", no_wrap=True)

    for d in debates:
        table.add_row(
            d["created_at"][:16],
            d["topic"][:80] + ("…" if len(d["topic"]) > 80 else ""),
            d["winner"] or "—",
            f"{d['winner_score']:.1f}",
        )

    console.print()
    console.print(table)
    console.print()


def _cmd_stats(args: Any) -> None:
    from .memory.sqlite_store import SQLiteMemoryStore

    store = SQLiteMemoryStore(db_path=args.db)

    if args.agent:
        perf = store.get_agent_performance(args.agent)
        console.print(Panel(
            f"[bold cyan]{perf['agent_name']}[/bold cyan]\n\n"
            f"Total runs:           [green]{perf['total_runs']}[/green]\n"
            f"Avg run duration:     [yellow]{perf['avg_duration_seconds']:.2f}s[/yellow]\n"
            f"Debates participated: [green]{perf['debates_participated']}[/green]\n"
            f"Debate wins:          [green]{perf['debate_wins']}[/green]\n"
            f"Win rate:             [yellow]{perf['win_rate'] * 100:.1f}%[/yellow]\n"
            f"Avg debate score:     [yellow]{perf['avg_score']:.2f}/10[/yellow]",
            title="Agent Performance",
        ))
        return

    stats = store.get_stats()

    summary = (
        f"[bold cyan]Memory Store Statistics[/bold cyan]\n\n"
        f"Debates:    [green]{stats['debates']}[/green]\n"
        f"Decisions:  [green]{stats['decisions']}[/green]\n"
        f"Learnings:  [green]{stats['learnings']}[/green]\n"
        f"Agent runs: [green]{stats['agent_runs']}[/green]\n"
        f"Memories:   [green]{stats['memories']}[/green]"
    )
    console.print(Panel(summary, title="Stats"))

    if stats["top_agents"]:
        table = Table(title="Top Agents by Runs", show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan")
        table.add_column("Runs", justify="right")
        for row in stats["top_agents"]:
            table.add_row(row["agent_name"], str(row["runs"]))
        console.print(table)

    if stats["debate_winners"]:
        table = Table(title="Debate Winners", show_header=True, header_style="bold magenta")
        table.add_column("Winner", style="green")
        table.add_column("Wins", justify="right")
        for row in stats["debate_winners"]:
            table.add_row(row["winner"], str(row["wins"]))
        console.print(table)

    console.print()


def _cmd_plugins(args: Any) -> None:
    from .plugins.registry import PluginRegistry
    from .plugins.loader import PluginLoader

    plugins_dir = getattr(args, "plugins_dir", None) or getattr(args, "plugins_command_plugins_dir", None)
    # Support --plugins-dir on the subcommand itself
    if hasattr(args, "plugins_dir") and args.plugins_dir:
        loader = PluginLoader()
        loader.load_from_directory(args.plugins_dir)
        loader.load_from_entry_points()

    sub = getattr(args, "plugins_command", None)
    if sub == "list" or sub is None:
        plugins = PluginRegistry.instance().list_plugins()
        if not plugins:
            console.print("[yellow]No plugins registered.[/yellow]")
            console.print(
                "\n[dim]Load plugins with:[/dim] "
                "[green]crucible --plugins-dir ./my_plugins plugins list[/green]"
            )
            return

        table = Table(
            title="Registered Plugins",
            show_header=True,
            header_style="bold magenta",
            expand=True,
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Version", no_wrap=True)
        table.add_column("Source", no_wrap=True)
        table.add_column("Description")

        for p in sorted(plugins, key=lambda x: x.name):
            table.add_row(p.name, p.version, p.source, p.description or "—")

        console.print()
        console.print(table)
        console.print()
    else:
        console.print(f"[red]Unknown plugins command: {sub}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
