# Excel CLI Agent

Small CLI utility that routes a workbook question to one of two actions:

- `list_sheets`
- `preview`

The script uses a structured LLM output to decide which tool to call, then runs
the selected Excel helper on a local `.xlsx` file.

## Current tools

- `list_sheets(path)`  
  returns workbook sheet names

- `preview(path, sheet, n)`  
  returns the first `n` rows of a selected sheet

## Usage

```bash
python cli.py <workbook_path> "<question>"
```

Example:

```bash
python cli.py workbook.xlsx "Show me the first 5 rows of the Input sheet"
```
## Notes

- requires `OPENAI_API_KEY` in the environment
- uses `openpyxl`, `pydantic`, and `pydantic_ai`
- currently supports simple sheet listing and preview workflows
