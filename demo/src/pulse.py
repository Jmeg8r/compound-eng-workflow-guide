#!/usr/bin/env python3
"""
pulse — personal health metrics CLI
Session 3: Plugin architecture for metric types.

WHAT: Metrics now route to registered plugins that can override display,
      stats computation, and thresholds. Default plugin handles unknown types.
WHY: Session 2 had a single stats function for all metrics. Adding metric-
     specific logic (e.g., sleep quality score, steps goal percentage) was
     heading toward a long if/elif chain. Plugin architecture avoids that.

Usage:
    python pulse.py <logfile.csv> [--filter METRIC] [--days N]

Session 2 learnings applied here:
  - date-parsing-local-vs-utc (9): Plugins receive (datetime.date, float) —
    no date parsing needed inside plugins. Architecture correct from Session 2.
  - plugin-interface-over-conditionals (NEW): Register plugins by metric key
    prefix, not by type field in data. Keeps data clean, routing in code.
  - confidence-score-predicts-fix-complexity (8): Plugin interface designed
    with flexibility first since it's a new abstraction (not premature).
"""

import csv
import sys
import argparse
import statistics
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich import box

# WHAT: Single console instance — pipe/TTY detection at startup
# WHY: rich-console-singleton learning — one instance, consistent behavior
console = Console()


# ---------------------------------------------------------------------------
# Plugin interface
# ---------------------------------------------------------------------------

class MetricPlugin(ABC):
    """
    WHAT: Base class for metric-type plugins.
    WHY: plugin-interface-over-conditionals learning — register by prefix,
         override only what the metric needs different from the default.

    Session 3 design note: The interface is intentionally minimal. Plugins
    receive pre-parsed (datetime.date, float) tuples — no date logic needed
    inside plugins (date-parsing-local-vs-utc learning applied at load time).
    """

    #: String prefix(es) this plugin handles. "sleep" matches "sleep_hours", "sleep_quality".
    prefix: str = ""

    @abstractmethod
    def label(self) -> str:
        """Human-readable display name for this metric type."""
        ...

    def extra_rows(self, values: list[tuple[date, float]]) -> list[tuple[str, str]]:
        """
        WHAT: Optional extra (label, value) rows to add to the Rich table.
        WHY: Plugins can add metric-specific display (goal %, score, trend) without
             touching the default stats rows that always appear.
        Default: no extra rows.
        """
        return []

    def threshold_warning(self, values: list[tuple[date, float]]) -> Optional[str]:
        """
        WHAT: Return a warning string if the latest value exceeds a threshold.
        WHY: Allows per-metric alerting (e.g., 'sleep below 7h tonight').
        Default: no warning.
        """
        return None


class SleepPlugin(MetricPlugin):
    """Plugin for sleep_hours and sleep_quality metrics."""
    prefix = "sleep"

    def label(self) -> str:
        return "Sleep"

    def extra_rows(self, values):
        nums = [v for _, v in values]
        below_7 = sum(1 for n in nums if n < 7.0)
        pct = round(100 * below_7 / len(nums), 1) if nums else 0
        return [("Nights < 7h", f"{below_7} ({pct}%)")]

    def threshold_warning(self, values):
        if not values:
            return None
        latest_val = values[-1][1]
        if latest_val < 6.0:
            return f"Low sleep: {latest_val}h (below 6h threshold)"
        return None


class StepsPlugin(MetricPlugin):
    """Plugin for steps metric with 10,000-step goal tracking."""
    prefix = "steps"
    DAILY_GOAL = 10_000

    def label(self) -> str:
        return "Steps"

    def extra_rows(self, values):
        nums = [v for _, v in values]
        avg = statistics.mean(nums) if nums else 0
        goal_pct = round(100 * avg / self.DAILY_GOAL, 1)
        days_hit = sum(1 for n in nums if n >= self.DAILY_GOAL)
        return [
            ("Goal %", f"{goal_pct}% of {self.DAILY_GOAL:,}/day"),
            ("Days hit goal", f"{days_hit} / {len(nums)}"),
        ]


class DefaultPlugin(MetricPlugin):
    """
    WHAT: Fallback plugin for any unregistered metric name.
    WHY: Ensures every metric renders — unknown types don't crash or get skipped.
    """
    prefix = ""

    def label(self) -> str:
        return "Metric"


# ---------------------------------------------------------------------------
# Plugin registry
# ---------------------------------------------------------------------------

_PLUGINS: list[MetricPlugin] = [
    SleepPlugin(),
    StepsPlugin(),
]
_DEFAULT_PLUGIN = DefaultPlugin()


def get_plugin(metric_name: str) -> MetricPlugin:
    """
    WHAT: Return the best-matching plugin for a metric name.
    WHY: Prefix matching lets one plugin handle metric_name variants
         ('sleep_hours', 'sleep_quality') without registering each explicitly.
    """
    for plugin in _PLUGINS:
        if plugin.prefix and metric_name.lower().startswith(plugin.prefix):
            return plugin
    return _DEFAULT_PLUGIN


