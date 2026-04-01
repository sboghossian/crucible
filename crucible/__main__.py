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

    # pipelines subcommand — list pre-built pipelines
    subparsers.add_parser("pipelines", help="List pre-built pipelines")

    # pipeline subcommand — run a pre-built pipeline
    pipeline_parser = subparsers.add_parser("pipeline", help="Run a pre-built pipeline")
    pipeline_parser.add_argument("pipeline_name", help="Name of the pipeline to run")
    pipeline_parser.add_argument(
        "--subject", "-s", default="",
        help="Subject for the pipeline"
    )
    pipeline_parser.add_argument(
        "--plan", action="store_true",
        help="Show pipeline stages without running (no API key needed)"
    )

    # compose subcommand — ad-hoc pipeline from template names
    compose_parser = subparsers.add_parser(
        "compose", help="Create and run an ad-hoc pipeline from templates"
    )
    compose_parser.add_argument(
        "templates", nargs="+", help="Template names in execution order"
    )
    compose_parser.add_argument(
        "--subject", "-s", default="",
        help="Subject for the pipeline"
    )
    compose_parser.add_argument(
        "--debate-gates", "-d", action="store_true",
        help="Add a Debate Council gate between every stage"
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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # templates, pipelines and plan-mode don't need an API key
    needs_api_key = args.command not in ("templates", "pipelines") and not (
        args.command in ("deploy", "pipeline") and getattr(args, "plan", False)
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

    if args.command == "pipelines":
        _cmd_pipelines(args)
        return

    if args.command == "pipeline":
        await _cmd_pipeline(args)
        return

    if args.command == "compose":
        await _cmd_compose(args)
        return

    if args.command == "deploy":
        await _cmd_deploy(args)
        return

    from .core.orchestrator import Orchestrator

    orch = Orchestrator(api_key=args.api_key, model=args.model)

    if args.command == "debate":
        options = [o.strip() for o in args.options.split(",") if o.strip()]
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


def _cmd_pipelines(_args: Any) -> None:
    from .templates.pipelines import list_pipelines

    pipelines = list_pipelines()
    console.print()
    console.print(Panel(
        f"[bold cyan]Pre-built Pipelines[/bold cyan]\n"
        f"[dim]{len(pipelines)} pipeline(s) available[/dim]",
        title="Crucible",
    ))

    from rich.table import Table

    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Name", style="cyan", no_wrap=True, min_width=25)
    table.add_column("Stages", justify="center", no_wrap=True)
    table.add_column("Description")

    for p in pipelines:
        stage_chain = " → ".join(s.template_name for s in p.stages)
        table.add_row(p.name, str(len(p.stages)), p.description[:80] + ("…" if len(p.description) > 80 else ""))
        table.add_row("", "", f"[dim]{stage_chain}[/dim]")

    console.print(table)
    console.print()
    console.print(
        "[dim]Run a pipeline:[/dim] [green]crucible pipeline <name> --subject 'Your topic'[/green]"
    )
    console.print(
        "[dim]Ad-hoc pipeline:[/dim] [green]crucible compose t1 t2 t3 --subject 'Your topic'[/green]"
    )


async def _cmd_pipeline(args: Any) -> None:
    from .templates.pipelines import get_pipeline
    from .templates.composer import run_pipeline_cli

    try:
        pipeline = get_pipeline(args.pipeline_name)
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)

    if getattr(args, "plan", False):
        console.print(Panel(
            f"[bold cyan]{pipeline.name}[/bold cyan]\n"
            f"[dim]{pipeline.description}[/dim]\n\n"
            + "\n".join(
                f"  {i + 1}. [cyan]{s.template_name}[/cyan]"
                + (" [yellow](debate gate)[/yellow]" if s.debate_gate else "")
                for i, s in enumerate(pipeline.stages)
            ),
            title="Pipeline Plan",
        ))
        console.print("\n[dim]Run without --plan to execute.[/dim]")
        return

    subject = getattr(args, "subject", "") or pipeline.name
    await run_pipeline_cli(
        pipeline=pipeline,
        subject=subject,
        api_key=args.api_key,
        model=args.model,
        verbose=args.verbose,
    )


async def _cmd_compose(args: Any) -> None:
    from .templates.composer import Pipeline, PipelineBuilder, run_pipeline_cli

    builder = PipelineBuilder(
        name="ad-hoc",
        description=f"Ad-hoc pipeline: {' → '.join(args.templates)}",
    )
    for tmpl_name in args.templates:
        builder.then(
            tmpl_name,
            debate_gate=getattr(args, "debate_gates", False),
        )

    pipeline = builder.build()
    subject = getattr(args, "subject", "") or "ad-hoc pipeline"

    await run_pipeline_cli(
        pipeline=pipeline,
        subject=subject,
        api_key=args.api_key,
        model=args.model,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
