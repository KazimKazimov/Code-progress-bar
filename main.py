"""
ELD Bond Database Update Mock-Up
================================
Mock terminal dashboard for the ELD Bond Database Update process.

The mock-up simulates a 10-step workflow that runs across 23 countries:
    1. Load raw NOM data
    2. Clean and save NOM data
    3. Load raw LINK data
    4. Clean and save LINK data
    5. Load raw USD data
    6. Clean and save USD data
    7. Fit NSS / NS / DISC curves
    8. Calculate zero curves
    9. Calculate discount curves
   10. Calculate fair prices, cheapness, carry, and roll

Install dependencies first:
    pip install -r requirements.txt

Run:
    python3 main.py
"""

import random
import time

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

COUNTRIES = [
    "Brazil",
    "Mexico",
    "Chile",
    "Colombia",
    "Peru",
    "Argentina",
    "Poland",
    "Czech Republic",
    "Hungary",
    "Romania",
    "Turkey",
    "South Africa",
    "Israel",
    "Saudi Arabia",
    "UAE",
    "India",
    "China",
    "Malaysia",
    "Thailand",
    "Indonesia",
    "Philippines",
    "South Korea",
    "Egypt",
]

CURVE_MODELS = ["NSS", "NS", "DISC"]
ANALYTICS_METRICS = ["fair prices", "cheapness", "carry", "roll"]

PROCESS_STEPS = [
    {
        "name": "Load raw NOM data",
        "scope": "NOM ingest",
        "detail": "Load raw nominal sovereign bond files and source manifests for each country.",
        "kind": "raw_load",
        "datatype": "NOM",
    },
    {
        "name": "Clean and save NOM data",
        "scope": "NOM clean save",
        "detail": "Normalize fields, remove stale points, and save curated NOM bond data.",
        "kind": "clean_save",
        "datatype": "NOM",
    },
    {
        "name": "Load raw LINK data",
        "scope": "LINK ingest",
        "detail": "Load raw inflation-linked bond inputs country by country.",
        "kind": "raw_load",
        "datatype": "LINK",
    },
    {
        "name": "Clean and save LINK data",
        "scope": "LINK clean save",
        "detail": "Clean linker cashflows and save curated LINK datasets.",
        "kind": "clean_save",
        "datatype": "LINK",
    },
    {
        "name": "Load raw USD data",
        "scope": "USD ingest",
        "detail": "Stage hard-currency USD bond source data for every market.",
        "kind": "raw_load",
        "datatype": "USD",
    },
    {
        "name": "Clean and save USD data",
        "scope": "USD clean save",
        "detail": "Validate USD bond inputs and save clean downstream-ready outputs.",
        "kind": "clean_save",
        "datatype": "USD",
    },
    {
        "name": "Fit NSS / NS / DISC curves",
        "scope": "Curve calibration",
        "detail": "Fit the full NSS, NS, and DISC curve suite from cleaned bond universes.",
        "kind": "curve_fit",
    },
    {
        "name": "Calculate zero curves",
        "scope": "Zero curve build",
        "detail": "Transform fitted parameters into zero-rate term structures for each country.",
        "kind": "zero_curve",
    },
    {
        "name": "Calculate discount curves",
        "scope": "Discount curve build",
        "detail": "Generate discount factor curves and curve nodes for downstream analytics.",
        "kind": "discount_curve",
    },
    {
        "name": "Calculate fair prices, cheapness, carry, and roll",
        "scope": "Valuation analytics",
        "detail": "Produce final valuation and relative-value outputs for the ELD bond database.",
        "kind": "analytics",
    },
]

TOTAL_COUNTRY_PASSES = len(COUNTRIES) * len(PROCESS_STEPS)
RAW_COUNTRY_LOAD_TOTAL = len(COUNTRIES) * 3
CLEAN_COUNTRY_SAVE_TOTAL = len(COUNTRIES) * 3
CURVE_FIT_TOTAL = len(COUNTRIES) * len(CURVE_MODELS)
ZERO_CURVE_TOTAL = len(COUNTRIES)
DISCOUNT_CURVE_TOTAL = len(COUNTRIES)
ANALYTICS_TOTAL = len(COUNTRIES) * len(ANALYTICS_METRICS)


def _make_progress_bar(completed: int, total: int, width: int = 20) -> str:
    if total <= 0:
        return "[dim]No progress available[/dim]"

    filled = int(width * completed / total)
    percent = int((completed / total) * 100)
    return f"[cyan]{'█' * filled}[/cyan][dim]{'░' * (width - filled)}[/dim] [bold]{percent}%[/bold]"


