"""
Progress Visualization Demo
============================
Shows 3 ways to visualize progress in Python using the `rich` library:

  1. Progress Bar     — for loops / downloads with a count
  2. Step Tracker     — for multi-phase pipelines (auth → fetch → process → save)
  3. Live Dashboard   — real-time stats panel combining both of the above

Install dependencies first:
    pip install -r requirements.txt

Run:
    python main.py
"""

import time
import random
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
    TaskProgressColumn,
)
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 1 — Simple Progress Bar
# Best for: a single loop where you know the total count upfront.
# Replace the `time.sleep` with your actual work (e.g. API call per ticket).
# ─────────────────────────────────────────────────────────────────────────────

def demo_progress_bar():
    console.rule("[bold cyan]Demo 1: Progress Bar[/bold cyan]")
    console.print("[dim]Simulates downloading 80 tickets one by one.[/dim]\n")

    tickets = list(range(1, 81))  # pretend these are ticket IDs

    with Progress( 
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Downloading tickets", total=len(tickets))

        for ticket_id in tickets:
            # ── replace this with your real work ──
            time.sleep(0.04)
            # ──────────────────────────────────────
            progress.advance(task)

    console.print("\n[bold green]✓ All tickets downloaded![/bold green]\n")
    time.sleep(1)


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 2 — Step-by-Step Tracker
# Best for: pipelines with distinct phases (auth, fetch, process, save).
# Each step can also have its own nested progress bar.
# ─────────────────────────────────────────────────────────────────────────────

PIPELINE_STEPS = [
    ("Authenticating",      "Connecting to the API and validating credentials..."),
    ("Fetching projects",   "Retrieving list of available projects..."),
    ("Downloading tickets", "Pulling all open tickets from the board..."),
    ("Processing data",     "Parsing fields, labels, and attachments..."),
    ("Saving results",      "Writing output to tickets.json..."),
]


def demo_step_tracker():
    console.rule("[bold cyan]Demo 2: Step Tracker[/bold cyan]")
    console.print("[dim]Simulates a 5-step pipeline with individual progress per step.[/dim]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=30),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        overall = progress.add_task("Overall", total=len(PIPELINE_STEPS))
        detail  = progress.add_task("", total=100, visible=False)

        for i, (step_name, step_detail) in enumerate(PIPELINE_STEPS):
            # Update the overall bar label
            progress.update(overall, description=f"Step {i+1}/{len(PIPELINE_STEPS)}: {step_name}")
            console.print(f"  [dim]{step_detail}[/dim]")

            # Show a per-step detail bar
            step_ticks = random.randint(20, 60)
            progress.update(detail, description=f"  [dim]{step_name}[/dim]",
                            total=step_ticks, completed=0, visible=True)

            for _ in range(step_ticks):
                # ── replace this with your real work ──
                time.sleep(0.04)
                # ──────────────────────────────────────
                progress.advance(detail)

            progress.update(detail, visible=False)
            progress.advance(overall)
            console.print(f"  [green]✓ {step_name} complete[/green]")

    console.print("\n[bold green]✓ Pipeline finished![/bold green]\n")
    time.sleep(1)


# ─────────────────────────────────────────────────────────────────────────────
# DEMO 3 — Live Dashboard
# Best for: long-running jobs where you want everything on screen at once —
# current step, ticket count, error count, speed, and elapsed time.
# ─────────────────────────────────────────────────────────────────────────────

def _render_dashboard(
    current_step: int,
    tickets_done: int,
    tickets_total: int,
    errors: int,
    elapsed: float,
    speed: float,
) -> Layout:
    """Build the Rich layout that is refreshed on every tick."""

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body",   ratio=1),
        Layout(name="footer", size=3),
    )
    layout["body"].split_row(
        Layout(name="steps", ratio=2),
        Layout(name="stats", ratio=3),
    )

    # ── Header ────────────────────────────────────────────────────────────────
    layout["header"].update(
        Panel(
            Align.center(Text("Ticket Downloader — Live Dashboard", style="bold white on blue")),
            border_style="blue",
        )
    )

    # ── Steps panel ───────────────────────────────────────────────────────────
    step_names = [s[0] for s in PIPELINE_STEPS]
    step_table = Table(box=box.ROUNDED, show_header=False, expand=True, border_style="dim")
    step_table.add_column("Icon",  width=3)
    step_table.add_column("Step")

    for i, name in enumerate(step_names):
        if i < current_step:
            step_table.add_row("[bold green]✓[/bold green]", name)
        elif i == current_step:
            step_table.add_row("[bold yellow]▶[/bold yellow]", f"[bold yellow]{name}[/bold yellow]")
        else:
            step_table.add_row("[dim]○[/dim]", f"[dim]{name}[/dim]")

    layout["steps"].update(Panel(step_table, title="[bold]Pipeline Steps[/bold]", border_style="cyan"))

    # ── Stats panel ───────────────────────────────────────────────────────────
    pct = int((tickets_done / tickets_total) * 100) if tickets_total else 0
    filled = pct // 5
    bar = f"[cyan]{'█' * filled}[/cyan][dim]{'░' * (20 - filled)}[/dim]"

    stats_table = Table(box=box.ROUNDED, show_header=False, expand=True, border_style="dim")
    stats_table.add_column("Metric", style="bold", min_width=20)
    stats_table.add_column("Value")

    stats_table.add_row("Tickets downloaded",  f"{tickets_done:,} / {tickets_total:,}")
    stats_table.add_row("Progress",            f"{bar} [bold]{pct}%[/bold]")
    stats_table.add_row("Download speed",      f"{speed:.1f} tickets/s")
    stats_table.add_row("Errors",              f"[red]{errors}[/red]" if errors else "[green]0[/green]")
    stats_table.add_row("Elapsed",             f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}")
    stats_table.add_row(
        "Status",
        "[bold green]Complete![/bold green]"
        if current_step >= len(PIPELINE_STEPS)
        else "[bold yellow]Running...[/bold yellow]",
    )

    layout["stats"].update(Panel(stats_table, title="[bold]Stats[/bold]", border_style="cyan"))

    # ── Footer ────────────────────────────────────────────────────────────────
    layout["footer"].update(
        Panel("[dim]Press Ctrl+C to stop[/dim]", border_style="dim")
    )

    return layout


def demo_live_dashboard():
    console.rule("[bold cyan]Demo 3: Live Dashboard[/bold cyan]")
    console.print("[dim]Combines step tracking + stats into one live-updating screen.[/dim]\n")

    total_tickets = 200
    tickets_done  = 0
    errors        = 0
    start         = time.time()

    # Steps and how many tickets each step "downloads" (0 = no ticket work)
    step_workloads = [0, 0, total_tickets, 0, 0]

    with Live(
        _render_dashboard(0, 0, total_tickets, 0, 0, 0),
        refresh_per_second=15,
        console=console,
    ) as live:

        for step_idx, workload in enumerate(step_workloads):

            if workload > 0:
                # This step does the actual downloading
                for _ in range(workload):
                    # ── replace this with your real work ──
                    time.sleep(0.015)
                    # ──────────────────────────────────────
                    tickets_done += 1
                    if random.random() < 0.01:   # 1% error rate
                        errors += 1

                    elapsed = time.time() - start
                    speed   = tickets_done / elapsed if elapsed > 0 else 0
                    live.update(_render_dashboard(step_idx, tickets_done, total_tickets, errors, elapsed, speed))

            else:
                # Non-download step — just animate for a moment
                for _ in range(25):
                    elapsed = time.time() - start
                    speed   = tickets_done / elapsed if elapsed > 0 else 0
                    live.update(_render_dashboard(step_idx, tickets_done, total_tickets, errors, elapsed, speed))
                    time.sleep(0.05)

        # Final frame: mark all steps complete
        elapsed = time.time() - start
        speed   = tickets_done / elapsed if elapsed > 0 else 0
        live.update(_render_dashboard(len(PIPELINE_STEPS), tickets_done, total_tickets, errors, elapsed, speed))
        time.sleep(2)

    console.print("\n[bold green]✓ Dashboard demo complete![/bold green]\n")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    console.print()
    console.print(Panel.fit(
        "[bold]Progress Visualization Demo[/bold]\n"
        "[dim]Three approaches — pick the one that fits your project.[/dim]",
        border_style="blue",
    ))
    console.print()

    demo_progress_bar()
    demo_step_tracker()
    demo_live_dashboard()

    console.print(Panel.fit("[bold green]All demos complete![/bold green]", border_style="green"))
