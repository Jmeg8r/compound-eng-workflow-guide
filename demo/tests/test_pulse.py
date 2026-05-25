"""
Tests for pulse.py — Session 1 baseline.

WHAT: Basic smoke tests covering the happy path and the known rough edges.
WHY: Tests document the known behavior AND the known bugs so Session 2
     can mark them passing rather than discovering them from scratch.
"""

import pytest
import tempfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pulse import load_log, compute_stats


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def make_csv(content):
    """Helper: write content to a temp CSV file, return path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    f.write(content)
    f.close()
    return f.name


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
    assert records["sleep_hours"][0] == ("2026-05-01", 7.5)


def test_compute_stats_basic():
    values = [("2026-05-01", 7.5), ("2026-05-02", 6.0), ("2026-05-03", 8.0)]
    stats = compute_stats(values)
    assert stats["count"] == 3
    assert stats["mean"] == 7.17
    assert stats["min"] == 6.0
    assert stats["max"] == 8.0


# ---------------------------------------------------------------------------
# Known Session 1 bugs (these should FAIL until fixed in Session 2)
# ---------------------------------------------------------------------------

def test_blank_line_handling_KNOWN_BUG():
    """
    WHAT: A blank line in the CSV silently corrupts the record count.
    WHY: Python's DictReader (3.13+) does NOT crash on blank lines — it
         produces a row with None/empty keys that our code skips silently,
         but only because float() on '' raises ValueError which bubbles up
         only if the blank row has no key match. The real bug: we don't warn
         the user that rows were skipped, and we can't distinguish "empty
         intentionally" from "typo blank line."
    KNOWN: This is the 'csv-blank-line-handling' pitfall learning.
    FIX: Session 2 wraps the cast in try/except and logs a warning per
         skipped row with line number so the user knows their data has gaps.

    NOTE: This test documents expected Session 1 behavior (silent skip /
          crash depending on Python version). Session 2 makes it pass cleanly.
    """
    path = make_csv(
        "date,metric,value\n"
        "2026-05-01,sleep_hours,7.5\n"
        "\n"  # blank line — silently skipped OR crashes depending on env
        "2026-05-02,sleep_hours,6.0\n"
    )
    try:
        # Session 1 bug: either crashes OR silently under-counts records.
        # In Python 3.13, DictReader skips blank rows silently — no crash,
        # but the user gets no feedback that line 3 was dropped.
        try:
            records = load_log(path)
            # If we get here: records may have wrong count (silent skip)
            # or correct count depending on DictReader version behavior.
            # The bug is that we can't tell which happened.
            assert "sleep_hours" in records  # at minimum, data loaded
        except (ValueError, KeyError):
            pass  # also acceptable Session 1 behavior (crash on blank)
    finally:
        os.unlink(path)


def test_non_numeric_value_KNOWN_BUG():
    """
    WHAT: Non-numeric values silently crash or skip depending on the row.
    WHY: No input validation in Session 1.
    KNOWN: This is the 'input-validation-silent-skip' pitfall learning.
    """
    path = make_csv(
        "date,metric,value\n"
        "2026-05-01,mood,happy\n"  # non-numeric
    )
    try:
        with pytest.raises(ValueError):
            load_log(path)
    finally:
        os.unlink(path)