def _describe_focus(step: dict[str, str], country_index: int, country: str) -> str:
    kind = step["kind"]

    if kind == "raw_load":
        return f"Loading raw {step['datatype']} source files and metadata for {country}."

    if kind == "clean_save":
        return f"Cleaning {step['datatype']} records and saving curated outputs for {country}."

    if kind == "curve_fit":
        model = CURVE_MODELS[country_index % len(CURVE_MODELS)]
        return f"Running {model} calibration for {country} using cleaned NOM, LINK, and USD bonds."

    if kind == "zero_curve":
        return f"Building zero curve nodes for {country} from fitted curve parameters."

    if kind == "discount_curve":
        return f"Generating discount factors and discount curve points for {country}."

    metric = ANALYTICS_METRICS[country_index % len(ANALYTICS_METRICS)]
    return f"Calculating {metric} outputs for {country}."


def _advance_mock_state(state: dict[str, int | str], step: dict[str, str], rng: random.Random) -> None:
    kind = step["kind"]
    state["country_passes_done"] += 1

    if kind == "raw_load":
        state["raw_country_loads"] += 1
        state["staged_bonds"] += rng.randint(90, 220)
    elif kind == "clean_save":
        state["clean_country_saves"] += 1
        state["clean_bonds_saved"] += rng.randint(80, 210)
    elif kind == "curve_fit":
        state["curve_fits"] += len(CURVE_MODELS)
    elif kind == "zero_curve":
        state["zero_curves"] += 1
    elif kind == "discount_curve":
        state["discount_curves"] += 1
    elif kind == "analytics":
        state["analytics_metrics"] += len(ANALYTICS_METRICS)

    if rng.random() < 0.03:
        state["warnings"] += 1


def _render_dashboard(
    current_step: int,
    current_country_index: int,
    state: dict[str, int | str],
    elapsed: float,
    speed: float,
) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=4),
    )
    layout["body"].split_row(
        Layout(name="steps", ratio=3),
        Layout(name="stats", ratio=2),
    )

    layout["header"].update(
        Panel(
            Align.center(Text("ELD Bond Database Update", style="bold white on blue")),
            border_style="blue",
        )
    )

    if current_step >= len(PROCESS_STEPS):
        step_summary = Group(
            Text.from_markup("[bold green]Run complete[/bold green]"),
            Text.from_markup(
                f"[bold]Coverage:[/bold] {len(COUNTRIES)} countries across {len(PROCESS_STEPS)} pipeline steps"
            ),
            Text.from_markup(
                "[bold]Final action:[/bold] Publishing refreshed curves and valuation analytics to the database."
            ),
        )
    else:
        step = PROCESS_STEPS[current_step]
        step_summary = Group(
            Text.from_markup(
                f"[bold yellow]Current step {current_step + 1}/{len(PROCESS_STEPS)}: {step['name']}[/bold yellow]"
            ),
            Text.from_markup(
                f"[bold]Country {current_country_index + 1}/{len(COUNTRIES)}:[/bold] {state['current_country']}"
            ),
            Text.from_markup(f"[bold]Scope:[/bold] {step['scope']}"),
            Text.from_markup(f"[bold]Focus:[/bold] {state['current_focus']}"),
        )

    step_table = Table(
        box=box.ROUNDED,
        expand=True,
        border_style="dim",
        header_style="bold cyan",
    )
    step_table.add_column("State", width=9, no_wrap=True)
    step_table.add_column("Step", ratio=3)
    step_table.add_column("Scope", ratio=2)

    for index, step in enumerate(PROCESS_STEPS):
        if index < current_step:
            state_label = "[green]Done[/green]"
            name = f"[green]{step['name']}[/green]"
            scope = f"[green]{step['scope']}[/green]"
        elif index == current_step and current_step < len(PROCESS_STEPS):
            state_label = "[bold yellow]Running[/bold yellow]"
            name = f"[bold yellow]{step['name']}[/bold yellow]"
            scope = f"[yellow]{step['scope']}[/yellow]"
        else:
            state_label = "[dim]Pending[/dim]"
            name = f"[dim]{step['name']}[/dim]"
            scope = f"[dim]{step['scope']}[/dim]"

        step_table.add_row(state_label, name, scope)

    layout["steps"].update(
        Panel(
            Group(step_summary, Text(""), step_table),
            title="[bold]Pipeline Steps[/bold]",
            border_style="cyan",
        )
    )

    stats_table = Table(box=box.ROUNDED, show_header=False, expand=True, border_style="dim")
    stats_table.add_column("Metric", style="bold", min_width=22)
    stats_table.add_column("Value")

    stats_table.add_row(
        "Country-step progress",
        f"{state['country_passes_done']} / {TOTAL_COUNTRY_PASSES}",
    )
    stats_table.add_row(
        "Overall progress",
        _make_progress_bar(int(state["country_passes_done"]), TOTAL_COUNTRY_PASSES),
    )
    stats_table.add_row(
        "Raw country loads",
        f"{state['raw_country_loads']} / {RAW_COUNTRY_LOAD_TOTAL}",
    )
    stats_table.add_row(
        "Clean country saves",
        f"{state['clean_country_saves']} / {CLEAN_COUNTRY_SAVE_TOTAL}",
    )
    stats_table.add_row("Bond rows staged", f"{state['staged_bonds']:,}")
    stats_table.add_row("Clean bond rows saved", f"{state['clean_bonds_saved']:,}")
    stats_table.add_row("Curve fits", f"{state['curve_fits']} / {CURVE_FIT_TOTAL}")
    stats_table.add_row("Zero curves", f"{state['zero_curves']} / {ZERO_CURVE_TOTAL}")
    stats_table.add_row("Discount curves", f"{state['discount_curves']} / {DISCOUNT_CURVE_TOTAL}")
    stats_table.add_row("Analytics metrics", f"{state['analytics_metrics']} / {ANALYTICS_TOTAL}")
    stats_table.add_row(
        "Warnings",
        f"[yellow]{state['warnings']}[/yellow]" if state["warnings"] else "[green]0[/green]",
    )
    stats_table.add_row("Throughput", f"{speed:.1f} country-passes/s")
    stats_table.add_row("Elapsed", f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}")

    layout["stats"].update(
        Panel(stats_table, title="[bold]Run Stats[/bold]", border_style="cyan")
    )

    layout["footer"].update(
        Panel(
            "[dim]Mock-up run: 10 steps x 23 countries = 230 country passes[/dim]\n"
            "[dim]Press Ctrl+C to stop[/dim]",
            border_style="dim",
        )
    )

    return layout


