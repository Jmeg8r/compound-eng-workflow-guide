#!/usr/bin/env python3
"""
pulse — personal health metrics CLI
Session 1 (bootstrap): naive CSV reader, basic stats, no color output.

WHAT: Reads a CSV log file of daily health/habit metrics and prints summaries.
WHY: Demonstrate Compound Engineering with a simple real-world tool.

Usage:
    python pulse.py <logfile.csv>

Log file format (headers required):
    date,metric,value
    2026-05-01,sleep_hours,7.5
    2026-05-01,steps,8200
    2026-05-02,sleep_hours,6.0
"""

# WHAT: Standard library only — no deps in Session 1
import csv
import sys
import statistics
from collections import defaultdict


def load_log(filepath):
    """
    WHAT: Read CSV log file into a dict of metric -> list of (date, value) tuples.
    WHY: Centralizes parsing so stats functions stay clean.

    NOTE (Session 1): This is the naive version. It will crash on blank lines
    and silently ignore rows with bad float values. Fixed in Session 2.
    """
    records = defaultdict(list)

    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            metric = row["metric"]
            date = row["date"]
            value = float(row["value"])  # BUG: crashes on non-numeric, blank rows
            records[metric].append((date, value))

    return records


def compute_stats(values):
    """
    WHAT: Compute basic stats for a list of floats.
    WHY: Reused across all metric types.
    """
    nums = [v for _, v in values]
    return {
        "count": len(nums),
        "mean": round(statistics.mean(nums), 2),
        "min": min(nums),
        "max": max(nums),
        # TODO(james): add rolling 7-day average in Session 2
    }


def print_report(records):
    """
    WHAT: Print a plain-text summary of all metrics.
    WHY: Session 1 — no color yet. Rich terminal output added in Session 2.
    """
    print("=" * 50)
    print("PULSE — Health Metrics Report")
    print("=" * 50)

    if not records:
        print("No records found.")
        return

    for metric, values in sorted(records.items()):
        stats = compute_stats(values)
        print(f"\n{metric.upper().replace('_', ' ')}")
        print(f"  Entries : {stats['count']}")
        print(f"  Average : {stats['mean']}")
        print(f"  Range   : {stats['min']} – {stats['max']}")
        print(f"  Latest  : {values[-1][0]} → {values[-1][1]}")

    print("\n" + "=" * 50)


def main():
    # WHAT: Entry point — parse args, load, print
    # WHY: Kept flat for Session 1; refactored to argparse in Session 2
    if len(sys.argv) < 2:
        print("Usage: python pulse.py <logfile.csv>")
        sys.exit(1)

    filepath = sys.argv[1]
    records = load_log(filepath)
    print_report(records)


if __name__ == "__main__":
    main()
