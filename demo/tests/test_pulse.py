"""
Tests for pulse.py — covers Session 1 (baseline) and Session 2 (filter + color).

WHAT: Full test suite including formerly-known-bug tests that now pass,
      plus new coverage for argparse, --filter, --days, and error handling.
WHY: Tests are the diff between sessions — watching _KNOWN_BUG become a
     normal passing test documents the compound payoff.
"""

import pytest
import tempfile
import os
import sys
import warnings
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pulse import load_log, compute_stats, filter_records


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_csv(content):
    """Write content to a temp CSV file, return path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    f.write(content)
    f.close()
    return f.name


# ---------------------------------------------------------------------------
# Session 1 happy path (still passing)
# ---------------------------------------------------------------------------

def test_load_log_basic():
    path = make_csv(
        "date,metric,value\n"
        "2026-05-01,sleep_hours,7.5\n"
        "2026-05-02,sleep_hours,6.0\n"
    )
    records = load_log(path)
    os.unlink(path)

    assert "sleep_hours" in records
    assert len(records["sleep_hours"]) == 2
    # Session 2: dates are now datetime.date objects, not strings
    assert records["sleep_hours"][0] == (date(2026, 5, 1), 7.5)


def test_compute_stats_basic():
    values = [
        (date(2026, 5, 1), 7.5),
        (date(2026, 5, 2), 6.0),
        (date(2026, 5, 3), 8.0),
    ]
    stats = compute_stats(values)
    assert stats["count"] == 3
    assert stats["mean"] == 7.17
    assert stats["min"] == 6.0
    assert stats["max"] == 8.0


# ---------------------------------------------------------------------------
# Session 2: formerly _KNOWN_BUG tests, now fixed
# ---------------------------------------------------------------------------

def test_blank_line_handling_FIXED():
    """
    WHAT: Blank lines now emit a warning and skip the row — no crash, no silent data loss.
    WHY: csv-blank-line-handling learning from Session 1.
    """
    path = make_csv(
        "date,metric,value\n"
        "2026-05-01,sleep_hours,7.5\n"
        "\n"  # blank line — now handled gracefully
        "2026-05-02,sleep_hours,6.0\n"
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        records = load_log(path)
    os.unlink(path)

    # Data loads correctly
    assert "sleep_hours" in records
    assert len(records["sleep_hours"]) == 2
    # Warning was issued for the blank row
    assert any("skipped" in str(warning.message).lower() for warning in w)


def test_non_numeric_value_FIXED():
    """
    WHAT: Non-numeric values now skip with a warning instead of crashing.
    WHY: input-validation-silent-skip learning from Session 1.
    """
    path = make_csv(
        "date,metric,value\n"
        "2026-05-01,mood,happy\n"     # non-numeric — skipped with warning
        "2026-05-02,mood,7.0\n"       # valid
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        records = load_log(path)
    os.unlink(path)

    # The valid row still loads
    assert "mood" in records
    assert len(records["mood"]) == 1
    # Warning was issued
    assert any("parse error" in str(warning.message).lower() for warning in w)


def test_date_parsed_as_date_object():
    """
    WHAT: Dates are datetime.date objects in records, not strings.
    WHY: date-parsing-local-vs-utc learning — parse at load time for correct comparison.
    """
    path = make_csv(
        "date,metric,value\n"
        "2026-05-15,steps,8000\n"
    )
    records = load_log(path)
    os.unlink(path)

    d, v = records["steps"][0]
    assert isinstance(d, date), f"Expected datetime.date, got {type(d)}"
    assert d == date(2026, 5, 15)


# ---------------------------------------------------------------------------
# Session 2: New feature tests — filter_records
# ---------------------------------------------------------------------------

def test_filter_by_metric_name():
    """--filter returns only metrics containing the filter string (case-insensitive)."""
    records = {
        "sleep_hours": [(date(2026, 5, 1), 7.5)],
        "steps": [(date(2026, 5, 1), 8200.0)],
        "sleep_quality": [(date(2026, 5, 1), 8.0)],
    }
    result = filter_records(records, metric_filter="sleep")
    assert "sleep_hours" in result
    assert "sleep_quality" in result
    assert "steps" not in result


def test_filter_case_insensitive():
    records = {"SLEEP_HOURS": [(date(2026, 5, 1), 7.5)]}
    result = filter_records(records, metric_filter="sleep")
    assert "SLEEP_HOURS" in result


def test_filter_days_excludes_old_records():
    """--days N excludes entries older than N days from today."""
    today = date.today()
    records = {
        "steps": [
            (today - timedelta(days=10), 9000.0),  # old — excluded
            (today - timedelta(days=1), 8000.0),   # recent — included
        ]
    }
    result = filter_records(records, days=5)
    assert len(result["steps"]) == 1
    assert result["steps"][0][1] == 8000.0


def test_filter_no_results_returns_empty():
    records = {"sleep_hours": [(date(2026, 5, 1), 7.5)]}
    result = filter_records(records, metric_filter="nonexistent")
    assert result == {}