def run_eld_bond_database_update_mock() -> None:
    console.rule("[bold cyan]ELD Bond Database Update[/bold cyan]")
    console.print("[dim]Mock-up of the 10-step production refresh across 23 countries.[/dim]\n")

    rng = random.Random(7)
    state: dict[str, int | str] = {
        "country_passes_done": 0,
        "raw_country_loads": 0,
        "clean_country_saves": 0,
        "staged_bonds": 0,
        "clean_bonds_saved": 0,
        "curve_fits": 0,
        "zero_curves": 0,
        "discount_curves": 0,
        "analytics_metrics": 0,
        "warnings": 0,
        "current_country": COUNTRIES[0],
        "current_focus": "Initializing run control and loading update manifests.",
    }
    start = time.time()

    with Live(
        _render_dashboard(0, 0, state, 0, 0),
        refresh_per_second=12,
        console=console,
    ) as live:
        for step_index, step in enumerate(PROCESS_STEPS):
            for country_index, country in enumerate(COUNTRIES):
                state["current_country"] = country
                state["current_focus"] = _describe_focus(step, country_index, country)
                _advance_mock_state(state, step, rng)

                elapsed = time.time() - start
                speed = int(state["country_passes_done"]) / elapsed if elapsed > 0 else 0
                live.update(
                    _render_dashboard(step_index, country_index, state, elapsed, speed)
                )
                time.sleep(0.035 if step["kind"] in {"raw_load", "clean_save"} else 0.045)

        state["current_country"] = "All countries"
        state["current_focus"] = "Publishing refreshed data, curves, and analytics to the ELD bond database."
        elapsed = time.time() - start
        speed = int(state["country_passes_done"]) / elapsed if elapsed > 0 else 0
        live.update(
            _render_dashboard(len(PROCESS_STEPS), len(COUNTRIES) - 1, state, elapsed, speed)
        )
        time.sleep(1.5)

    console.print("\n[bold green]ELD Bond Database Update mock-up complete![/bold green]\n")


if __name__ == "__main__":
    console.print()
    console.print(
        Panel.fit(
            "[bold]ELD Bond Database Update[/bold]\n"
            "[dim]Mock-up of the 10-step, 23-country production refresh.[/dim]",
            border_style="blue",
        )
    )
    console.print()

    run_eld_bond_database_update_mock()

    console.print(
        Panel.fit(
            "[bold green]ELD Bond Database Update complete![/bold green]",
            border_style="green",
        )
    )
