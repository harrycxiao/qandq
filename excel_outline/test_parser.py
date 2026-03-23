from __future__ import annotations

from pathlib import Path

#import pytest

from .parser import parse_workbook

FIXTURES_DIR = Path(__file__).with_name("fixtures")
WORKBOOK_PATH = FIXTURES_DIR / "simple_outline_examples.xlsx"

EXPECTED_SHEETS = [
    {
        "name": "Input",
        "elements": [
            {
                "kind": "map",
                "anchor": "Input!A1",
                "entries": {
                    "a": {"anchor": "Input!A2", "value_anchor": "Input!B2", "value": 3},
                    "b": {"anchor": "Input!A3", "value_anchor": "Input!B3", "value": 4},
                },
            }
        ],
    },
    {
        "name": "Output",
        "elements": [
            {
                "kind": "table",
                "anchor": "Output!A1",
                "columns": {
                    "anchor": "Output!B1",
                    "range": "Output!B1:K1",
                    "kind": "integer_range",
                    "start": 1,
                    "end": 10,
                    "step": 1,
                },
                "series": {
                    "a": {
                        "anchor": "Output!A2",
                        "range": "Output!B2:K2",
                        "rule": "column * a",
                        "depends_on": ["Input.a", "column"],
                    },
                    "b": {
                        "anchor": "Output!A3",
                        "range": "Output!B3:K3",
                        "rule": "column * b",
                        "depends_on": ["Input.b", "column"],
                    },
                    "c": {
                        "anchor": "Output!A4",
                        "range": "Output!B4:K4",
                        "rule": "a + b",
                        "depends_on": ["a", "b"],
                    },
                },
            }
        ],
    },
]


#@pytest.mark.xfail(reason="Workbook outline parser is intentionally not implemented yet.")
def test_parse_workbook_spec_for_simple_example_fixture() -> None:
    assert WORKBOOK_PATH.exists(), f"Missing fixture workbook: {WORKBOOK_PATH}"

    outline = parse_workbook(WORKBOOK_PATH)
    assert isinstance(outline, dict)
    assert outline["sheets"] == EXPECTED_SHEETS