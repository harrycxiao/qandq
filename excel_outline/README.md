# Excel Outline Parser

Mini project for converting `.xlsx` workbooks into a compact JSON outline.

The goal is not to dump every populated cell, but to describe the **structure**
of the workbook in a way that is easy to use for analysis or LLM input.

The parser extracts high-level layout elements such as:

- anchors like `Sheet!A1`
- key/value maps
- tables
- integer column ranges
- series rules inferred from formulas

---

## Example

Fixture:


excel_outline/fixtures/simple_outline_examples.xlsx


Sheets:

- **Input**
  simple key/value map


var | value
a | 3
b | 4


- **Output**
  table with columns `1..10`


series | 1 | 2 | 3 | ... | 10
a | column * a
b | column * b
c | a + b


---

## Desired outline

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
          "columns": {
            "anchor": "Output!B1",
            "range": "Output!B1:K1",
            "start": 1,
            "end": 10,
            "step": 1
          },
          "series": {
            "a": { "rule": "column * a" },
            "b": { "rule": "column * b" },
            "c": { "rule": "a + b" }
          }
        }
      ]
    }
  ]
}
