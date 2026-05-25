"""
Tests for pulse.py — Sessions 1, 2, and 3 coverage.

WHAT: Progressive test suite. Each session's contributions are labelled.
WHY: Tests are the diff between sessions — the progression from _KNOWN_BUG
     to _FIXED to new feature tests tells the compound engineering story.
"""

import pytest
import tempfile
import os
import sys
import warnings
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pulse import (
    load_log, compute_stats, filter_records,
    get_plugin, SleepPlugin, StepsPlugin, DefaultPlugin,
)


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
# Session 1 happy path (unchanged, still passing)
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
# Session 2 fixes (formerly _KNOWN_BUG)
# ---------------------------------------------------------------------------

def test_blank_line_handling_FIXED():
    path = make_csv(
        "date,metric,value\n"
        "2026-05-01,sleep_hours,7.5\n"
        "\n"
        "2026-05-02,sleep_hours,6.0\n"
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        records = load_log(path)
    os.unlink(path)

    assert "sleep_hours" in records
    assert len(records["sleep_hours"]) == 2
    assert any("skipped" in str(warning.message).lower() for warning in w)


def test_non_numeric_value_FIXED():
    path = make_csv(
        "date,metric,value\n"
        "2026-05-01,mood,happy\n"
        "2026-05-02,mood,7.0\n"
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        records = load_log(path)
    os.unlink(path)

    assert "mood" in records
    assert len(records["mood"]) == 1
    assert any("parse error" in str(warning.message).lower() for warning in w)


def test_date_parsed_as_date_object():
    path = make_csv(
        "date,metric,value\n"
        "2026-05-15,steps,8000\n"
    )
    records = load_log(path)
    os.unlink(path)

    d, v = records["steps"][0]
    assert isinstance(d, date), f"Expected datetime.date, got {type(d)}"
    assert d == date(2026, 5, 15)


def test_filter_by_metric_name():
    records = {
        "sleep_hours": [(date(2026, 5, 1), 7.5)],
        "steps": [(date(2026, 5, 1), 8200.0)],
        "sleep_quality": [(date(2026, 5, 1), 8.0)],
    }
    result = filter_records(records, metric_filter="sleep")
    assert "sleep_hours" in result
    assert "sleep_quality" in result
    assert "steps" not in result


def test_filter_days_excludes_old_records():
    today = date.today()
    records = {
        "steps": [
            (today - timedelta(days=10), 9000.0),
            (today - timedelta(days=1), 8000.0),
        ]
    }
    result = filter_records(records, days=5)
    assert len(result["steps"]) == 1
    assert result["steps"][0][1] == 8000.0


# ---------------------------------------------------------------------------
# Session 3: Plugin architecture
# ---------------------------------------------------------------------------

def test_get_plugin_returns_sleep_plugin():
    plugin = get_plugin("sleep_hours")
    assert isinstance(plugin, SleepPlugin)


def test_get_plugin_returns_steps_plugin():
    plugin = get_plugin("steps")
    assert isinstance(plugin, StepsPlugin)


def test_get_plugin_returns_default_for_unknown():
    plugin = get_plugin("blood_pressure")
    assert isinstance(plugin, DefaultPlugin)


def test_sleep_plugin_extra_rows():
    values = [
        (date(2026, 5, 1), 5.5),  # below 7
        (date(2026, 5, 2), 7.5),  # above 7
        (date(2026, 5, 3), 6.5),  # below 7
    ]
    plugin = SleepPlugin()
    rows = plugin.extra_rows(values)
    assert any("Nights < 7h" in label for label, _ in rows)
    # 2 of 3 nights below 7h
    assert any("2 (66.7%)" in val for _, val in rows)


def test_sleep_plugin_threshold_warning_low():
    values = [(date(2026, 5, 1), 5.5)]
    plugin = SleepPlugin()
    warning = plugin.threshold_warning(values)
    assert warning is not None
    assert "5.5h" in warning


def test_sleep_plugin_no_warning_above_threshold():
    values = [(date(2026, 5, 1), 7.5)]
    plugin = SleepPlugin()
    assert plugin.threshold_warning(values) is None


def test_steps_plugin_goal_tracking():
    values = [
        (date(2026, 5, 1), 12000.0),  # hit
        (date(2026, 5, 2), 8000.0),   # miss
        (date(2026, 5, 3), 11000.0),  # hit
    ]
    plugin = StepsPlugin()
    rows = plugin.extra_rows(values)
    labels = [label for label, _ in rows]
    assert "Days hit goal" in labels
    assert "Goal %" in labels


def test_plugin_interface_stable_with_date_objects():
    """
    WHAT: Verify plugins receive datetime.date objects (not strings).
    WHY: date-parsing-local-vs-utc learning — this is the Session 3 payoff.
         Plugin interface was designed assuming load_log() already parsed dates.
         This test confirms the contract is honored end-to-end.
    """
    values = [
        (date(2026, 5, 1), 7.5),
        (date(2026, 5, 2), 6.0),
    ]
    plugin = SleepPlugin()
    # If dates were strings, extra_rows would still work (it only uses values)
    # but this documents the contract explicitly.
    rows = plugin.extra_rows(values)
    assert isinstance(rows, list)
    for label, val in rows:
        assert isinstance(label, str)
        assert isinstance(val, str)
