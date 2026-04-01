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

    # debates subcommand
    debates_parser = subparsers.add_parser(
        "debates", help="List all recorded debate sessions with branch trees"
    )
    debates_parser.add_argument(
        "--limit", "-n", type=int, default=30,
        help="Number of sessions to show (default: 30)"
    )
    debates_parser.add_argument(
        "--db", default=".crucible_memory.db",
        help="Path to the SQLite memory database"
    )

    # replay subcommand
    replay_parser = subparsers.add_parser("replay", help="Replay a recorded debate")
    replay_parser.add_argument("debate_id", help="Debate session ID to replay")
    replay_parser.add_argument(
        "--from-round", type=int, default=None, metavar="N",
        help="Start replay from round N"
    )
    replay_parser.add_argument(
        "--speed", type=float, default=1.0,
        help="Playback speed multiplier (default: 1.0, use 0 for instant)"
    )
    replay_parser.add_argument(
        "--db", default=".crucible_memory.db",
        help="Path to the SQLite memory database"
    )

    # branch subcommand
    branch_parser = subparsers.add_parser(
        "branch", help="Fork a recorded debate from a specific round"
    )
    branch_parser.add_argument("debate_id", help="Source debate session ID")
    branch_parser.add_argument(
        "--round", "-r", type=int, required=True, dest="branch_round",
        help="Round number to branch from (1=after openings, 2=after cross-exam)"
    )
    branch_parser.add_argument(
        "--persona", action="append", dest="personas", default=[],
        help="Persona name to include in the branch (repeat for multiple)"
    )
    branch_parser.add_argument(
        "--prompt", default=None,
        help="Override the debate topic/prompt for the branch"
    )
    branch_parser.add_argument(
        "--db", default=".crucible_memory.db",
        help="Path to the SQLite memory database"
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

    # web subcommand
    web_parser = subparsers.add_parser("web", help="Start the debate web UI")
    web_parser.add_argument(
        "--port", "-p", type=int, default=8420,
        help="Port to listen on (default: 8420)"
    )
    web_parser.add_argument(
        "--db", default=".crucible_memory.db",
        help="Path to the SQLite memory database"
    )
    web_parser.add_argument(
        "--no-browser", action="store_true",
        help="Do not open browser automatically"
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

    # society subcommand
    society_parser = subparsers.add_parser(
        "society", help="Inspect the Agent Society — identities, XP, relationships"
    )
    society_sub = society_parser.add_subparsers(dest="society_command")

    society_status_parser = society_sub.add_parser(
        "status", help="Show all agents: level, XP, top skills"
    )
    society_status_parser.add_argument(
        "--db", default=".crucible_memory.db",
        help="Path to the SQLite database (default: .crucible_memory.db)"
    )

    society_rel_parser = society_sub.add_parser(
        "relationships", help="Show the trust graph between agents"
    )
    society_rel_parser.add_argument(
        "--db", default=".crucible_memory.db",
        help="Path to the SQLite database"
    )

    society_hist_parser = society_sub.add_parser(
        "history", help="Show an agent's evolution over time"
    )
    society_hist_parser.add_argument("agent_name", help="Agent name to inspect")
    society_hist_parser.add_argument(
        "--db", default=".crucible_memory.db",
        help="Path to the SQLite database"
    )

    society_reset_parser = society_sub.add_parser(
        "reset", help="Reset all society data (requires confirmation)"
    )
    society_reset_parser.add_argument(
        "--db", default=".crucible_memory.db",
        help="Path to the SQLite database"
    )
    society_reset_parser.add_argument(
        "--yes", action="store_true",
        help="Skip confirmation prompt"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # these commands don't need an API key
    needs_api_key = args.command not in (
        "templates", "history", "stats", "debates", "replay", "society"
    ) and not (
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

    if args.command == "debates":
        _cmd_debates(args)
        return

    if args.command == "replay":
        await _cmd_replay(args)
        return

    if args.command == "branch":
        await _cmd_branch(args)
        return

    if args.command == "society":
        _cmd_society(args)
        return

    if args.command == "deploy":
        await _cmd_deploy(args)
        return

    if args.command == "web":
        await _cmd_web(args)
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
    """Run a debate with real-time streaming output using Rich. Auto-records to SQLite."""
    import anthropic as _anthropic
    from .streaming import DebateRenderer
    from .streaming.stream import DebateStream
    from .replay import DebateRecorder
    from .memory.sqlite_store import SQLiteMemoryStore

    db_path = getattr(args, "db", ".crucible_memory.db")
    store = SQLiteMemoryStore(db_path=db_path)
    recorder = DebateRecorder(store)
    renderer = DebateRenderer(console=console)
    client = _anthropic.AsyncAnthropic(api_key=args.api_key)
    stream = DebateStream(client=client, model=args.model)

    context = getattr(args, "context", "")
    debate_id = recorder.new_session(
        topic=args.topic,
        context=context,
        options=options,
    )

    async for event in recorder.record(
        debate_id,
        stream.run(topic=args.topic, context=context, options=options),
    ):
        renderer.render(event)

    console.print(f"\n[dim]Debate recorded — ID: [cyan]{debate_id}[/cyan][/dim]")
    console.print(f"[dim]Replay: [green]crucible replay {debate_id}[/green][/dim]")


def _cmd_debates(args: Any) -> None:
    """List all recorded debate sessions, grouped into root debates and branches."""
    from .memory.sqlite_store import SQLiteMemoryStore

    store = SQLiteMemoryStore(db_path=args.db)
    sessions = store.list_debate_sessions(limit=args.limit)

    if not sessions:
        console.print("[yellow]No recorded debate sessions found.[/yellow]")
        console.print(
            "[dim]Run a debate with --stream to record it: "
            "[green]crucible debate 'topic' --stream[/green][/dim]"
        )
        return

    # Separate roots from branches
    roots = [s for s in sessions if s["parent_debate_id"] is None]
    branches = {s["id"]: s for s in sessions if s["parent_debate_id"] is not None}

    table = Table(
        title=f"Recorded Debates ({len(sessions)} session(s))",
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("Date", no_wrap=True, style="dim", min_width=16)
    table.add_column("ID", no_wrap=True, style="cyan", min_width=8)
    table.add_column("Topic / Branch info")
    table.add_column("Events", justify="right", no_wrap=True)
    table.add_column("Done", justify="center", no_wrap=True)

    def _short_id(sid: str) -> str:
        return sid[:8]

    def _add_row(s: dict, indent: str = "") -> None:
        done = "[green]✓[/green]" if s["completed"] else "[yellow]…[/yellow]"
        topic_text = indent + s["topic"][:70] + ("…" if len(s["topic"]) > 70 else "")
        table.add_row(
            s["created_at"][:16],
            _short_id(s["id"]),
            topic_text,
            str(s["total_events"]),
            done,
        )

    for root in roots:
        _add_row(root)
        # Show direct children
        children = [b for b in branches.values() if b["parent_debate_id"] == root["id"]]
        for child in children:
            branch_info = f"  └─ [branch @ round {child['branch_round']}] {child['topic'][:50]}"
            done = "[green]✓[/green]" if child["completed"] else "[yellow]…[/yellow]"
            table.add_row(
                child["created_at"][:16],
                _short_id(child["id"]),
                branch_info,
                str(child["total_events"]),
                done,
            )

    # Orphaned branches (parent not in current page)
    known_ids = {s["id"] for s in sessions}
    orphans = [b for b in branches.values() if b["parent_debate_id"] not in known_ids]
    for orphan in orphans:
        _add_row(orphan, indent="[dim](branch)[/dim] ")

    console.print()
    console.print(table)
    console.print()
    console.print(
        "[dim]Replay:[/dim] [green]crucible replay <id>[/green]  "
        "[dim]Branch:[/dim] [green]crucible branch <id> --round 2 --persona pragmatist[/green]"
    )


async def _cmd_replay(args: Any) -> None:
    """Replay a recorded debate to the terminal."""
    from .memory.sqlite_store import SQLiteMemoryStore
    from .replay import DebatePlayer
    from .streaming import DebateRenderer

    store = SQLiteMemoryStore(db_path=args.db)
    session = store.get_debate_session(args.debate_id)
    if session is None:
        console.print(f"[red]No debate session found with ID: {args.debate_id}[/red]")
        console.print("[dim]Run 'crucible debates' to list recorded sessions.[/dim]")
        return

    speed = args.speed if args.speed > 0 else float("inf")
    player = DebatePlayer(store)
    renderer = DebateRenderer(console=console)

    from_round = getattr(args, "from_round", None)
    label = f"from round {from_round}" if from_round else "full replay"
    console.print(Panel(
        f"[bold cyan]Replaying debate[/bold cyan] ({label})\n\n"
        f"Topic: [yellow]{session['topic']}[/yellow]\n"
        f"ID: [dim]{args.debate_id}[/dim]  |  "
        f"Events: {session['total_events']}  |  Speed: {speed}x",
        title="Crucible Replay",
    ))

    if from_round is not None:
        gen = player.replay_from(args.debate_id, round_number=from_round, speed=speed)
    else:
        gen = player.replay(args.debate_id, speed=speed)

    async for event in gen:
        renderer.render(event)


async def _cmd_branch(args: Any) -> None:
    """Fork a recorded debate from a specific round with new personas or prompt."""
    import anthropic as _anthropic
    from .memory.sqlite_store import SQLiteMemoryStore
    from .replay import DebateBrancher, DebateRecorder
    from .streaming import DebateRenderer

    store = SQLiteMemoryStore(db_path=args.db)
    session = store.get_debate_session(args.debate_id)
    if session is None:
        console.print(f"[red]No debate session found with ID: {args.debate_id}[/red]")
        return

    brancher = DebateBrancher(store)
    new_personas = args.personas if args.personas else None
    branch_id = brancher.branch(
        debate_id=args.debate_id,
        round_number=args.branch_round,
        new_personas=new_personas,
        new_prompt=args.prompt,
    )

    console.print(Panel(
        f"[bold cyan]Branch created[/bold cyan]\n\n"
        f"Source: [dim]{args.debate_id[:8]}[/dim]  →  Branch: [cyan]{branch_id[:8]}[/cyan]\n"
        f"Topic: [yellow]{args.prompt or session['topic']}[/yellow]\n"
        f"Forked at: round {args.branch_round}  |  "
        f"Personas: {new_personas or session['personas'] or 'default'}",
        title="Crucible Branch",
    ))

    client = _anthropic.AsyncAnthropic(api_key=args.api_key)
    renderer = DebateRenderer(console=console)

    async for event in brancher.run_branch(branch_id, client=client, model=args.model):
        renderer.render(event)

    console.print(f"\n[dim]Branch complete — ID: [cyan]{branch_id}[/cyan][/dim]")
    console.print(f"[dim]Replay: [green]crucible replay {branch_id}[/green][/dim]")


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


async def _cmd_web(args: Any) -> None:
    from .web.server import run_server

    port: int = getattr(args, "port", 8420)
    db: str = getattr(args, "db", ".crucible_memory.db")
    no_browser: bool = getattr(args, "no_browser", False)
    api_key: str = getattr(args, "api_key", "") or ""
    model: str = getattr(args, "model", "claude-opus-4-6")

    if not no_browser:
        import threading, webbrowser
        threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{port}")).start()

    await run_server(port=port, api_key=api_key, model=model, db_path=db)


def _cmd_society(args: Any) -> None:
    """Dispatch society sub-commands."""
    cmd = getattr(args, "society_command", None)
    if cmd is None:
        console.print("[yellow]Usage: crucible society {status|relationships|history|reset}[/yellow]")
        return
    if cmd == "status":
        _society_status(args)
    elif cmd == "relationships":
        _society_relationships(args)
    elif cmd == "history":
        _society_history(args)
    elif cmd == "reset":
        _society_reset(args)
    else:
        console.print(f"[red]Unknown society command: {cmd}[/red]")


def _society_status(args: Any) -> None:
    from .society.store import SocietyStore

    store = SocietyStore(db_path=args.db)
    identities = store.list_identities()

    if not identities:
        console.print("[yellow]No agents in the society yet.[/yellow]")
        console.print("[dim]Run a debate or research task to populate society data.[/dim]")
        return

    table = Table(
        title=f"Agent Society — {len(identities)} agent(s)",
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Level", no_wrap=True)
    table.add_column("XP", justify="right", no_wrap=True)
    table.add_column("To Next", justify="right", no_wrap=True, style="dim")
    table.add_column("Top Skills")
    table.add_column("Creator", no_wrap=True, style="dim")
    table.add_column("Last Active", no_wrap=True, style="dim")

    for ident in identities:
        skills = store.get_skills(ident.agent_id)
        top = ", ".join(s.name for s in sorted(skills, key=lambda x: x.proficiency, reverse=True)[:3])
        to_next = str(ident.xp_to_next_level) if ident.xp_to_next_level else "—"
        level_color = {
            "Novice": "white",
            "Apprentice": "green",
            "Journeyman": "yellow",
            "Expert": "orange3",
            "Master": "bold red",
        }.get(ident.level.value, "white")
        table.add_row(
            ident.name,
            f"[{level_color}]{ident.level.value}[/{level_color}]",
            str(ident.xp),
            to_next,
            top or "—",
            ident.creator,
            ident.last_active.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


def _society_relationships(args: Any) -> None:
    from .society.store import SocietyStore

    store = SocietyStore(db_path=args.db)
    relationships = store.all_relationships()

    if not relationships:
        console.print("[yellow]No agent relationships recorded yet.[/yellow]")
        return

    table = Table(
        title="Agent Trust Graph",
        show_header=True,
        header_style="bold magenta",
        expand=True,
    )
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Peer", style="cyan", no_wrap=True)
    table.add_column("Trust", justify="right", no_wrap=True)
    table.add_column("Collaborations", justify="right", no_wrap=True)
    table.add_column("Success Rate", justify="right", no_wrap=True)
    table.add_column("Auto-Team?", justify="center", no_wrap=True)
    table.add_column("Last Interaction", no_wrap=True, style="dim")

    for rel in relationships:
        trust_color = "green" if rel.trust >= 0.7 else "yellow" if rel.trust >= 0.5 else "red"
        table.add_row(
            rel.agent_id,
            rel.peer_id,
            f"[{trust_color}]{rel.trust:.2f}[/{trust_color}]",
            str(rel.collaboration_count),
            f"{rel.success_rate:.0%}",
            "[green]yes[/green]" if rel.can_form_team else "[dim]no[/dim]",
            rel.last_interaction.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


def _society_history(args: Any) -> None:
    from .society.store import SocietyStore

    store = SocietyStore(db_path=args.db)
    identity = store.get_identity_by_name(args.agent_name)

    if identity is None:
        console.print(f"[red]Agent '{args.agent_name}' not found.[/red]")
        return

    console.print(Panel(
        f"[bold cyan]{identity.name}[/bold cyan]\n"
        f"Level: [yellow]{identity.level.value}[/yellow]  XP: {identity.xp}\n"
        f"Creator: {identity.creator}  Type: {identity.agent_type}\n"
        f"Born: {identity.created_at.strftime('%Y-%m-%d %H:%M')}  "
        f"Last active: {identity.last_active.strftime('%Y-%m-%d %H:%M')}",
        title="Identity",
    ))

    # Personality evolution
    snapshots = store.get_personality_history(identity.agent_id, limit=20)
    if snapshots:
        snap_table = Table(title="Personality Evolution", expand=True)
        snap_table.add_column("Cycle", justify="right", no_wrap=True, style="dim")
        snap_table.add_column("Curiosity", justify="right")
        snap_table.add_column("Caution", justify="right")
        snap_table.add_column("Creativity", justify="right")
        snap_table.add_column("Precision", justify="right")
        snap_table.add_column("Collab", justify="right")
        snap_table.add_column("Independence", justify="right")
        snap_table.add_column("Reason", style="dim")
        for s in snapshots:
            t = s.traits
            snap_table.add_row(
                str(s.cycle),
                f"{t.get('curiosity', 0):.2f}",
                f"{t.get('caution', 0):.2f}",
                f"{t.get('creativity', 0):.2f}",
                f"{t.get('precision', 0):.2f}",
                f"{t.get('collaboration', 0):.2f}",
                f"{t.get('independence', 0):.2f}",
                s.reason[:40],
            )
        console.print(snap_table)
    else:
        console.print("[dim]No personality snapshots recorded yet.[/dim]")

    # XP history
    xp_history = store.get_xp_history(identity.agent_id, limit=15)
    if xp_history:
        xp_table = Table(title="XP History (latest 15)", expand=True)
        xp_table.add_column("Event", style="cyan")
        xp_table.add_column("Amount", justify="right")
        xp_table.add_column("Balance", justify="right")
        xp_table.add_column("Context", style="dim")
        xp_table.add_column("When", style="dim", no_wrap=True)
        for tx in xp_history:
            amt = tx["amount"]
            color = "green" if amt > 0 else "red" if amt < 0 else "dim"
            xp_table.add_row(
                tx["event"],
                f"[{color}]{amt:+d}[/{color}]",
                str(tx["balance_after"]),
                tx["context"][:40],
                tx["occurred_at"][:16],
            )
        console.print(xp_table)


def _society_reset(args: Any) -> None:
    from .society.store import SocietyStore

    if not getattr(args, "yes", False):
        confirm = input("This will wipe ALL society data. Type 'yes' to confirm: ")
        if confirm.strip().lower() != "yes":
            console.print("[yellow]Aborted.[/yellow]")
            return

    store = SocietyStore(db_path=args.db)
    store.reset()
    console.print("[green]Society data reset successfully.[/green]")


if __name__ == "__main__":
    main()
