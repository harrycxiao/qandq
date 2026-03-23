# Excel Outline (mini version)

Goal: turn a `.xlsx` workbook into a compact JSON outline for LLM use.

The point is not to dump every populated cell. The point is to describe the
layout skeleton:

- anchors like `Sheet!A1`
- maps
- tables
- series rules

## Example

Fixture:

- `intern/excel_outline/fixtures/simple_outline_examples.xlsx`

Sheets:

- `Input`
  `var/value`, with `a = 3` and `b = 4`
- `Output`
  one table with columns `1..10`
  row `a`: `column * a`
  row `b`: `column * b`
  row `c`: `a + b`

Desired idea:

```json
{
  "sheets": [
    {
      "name": "Input",
      "elements": [
        {
          "kind": "map",
          "anchor": "Input!A1",
          "entries": {
            "a": { "anchor": "Input!A2", "value_anchor": "Input!B2", "value": 3 },
            "b": { "anchor": "Input!A3", "value_anchor": "Input!B3", "value": 4 }
          }
        }
      ]
    },
    {
      "name": "Output",
      "elements": [
        {
          "kind": "table",
          "anchor": "Output!A1",
          "columns": { "anchor": "Output!B1", "range": "Output!B1:K1", "start": 1, "end": 10, "step": 1 },
          "series": {
            "a": { "anchor": "Output!A2", "range": "Output!B2:K2", "rule": "column * a" },
            "b": { "anchor": "Output!A3", "range": "Output!B3:K3", "rule": "column * b" },
            "c": { "anchor": "Output!A4", "range": "Output!B4:K4", "rule": "a + b" }
          }
        }
      ]
    }
  ]
}
```

That is the core idea: keep the schema, not the expanded grid.

## Status

- `.xlsx` only
- implementation intentionally not written yet
- spec lives in `intern/excel_outline/test_parser.py`
- parser stub raises `NotImplementedError`