# ---------------------------------------------------------------------------
# Data loading (unchanged from Session 2)
# ---------------------------------------------------------------------------

def load_log(filepath):
    """
    WHAT: Read CSV log file into a dict of metric -> list of (date, value) tuples.
    Session 2 fixes retained: raw line parsing for blank detection, field validation,
    datetime.date parsing at load time (date-parsing-local-vs-utc).
    """
    records = defaultdict(list)
    skipped = 0

    with open(filepath, newline="") as f:
        raw_lines = f.readlines()

    header_line = raw_lines[0] if raw_lines else ""
    fieldnames = [h.strip() for h in header_line.strip().split(",")]

    for line_num, raw_line in enumerate(raw_lines[1:], start=2):
        stripped = raw_line.strip()

        if not stripped:
            warnings.warn(f"Line {line_num}: blank row skipped", stacklevel=2)
            skipped += 1
            continue

        parsed_row = next(csv.reader([stripped]))
        if len(parsed_row) != len(fieldnames):
            warnings.warn(
                f"Line {line_num}: expected {len(fieldnames)} columns, "
                f"got {len(parsed_row)} — skipped",
                stacklevel=2,
            )
            skipped += 1
            continue

        row = dict(zip(fieldnames, parsed_row))

        try:
            metric = row.get("metric", "").strip()
            date_str = row.get("date", "").strip()
            value_str = row.get("value", "").strip()

            if not metric or not date_str or not value_str:
                warnings.warn(f"Line {line_num}: missing field(s) — skipped", stacklevel=2)
                skipped += 1
                continue

            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            value = float(value_str)
        except ValueError as e:
            warnings.warn(f"Line {line_num}: parse error ({e}) — skipped", stacklevel=2)
            skipped += 1
            continue

        records[metric].append((parsed_date, value))

    if skipped:
        console.print(f"[yellow]Warning:[/yellow] {skipped} row(s) skipped during load.")

    return records


def filter_records(records, metric_filter=None, days=None):
    """Unchanged from Session 2."""
    result = {}
    cutoff = None
    if days is not None:
        cutoff = date.today() - timedelta(days=days)

    for metric, values in records.items():
        if metric_filter and metric_filter.lower() not in metric.lower():
            continue
        if cutoff:
            values = [(d, v) for d, v in values if d >= cutoff]
        if values:
            result[metric] = values

    return result


def compute_stats(values):
    """Unchanged from Session 2."""
    nums = [v for _, v in values]
    rolling_7 = None
    if len(nums) >= 2:
        window = nums[-7:]
        rolling_7 = round(statistics.mean(window), 2)

    return {
        "count": len(nums),
        "mean": round(statistics.mean(nums), 2),
        "min": min(nums),
        "max": max(nums),
        "rolling_7": rolling_7,
        "latest_date": values[-1][0],
        "latest_value": values[-1][1],
    }


# ---------------------------------------------------------------------------
# Report (Session 3: plugin-aware)
# ---------------------------------------------------------------------------

def print_report(records):
    """
    WHAT: Print a rich terminal dashboard — delegates extra rows to plugins.
    WHY: Session 3 change: each metric's table can now include plugin-specific
         rows (goal %, below-threshold count) without changing this function.
    """
    if not records:
        console.print("[red]No records found (or all filtered out).[/red]")
        return

    for metric, values in sorted(records.items()):
        plugin = get_plugin(metric)
        stats = compute_stats(values)

        title_label = f"{metric.upper().replace('_', ' ')}"
        table = Table(
            title=f"[bold cyan]{title_label}[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Field", style="dim")
        table.add_column("Value", justify="right")

        # Standard rows (same for all metrics)
        table.add_row("Entries", str(stats["count"]))
        table.add_row("Average", str(stats["mean"]))
        table.add_row("Min / Max", f"{stats['min']} / {stats['max']}")
        if stats["rolling_7"]:
            table.add_row("Rolling 7-day avg", str(stats["rolling_7"]))
        table.add_row("Latest", f"{stats['latest_date']} → {stats['latest_value']}")

        # Plugin-specific rows
        for label, val in plugin.extra_rows(values):
            table.add_row(label, val)

        console.print(table)

        # Plugin threshold warning
        warning = plugin.threshold_warning(values)
        if warning:
            console.print(f"  [bold red]⚠[/bold red]  {warning}")

        console.print()


# ---------------------------------------------------------------------------
# Entry point (unchanged from Session 2)
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="pulse",
        description="Personal health metrics dashboard from a CSV log file.",
    )
    parser.add_argument("logfile", help="Path to CSV log file (date,metric,value)")
    parser.add_argument(
        "--filter",
        dest="metric_filter",
        metavar="METRIC",
        help="Filter to metrics containing this string (case-insensitive)",
    )
    parser.add_argument(
        "--days",
        type=int,
        metavar="N",
        help="Only show data from the last N days",
    )
    args = parser.parse_args()

    records = load_log(args.logfile)
    records = filter_records(records, metric_filter=args.metric_filter, days=args.days)
    print_report(records)


if __name__ == "__main__":
    main()
