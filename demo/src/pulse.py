#!/usr/bin/env python3
"""
pulse — personal health metrics CLI
Session 2: argparse, rich output, error handling, --filter flag.

WHAT: Reads a CSV log of daily health/habit metrics, filters by metric
      name and/or date range, and prints a color-coded terminal dashboard.
WHY: Session 2 applies learnings from Session 1 — error handling, argparse,
     date parsing at load time.

Usage:
    python pulse.py <logfile.csv> [--filter METRIC] [--days N]

Session 1 learnings applied here:
  - csv-blank-line-handling: wrap CSV parsing in try/except, log skipped rows
  - input-validation-silent-skip: validate before casting, surface row index
  - flat-main-before-argparse: refactor sys.argv → argparse now we know the flags
  - date-parsing-local-vs-utc: parse to datetime.date at load time (not display time)
"""

# WHAT: stdlib + rich (see requirements.txt)
import csv
import sys
import argparse
import statistics
import warnings
from collections import defaultdict
from datetime import date, datetime, timedelta

from rich.console import Console
from rich.table import Table
from rich import box

# WHAT: Single console instance — handles color/no-color automatically
# WHY: Rich strips escape codes when stdout is piped; test with `| cat` (terminal-color-fallback learning)
console = Console()


def load_log(filepath):
    """
    WHAT: Read CSV log file into a dict of metric -> list of (date, value) tuples.
    WHY: Centralized parsing with error handling.

    Session 2 fixes from Session 1 learnings:
    - csv-blank-line-handling: skip blank rows, warn with line number
    - input-validation-silent-skip: validate float cast, surface row + column in error
    - date-parsing-local-vs-utc: parse date strings to datetime.date objects HERE,
      not in stats/display functions. Deferring caused inconsistent behavior.
    """
    records = defaultdict(list)
    skipped = 0

    # FIX: csv-blank-line-handling (Session 2) — Python 3.13 DictReader silently
    # drops blank lines without yielding a row. We can't detect them via the
    # DictReader loop. Solution: pre-scan with enumerate() on raw file lines,
    # then parse non-blank lines manually via csv.reader for full row control.
    with open(filepath, newline="") as f:
        raw_lines = f.readlines()

    header_line = raw_lines[0] if raw_lines else ""
    fieldnames = [h.strip() for h in header_line.strip().split(",")]

    for line_num, raw_line in enumerate(raw_lines[1:], start=2):
        stripped = raw_line.strip()

        # Detect blank lines explicitly — they vanish in DictReader
        if not stripped:
            warnings.warn(f"Line {line_num}: blank row skipped", stacklevel=2)
            skipped += 1
            continue

        # Parse the row via csv.reader for proper quoting/escaping
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

        # FIX: input-validation-silent-skip — validate each field before casting
        try:
            metric = row.get("metric", "").strip()
            date_str = row.get("date", "").strip()
            value_str = row.get("value", "").strip()

            if not metric or not date_str or not value_str:
                warnings.warn(
                    f"Line {line_num}: missing field(s) — skipped",
                    stacklevel=2,
                )
                skipped += 1
                continue

            # FIX: date-parsing-local-vs-utc — parse at load time
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
    """
    WHAT: Apply optional metric name filter and date range filter.
    WHY: --filter is Session 2's main new feature.

    Architecture note: date comparison now works correctly because load_log()
    parses dates to datetime.date objects. If we had deferred parsing to here,
    we'd be comparing strings like "2026-05-07" > "2026-05-01" which happens
    to work for ISO dates but is fragile (date-parsing-local-vs-utc learning).
    """
    result = {}

    cutoff = None
    if days is not None:
        cutoff = date.today() - timedelta(days=days)

    for metric, values in records.items():
        # Apply metric filter (case-insensitive substring match)
        if metric_filter and metric_filter.lower() not in metric.lower():
            continue

        # Apply date range filter
        if cutoff:
            values = [(d, v) for d, v in values if d >= cutoff]

        if values:
            result[metric] = values

    return result


def compute_stats(values):
    """
    WHAT: Compute stats for a list of (date, float) tuples.
    WHY: Unchanged from Session 1 except input type is now (datetime.date, float).
    """
    nums = [v for _, v in values]
    rolling_7 = None

    if len(nums) >= 2:
        # WHAT: Rolling 7-day average using the last 7 values (or all if fewer)
        # WHY: 7-day window is the standard for health metric smoothing
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


def print_report(records):
    """
    WHAT: Print a rich terminal dashboard of all metrics.
    WHY: Session 2 — replacing the plain print() calls with rich Table.
    """
    if not records:
        console.print("[red]No records found (or all filtered out).[/red]")
        return

    for metric, values in sorted(records.items()):
        stats = compute_stats(values)

        table = Table(
            title=f"[bold cyan]{metric.upper().replace('_', ' ')}[/bold cyan]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Field", style="dim")
        table.add_column("Value", justify="right")

        table.add_row("Entries", str(stats["count"]))
        table.add_row("Average", str(stats["mean"]))
        table.add_row("Min / Max", f"{stats['min']} / {stats['max']}")
        if stats["rolling_7"]:
            table.add_row("Rolling 7-day avg", str(stats["rolling_7"]))
        table.add_row("Latest", f"{stats['latest_date']} → {stats['latest_value']}")

        console.print(table)
        console.print()


def main():
    # WHAT: argparse entry point (replaces sys.argv from Session 1)
    # WHY: flat-main-before-argparse learning — defer argparse until flags are known
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
